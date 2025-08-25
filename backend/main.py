# enhanced_main.py
from flask import Flask, request, jsonify, render_template, redirect, url_for, flash
from flask_cors import CORS
import os, time, base64, requests
from io import BytesIO
from PIL import Image
from werkzeug.utils import secure_filename
from enhanced_analyzer import EnhancedCTAAnalyzer

# Pillow 10 compatibility
if not hasattr(Image, 'ANTIALIAS'):
    Image.ANTIALIAS = Image.LANCZOS

app = Flask(__name__)
app.secret_key = 'enhanced-cta-analyzer-secret-key-2024'
CORS(app)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

analyzer = EnhancedCTAAnalyzer()

# ---------- helpers ----------
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png','jpg','jpeg','gif','bmp','webp'}

def _ensure_min_width(img: Image.Image, min_w: int = 1024):
    """Upscale narrow screenshots to improve text readability for the vision model."""
    if img.width >= min_w:
        return img, None
    scale = float(min_w) / float(img.width)
    new_size = (min_w, int(round(img.height * scale)))
    up = img.resize(new_size, Image.LANCZOS)
    buf = BytesIO()
    up.save(buf, format="PNG")
    return up, buf.getvalue()

# ---------- routes ----------
@app.route('/')
def index():
    return render_template('enhanced_index.html')

