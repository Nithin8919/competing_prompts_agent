# enhanced_analyzer.py
import os, io, json, base64, re
from typing import Dict, Any, List, Tuple
from pathlib import Path
from PIL import Image
import requests
from bs4 import BeautifulSoup

# Load .env
try:
    from dotenv import load_dotenv, find_dotenv
    load_dotenv(find_dotenv(), override=False)
    load_dotenv(Path(__file__).resolve().parents[1] / ".env", override=False)
except Exception:
    pass

from openai import OpenAI
import easyocr

# Enhanced CTA detection patterns
CTA_VERBS = {
    "book", "schedule", "get", "start", "join", "apply", "enroll", "try", "download",
    "learn", "read", "view", "see", "buy", "purchase", "contact", "call", "subscribe",
    "request", "speak", "talk", "watch", "play", "claim", "choose", "select", "download",
    "claim", "claim your", "limited time", "exclusive", "bonus", "bonuses", "free",
    "money back", "guarantee", "total", "all bonuses", "included", "spots available",
    "sign up", "register", "login", "checkout", "order", "reserve", "save", "upgrade"
}

# Behavioral science insights
BEHAVIORAL_INSIGHTS = {
    "choice_overload": {
        "title": "Choice Overload",
        "description": "With more than 7 options, users experience decision paralysis (Miller's Magic Number)",
        "icon": "🧠",
        "threshold": 7
    },
    "hicks_law": {
        "title": "Hick's Law", 
        "description": "Decision time increases logarithmically with each additional option",
        "icon": "⚡",
        "threshold": 5
    },
    "decision_fatigue": {
        "title": "Decision Fatigue",
        "description": "Multiple choices exhaust mental energy, leading to poor decisions or abandonment", 
        "icon": "🔋",
        "threshold": 6
    },
    "attention_residue": {
        "title": "Attention Residue",
        "description": "Each competing element steals cognitive resources from your main goal",
        "icon": "👁️",
        "threshold": 4
    }
}

# Enhanced system prompt for better conflict detection
ENHANCED_SYSTEM_PROMPT = """You are a world-class CRO analyst specializing in Call-to-Action (CTA) analysis and behavioral psychology. You will analyze a screenshot and OCR-derived CTA candidates to identify competing prompts that hurt conversions.

Your task: Provide detailed analysis of competing CTAs with explicit priority levels, context, and behavioral science reasoning.

CRITICAL REQUIREMENTS:
- USE ONLY the provided OCR candidates. Do not invent text.
- All indices refer to the input candidates list order.
- Output STRICT JSON that validates perfectly.
- Focus on REAL conflicts that confuse users and hurt conversions.
- Provide explicit priority levels (HIGH, MEDIUM, LOW) with clear reasoning.

ANALYSIS FRAMEWORK:

1. CONFLICT DETECTION (be precise):
   - Visual Competition: CTAs with score >= 75 AND within 30% proximity
   - Semantic Competition: Similar actions (e.g., "Get Started" vs "Start Free Trial")
   - Priority Confusion: Multiple high-prominence CTAs competing for same user intent
   - Context Conflicts: CTAs that contradict the user's primary goal

2. PRIORITY CLASSIFICATION:
   - HIGH Priority: Direct competition with primary goal, appears multiple times, or creates major confusion
   - MEDIUM Priority: Indirect competition, moderate visual prominence, distracts from main flow
   - LOW Priority: Minor competition, low prominence, minimal impact on primary conversion

3. BEHAVIORAL SCIENCE APPLICATION:
   - Choice Overload (>7 options)
   - Hick's Law (decision time increase)
   - Decision Fatigue (mental exhaustion)
   - Attention Residue (cognitive resource theft)

4. CONTEXT ANALYSIS:
   For each conflict, provide:
   - Element type and text
   - Why it competes (specific reason)
   - How it appears (frequency/prominence)
   - Impact on user behavior

OUTPUT SCHEMA (STRICT JSON):
{
  "ctas": [
    {
      "index": <int>,
      "extracted_text": "<exact OCR text>",
      "bbox": [x1,y1,x2,y2],
      "score": <0-100>,
      "goal_role": "primary" | "supporting" | "off-goal" | "neutral",
      "element_type": "button" | "link" | "banner" | "form" | "menu" | "text"
    }
  ],
  "competing_prompts": {
    "conflict_level": "low" | "medium" | "high" | "critical",
    "total_competing": <int>,
    "conflicts": [
      {
        "priority": "HIGH" | "MEDIUM" | "LOW",
        "element_type": "Button" | "Link" | "Banner" | "Form",
        "element_text": "<exact text>",
        "context": "<why it appears/how frequent>",
        "why_competes": "<specific reason it competes with primary goal>",
        "behavioral_impact": "<psychological effect on users>",
        "affected_cta_indices": [<indices>],
        "severity_score": <1-10>
      }
    ],
    "behavioral_insights": [
      {
        "principle": "Choice Overload" | "Hick's Law" | "Decision Fatigue" | "Attention Residue",
        "description": "<explanation>",
        "applies": true | false,
        "impact_level": "high" | "medium" | "low"
      }
    ],
    "recommendations": [
      {
        "priority": "HIGH" | "MEDIUM" | "LOW", 
        "action": "<specific action to take>",
        "rationale": "<why this will improve conversions>",
        "expected_impact": "<quantified improvement estimate>"
      }
    ],
    "goal_summary": {
      "desired_behavior": "<user's goal>",
      "primary_ctas_found": <int>,
      "competing_ctas_found": <int>,
      "total_choice_options": <int>
    }
  }
}

Be conservative but precise. Only flag REAL conflicts that genuinely hurt conversions."""

