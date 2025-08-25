# analyzer.py
import os, io, json, base64, re
from typing import Dict, Any, List, Tuple
from pathlib import Path
from PIL import Image

# Load .env from project root and current dir
try:
    from dotenv import load_dotenv, find_dotenv
    load_dotenv(find_dotenv(), override=False)
    load_dotenv(Path(__file__).resolve().parents[1] / ".env", override=False)
except Exception:
    pass

from openai import OpenAI

# EasyOCR for grounding CTAs (prevents LLM hallucinations)
import easyocr


# ---------- CTA heuristics ----------
CTA_VERBS = {
    "book","schedule","get","start","join","apply","enroll","try","download",
    "learn","read","view","see","buy","purchase","contact","call","subscribe",
    "request","speak","talk","watch","play","claim","choose","select","download",
    "claim","claim your","limited time","exclusive","bonus","bonuses","free",
    "money back","guarantee","total","all bonuses","included","spots available"
}
GOAL_SYNONYMS = {
    "book_call": [
        "book a call","schedule a call","book call","schedule call",
        "speak to sales","talk to sales","discovery call","strategy call",
        "free consultation","consultation","meeting","request a call","call now"
    ],
    "get_demo": ["get a demo","book a demo","request demo","see a demo","schedule demo","product tour"],
    "signup": ["sign up","create account","register","join now","get started","start trial","start free"],
    "purchase": ["buy now","purchase","checkout","add to cart","select plan","choose plan","subscribe now"],
    "learn_more": ["learn more","read more","see more","view details","view more","explore"],
    "download": ["download guide","download","get guide","free guide"],
    "claim": ["claim your","claim now","claim today","claim bonus","claim offer"]
}
REVIEW_MARKERS = [
    "review","reviews","testimonial","testimonials","case study","stars","rating","rated",
    "months ago","weeks ago","days ago","★★★★★","★★★★","★★★","★★","★","⭐","4.9/5","4.8/5","5/5","4/5"
]

def _normalize(s: str) -> str:
    return re.sub(r"\s+"," ",re.sub(r"[^a-z0-9 %\-\+\$]"," ",str(s).lower())).strip()

def _is_reviewish(t: str) -> bool:
    tl=_normalize(t)
    return any(m in tl for m in REVIEW_MARKERS)

def _looks_like_cta(t: str) -> bool:
    tl=_normalize(t)
    if not tl or len(tl.split())>12: return False  # Increased from 8 to 12
    
    # Check for exact matches in goal synonyms first
    if any(p in tl for v in GOAL_SYNONYMS.values() for p in v): return True
    
    # Check for CTA verbs at start
    words = tl.split()
    if words and (words[0] in CTA_VERBS): return True
    
    # Check for common CTA patterns
    if any(tl.endswith(s) for s in [" now"," today"," free"," included"," available"]): return True
    
    # Check for action-oriented phrases
    action_patterns = [
        "get started", "start getting", "see how", "see all", "see results",
        "limited time", "exclusive", "bonus", "bonuses", "free", "money back",
        "guarantee", "total", "all bonuses", "included", "spots available",
        "claim your", "custom strategy", "growth plan", "choose your",
        "more leads", "sales calls", "pipeline", "results", "timeline",
        "zero to results", "what you get", "exclusive bonuses", "growth plan",
        "dmp plug", "dmp scale", "dmp agency", "done for you", "custom done"
    ]
    
    if any(pattern in tl for pattern in action_patterns): return True
    
    # Check for button-like text (short, action-oriented)
    if len(words) <= 4 and any(word in CTA_VERBS for word in words): return True
    
    # Check for specific landing page patterns
    landing_page_patterns = [
        "start getting more leads", "book a call", "see how we get you",
        "see all the results", "get started today", "total money back guarantee",
        "limited time all bonuses included", "get 6000 free", "get started",
        "download guide", "claim your custom strategy call"
    ]
    
    if any(pattern in tl for pattern in landing_page_patterns): return True
    
    return False


