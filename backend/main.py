from flask import Flask, request, jsonify, render_template, redirect, url_for, flash
from flask_cors import CORS
import os, time, base64, requests
from io import BytesIO
from PIL import Image
from werkzeug.utils import secure_filename
from analyzer import CTAAnalyzer

# Pillow 10 compat
if not hasattr(Image, 'ANTIALIAS'):
    Image.ANTIALIAS = Image.LANCZOS

app = Flask(__name__)
app.secret_key = 'cta-analyzer-secret-key-2024'
CORS(app)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

analyzer = CTAAnalyzer()


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
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze_design():
    design_url = request.form.get('design_url', '').strip()
    desired_behavior = request.form.get('desired_behavior', '').strip()
    if not desired_behavior:
        flash('Please describe your desired user behavior/goal (e.g., "Book calls")', 'error')
        return redirect(url_for('index'))

    image = None
    image_bytes = None
    filename = None

    if design_url:
        try:
            r = requests.get(design_url, timeout=12)
            r.raise_for_status()
            if not r.headers.get('content-type','').startswith('image/'):
                flash('URL does not point to an image', 'error')
                return redirect(url_for('index'))
            image_bytes = r.content
            image = Image.open(BytesIO(image_bytes)).convert('RGB')
            filename = design_url.split('/')[-1] or 'url-image'
        except Exception as e:
            flash(f'Error loading image: {e}', 'error')
            return redirect(url_for('index'))

    elif 'file' in request.files and request.files['file'].filename:
        file = request.files['file']
        if not allowed_file(file.filename):
            flash('Invalid file type. Upload PNG/JPG/JPEG/GIF/BMP/WebP', 'error')
            return redirect(url_for('index'))
        try:
            image_bytes = file.read()
            image = Image.open(BytesIO(image_bytes)).convert('RGB')
            filename = secure_filename(file.filename)
        except Exception as e:
            flash(f'Error processing upload: {e}', 'error')
            return redirect(url_for('index'))
    else:
        flash('Provide a design URL or upload an image', 'error')
        return redirect(url_for('index'))

    try:
        # Optional upscale to aid model readability
        image, up_bytes = _ensure_min_width(image, min_w=1024)
        if up_bytes is not None:
            image_bytes = up_bytes

        start = time.time()
        results = analyzer.analyze(image, desired_behavior=desired_behavior)
        processing_time = round(time.time() - start, 2)

        analysis_data = {
            'results': results,
            'image_data': base64.b64encode(image_bytes).decode('utf-8'),
            'filename': filename,
            'processing_time': processing_time,
            'image_dims': f"{image.width}x{image.height}",
            'total_ctas': len(results.get('ctas', [])),
            'desired_behavior': desired_behavior,
            'design_source': 'URL' if design_url else 'Upload',
            'ctas': results.get('ctas', []),
            'competing_prompts': results.get('competing_prompts', {}),
            'conflicts': results.get('competing_prompts', {}).get('primary_conflicts', []),
            'conflict_level': results.get('competing_prompts', {}).get('conflict_level', 'low'),
            'total_conflicts': len(results.get('competing_prompts', {}).get('primary_conflicts', [])),
            'recommendations': results.get('competing_prompts', {}).get('recommendations', [])
        }
        return render_template('results.html', data=analysis_data)
    except Exception as e:
        flash(f'Error analyzing image: {e}', 'error')
        return redirect(url_for('index'))

@app.route('/api/analyze', methods=['POST'])
def api_analyze():
    try:
        start = time.time()
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
        return jsonify({
            "ctas": results.get("ctas", []),
            "competing_prompts": results.get("competing_prompts", {}),
            "meta": {
                "processing_time": f"{processing_time}s",
                "image_dims": f"{image.width}x{image.height}",
                "total_ctas_found": len(results.get("ctas", [])),
                "desired_behavior": desired_behavior or None
            }
        })
    except Exception as e:
        return jsonify({"error": f"Processing failed: {e}"}), 500

@app.get('/api/health')
def health():
    return {"status": "healthy", "service": "CTA Focus Analyzer API", "version": "1.1.0"}

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=False)