class EnhancedCTAAnalyzer:
    def __init__(self):
        api_key = (os.getenv("OPENAI_API_KEY") or "").strip()
        if not api_key:
            raise RuntimeError("Missing OPENAI_API_KEY")
        self.client = OpenAI(api_key=api_key)
        self.model = (os.getenv("OPENAI_MODEL") or "gpt-4o-mini").strip()
        self.ocr = easyocr.Reader(['en'], gpu=False, verbose=False)

    def analyze_url(self, url: str, desired_behavior: str = "") -> Dict[str, Any]:
        """Analyze CTA conflicts from a webpage URL"""
        try:
            # Take screenshot of the webpage
            screenshot = self._capture_webpage_screenshot(url)
            if not screenshot:
                raise ValueError("Failed to capture webpage screenshot")
            
            return self.analyze(screenshot, desired_behavior, source_url=url)
        except Exception as e:
            return self._error_response(f"URL analysis failed: {e}")

    def _capture_webpage_screenshot(self, url: str) -> Image.Image:
        """Capture a screenshot of the webpage using a screenshot service"""
        try:
            # Using a free screenshot API service
            screenshot_api_url = f"https://api.screenshotone.com/take"
            params = {
                'access_key': os.getenv('SCREENSHOT_API_KEY', 'demo'),  # Use demo for testing
                'url': url,
                'viewport_width': 1200,
                'viewport_height': 800,
                'device_scale_factor': 1,
                'format': 'png',
                'cache': True,
                'cache_ttl': 2592000,
                'wait_until': 'load'
            }
            
            response = requests.get(screenshot_api_url, params=params, timeout=30)
            if response.status_code == 200:
                image = Image.open(io.BytesIO(response.content))
                return image.convert('RGB')
            else:
                # Fallback: try a different service or method
                return self._fallback_screenshot(url)
                
        except Exception as e:
            print(f"Screenshot capture failed: {e}")
            return None

    def _fallback_screenshot(self, url: str) -> Image.Image:
        """Fallback screenshot method using htmlcsstoimage.com API"""
        try:
            api_url = "https://hcti.io/v1/image"
            data = {
                'url': url,
                'viewport_width': 1200,
                'viewport_height': 800,
                'device_scale_factor': 1
            }
            
            # Use demo credentials or user's API key
            auth = (
                os.getenv('HTMLCSS_USER_ID', 'demo'), 
                os.getenv('HTMLCSS_API_KEY', 'demo')
            )
            
            response = requests.post(api_url, data=data, auth=auth, timeout=30)
            if response.status_code == 200:
                result = response.json()
                image_url = result.get('url')
                if image_url:
                    img_response = requests.get(image_url, timeout=10)
                    if img_response.status_code == 200:
                        image = Image.open(io.BytesIO(img_response.content))
                        return image.convert('RGB')
        except Exception as e:
            print(f"Fallback screenshot failed: {e}")
        
        return None

    def analyze(self, image: Image.Image, desired_behavior: str = "", source_url: str = None) -> Dict[str, Any]:
        """Enhanced analysis with detailed conflict detection"""
        w, h = image.size
        data_url = "data:image/jpeg;base64," + base64.b64encode(self._to_jpeg(image, 85)).decode()

        # 1) Extract CTA candidates using OCR
        candidates = self._extract_enhanced_cta_candidates(image)
        
        print(f"DEBUG: Found {len(candidates)} CTA candidates")
        for i, c in enumerate(candidates):
            print(f"  {i}: '{c['extracted_text']}' (type: {c.get('element_type', 'unknown')})")

        user_payload = {
            "goal": desired_behavior or "not specified",
            "source_url": source_url,
            "image_dimensions": {"width": w, "height": h},
            "candidates": candidates,
            "total_candidates": len(candidates)
        }

        # 2) Get enhanced analysis from LLM
        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                temperature=0.1,  # Lower temperature for more consistent analysis
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": ENHANCED_SYSTEM_PROMPT},
                    {"role": "user", "content": [
                        {"type": "text", "text": f"""Analyze these CTA candidates for competing prompts:

{json.dumps(user_payload, indent=2)}

Focus on finding REAL conflicts that hurt conversions. Provide detailed priority analysis with explicit reasons.

Respond with STRICT JSON following the schema."""},
                        {"type": "image_url", "image_url": {"url": data_url}}
                    ]}
                ]
            )
            parsed_raw = resp.choices[0].message.content
            parsed = json.loads(parsed_raw) if isinstance(parsed_raw, str) else (parsed_raw or {})
        except Exception as e:
            print(f"LLM Analysis Error: {e}")
            parsed = self._fallback_analysis_response(candidates, desired_behavior)

        # 3) Process and enhance the results
        return self._process_enhanced_results(parsed, candidates, desired_behavior, w, h)

    def _extract_enhanced_cta_candidates(self, image: Image.Image) -> List[Dict[str, Any]]:
        """Enhanced CTA extraction with element type detection"""
        img = image.convert("RGB")
        if img.width >= 960:
            arr_img = img
        else:
            arr_img = img.resize((960, int(img.height*960/img.width)), Image.LANCZOS)

        res = self.ocr.readtext(self._to_numpy(arr_img), detail=1, paragraph=False)
        candidates = []
        
        for (quad, text, conf) in res:
            try:
                if not text or float(conf) < 0.15:
                    continue
                    
                cleaned_text = self._clean_text(text).strip()
                if not cleaned_text or len(cleaned_text) < 2:
                    continue
                    
                if len(cleaned_text.split()) > 12:
                    continue
                    
                if self._is_review_content(cleaned_text):
                    continue
                
                if not self._looks_like_cta(cleaned_text):
                    continue

                x1 = int(min(p[0] for p in quad))
                y1 = int(min(p[1] for p in quad))
                x2 = int(max(p[0] for p in quad))
                y2 = int(max(p[1] for p in quad))

                # Scale back to original image coordinates
                sx = image.width / arr_img.width
                sy = image.height / arr_img.height
                bbox = [int(x1*sx), int(y1*sy), int(x2*sx), int(y2*sy)]
                
                area_px = (bbox[2] - bbox[0]) * (bbox[3] - bbox[1])
                if area_px < 100:
                    continue

                # Detect element type based on text patterns
                element_type = self._detect_element_type(cleaned_text, bbox, image.width, image.height)

                candidates.append({
                    "extracted_text": cleaned_text,
                    "bbox": bbox,
                    "ocr_confidence": round(float(conf), 3),
                    "element_type": element_type,
                    "area_px": area_px
                })
                
            except Exception:
                continue

        # Remove duplicates and sort by prominence
        seen = {}
        for c in candidates:
            key = self._normalize_text(c["extracted_text"])
            if key not in seen or seen[key]["area_px"] < c["area_px"]:
                seen[key] = c
                
        result = list(seen.values())
        result.sort(key=lambda x: x["area_px"], reverse=True)
        
        return result[:20]  # Limit to top 20 most prominent CTAs

    def _detect_element_type(self, text: str, bbox: List[int], img_width: int, img_height: int) -> str:
        """Detect the type of UI element based on text and positioning"""
        text_lower = text.lower()
        width = bbox[2] - bbox[0]
        height = bbox[3] - bbox[1]
        aspect_ratio = width / height if height > 0 else 1
        
        # Button indicators
        button_keywords = ['get', 'start', 'buy', 'book', 'download', 'subscribe', 'sign up', 'try', 'claim']
        if any(keyword in text_lower for keyword in button_keywords):
            return "button"
        
        # Link indicators  
        link_keywords = ['learn more', 'read more', 'see more', 'view', 'about', 'contact', 'help']
        if any(keyword in text_lower for keyword in link_keywords):
            return "link"
            
        # Navigation menu indicators
        if len(text.split()) <= 2 and bbox[1] < img_height * 0.15:  # Top 15% of page
            return "menu"
            
        # Form indicators
        form_keywords = ['email', 'name', 'phone', 'submit', 'send', 'register']
        if any(keyword in text_lower for keyword in form_keywords):
            return "form"
            
        # Banner/promotional indicators
        banner_keywords = ['free', 'discount', 'offer', 'limited', 'exclusive', 'bonus']
        if any(keyword in text_lower for keyword in banner_keywords):
            return "banner"
        
        # Default classification based on size and position
        area_percentage = (width * height) / (img_width * img_height) * 100
        
        if area_percentage > 2 and aspect_ratio > 2:
            return "banner"
        elif aspect_ratio > 3 and area_percentage > 0.5:
            return "button" 
        else:
            return "text"

    def _process_enhanced_results(self, parsed: Dict[str, Any], candidates: List[Dict[str, Any]], 
                                 desired_behavior: str, w: int, h: int) -> Dict[str, Any]:
        """Process and enhance the LLM analysis results"""
        
        ctas_raw = parsed.get("ctas", [])
        comp_raw = parsed.get("competing_prompts", {})
        
        # Build candidate lookup
        cand_by_text = {self._normalize_text(c["extracted_text"]): c for c in candidates}
        
        final_ctas = []
        for c in ctas_raw:
            text = str(c.get("extracted_text", ""))
            match = cand_by_text.get(self._normalize_text(text))
            if not match:
                continue
                
            # Calculate enhanced scoring
            score = self._calculate_enhanced_score(match, desired_behavior, w, h)
            
            enhanced_cta = {
                "extracted_text": match["extracted_text"],
                "bbox": match["bbox"],
                "score": score,
                "goal_role": self._determine_goal_role(match["extracted_text"], desired_behavior),
                "element_type": match.get("element_type", "text"),
                "confidence_estimate": match["ocr_confidence"],
                "area_percentage": round((match["area_px"] / (w * h)) * 100, 2),
                "prominence_factors": self._get_prominence_factors(match["bbox"], w, h)
            }
            final_ctas.append(enhanced_cta)

        # If no CTAs from LLM, use candidates directly
        if not final_ctas:
            for c in candidates[:10]:  # Top 10 candidates
                score = self._calculate_enhanced_score(c, desired_behavior, w, h)
                final_ctas.append({
                    "extracted_text": c["extracted_text"],
                    "bbox": c["bbox"], 
                    "score": score,
                    "goal_role": self._determine_goal_role(c["extracted_text"], desired_behavior),
                    "element_type": c.get("element_type", "text"),
                    "confidence_estimate": c["ocr_confidence"],
                    "area_percentage": round((c["area_px"] / (w * h)) * 100, 2),
                    "prominence_factors": self._get_prominence_factors(c["bbox"], w, h)
                })

        # Process competing prompts with enhanced analysis
        enhanced_competing = self._enhance_competing_prompts(comp_raw, final_ctas, desired_behavior)
        
        return {
            "ctas": final_ctas,
            "competing_prompts": enhanced_competing,
            "total_text_extracted": len(final_ctas),
            "behavioral_insights": self._generate_behavioral_insights(final_ctas),
            "meta": {
                "width": w,
                "height": h, 
                "model": self.model,
                "analysis_version": "enhanced_v2",
                "total_candidates_processed": len(candidates)
            }
        }

    def _enhance_competing_prompts(self, comp_raw: Dict[str, Any], ctas: List[Dict[str, Any]], 
                                  desired_behavior: str) -> Dict[str, Any]:
        """Enhance competing prompts analysis with detailed breakdown"""
        
        conflicts = comp_raw.get("conflicts", [])
        if isinstance(conflicts, dict):
            conflicts = [conflicts]
        if not isinstance(conflicts, list):
            conflicts = []

        enhanced_conflicts = []
        for conflict in conflicts:
            if not isinstance(conflict, dict):
                continue
                
            enhanced_conflict = {
                "priority": conflict.get("priority", "MEDIUM").upper(),
                "element_type": conflict.get("element_type", "Element"),
                "element_text": conflict.get("element_text", ""),
                "context": conflict.get("context", "Appears on the page"),
                "why_competes": conflict.get("why_competes", "Competes for user attention"),
                "behavioral_impact": conflict.get("behavioral_impact", "May cause decision confusion"),
                "affected_cta_indices": conflict.get("affected_cta_indices", []),
                "severity_score": min(10, max(1, conflict.get("severity_score", 5)))
            }
            enhanced_conflicts.append(enhanced_conflict)

        # Generate behavioral insights
        behavioral_insights = comp_raw.get("behavioral_insights", [])
        if not behavioral_insights:
            behavioral_insights = self._generate_behavioral_insights_from_conflicts(enhanced_conflicts, len(ctas))

        # Generate enhanced recommendations
        recommendations = comp_raw.get("recommendations", [])
        if not recommendations:
            recommendations = self._generate_enhanced_recommendations(enhanced_conflicts, ctas)

        # Calculate conflict level
        conflict_level = self._calculate_conflict_level(enhanced_conflicts, len(ctas))

        return {
            "total_competing": len(enhanced_conflicts),
            "conflict_level": conflict_level,
            "conflicts": enhanced_conflicts,
            "behavioral_insights": behavioral_insights,
            "recommendations": recommendations,
            "goal_summary": {
                "desired_behavior": desired_behavior,
                "primary_ctas_found": sum(1 for c in ctas if c.get("goal_role") == "primary"),
                "competing_ctas_found": len(enhanced_conflicts),
                "total_choice_options": len(ctas)
            }
        }

    def _calculate_enhanced_score(self, candidate: Dict[str, Any], desired_behavior: str, w: int, h: int) -> int:
        """Calculate enhanced CTA prominence score"""
        bbox = candidate["bbox"]
        x1, y1, x2, y2 = bbox
        
        # Size score (0-50)
        area = (x2 - x1) * (y2 - y1)
        area_pct = (area / (w * h)) * 100
        size_score = min(50, area_pct * 10)  # Cap at 50
        
        # Centrality score (0-30) 
        center_x, center_y = (x1 + x2) / 2, (y1 + y2) / 2
        dx = abs(center_x - w/2) / (w/2)
        dy = abs(center_y - h/2) / (h/2)
        centrality = max(0, 1 - (dx*dx + dy*dy)**0.5)
        centrality_score = centrality * 30
        
        # Position bonus (0-10)
        above_fold_bonus = 10 if center_y <= h * 0.6 else 0
        
        # Goal alignment bonus (0-10)
        goal_bonus = self._calculate_goal_alignment(candidate["extracted_text"], desired_behavior)
        
        total_score = int(size_score + centrality_score + above_fold_bonus + goal_bonus)
        return min(100, max(0, total_score))

    def _calculate_goal_alignment(self, text: str, desired_behavior: str) -> int:
        """Calculate how well the CTA aligns with the desired behavior"""
        if not desired_behavior:
            return 0
            
        text_lower = text.lower()
        behavior_lower = desired_behavior.lower()
        
        # Direct text matching
        if text_lower in behavior_lower or behavior_lower in text_lower:
            return 10
            
        # Semantic matching for common goals
        goal_mappings = {
            "sign up": ["register", "join", "create account", "get started"],
            "purchase": ["buy", "order", "checkout", "add to cart"],
            "contact": ["call", "message", "reach out", "speak"],
            "trial": ["try", "demo", "test", "preview"],
            "download": ["get", "grab", "save", "install"]
        }
        
        for goal, keywords in goal_mappings.items():
            if goal in behavior_lower:
                if any(keyword in text_lower for keyword in keywords):
                    return 8
                    
        # Partial matching
        behavior_words = set(behavior_lower.split())
        text_words = set(text_lower.split())
        overlap = len(behavior_words & text_words)
        
        if overlap > 0:
            return min(6, overlap * 2)
            
        return 0

    def _generate_behavioral_insights(self, ctas: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate behavioral science insights based on CTA analysis"""
        insights = []
        total_ctas = len(ctas)
        high_prominence_ctas = len([c for c in ctas if c["score"] >= 70])
        
        for principle, data in BEHAVIORAL_INSIGHTS.items():
            applies = False
            impact_level = "low"
            
            if principle == "choice_overload" and total_ctas > data["threshold"]:
                applies = True
                impact_level = "high" if total_ctas > 10 else "medium"
            elif principle == "hicks_law" and total_ctas > data["threshold"]:
                applies = True  
                impact_level = "medium" if total_ctas > 8 else "low"
            elif principle == "decision_fatigue" and high_prominence_ctas > data["threshold"]:
                applies = True
                impact_level = "high" if high_prominence_ctas > 8 else "medium"
            elif principle == "attention_residue" and high_prominence_ctas > data["threshold"]:
                applies = True
                impact_level = "medium"
                
            insights.append({
                "principle": data["title"],
                "description": data["description"], 
                "icon": data["icon"],
                "applies": applies,
                "impact_level": impact_level
            })
            
        return insights

    # Helper methods
    def _to_jpeg(self, img: Image.Image, quality: int = 85) -> bytes:
        if img.mode not in ("RGB", "L"):
            img = img.convert("RGB")
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=quality, optimize=True)
        return buf.getvalue()

    def _to_numpy(self, pil_img: Image.Image):
        import numpy as np
        return np.array(pil_img)

    def _clean_text(self, s: str) -> str:
        s = str(s).strip()
        s = re.sub(r'[^\w\s\-\.\,\!\?\(\)\$\+\%]', ' ', s)
        s = re.sub(r'\s+', ' ', s)
        return s[:80]

    def _normalize_text(self, s: str) -> str:
        return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 %\-\+\$]", " ", str(s).lower())).strip()

    def _is_review_content(self, text: str) -> bool:
        review_markers = ["review", "★", "⭐", "rating", "stars", "months ago", "days ago"]
        return any(marker in text.lower() for marker in review_markers)

    def _looks_like_cta(self, text: str) -> bool:
        text_lower = self._normalize_text(text)
        if not text_lower or len(text_lower.split()) > 12:
            return False
            
        words = text_lower.split()
        if words and words[0] in CTA_VERBS:
            return True
            
        cta_patterns = [
            "get started", "sign up", "learn more", "buy now", "contact us",
            "free trial", "download", "register", "subscribe", "book now"
        ]
        
        return any(pattern in text_lower for pattern in cta_patterns)

    def _determine_goal_role(self, text: str, desired_behavior: str) -> str:
        if not desired_behavior:
            return "neutral"
            
        alignment_score = self._calculate_goal_alignment(text, desired_behavior)
        
        if alignment_score >= 8:
            return "primary"
        elif alignment_score >= 4:
            return "supporting" 
        elif alignment_score == 0:
            return "off-goal"
        else:
            return "neutral"

    def _get_prominence_factors(self, bbox: List[int], w: int, h: int) -> Dict[str, Any]:
        """Get factors that contribute to visual prominence"""
        x1, y1, x2, y2 = bbox
        center_x, center_y = (x1 + x2) / 2, (y1 + y2) / 2
        
        return {
            "above_fold": center_y <= h * 0.6,
            "center_proximity": 1 - ((center_x - w/2)**2 + (center_y - h/2)**2)**0.5 / (w/2),
            "size_factor": ((x2-x1) * (y2-y1)) / (w * h),
            "aspect_ratio": (x2-x1) / max(1, y2-y1)
        }

    def _calculate_conflict_level(self, conflicts: List[Dict[str, Any]], total_ctas: int) -> str:
        """Calculate overall conflict level"""
        if not conflicts:
            return "low"
            
        high_priority_count = sum(1 for c in conflicts if c.get("priority") == "HIGH") 
        total_conflicts = len(conflicts)
        
        if high_priority_count >= 3 or total_conflicts >= 8:
            return "critical"
        elif high_priority_count >= 2 or total_conflicts >= 5:
            return "high"
        elif high_priority_count >= 1 or total_conflicts >= 3:
            return "medium"
        else:
            return "low"

    def _generate_enhanced_recommendations(self, conflicts: List[Dict[str, Any]], 
                                         ctas: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate actionable recommendations based on conflicts"""
        recommendations = []
        
        high_priority_conflicts = [c for c in conflicts if c.get("priority") == "HIGH"]
        
        if high_priority_conflicts:
            recommendations.append({
                "priority": "HIGH",
                "action": f"Remove or reduce the number of competing prompts on the page to avoid choice overload and decision fatigue",
                "rationale": "High-priority conflicts directly compete with your primary goal and significantly hurt conversion rates",
                "expected_impact": "15-25% improvement in conversion rate"
            })
            
        primary_ctas = [c for c in ctas if c.get("goal_role") == "primary"]
        if len(primary_ctas) > 1:
            recommendations.append({
                "priority": "HIGH",
                "action": f"Make one primary CTA more prominent and visually appealing to draw users' attention",
                "rationale": "Multiple primary CTAs create confusion about the main desired action",
                "expected_impact": "10-20% improvement in primary conversion"
            })
            
        if len(conflicts) > 6:
            recommendations.append({
                "priority": "MEDIUM", 
                "action": "Consider repositioning or redesigning less important elements to reduce their competition level",
                "rationale": "Too many competing elements exhaust users' mental energy and decision-making capacity",
                "expected_impact": "8-15% improvement in overall engagement"
            })
            
        off_goal_ctas = [c for c in ctas if c.get("goal_role") == "off-goal"]
        if off_goal_ctas:
            recommendations.append({
                "priority": "MEDIUM",
                "action": f"Remove or de-emphasize {len(off_goal_ctas)} off-goal CTAs that distract from your primary objective", 
                "rationale": "Off-goal CTAs steal attention and cognitive resources from your main conversion goal",
                "expected_impact": "5-12% improvement in goal completion rate"
            })
            
        return recommendations

    def _generate_behavioral_insights_from_conflicts(self, conflicts: List[Dict[str, Any]], 
                                                   total_ctas: int) -> List[Dict[str, Any]]:
        """Generate behavioral insights when LLM doesn't provide them"""
        insights = []
        
        # Choice Overload
        choice_overload_applies = total_ctas > 7
        insights.append({
            "principle": "Choice Overload",
            "description": "With more than 7 options, users experience decision paralysis (Miller's Magic Number)",
            "applies": choice_overload_applies,
            "impact_level": "high" if total_ctas > 10 else "medium" if choice_overload_applies else "low"
        })
        
        # Hick's Law
        hicks_law_applies = total_ctas > 5
        insights.append({
            "principle": "Hick's Law", 
            "description": "Decision time increases logarithmically with each additional option",
            "applies": hicks_law_applies,
            "impact_level": "medium" if total_ctas > 8 else "low"
        })
        
        # Decision Fatigue
        high_priority_conflicts = len([c for c in conflicts if c.get("priority") == "HIGH"])
        decision_fatigue_applies = high_priority_conflicts > 3
        insights.append({
            "principle": "Decision Fatigue",
            "description": "Multiple choices exhaust mental energy, leading to poor decisions or abandonment",
            "applies": decision_fatigue_applies,
            "impact_level": "high" if high_priority_conflicts > 5 else "medium"
        })
        
        # Attention Residue
        attention_residue_applies = len(conflicts) > 4
        insights.append({
            "principle": "Attention Residue",
            "description": "Each competing element steals cognitive resources from your main goal",
            "applies": attention_residue_applies,
            "impact_level": "medium" if len(conflicts) > 6 else "low"
        })
        
        return insights

    def _fallback_analysis_response(self, candidates: List[Dict[str, Any]], desired_behavior: str) -> Dict[str, Any]:
        """Fallback analysis when LLM fails"""
        conflicts = []
        
        # Simple conflict detection based on text similarity and prominence
        high_score_candidates = [c for c in candidates if c.get("area_px", 0) > 1000]
        
        for i, cand1 in enumerate(high_score_candidates):
            for j, cand2 in enumerate(high_score_candidates[i+1:], i+1):
                # Check for similar text patterns
                text1_words = set(cand1["extracted_text"].lower().split())
                text2_words = set(cand2["extracted_text"].lower().split()) 
                
                if len(text1_words & text2_words) > 0:
                    conflicts.append({
                        "priority": "MEDIUM",
                        "element_type": "Button",
                        "element_text": cand1["extracted_text"],
                        "context": "Appears with similar competing element",
                        "why_competes": f"Similar text to '{cand2['extracted_text']}' creates user confusion",
                        "behavioral_impact": "Users may hesitate between similar options",
                        "affected_cta_indices": [i, j],
                        "severity_score": 6
                    })
                    
        return {
            "ctas": [
                {
                    "index": i,
                    "extracted_text": c["extracted_text"],
                    "bbox": c["bbox"],
                    "score": 60,
                    "goal_role": "neutral",
                    "element_type": c.get("element_type", "text")
                } for i, c in enumerate(candidates[:10])
            ],
            "competing_prompts": {
                "conflict_level": "medium" if len(conflicts) > 3 else "low",
                "total_competing": len(conflicts),
                "conflicts": conflicts,
                "behavioral_insights": [],
                "recommendations": [],
                "goal_summary": {
                    "desired_behavior": desired_behavior,
                    "primary_ctas_found": 0,
                    "competing_ctas_found": len(conflicts),
                    "total_choice_options": len(candidates)
                }
            }
        }

    def _error_response(self, error_message: str) -> Dict[str, Any]:
        """Return structured error response"""
        return {
            "error": True,
            "message": error_message,
            "ctas": [],
            "competing_prompts": {
                "total_competing": 0,
                "conflict_level": "low",
                "conflicts": [],
                "behavioral_insights": [],
                "recommendations": [{"priority": "HIGH", "action": f"Error: {error_message}"}],
                "goal_summary": {"desired_behavior": "", "primary_ctas_found": 0, "competing_ctas_found": 0, "total_choice_options": 0}
            },
            "meta": {"error": error_message}
        }