# ---------- LLM prompt ----------
SYSTEM_PROMPT = """You are a CRO analyst specializing in Call-to-Action (CTA) analysis. You will be given:
(1) a screenshot and (2) a list of OCR-derived CTA candidates (text + bbox).

Your task: Analyze the CTAs and identify any that COMPETE for user attention, focusing on visual and semantic conflicts.

Hard rules
- USE ONLY the provided candidates. Do not invent or change any text.
- All indices in your answer refer to the order of the input candidates list.
- Output STRICT JSON that validates. No extra keys, comments, or prose.
- Focus on ACTUAL conflicts, not just multiple CTAs on a page.

Definitions
- A CTA is "goal-related" if its text matches or closely supports the desired goal.
- A COMPETING SET is 2+ CTAs that genuinely pull attention away from each other because they:
  * Are visually prominent (large, centered, above-the-fold)
  * Have similar or conflicting user intent
  * Are positioned to create user confusion about which action to take

Heuristics you MUST use (deterministic and simple)
Given image size (W,H) and candidate bbox [x1,y1,x2,y2]:
- area_pct = 100 * ((x2-x1)*(y2-y1)) / (W*H)
- center = ((x1+x2)/2, (y1+y2)/2); dx = |center.x - W/2|/(W/2); dy = |center.y - H/2|/(H/2)
- centrality = 100 * (1 - min(1, sqrt(dx^2 + dy^2)))
- above_fold_bonus = 8 if center.y <= 0.6*H else 0
- goal_bonus = 12 if strongly matches desired goal; 6 if loosely related; else 0
- score = clamp( round(0.5*area_pct + 0.5*centrality + above_fold_bonus + goal_bonus), 0, 100 )

Competition rules (apply conservatively - only flag REAL conflicts)
- Visual competition: two or more CTAs with score >= 75 (raised from 70) AND within 30% of image width/height of each other.
- Semantic competition: two or more CTAs whose texts express the SAME primary action (e.g., "Get Started" vs "Get Started Today") AND each has score >= 65.
- Proximity amplification: if centers are within 20% of min(W,H) in distance, consider proximity conflict.

Conflict severity (be conservative)
- low: minor visual overlap, no real user confusion
- medium: some visual competition, slight user confusion possible
- high: clear visual/semantic competition, user confusion likely
- critical: severe competition that will definitely hurt conversion

Output JSON schema (STRICT):
{
  "ctas": [
    {
      "index": <int index in input candidates>,
      "extracted_text": "<exact text from candidate>",
      "bbox": [x1,y1,x2,y2],
      "score": <0-100 int>,
      "goal_role": "primary" | "supporting" | "off-goal" | "neutral"
    }
  ],
  "competing_prompts": {
    "conflict_level": "low" | "medium" | "high" | "critical",
    "sets": [
      {
        "reason": "visual" | "semantic" | "mixed",
        "severity": "low" | "medium" | "high" | "critical",
        "cta_indices": [<int>, <int>, ...],
        "explanation": "<1 short sentence>"
      }
    ],
    "recommendations": [
      "<concise action, e.g., Demote 'Learn more' to link style>",
      "<another action>"
    ],
    "goal_summary": {
      "goal": "<desired behavior string>",
      "primary_found": <int>,
      "supporting_found": <int>,
      "off_goal_found": <int>
    }
  }
}"""


