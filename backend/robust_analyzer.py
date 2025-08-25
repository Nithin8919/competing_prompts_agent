# robust_analyzer.py - Multiple URL capture methods
import os, io, json, base64, re, time, subprocess, sys, platform
from typing import Dict, Any, List, Optional
from pathlib import Path
from PIL import Image
import requests
from urllib.parse import quote, urljoin, urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed

# Load .env
try:
    from dotenv import load_dotenv, find_dotenv
    load_dotenv(find_dotenv(), override=False)
    load_dotenv(Path(__file__).resolve().parents[1] / ".env", override=False)
except Exception:
    pass

from openai import OpenAI
import easyocr

# CTA detection patterns
CTA_VERBS = {
    "get", "start", "try", "book", "buy", "download", "sign", "register", "join", 
    "subscribe", "contact", "call", "learn", "see", "view", "watch", "play", 
    "claim", "grab", "save", "upgrade", "unlock", "access", "discover", "explore",
    "request", "order", "checkout", "add", "select", "choose", "pick", "find",
    "free", "demo", "trial", "now", "today", "instant", "click", "shop"
}

SYSTEM_PROMPT = """You are a world-class CRO analyst. Analyze the screenshot and OCR text to find competing CTAs that hurt conversions.

REQUIREMENTS:
- USE ONLY the provided OCR text. Never invent text.
- Output STRICT JSON that validates perfectly.
- Focus on REAL conflicts that confuse users.

OUTPUT SCHEMA:
{
  "ctas": [
    {
      "index": <int>,
      "extracted_text": "<exact OCR text>",
      "bbox": [x1,y1,x2,y2],
      "score": <0-100>,
      "goal_role": "primary" | "supporting" | "off-goal" | "neutral",
      "element_type": "button" | "link" | "banner" | "menu" | "form"
    }
  ],
  "competing_prompts": {
    "conflict_level": "low" | "medium" | "high" | "critical",
    "total_competing": <int>,
    "conflicts": [
      {
        "priority": "HIGH" | "MEDIUM" | "LOW",
        "element_type": "Button" | "Link" | "Banner" | "Menu",
        "element_text": "<exact text>",
        "context": "<how it appears>",
        "why_competes": "<competition reason>",
        "behavioral_impact": "<user psychology effect>",
        "severity_score": <1-10>
      }
    ],
    "behavioral_insights": [
      {
        "insight": "<insight name>",
        "description": "<explanation>",
        "applies": true | false,
        "impact": "high" | "medium" | "low",
        "recommendation": "<fix>"
      }
    ],
    "recommendations": [
      {
        "priority": "HIGH" | "MEDIUM" | "LOW",
        "action": "<actionable fix>",
        "rationale": "<why this improves conversions>",
        "expected_impact": "<estimated improvement>"
      }
    ]
  }
}"""