@app.route('/analyze', methods=['POST'])
def analyze_design():
    """Enhanced analysis endpoint supporting both URL and file upload"""
    design_url = request.form.get('design_url', '').strip()
    desired_behavior = request.form.get('desired_behavior', '').strip()
    
    if not desired_behavior:
        flash('Please describe your desired user behavior/goal', 'error')
        return redirect(url_for('index'))

    image = None
    image_bytes = None
    filename = None
    source_type = None

    try:
        # Handle URL analysis
        if design_url:
            try:
                source_type = 'URL'
                filename = design_url.split('/')[-1] or 'webpage-analysis'
                
                # Check if it's a direct image URL
                if any(design_url.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp']):
                    # Direct image URL
                    r = requests.get(design_url, timeout=15, headers={
                        'User-Agent': 'Mozilla/5.0 (compatible; CTA-Analyzer/1.0)'
                    })
                    r.raise_for_status()
                    
                    if not r.headers.get('content-type','').startswith('image/'):
                        flash('URL does not point to an image', 'error')
                        return redirect(url_for('index'))
                        
                    image_bytes = r.content
                    image = Image.open(BytesIO(image_bytes)).convert('RGB')
                    
                    # Use enhanced analyzer for image analysis
                    start = time.time()
                    results = analyzer.analyze(image, desired_behavior=desired_behavior)
                    processing_time = round(time.time() - start, 2)
                    
                else:
                    # Webpage URL - use URL analysis method
                    start = time.time()
                    results = analyzer.analyze_url(design_url, desired_behavior=desired_behavior)
                    processing_time = round(time.time() - start, 2)
                    
                    # For webpage analysis, we'll get the screenshot from the analyzer
                    # This is a placeholder - in practice, the analyzer handles this
                    image_bytes = b''  # Placeholder
                    
            except requests.exceptions.RequestException as e:
                flash(f'Error loading URL: {str(e)}', 'error')
                return redirect(url_for('index'))
            except Exception as e:
                flash(f'Error analyzing URL: {str(e)}', 'error')
                return redirect(url_for('index'))

        # Handle file upload
        elif 'file' in request.files and request.files['file'].filename:
            file = request.files['file']
            if not allowed_file(file.filename):
                flash('Invalid file type. Upload PNG/JPG/JPEG/GIF/BMP/WebP', 'error')
                return redirect(url_for('index'))
                
            try:
                source_type = 'Upload'
                image_bytes = file.read()
                image = Image.open(BytesIO(image_bytes)).convert('RGB')
                filename = secure_filename(file.filename)
                
                # Optional upscale to aid model readability
                image, up_bytes = _ensure_min_width(image, min_w=1024)
                if up_bytes is not None:
                    image_bytes = up_bytes

                start = time.time()
                results = analyzer.analyze(image, desired_behavior=desired_behavior)
                processing_time = round(time.time() - start, 2)
                
            except Exception as e:
                flash(f'Error processing upload: {str(e)}', 'error')
                return redirect(url_for('index'))
        else:
            flash('Provide a design URL or upload an image', 'error')
            return redirect(url_for('index'))

        # Check for analysis errors
        if results.get('error'):
            flash(f'Analysis error: {results.get("message", "Unknown error")}', 'error')
            return redirect(url_for('index'))

        # Process results for template
        ctas = results.get('ctas', [])
        competing_prompts = results.get('competing_prompts', {})
        conflicts = competing_prompts.get('conflicts', [])
        
        analysis_data = {
            'results': results,
            'image_data': base64.b64encode(image_bytes).decode('utf-8') if image_bytes else '',
            'filename': filename,
            'processing_time': processing_time,
            'image_dims': f"{image.width}x{image.height}" if image else "Unknown",
            'total_ctas': len(ctas),
            'desired_behavior': desired_behavior,
            'design_source': source_type,
            'source_url': design_url if design_url else None,
            
            # Enhanced data for the new template
            'ctas': ctas,
            'competing_prompts': competing_prompts,
            'conflicts': conflicts,
            'conflict_level': competing_prompts.get('conflict_level', 'low'),
            'total_conflicts': len(conflicts),
            'behavioral_insights': results.get('behavioral_insights', []),
            'recommendations': competing_prompts.get('recommendations', []),
            'goal_summary': competing_prompts.get('goal_summary', {}),
            
            # Priority breakdown
            'high_priority_conflicts': [c for c in conflicts if c.get('priority') == 'HIGH'],
            'medium_priority_conflicts': [c for c in conflicts if c.get('priority') == 'MEDIUM'], 
            'low_priority_conflicts': [c for c in conflicts if c.get('priority') == 'LOW'],
        }
        
        return render_template('enhanced_results.html', data=analysis_data)
        
    except Exception as e:
        flash(f'Analysis failed: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/api/analyze', methods=['POST'])
def api_analyze():
    """Enhanced API endpoint for programmatic access"""
    try:
        start = time.time()
        
        # Handle URL analysis via API
        if request.is_json:
            data = request.get_json()
            design_url = data.get('design_url', '').strip()
            desired_behavior = data.get('desired_behavior', '').strip()
            
            if not design_url:
                return jsonify({"error": "No design_url provided"}), 400
                
            results = analyzer.analyze_url(design_url, desired_behavior=desired_behavior)
            
        # Handle file upload via API
        else:
            if 'image' not in request.files:
                return jsonify({"error": "No image file provided"}), 400
                
            f = request.files['image']
            if f.filename == '':
                return jsonify({"error": "No image file selected"}), 400
                
            if not allowed_file(f.filename):
                return jsonify({"error": "Invalid file type"}), 400

            desired_behavior = request.form.get('desired_behavior', '').strip()

            image_bytes = f.read()
            image = Image.open(BytesIO(image_bytes)).convert('RGB')
            image, _ = _ensure_min_width(image, min_w=1024)

            results = analyzer.analyze(image, desired_behavior=desired_behavior)

        processing_time = round(time.time() - start, 2)
        
        # Check for errors in results
        if results.get('error'):
            return jsonify({
                "error": results.get('message', 'Analysis failed'),
                "processing_time": processing_time
            }), 500

        # Format API response
        api_response = {
            "ctas": results.get("ctas", []),
            "competing_prompts": results.get("competing_prompts", {}),
            "behavioral_insights": results.get("behavioral_insights", []),
            "meta": {
                "processing_time": f"{processing_time}s",
                "image_dims": results.get("meta", {}).get("width", 0) and results.get("meta", {}).get("height", 0) 
                            and f"{results['meta']['width']}x{results['meta']['height']}" or "unknown",
                "total_ctas_found": len(results.get("ctas", [])),
                "desired_behavior": desired_behavior or None,
                "analysis_version": results.get("meta", {}).get("analysis_version", "enhanced_v2")
            }
        }
        
        return jsonify(api_response)
        
    except Exception as e:
        return jsonify({"error": f"Processing failed: {e}"}), 500

@app.route('/api/analyze-url', methods=['POST'])
def api_analyze_url():
    """Dedicated API endpoint for URL analysis"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "JSON data required"}), 400
            
        design_url = data.get('design_url', '').strip()
        desired_behavior = data.get('desired_behavior', '').strip()
        
        if not design_url:
            return jsonify({"error": "design_url is required"}), 400
            
        start = time.time()
        results = analyzer.analyze_url(design_url, desired_behavior=desired_behavior)
        processing_time = round(time.time() - start, 2)
        
        if results.get('error'):
            return jsonify({
                "error": results.get('message', 'URL analysis failed'),
                "processing_time": processing_time
            }), 500

        api_response = {
            "url_analyzed": design_url,
            "ctas": results.get("ctas", []),
            "competing_prompts": results.get("competing_prompts", {}),
            "behavioral_insights": results.get("behavioral_insights", []),
            "meta": {
                "processing_time": f"{processing_time}s",
                "total_ctas_found": len(results.get("ctas", [])),
                "desired_behavior": desired_behavior or None,
                "analysis_version": results.get("meta", {}).get("analysis_version", "enhanced_v2"),
                "source_type": "url"
            }
        }
        
        return jsonify(api_response)
        
    except Exception as e:
        return jsonify({"error": f"URL analysis failed: {e}"}), 500

@app.get('/api/health')
def health():
    return {
        "status": "healthy", 
        "service": "Enhanced CTA Focus Analyzer API", 
        "version": "2.0.0",
        "features": ["image_analysis", "url_analysis", "behavioral_insights", "priority_classification"]
    }

@app.route('/debug/ocr')
def debug_ocr():
    """Debug endpoint to test OCR functionality"""
    return render_template('debug_ocr.html')

@app.route('/api/debug/ocr', methods=['POST'])
def api_debug_ocr():
    """API endpoint for OCR debugging"""
    try:
        if 'image' not in request.files:
            return jsonify({"error": "No image file provided"}), 400
            
        f = request.files['image']
        if not allowed_file(f.filename):
            return jsonify({"error": "Invalid file type"}), 400

        image_bytes = f.read()
        image = Image.open(BytesIO(image_bytes)).convert('RGB')
        
        debug_results = analyzer.debug_ocr(image)
        
        return jsonify(debug_results)
        
    except Exception as e:
        return jsonify({"error": f"OCR debug failed: {e}"}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug_mode)