class CTAAnalyzer:
    def __init__(self):
        api_key = (os.getenv("OPENAI_API_KEY") or "").strip()
        if not api_key:
            raise RuntimeError("Missing OPENAI_API_KEY")
        self.client = OpenAI(api_key=api_key)
        self.model = (os.getenv("OPENAI_MODEL") or "gpt-4o-mini").strip()
        self.ocr = easyocr.Reader(['en'], gpu=False, verbose=False)

    # ---------- public ----------
    def analyze(self, image: Image.Image, desired_behavior: str = "") -> Dict[str, Any]:
        w,h = image.size
        data_url = "data:image/jpeg;base64," + base64.b64encode(self._to_jpeg(image,85)).decode()

        # 1) OCR → candidate CTAs (ground truth to prevent hallucinations)
        candidates = self._extract_cta_candidates(image)
        
        # Debug: Log what we found
        print(f"DEBUG: Found {len(candidates)} CTA candidates:")
        for i, c in enumerate(candidates):
            print(f"  {i}: '{c['extracted_text']}' (bbox: {c['bbox']}, conf: {c['ocr_confidence']})")

        user_payload = {
            "goal": desired_behavior or "not specified",
            "image_dimensions": {"width": w, "height": h},
            "candidates": candidates
        }

        # 2) Ask LLM but force it to use only candidates
        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                temperature=0.2,
                response_format={"type":"json_object"},
                messages=[
                    {"role":"system","content":SYSTEM_PROMPT},
                    {"role":"user","content":[
                        {"type":"text","text": "Use ONLY these candidates (no invention):\n" + json.dumps(user_payload, indent=2) +
                         "\nRespond in STRICT JSON with keys: ctas, competing_prompts.\nHere is the screenshot."},
                        {"type":"image_url","image_url":{"url": data_url}}
                    ]}
                ]
            )
            parsed_raw = resp.choices[0].message.content
            parsed = json.loads(parsed_raw) if isinstance(parsed_raw, str) else (parsed_raw or {})
        except Exception as e:
            parsed = {"ctas": [], "competing_prompts": {
                "total_competing": 0, "conflict_level": "low",
                "primary_conflicts": [], "recommendations": [f"LLM error: {e}"],
                "goal_summary": {"goal": desired_behavior or "not specified"}
            }}

        # 3) Sanitize LLM payload
        ctas_raw = self._safe_list(parsed.get("ctas"))
        comp_raw = self._safe_dict(parsed.get("competing_prompts"))

        # 4) Keep ONLY CTAs that exist in candidates (map by normalized text)
        cand_by_text = { _normalize(c["extracted_text"]): c for c in candidates }
        final_ctas: List[Dict[str, Any]] = []
        for c in ctas_raw:
            text = str(c.get("extracted_text",""))
            match = cand_by_text.get(_normalize(text))
            if not match:
                continue  # ignore anything not grounded in OCR
            # force exact text/bbox from OCR, coerce scores safely
            coerced = {
                "extracted_text": match["extracted_text"],
                "bbox": match["bbox"],
                "score": self._coerce_int(c.get("score"), default=50, lo=0, hi=100),
                "goal_role": self._coerce_role(c.get("goal_role")),
                "confidence_estimate": self._coerce_float(c.get("confidence_estimate"), default=0.6, lo=0.0, hi=1.0),
            }
            area_px = (match["bbox"][2]-match["bbox"][0]) * (match["bbox"][3]-match["bbox"][1])
            coerced["area_percentage"] = round(area_px / max(1,w*h) * 100.0, 2)
            final_ctas.append(coerced)

        # If LLM returned none, still return candidates as neutral so UI shows overlays
        if not final_ctas:
            for c in candidates:
                final_ctas.append({
                    "extracted_text": c["extracted_text"],
                    "bbox": c["bbox"],
                    "score": 45,
                    "goal_role": "neutral",
                    "confidence_estimate": 0.6,
                    "area_percentage": round(((c["bbox"][2]-c["bbox"][0]) * (c["bbox"][3]-c["bbox"][1])) / max(1,w*h) * 100.0, 2)
                })

        # 5) Normalize competing_prompts (defend against strings/invalid shapes)
        comp = self._normalize_competing(comp_raw, final_ctas, desired_behavior)

        return {
            "ctas": final_ctas,
            "confidence_threshold": None,
            "competing_prompts": comp,
            "total_text_extracted": len(final_ctas),
            "meta": {"w": w, "h": h, "model": self.model, "grounded_by": "easyocr"}
        }
        
    def debug_ocr(self, image: Image.Image) -> Dict[str, Any]:
        """Debug method to see raw OCR results and filtering"""
        img = image.convert("RGB")
        if img.width >= 960:
            arr_img = img
        else:
            arr_img = img.resize((960, int(img.height*960/img.width)), Image.LANCZOS)

        res = self.ocr.readtext(np_array(arr_img), detail=1, paragraph=False)
        
        all_text = []
        filtered_text = []
        
        for (quad, text, conf) in res:
            if not text or float(conf) < 0.15:
                continue
                
            cleaned_text = self._pretty(text).strip()
            if not cleaned_text or len(cleaned_text) < 2:
                continue
                
            all_text.append({
                "text": cleaned_text,
                "confidence": round(float(conf), 3),
                "bbox": [int(min(p[0] for p in quad)), int(min(p[1] for p in quad)), 
                        int(max(p[0] for p in quad)), int(max(p[1] for p in quad))]
            })
            
            # Check what gets filtered out
            if _is_reviewish(cleaned_text):
                filtered_text.append({"text": cleaned_text, "reason": "reviewish"})
                continue
                
            if not _looks_like_cta(cleaned_text):
                filtered_text.append({"text": cleaned_text, "reason": "not_like_cta"})
                continue
                
            # Check area
            x1, y1, x2, y2 = [int(min(p[0] for p in quad)), int(min(p[1] for p in quad)), 
                              int(max(p[0] for p in quad)), int(max(p[1] for p in quad))]
            area_px = (x2 - x1) * (y2 - y1)
            if area_px < 100:
                filtered_text.append({"text": cleaned_text, "reason": "too_small", "area": area_px})
                continue
                
        return {
            "all_text": all_text,
            "filtered_text": filtered_text,
            "total_all": len(all_text),
            "total_filtered": len(filtered_text)
        }

    # ---------- OCR candidates ----------
    def _extract_cta_candidates(self, image: Image.Image) -> List[Dict[str, Any]]:
        img = image.convert("RGB")
        if img.width >= 960:
            arr_img = img
        else:
            arr_img = img.resize((960, int(img.height*960/img.width)), Image.LANCZOS)

        res = self.ocr.readtext(np_array(arr_img), detail=1, paragraph=False)  # [([quad], text, bbox), ...]
        candidates: List[Dict[str, Any]] = []
        
        for (quad, text, conf) in res:
            try:
                if not text or float(conf) < 0.15:  # Lowered confidence threshold from 0.25 to 0.15
                    continue
                    
                # Clean and normalize text
                cleaned_text = self._pretty(text).strip()
                if not cleaned_text or len(cleaned_text) < 2:
                    continue
                    
                # Skip very long text that's unlikely to be a CTA
                if len(cleaned_text.split()) > 15:
                    continue
                    
                # Skip review/testimonial content
                if _is_reviewish(cleaned_text):
                    continue
                
                # Check if it looks like a CTA
                if not _looks_like_cta(cleaned_text):
                    continue

                x1 = int(min(p[0] for p in quad)); y1 = int(min(p[1] for p in quad))
                x2 = int(max(p[0] for p in quad)); y2 = int(max(p[1] for p in quad))

                # scale back to ORIGINAL image space if we upscaled for OCR
                sx = image.width / arr_img.width
                sy = image.height / arr_img.height
                bbox = [int(x1*sx), int(y1*sy), int(x2*sx), int(y2*sy)]
                
                # Skip very small text areas (likely not buttons/CTAs)
                area_px = (bbox[2] - bbox[0]) * (bbox[3] - bbox[1])
                if area_px < 100:  # Minimum area threshold
                    continue

                candidates.append({
                    "extracted_text": cleaned_text,
                    "bbox": bbox,
                    "ocr_confidence": round(float(conf), 3)
                })
            except Exception:
                continue

        # dedupe by normalized text (keep largest area)
        seen: Dict[str, Dict[str, Any]] = {}
        for c in candidates:
            key = _normalize(c["extracted_text"])
            if key not in seen:
                seen[key] = c
            else:
                if area(seen[key]["bbox"]) < area(c["bbox"]):
                    seen[key] = c
                    
        # Sort by area (largest first) to prioritize prominent CTAs
        result = list(seen.values())
        result.sort(key=lambda x: area(x["bbox"]), reverse=True)
        
        return result

    # ---------- normalization & utils ----------
    def _normalize_competing(self, comp_raw: Dict[str, Any], ctas: List[Dict[str, Any]], goal: str) -> Dict[str, Any]:
        # Ensure dict shape
        if not isinstance(comp_raw, dict):
            comp_raw = {}

        lvl = _normalize(comp_raw.get("conflict_level") or "low")
        if lvl not in {"low","medium","high","critical"}:
            lvl = "low"

        # primary_conflicts can be wrong type; normalize to list[dict]
        raw_confs = comp_raw.get("primary_conflicts")
        if isinstance(raw_confs, dict):
            raw_confs = [raw_confs]
        if not isinstance(raw_confs, list):
            raw_confs = []

        recs = comp_raw.get("recommendations")
        if isinstance(recs, str):
            recs = [recs]
        if not isinstance(recs, list):
            recs = []

        goal_sum = comp_raw.get("goal_summary")
        if not isinstance(goal_sum, dict):
            goal_sum = {}
        roles=[c.get("goal_role","neutral") for c in ctas]
        goal_sum.setdefault("goal", goal or "not specified")
        goal_sum.setdefault("primary_found", sum(r=="primary" for r in roles))
        goal_sum.setdefault("supporting_found", sum(r=="supporting" for r in roles))
        goal_sum.setdefault("off_goal_found", sum(r=="off-goal" for r in roles))

        def sev_default():
            return "high" if lvl in {"high","critical"} else ("medium" if lvl=="medium" else "low")

        norm_confs=[]
        for cf in raw_confs:
            if not isinstance(cf, dict):
                continue
            s = _normalize(cf.get("severity") or sev_default())
            if s not in {"low","medium","high","critical"}:
                s = sev_default()
            idxs = cf.get("affected_cta_indices")
            if isinstance(idxs, int):
                idxs = [idxs]
            if not isinstance(idxs, list):
                idxs = []
            mapped = [ctas[i] for i in idxs if isinstance(i,int) and 0<=i<len(ctas)]
            norm_confs.append({
                "type": cf.get("type","competing_prompts"),
                "title": cf.get("title") or str(cf.get("type","Competing Prompts")).replace("_"," ").title(),
                "description": cf.get("description","CTAs may be competing for attention."),
                "severity": s,
                "affected_cta_indices": idxs,
                "ctas": mapped
            })

        total = comp_raw.get("total_competing")
        if not isinstance(total, int):
            total = len(norm_confs)

        return {
            "total_competing": total,
            "conflict_level": lvl,
            "primary_conflicts": norm_confs,
            "recommendations": recs,
            "goal_summary": goal_sum
        }

    @staticmethod
    def _to_jpeg(img: Image.Image, quality: int=85) -> bytes:
        if img.mode not in ("RGB","L"): img = img.convert("RGB")
        buf = io.BytesIO(); img.save(buf, format="JPEG", quality=quality, optimize=True)
        return buf.getvalue()

    @staticmethod
    def _pretty(s: str) -> str:
        # Remove common OCR artifacts and normalize text
        s = str(s).strip()
        
        # Remove common OCR noise
        s = re.sub(r'[^\w\s\-\.\,\!\?\(\)\$\+\%]', ' ', s)  # Keep only alphanumeric, spaces, and common punctuation
        s = re.sub(r'\s+', ' ', s)  # Normalize multiple spaces to single space
        
        # Clean up common OCR mistakes
        s = re.sub(r'\b(\w)\1{2,}\b', r'\1', s)  # Remove repeated characters (e.g., "Gooo" -> "Go")
        s = re.sub(r'\b(\w)\1\b', r'\1', s)  # Remove double characters (e.g., "Gett" -> "Get")
        
        # Fix common OCR substitutions
        s = s.replace('0', 'o').replace('1', 'l').replace('5', 's')  # Common OCR confusions
        
        return s[:80]  # Increased from 60 to 80 for longer CTA text

    @staticmethod
    def _safe_dict(v: Any) -> Dict[str, Any]:
        return v if isinstance(v, dict) else {}

    @staticmethod
    def _safe_list(v: Any) -> List[Any]:
        return v if isinstance(v, list) else []

    @staticmethod
    def _coerce_int(v: Any, default=0, lo=0, hi=100) -> int:
        try:
            x = int(float(v))
            return max(lo, min(hi, x))
        except Exception:
            return default

    @staticmethod
    def _coerce_float(v: Any, default=0.0, lo=0.0, hi=1.0) -> float:
        try:
            x = float(v)
            return max(lo, min(hi, x))
        except Exception:
            return default

    @staticmethod
    def _coerce_role(v: Any) -> str:
        s = _normalize(v)
        return s if s in {"primary","supporting","off-goal","neutral"} else "neutral"


# --- small helpers ---
def np_array(pil_img: Image.Image):
    import numpy as _np
    return _np.array(pil_img)

def area(b: List[int]) -> int:
    return max(0, b[2]-b[0]) * max(0, b[3]-b[1])