class RobustCTAAnalyzer:
    def __init__(self):
        api_key = (os.getenv("OPENAI_API_KEY") or "").strip()
        if not api_key:
            raise RuntimeError("Missing OPENAI_API_KEY")
        self.client = OpenAI(api_key=api_key)
        self.model = (os.getenv("OPENAI_MODEL") or "gpt-4o-mini").strip()
        self.ocr = easyocr.Reader(['en'], gpu=False, verbose=False)
        
        # Initialize all capture methods
        self._init_all_methods()
        print("🔥 Robust CTA Analyzer initialized with multiple capture methods")

    def _init_all_methods(self):
        """Initialize all available capture methods"""
        self.methods = {
            'selenium': self._init_selenium(),
            'playwright': self._init_playwright(),
            'puppeteer': self._init_puppeteer(),
            'chrome_headless': self._init_chrome_headless()
        }
        
        available = [method for method, status in self.methods.items() if status]
        print(f"🚀 Available capture methods: {available}")

    def _init_selenium(self):
        """Initialize Selenium with multiple driver options"""
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            
            # Try multiple approaches
            approaches = [
                self._try_webdriver_manager,
                self._try_system_chrome,
                self._try_custom_chrome_path
            ]
            
            for approach in approaches:
                if approach():
                    print("✅ Selenium initialized")
                    return True
                    
            return False
        except ImportError:
            return False

    def _try_webdriver_manager(self):
        """Try webdriver-manager approach"""
        try:
            from webdriver_manager.chrome import ChromeDriverManager
            from selenium import webdriver
            from selenium.webdriver.chrome.service import Service
            from selenium.webdriver.chrome.options import Options
            
            options = Options()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
            driver.quit()
            return True
        except Exception:
            return False

    def _try_system_chrome(self):
        """Try system Chrome"""
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            
            options = Options()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            
            driver = webdriver.Chrome(options=options)
            driver.quit()
            return True
        except Exception:
            return False

    def _try_custom_chrome_path(self):
        """Try common Chrome installation paths"""
        chrome_paths = [
            "/usr/bin/google-chrome",
            "/usr/bin/chromium-browser",
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
            "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe"
        ]
        
        for path in chrome_paths:
            if os.path.exists(path):
                try:
                    from selenium import webdriver
                    from selenium.webdriver.chrome.options import Options
                    
                    options = Options()
                    options.binary_location = path
                    options.add_argument('--headless')
                    options.add_argument('--no-sandbox')
                    options.add_argument('--disable-dev-shm-usage')
                    
                    driver = webdriver.Chrome(options=options)
                    driver.quit()
                    return True
                except Exception:
                    continue
        return False

    def _init_playwright(self):
        """Initialize Playwright"""
        try:
            import subprocess
            # Try to install playwright if not available
            try:
                from playwright.sync_api import sync_playwright
                return True
            except ImportError:
                # Try to install playwright
                subprocess.run([sys.executable, "-m", "pip", "install", "playwright"], 
                             check=True, capture_output=True)
                subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], 
                             check=True, capture_output=True)
                from playwright.sync_api import sync_playwright
                print("✅ Playwright installed and initialized")
                return True
        except Exception as e:
            print(f"❌ Playwright failed: {e}")
            return False

    def _init_puppeteer(self):
        """Check if Node.js and Puppeteer are available"""
        try:
            result = subprocess.run(["node", "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                # Check if puppeteer is installed
                result = subprocess.run(["npm", "list", "puppeteer"], capture_output=True, text=True)
                if "puppeteer@" in result.stdout or result.returncode == 0:
                    return True
        except Exception:
            pass
        return False

    def _init_chrome_headless(self):
        """Check if Chrome is available for direct command line use"""
        chrome_commands = [
            "google-chrome",
            "chromium-browser",
            "chrome",
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        ]
        
        for cmd in chrome_commands:
            try:
                result = subprocess.run([cmd, "--version"], capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    return True
            except Exception:
                continue
        return False

    def analyze_url(self, url: str, desired_behavior: str = "") -> Dict[str, Any]:
        """Robust URL analysis with multiple fallback methods"""
        print(f"🌐 Starting robust URL analysis for: {url}")
        
        # Try all available methods in parallel for speed
        methods_to_try = [
            ('selenium', self._capture_with_selenium),
            ('playwright', self._capture_with_playwright),
            ('chrome_headless', self._capture_with_chrome_headless),
            ('puppeteer', self._capture_with_puppeteer),
            ('screenshot_services', self._capture_with_services),
            ('direct_image', self._capture_direct_image)
        ]
        
        # Filter to only available methods
        available_methods = [(name, func) for name, func in methods_to_try 
                           if name in ['direct_image', 'screenshot_services'] or self.methods.get(name, False)]
        
        print(f"🔄 Trying {len(available_methods)} capture methods...")
        
        # Try methods in order of reliability
        for method_name, method_func in available_methods:
            try:
                print(f"🎯 Attempting {method_name}...")
                screenshot = method_func(url)
                if screenshot:
                    print(f"✅ {method_name} successful!")
                    return self.analyze(screenshot, desired_behavior, source_url=url, 
                                     capture_method=method_name)
            except Exception as e:
                print(f"❌ {method_name} failed: {e}")
                continue
        
        # If all methods fail, return comprehensive error
        return self._comprehensive_error_response(url)

    def _capture_with_selenium(self, url: str) -> Optional[Image.Image]:
        """Selenium capture with robust error handling"""
        if not self.methods.get('selenium', False):
            return None
            
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.chrome.service import Service
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            
            options = Options()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--window-size=1920,1080')
            options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            
            driver = None
            try:
                # Try multiple driver creation approaches
                approaches = [
                    lambda: self._create_driver_with_manager(options),
                    lambda: webdriver.Chrome(options=options),
                    lambda: self._create_driver_with_custom_path(options)
                ]
                
                for approach in approaches:
                    try:
                        driver = approach()
                        break
                    except Exception:
                        continue
                
                if not driver:
                    return None
                
                driver.set_page_load_timeout(30)
                driver.get(url)
                
                # Wait for page load and scroll to capture full page
                time.sleep(3)
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                
                # Scroll to bottom to trigger lazy loading
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                driver.execute_script("window.scrollTo(0, 0);")
                time.sleep(1)
                
                screenshot_bytes = driver.get_screenshot_as_png()
                return Image.open(io.BytesIO(screenshot_bytes)).convert('RGB')
                
            finally:
                if driver:
                    driver.quit()
                    
        except Exception as e:
            print(f"Selenium error: {e}")
            return None

    def _create_driver_with_manager(self, options):
        """Create driver with webdriver manager"""
        from webdriver_manager.chrome import ChromeDriverManager
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service
        
        service = Service(ChromeDriverManager().install())
        return webdriver.Chrome(service=service, options=options)

    def _create_driver_with_custom_path(self, options):
        """Create driver with custom Chrome path"""
        chrome_paths = [
            "/usr/bin/google-chrome",
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
        ]
        
        from selenium import webdriver
        for path in chrome_paths:
            if os.path.exists(path):
                options.binary_location = path
                return webdriver.Chrome(options=options)
        raise Exception("No Chrome binary found")

    def _capture_with_playwright(self, url: str) -> Optional[Image.Image]:
        """Playwright capture"""
        if not self.methods.get('playwright', False):
            return None
            
        try:
            from playwright.sync_api import sync_playwright
            
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page(viewport={'width': 1920, 'height': 1080})
                page.goto(url, wait_until='networkidle', timeout=30000)
                
                # Scroll to capture full page content
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                page.wait_for_timeout(2000)
                page.evaluate("window.scrollTo(0, 0)")
                page.wait_for_timeout(1000)
                
                screenshot_bytes = page.screenshot(full_page=True)
                browser.close()
                
                return Image.open(io.BytesIO(screenshot_bytes)).convert('RGB')
                
        except Exception as e:
            print(f"Playwright error: {e}")
            return None

    def _capture_with_chrome_headless(self, url: str) -> Optional[Image.Image]:
        """Direct Chrome headless command"""
        if not self.methods.get('chrome_headless', False):
            return None
            
        try:
            import tempfile
            
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
                temp_path = f.name
            
            chrome_commands = [
                "google-chrome",
                "chromium-browser",
                "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
            ]
            
            for chrome_cmd in chrome_commands:
                try:
                    cmd = [
                        chrome_cmd,
                        "--headless",
                        "--no-sandbox",
                        "--disable-dev-shm-usage",
                        "--window-size=1920,1080",
                        f"--screenshot={temp_path}",
                        url
                    ]
                    
                    result = subprocess.run(cmd, capture_output=True, timeout=30)
                    if result.returncode == 0 and os.path.exists(temp_path):
                        image = Image.open(temp_path).convert('RGB')
                        os.unlink(temp_path)
                        return image
                except Exception:
                    continue
            
            return None
            
        except Exception as e:
            print(f"Chrome headless error: {e}")
            return None

    def _capture_with_puppeteer(self, url: str) -> Optional[Image.Image]:
        """Puppeteer capture via Node.js"""
        if not self.methods.get('puppeteer', False):
            return None
            
        try:
            import tempfile
            
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
                temp_path = f.name
                
            # Create puppeteer script
            script = f"""
const puppeteer = require('puppeteer');
(async () => {{
  const browser = await puppeteer.launch({{headless: true}});
  const page = await browser.newPage();
  await page.setViewport({{width: 1920, height: 1080}});
  await page.goto('{url}', {{waitUntil: 'networkidle2', timeout: 30000}});
  await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
  await page.waitForTimeout(2000);
  await page.evaluate(() => window.scrollTo(0, 0));
  await page.waitForTimeout(1000);
  await page.screenshot({{path: '{temp_path}', fullPage: true}});
  await browser.close();
}})();
"""
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
                script_path = f.name
                f.write(script)
            
            result = subprocess.run(['node', script_path], capture_output=True, timeout=60)
            
            if result.returncode == 0 and os.path.exists(temp_path):
                image = Image.open(temp_path).convert('RGB')
                os.unlink(temp_path)
                os.unlink(script_path)
                return image
                
            return None
            
        except Exception as e:
            print(f"Puppeteer error: {e}")
            return None

    def _capture_with_services(self, url: str) -> Optional[Image.Image]:
        """Multiple screenshot services"""
        services = [
            {
                "name": "ScreenshotAPI",
                "url": f"https://shot.screenshotapi.net/screenshot?token=YOUR_TOKEN&url={quote(url)}&width=1920&height=1080&output=image&file_type=png&wait_for_event=load",
                "headers": {}
            },
            {
                "name": "HTMLCSStoImage",
                "url": f"https://hcti.io/v1/image?url={quote(url)}&viewport_width=1920&viewport_height=1080",
                "headers": {}
            },
            {
                "name": "UrlBox",
                "url": f"https://api.urlbox.io/v1/YOUR_KEY/png?url={quote(url)}&width=1920&height=1080&full_page=true",
                "headers": {}
            }
        ]
        
        for service in services:
            try:
                if "YOUR_TOKEN" in service["url"] or "YOUR_KEY" in service["url"]:
                    continue  # Skip unconfigured services
                    
                response = requests.get(
                    service["url"], 
                    headers=service["headers"],
                    timeout=45
                )
                
                if (response.status_code == 200 and 
                    response.headers.get('content-type', '').startswith('image/')):
                    return Image.open(io.BytesIO(response.content)).convert('RGB')
                    
            except Exception:
                continue
                
        return None

    def _capture_direct_image(self, url: str) -> Optional[Image.Image]:
        """Direct image download"""
        if not any(url.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp']):
            return None
            
        try:
            response = requests.get(url, timeout=20, headers={
                'User-Agent': 'Mozilla/5.0 (compatible; CTA-Analyzer/1.0)'
            })
            response.raise_for_status()
            
            if response.headers.get('content-type', '').startswith('image/'):
                return Image.open(io.BytesIO(response.content)).convert('RGB')
        except Exception:
            pass
        return None

    def analyze(self, image: Image.Image, desired_behavior: str = "", 
               source_url: str = None, capture_method: str = "unknown") -> Dict[str, Any]:
        """Enhanced analysis method"""
        w, h = image.size
        data_url = "data:image/jpeg;base64," + base64.b64encode(self._to_jpeg(image, 85)).decode()

        # Extract CTA candidates
        candidates = self._extract_cta_candidates(image)
        print(f"📝 Found {len(candidates)} CTA candidates")

        user_payload = {
            "goal": desired_behavior or "increase conversions",
            "source_url": source_url,
            "image_dimensions": {"width": w, "height": h},
            "candidates": candidates,
            "total_candidates": len(candidates)
        }

        # Get LLM analysis
        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                temperature=0.1,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": [
                        {"type": "text", "text": f"""Analyze CTA candidates for conflicts:

{json.dumps(user_payload, indent=2)}

Find real conflicts that hurt conversions. Be practical and actionable.
Respond with STRICT JSON only."""},
                        {"type": "image_url", "image_url": {"url": data_url}}
                    ]}
                ]
            )
            parsed = json.loads(resp.choices[0].message.content)
        except Exception as e:
            print(f"❌ LLM Error: {e}")
            parsed = self._fallback_analysis(candidates, desired_behavior)

        return self._process_results(parsed, candidates, desired_behavior, w, h, source_url, capture_method)

    def _extract_cta_candidates(self, image: Image.Image) -> List[Dict[str, Any]]:
        """Enhanced CTA extraction"""
        img = image.convert("RGB")
        
        # Use multiple OCR passes for better results
        ocr_results = []
        
        # Pass 1: Normal resolution
        results1 = self.ocr.readtext(self._to_numpy(img), detail=1, paragraph=False)
        ocr_results.extend(results1)
        
        # Pass 2: High resolution if image is small
        if img.width < 1200:
            scale = 1200 / img.width
            large_img = img.resize((1200, int(img.height * scale)), Image.LANCZOS)
            results2 = self.ocr.readtext(self._to_numpy(large_img), detail=1, paragraph=False)
            # Scale coordinates back
            for quad, text, conf in results2:
                scaled_quad = [(p[0]/scale, p[1]/scale) for p in quad]
                ocr_results.append((scaled_quad, text, conf))
        
        candidates = []
        for (quad, text, conf) in ocr_results:
            try:
                if not text or float(conf) < 0.2:
                    continue
                    
                cleaned_text = self._clean_text(text).strip()
                if not cleaned_text or len(cleaned_text) < 2:
                    continue
                    
                if len(cleaned_text.split()) > 10:
                    continue
                    
                if not self._looks_like_cta(cleaned_text):
                    continue

                x1, y1 = int(min(p[0] for p in quad)), int(min(p[1] for p in quad))
                x2, y2 = int(max(p[0] for p in quad)), int(max(p[1] for p in quad))
                
                bbox = [x1, y1, x2, y2]
                area_px = (x2 - x1) * (y2 - y1)
                
                if area_px < 50:
                    continue

                # Enhanced scoring
                area_pct = (area_px / (img.width * img.height)) * 100
                center_y = (y1 + y2) / 2
                center_x = (x1 + x2) / 2
                
                # Position bonuses
                above_fold_bonus = 20 if center_y <= img.height * 0.6 else 0
                center_bonus = 10 if abs(center_x - img.width/2) < img.width * 0.3 else 0
                
                # Content bonuses
                cta_bonus = 15 if any(verb in cleaned_text.lower() for verb in ['get', 'start', 'buy', 'book', 'try']) else 0
                
                score = min(100, int(area_pct * 5 + above_fold_bonus + center_bonus + cta_bonus))

                candidates.append({
                    "extracted_text": cleaned_text,
                    "bbox": bbox,
                    "ocr_confidence": round(float(conf), 3),
                    "area_px": area_px,
                    "preliminary_score": score,
                    "element_type": self._guess_element_type(cleaned_text, bbox, img.width, img.height)
                })
                
            except Exception:
                continue

        # Advanced deduplication and filtering
        seen = {}
        for c in candidates:
            key = self._normalize_text(c["extracted_text"])
            if key not in seen or seen[key]["preliminary_score"] < c["preliminary_score"]:
                seen[key] = c
                
        result = list(seen.values())
        result.sort(key=lambda x: x["preliminary_score"], reverse=True)
        return result[:15]

    def _guess_element_type(self, text: str, bbox: List[int], img_width: int, img_height: int) -> str:
        """Enhanced element type detection"""
        text_lower = text.lower()
        width = bbox[2] - bbox[0]
        height = bbox[3] - bbox[1]
        y_pos = bbox[1]
        
        # Button indicators (action words)
        if any(word in text_lower for word in ['get', 'start', 'buy', 'book', 'sign up', 'try', 'download', 'subscribe', 'join', 'register']):
            return "button"
        
        # Navigation/menu (top of page)
        if y_pos < img_height * 0.15:
            if any(word in text_lower for word in ['home', 'about', 'contact', 'services', 'products', 'login', 'menu']):
                return "menu"
        
        # Footer links (bottom of page)
        if y_pos > img_height * 0.85:
            return "link"
            
        # Banner/promotional (large, marketing language)
        if width > img_width * 0.3 and any(word in text_lower for word in ['free', 'discount', 'offer', 'limited', 'save', 'sale', '%']):
            return "banner"
        
        # Form elements
        if any(word in text_lower for word in ['submit', 'send', 'search', 'go', 'find']):
            return "form"
            
        # Links (descriptive text)
        if any(word in text_lower for word in ['learn more', 'read more', 'see more', 'view all', 'details']):
            return "link"
            
        # Default based on aspect ratio
        return "button" if width > height * 1.5 else "text"

    def _process_results(self, parsed: Dict[str, Any], candidates: List[Dict[str, Any]], 
                        desired_behavior: str, w: int, h: int, source_url: str = None,
                        capture_method: str = "unknown") -> Dict[str, Any]:
        """Enhanced results processing"""
        
        ctas_raw = parsed.get("ctas", [])
        cand_lookup = {self._normalize_text(c["extracted_text"]): c for c in candidates}
        
        final_ctas = []
        for c in ctas_raw:
            text = str(c.get("extracted_text", ""))
            match = cand_lookup.get(self._normalize_text(text))
            if match:
                final_ctas.append({
                    "extracted_text": match["extracted_text"],
                    "bbox": match["bbox"],
                    "score": min(100, max(0, int(c.get("score", match["preliminary_score"])))),
                    "goal_role": c.get("goal_role", "neutral"),
                    "element_type": c.get("element_type", match["element_type"]),
                    "confidence_estimate": match["ocr_confidence"],
                    "area_percentage": round((match["area_px"] / (w * h)) * 100, 2)
                })

        if not final_ctas:
            final_ctas = [
                {
                    "extracted_text": c["extracted_text"],
                    "bbox": c["bbox"],
                    "score": c["preliminary_score"],
                    "goal_role": "neutral",
                    "element_type": c["element_type"],
                    "confidence_estimate": c["ocr_confidence"],
                    "area_percentage": round((c["area_px"] / (w * h)) * 100, 2)
                } for c in candidates[:10]
            ]

        comp_data = parsed.get("competing_prompts", {})
        conflicts = comp_data.get("conflicts", [])
        if not isinstance(conflicts, list):
            conflicts = []

        insights = comp_data.get("behavioral_insights", [])
        if not insights:
            insights = self._generate_insights(final_ctas, conflicts)

        recommendations = comp_data.get("recommendations", [])
        if not recommendations:
            recommendations = self._generate_recommendations(final_ctas, conflicts)

        return {
            "ctas": final_ctas,
            "competing_prompts": {
                "total_competing": len(conflicts),
                "conflict_level": comp_data.get("conflict_level", self._calc_conflict_level(conflicts)),
                "conflicts": conflicts,
                "behavioral_insights": insights,
                "recommendations": recommendations,
                "goal_summary": {
                    "goal": desired_behavior or "increase conversions",
                    "primary_found": sum(1 for c in final_ctas if c["goal_role"] == "primary"),
                    "supporting_found": sum(1 for c in final_ctas if c["goal_role"] == "supporting"),
                    "off_goal_found": sum(1 for c in final_ctas if c["goal_role"] == "off-goal"),
                    "neutral_found": sum(1 for c in final_ctas if c["goal_role"] == "neutral")
                }
            },
            "meta": {
                "source_url": source_url,
                "capture_method": capture_method,
                "processing_time": "analysis_complete",
                "image_dimensions": f"{w}x{h}",
                "total_candidates": len(candidates),
                "total_ctas_found": len(final_ctas),
                "model_used": self.model
            }
        }

    def _generate_insights(self, ctas: List[Dict], conflicts: List[Dict]) -> List[Dict]:
        """Generate behavioral insights based on CTA analysis"""
        insights = []
        
        # Choice overload analysis
        high_score_ctas = [c for c in ctas if c["score"] >= 70]
        if len(high_score_ctas) > 3:
            insights.append({
                "insight": "Choice Overload Risk",
                "description": f"Found {len(high_score_ctas)} high-prominence CTAs competing for attention",
                "applies": True,
                "impact": "high",
                "recommendation": "Reduce to 1-2 primary CTAs to improve decision clarity"
            })
        
        # Visual hierarchy analysis
        primary_ctas = [c for c in ctas if c["goal_role"] == "primary"]
        if not primary_ctas:
            insights.append({
                "insight": "Missing Primary CTA",
                "description": "No clear primary action identified for users to take",
                "applies": True,
                "impact": "high", 
                "recommendation": "Designate one main CTA with highest visual prominence"
            })
        
        # Above-the-fold analysis
        above_fold_ctas = [c for c in ctas if c["bbox"][1] < 400]  # Approximate fold line
        if len(above_fold_ctas) < 1:
            insights.append({
                "insight": "Below-the-Fold CTAs",
                "description": "Important CTAs may not be immediately visible",
                "applies": True,
                "impact": "medium",
                "recommendation": "Move primary CTA above the fold for immediate visibility"
            })
        
        # Element type distribution
        button_count = sum(1 for c in ctas if c["element_type"] == "button")
        link_count = sum(1 for c in ctas if c["element_type"] == "link")
        
        if link_count > button_count * 2:
            insights.append({
                "insight": "Button vs Link Imbalance",
                "description": f"Too many links ({link_count}) vs buttons ({button_count})",
                "applies": True,
                "impact": "medium",
                "recommendation": "Convert key links to prominent buttons for better action clarity"
            })
        
        return insights

    def _generate_recommendations(self, ctas: List[Dict], conflicts: List[Dict]) -> List[Dict]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # High-level strategic recommendations
        high_score_ctas = [c for c in ctas if c["score"] >= 70]
        if len(high_score_ctas) > 2:
            recommendations.append({
                "priority": "HIGH",
                "action": f"Consolidate or de-emphasize {len(high_score_ctas)-1} competing CTAs",
                "rationale": "Too many prominent CTAs create decision paralysis",
                "expected_impact": "15-25% conversion increase"
            })
        
        # Primary CTA optimization
        primary_ctas = [c for c in ctas if c["goal_role"] == "primary"]
        if primary_ctas:
            max_score = max(c["score"] for c in primary_ctas)
            if max_score < 80:
                recommendations.append({
                    "priority": "HIGH",
                    "action": "Increase primary CTA visual prominence (size, color, position)",
                    "rationale": f"Primary CTA score of {max_score} is below optimal (80+)",
                    "expected_impact": "10-20% conversion increase"
                })
        
        # Specific conflict resolutions
        for conflict in conflicts[:3]:  # Top 3 conflicts
            if conflict.get("severity_score", 0) >= 7:
                recommendations.append({
                    "priority": "HIGH" if conflict.get("severity_score", 0) >= 8 else "MEDIUM",
                    "action": f"Resolve '{conflict.get('element_text', 'N/A')}' competition",
                    "rationale": conflict.get("why_competes", "Creates user confusion"),
                    "expected_impact": "5-15% conversion increase"
                })
        
        # Element type recommendations
        buttons = [c for c in ctas if c["element_type"] == "button"]
        links = [c for c in ctas if c["element_type"] == "link" and c["score"] > 60]
        
        if len(links) > len(buttons):
            recommendations.append({
                "priority": "MEDIUM",
                "action": "Convert high-scoring links to button style",
                "rationale": "Buttons have higher click-through rates than text links",
                "expected_impact": "8-12% conversion increase"
            })
        
        return recommendations

    def _calc_conflict_level(self, conflicts: List[Dict]) -> str:
        """Calculate overall conflict level"""
        if not conflicts:
            return "low"
        
        max_severity = max((c.get("severity_score", 1) for c in conflicts), default=1)
        conflict_count = len(conflicts)
        
        if max_severity >= 8 or conflict_count >= 5:
            return "critical"
        elif max_severity >= 6 or conflict_count >= 3:
            return "high"
        elif max_severity >= 4 or conflict_count >= 2:
            return "medium"
        else:
            return "low"

    def _fallback_analysis(self, candidates: List[Dict], desired_behavior: str) -> Dict:
        """Fallback analysis when LLM fails"""
        ctas = []
        conflicts = []
        
        # Score candidates based on heuristics
        for i, c in enumerate(candidates[:10]):
            score = c["preliminary_score"]
            role = "primary" if score >= 80 else ("supporting" if score >= 60 else "neutral")
            
            ctas.append({
                "index": i,
                "extracted_text": c["extracted_text"],
                "bbox": c["bbox"],
                "score": score,
                "goal_role": role,
                "element_type": c["element_type"]
            })
        
        # Find conflicts based on simple heuristics
        high_score_ctas = [c for c in ctas if c["score"] >= 70]
        if len(high_score_ctas) > 2:
            conflicts.append({
                "priority": "HIGH",
                "element_type": "Multiple",
                "element_text": f"{len(high_score_ctas)} competing CTAs",
                "context": "Multiple high-prominence elements",
                "why_competes": "Visual competition for user attention",
                "behavioral_impact": "Choice overload reduces conversion rates",
                "severity_score": min(10, len(high_score_ctas))
            })
        
        return {
            "ctas": ctas,
            "competing_prompts": {
                "conflict_level": self._calc_conflict_level(conflicts),
                "total_competing": len(conflicts),
                "conflicts": conflicts,
                "behavioral_insights": self._generate_insights(ctas, conflicts),
                "recommendations": self._generate_recommendations(ctas, conflicts)
            }
        }

    def _comprehensive_error_response(self, url: str) -> Dict[str, Any]:
        """Return comprehensive error when all methods fail"""
        return {
            "error": True,
            "message": "Unable to capture screenshot from URL",
            "url": url,
            "attempted_methods": list(self.methods.keys()),
            "available_methods": [k for k, v in self.methods.items() if v],
            "suggestions": [
                "Verify the URL is accessible and loads correctly",
                "Check if the website blocks automated access (Cloudflare, etc.)",
                "Try installing additional dependencies (selenium, playwright)",
                "Consider using a direct image URL instead",
                "Ensure Chrome/Chromium is installed on the system"
            ],
            "ctas": [],
            "competing_prompts": {
                "conflict_level": "unknown",
                "total_competing": 0,
                "conflicts": [],
                "behavioral_insights": [],
                "recommendations": [
                    {
                        "priority": "HIGH",
                        "action": "Verify URL accessibility",
                        "rationale": "Screenshot capture failed for technical reasons",
                        "expected_impact": "Enable analysis functionality"
                    }
                ]
            },
            "meta": {
                "source_url": url,
                "capture_method": "failed",
                "error_details": "All capture methods exhausted"
            }
        }

    def _clean_text(self, text: str) -> str:
        """Enhanced text cleaning"""
        if not text:
            return ""
        
        # Remove OCR artifacts
        text = re.sub(r'[^\w\s\-\.\,\!\?\(\)\$\+\%\&]', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        
        # Fix common OCR mistakes
        replacements = {
            '0': 'O', '1': 'I', '5': 'S', '8': 'B',  # Numbers to letters
            'rn': 'm', 'vv': 'w', 'ii': 'n'  # Common OCR confusions
        }
        
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        return text.strip()[:100]  # Limit length

    def _looks_like_cta(self, text: str) -> bool:
        """Enhanced CTA detection"""
        text_lower = text.lower().strip()
        
        if not text_lower or len(text_lower) < 2:
            return False
        
        words = text_lower.split()
        
        # Direct CTA verb matches
        if any(verb in text_lower for verb in CTA_VERBS):
            return True
        
        # Common CTA patterns
        cta_patterns = [
            "click here", "learn more", "read more", "see more", "view all",
            "get started", "sign up", "log in", "register now", "join now",
            "buy now", "order now", "shop now", "add to cart", "checkout",
            "book now", "reserve", "schedule", "contact us", "call now",
            "download", "subscribe", "follow us", "share", "like us"
        ]
        
        if any(pattern in text_lower for pattern in cta_patterns):
            return True
        
        # Button-like characteristics
        if (len(words) <= 4 and 
            any(word in CTA_VERBS for word in words) and
            not any(word in text_lower for word in ['the', 'and', 'or', 'but', 'with'])):
            return True
        
        # Promotional language
        promo_words = ['free', 'discount', 'save', 'offer', 'deal', 'limited', 'exclusive']
        if any(word in text_lower for word in promo_words):
            return True
        
        return False

    def _normalize_text(self, text: str) -> str:
        """Normalize text for deduplication"""
        return re.sub(r'\s+', ' ', re.sub(r'[^\w\s]', ' ', text.lower())).strip()

    def _to_numpy(self, pil_image: Image.Image):
        """Convert PIL to numpy array"""
        import numpy as np
        return np.array(pil_image)

    def _to_jpeg(self, img: Image.Image, quality: int = 85) -> bytes:
        """Convert to JPEG bytes"""
        if img.mode not in ("RGB", "L"):
            img = img.convert("RGB")
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=quality, optimize=True)
        return buf.getvalue()

# Usage example and testing
if __name__ == "__main__":
    analyzer = RobustCTAAnalyzer()
    
    # Test with a URL
    test_url = "https://example.com"
    results = analyzer.analyze_url(test_url, "Get users to sign up for the newsletter")
    
    print("🎯 Analysis Results:")
    print(f"📊 Found {len(results['ctas'])} CTAs")
    print(f"⚠️ Conflict level: {results['competing_prompts']['conflict_level']}")
    print(f"🔧 {len(results['competing_prompts']['recommendations'])} recommendations")