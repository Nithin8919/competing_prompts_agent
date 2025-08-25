# main.py - Robust CTA analyzer with multiple URL capture methods
from flask import Flask, request, jsonify, render_template, redirect, url_for, flash, send_file
from flask_cors import CORS
import os, time, base64, requests
from io import BytesIO
from PIL import Image
from werkzeug.utils import secure_filename
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors

# Import our robust analyzer (save the previous artifact as robust_analyzer.py)
try:
    from robust_analyzer import RobustCTAAnalyzer
    ANALYZER_TYPE = "robust"
except ImportError:
    try:
        from enhanced_analyzer import FixedCTAAnalyzer as RobustCTAAnalyzer
        ANALYZER_TYPE = "enhanced"
    except ImportError:
        from analyzer import CTAAnalyzer as RobustCTAAnalyzer
        ANALYZER_TYPE = "basic"

# Pillow compatibility
if not hasattr(Image, 'ANTIALIAS'):
    Image.ANTIALIAS = Image.LANCZOS

app = Flask(__name__)
app.secret_key = 'robust-cta-analyzer-secret-key-2024'
CORS(app)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

# Initialize the robust analyzer
try:
    analyzer = RobustCTAAnalyzer()
    print(f"✅ {ANALYZER_TYPE.title()} CTA Analyzer initialized successfully")
except Exception as e:
    print(f"❌ Failed to initialize analyzer: {e}")
    analyzer = None

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png','jpg','jpeg','gif','bmp','webp'}

def _ensure_min_width(img: Image.Image, min_w: int = 1024):
    """Upscale narrow screenshots for better OCR"""
    if img.width >= min_w:
        return img, None
    scale = float(min_w) / float(img.width)
    new_size = (min_w, int(round(img.height * scale)))
    up = img.resize(new_size, Image.LANCZOS)
    buf = BytesIO()
    up.save(buf, format="PNG")
    return up, buf.getvalue()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze_design():
    """Main analysis endpoint with robust URL handling"""
    if not analyzer:
        flash('Analyzer not initialized. Please check server configuration.', 'error')
        return redirect(url_for('index'))
    
    design_url = request.form.get('design_url', '').strip()
    desired_behavior = request.form.get('desired_behavior', '').strip()
    
    if not desired_behavior:
        flash('Please describe your desired user behavior/goal', 'error')
        return redirect(url_for('index'))

    try:
        start = time.time()
        results = None
        image_bytes = b''
        filename = None
        
        # URL Analysis with robust methods
        if design_url:
            print(f"🌐 Starting robust URL analysis for: {design_url}")
            results = analyzer.analyze_url(design_url, desired_behavior=desired_behavior)
            source_type = 'URL'
            filename = design_url.split('/')[-1] or 'webpage-analysis'
            
            # Check if we got an actual analysis or an error
            if results.get('error'):
                error_msg = results.get('message', 'Unknown error')
                # Check if this is a "helpful" error with recommendations
                if results.get('competing_prompts', {}).get('recommendations'):
                    # Show the error with helpful suggestions
                    flash(f'URL capture failed: {error_msg}. See recommendations below for alternatives.', 'error')
                    # Still show the error "results" which contain helpful suggestions
                    image_dims = "N/A"
                else:
                    flash(f'URL analysis failed: {error_msg}', 'error')
                    return redirect(url_for('index'))
            else:
                # Successful analysis
                meta = results.get('meta', {})
                image_dims = f"{meta.get('width', 'N/A')}x{meta.get('height', 'N/A')}"
                
        # File Upload Analysis
        elif 'file' in request.files and request.files['file'].filename:
            print("📁 Starting file upload analysis")
            file = request.files['file']
            if not allowed_file(file.filename):
                flash('Invalid file type. Upload PNG/JPG/JPEG/GIF/BMP/WebP', 'error')
                return redirect(url_for('index'))
                
            try:
                source_type = 'Upload'
                image_bytes = file.read()
                image = Image.open(BytesIO(image_bytes)).convert('RGB')
                filename = secure_filename(file.filename)
                
                # Optional upscale for better OCR
                image, up_bytes = _ensure_min_width(image, min_w=1024)
                if up_bytes is not None:
                    image_bytes = up_bytes

                results = analyzer.analyze(image, desired_behavior=desired_behavior)
                image_dims = f"{image.width}x{image.height}"
                
            except Exception as e:
                flash(f'Error processing upload: {str(e)}', 'error')
                return redirect(url_for('index'))
        else:
            flash('Provide a design URL or upload an image', 'error')
            return redirect(url_for('index'))

        processing_time = round(time.time() - start, 2)
        print(f"✅ Analysis completed in {processing_time}s")

        # Process results for template
        ctas = results.get('ctas', [])
        competing_prompts = results.get('competing_prompts', {})
        conflicts = competing_prompts.get('conflicts', [])
        behavioral_insights = results.get('behavioral_insights', [])
        
        # Enhanced conflict grouping
        high_priority_conflicts = [c for c in conflicts if c.get('priority') == 'HIGH']
        medium_priority_conflicts = [c for c in conflicts if c.get('priority') == 'MEDIUM'] 
        low_priority_conflicts = [c for c in conflicts if c.get('priority') == 'LOW']
        
        # Calculate additional metrics
        total_high_score_ctas = len([c for c in ctas if c.get('score', 0) >= 70])
        primary_ctas = [c for c in ctas if c.get('goal_role') == 'primary']
        off_goal_ctas = [c for c in ctas if c.get('goal_role') == 'off-goal']
        
        analysis_data = {
            'results': results,
            'image_data': base64.b64encode(image_bytes).decode('utf-8') if image_bytes else '',
            'filename': filename,
            'processing_time': processing_time,
            'image_dims': image_dims,
            'total_ctas': len(ctas),
            'desired_behavior': desired_behavior,
            'design_source': source_type,
            'source_url': design_url if design_url else None,
            
            # Core analysis data
            'ctas': ctas,
            'competing_prompts': competing_prompts,
            'conflicts': conflicts,
            'conflict_level': competing_prompts.get('conflict_level', 'low'),
            'total_conflicts': len(conflicts),
            'behavioral_insights': behavioral_insights,
            'recommendations': competing_prompts.get('recommendations', []),
            'goal_summary': competing_prompts.get('goal_summary', {}),
            
            # Enhanced analytics
            'high_priority_conflicts': high_priority_conflicts,
            'medium_priority_conflicts': medium_priority_conflicts, 
            'low_priority_conflicts': low_priority_conflicts,
            'total_high_score_ctas': total_high_score_ctas,
            'primary_ctas': primary_ctas,
            'off_goal_ctas': off_goal_ctas,
            
            # Metadata for debugging
            'capture_method': results.get('meta', {}).get('capture_method', 'unknown'),
            'analyzer_type': ANALYZER_TYPE,
            'is_error': results.get('error', False)
        }
        
        return render_template('results.html', data=analysis_data)
        
    except Exception as e:
        print(f"❌ Analysis failed: {str(e)}")
        flash(f'Analysis failed: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/api/analyze', methods=['POST'])
def api_analyze():
    """Enhanced API endpoint with robust URL support"""
    if not analyzer:
        return jsonify({"error": "Analyzer not initialized"}), 500
        
    try:
        start = time.time()
        
        # Handle JSON requests (URL analysis)
        if request.is_json:
            data = request.get_json()
            design_url = data.get('design_url', '').strip()
            desired_behavior = data.get('desired_behavior', '').strip()
            
            if not design_url:
                return jsonify({"error": "No design_url provided"}), 400
                
            results = analyzer.analyze_url(design_url, desired_behavior=desired_behavior)
            
        # Handle file uploads
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
        
        # Handle errors in results
        if results.get('error'):
            return jsonify({
                "error": results.get('message', 'Analysis failed'),
                "processing_time": processing_time,
                "debug_info": results.get('meta', {}),
                "suggestions": results.get('competing_prompts', {}).get('recommendations', [])
            }), 500

        # Format enhanced API response
        api_response = {
            "success": True,
            "ctas": results.get("ctas", []),
            "competing_prompts": results.get("competing_prompts", {}),
            "behavioral_insights": results.get("behavioral_insights", []),
            "analytics": {
                "total_ctas": len(results.get("ctas", [])),
                "high_score_ctas": len([c for c in results.get("ctas", []) if c.get("score", 0) >= 70]),
                "primary_ctas": len([c for c in results.get("ctas", []) if c.get("goal_role") == "primary"]),
                "conflicts_found": len(results.get("competing_prompts", {}).get("conflicts", [])),
                "conflict_level": results.get("competing_prompts", {}).get("conflict_level", "low")
            },
            "meta": {
                "processing_time": f"{processing_time}s",
                "desired_behavior": desired_behavior or None,
                "analysis_version": results.get("meta", {}).get("analysis_version", ANALYZER_TYPE),
                "capture_method": results.get("meta", {}).get("capture_method", "unknown"),
                "source_url": results.get("meta", {}).get("source_url"),
                "analyzer_type": ANALYZER_TYPE
            }
        }
        
        return jsonify(api_response)
        
    except Exception as e:
        print(f"❌ API Error: {e}")
        return jsonify({"error": f"Processing failed: {e}"}), 500

@app.route('/api/analyze-url', methods=['POST'])
def api_analyze_url():
    """Dedicated robust URL analysis endpoint"""
    if not analyzer:
        return jsonify({"error": "Analyzer not initialized"}), 500
        
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "JSON data required"}), 400
            
        design_url = data.get('design_url', '').strip()
        desired_behavior = data.get('desired_behavior', '').strip()
        
        if not design_url:
            return jsonify({"error": "design_url is required"}), 400
            
        print(f"🌐 API URL Analysis for: {design_url}")
        start = time.time()
        results = analyzer.analyze_url(design_url, desired_behavior=desired_behavior)
        processing_time = round(time.time() - start, 2)
        
        # Handle analysis errors
        if results.get('error'):
            return jsonify({
                "error": results.get('message', 'URL analysis failed'),
                "processing_time": processing_time,
                "debug_info": results.get('meta', {}),
                "attempted_methods": results.get('meta', {}).get('attempted_methods', []),
                "suggestions": results.get('competing_prompts', {}).get('recommendations', [])
            }), 500

        # Successful analysis response
        api_response = {
            "success": True,
            "url_analyzed": design_url,
            "ctas": results.get("ctas", []),
            "competing_prompts": results.get("competing_prompts", {}),
            "behavioral_insights": results.get("behavioral_insights", []),
            "capture_info": {
                "method_used": results.get("meta", {}).get("capture_method", "unknown"),
                "capture_successful": True,
                "image_dimensions": f"{results.get('meta', {}).get('width', 'N/A')}x{results.get('meta', {}).get('height', 'N/A')}"
            },
            "meta": {
                "processing_time": f"{processing_time}s",
                "total_ctas_found": len(results.get("ctas", [])),
                "desired_behavior": desired_behavior or None,
                "analysis_version": results.get("meta", {}).get("analysis_version", "robust_v1"),
                "analyzer_capabilities": getattr(analyzer, 'methods', {})
            }
        }
        
        return jsonify(api_response)
        
    except Exception as e:
        print(f"❌ URL API Error: {e}")
        return jsonify({"error": f"URL analysis failed: {e}"}), 500

@app.get('/api/health')
def health():
    analyzer_status = "healthy" if analyzer else "error"
    capabilities = {}
    
    if analyzer and hasattr(analyzer, 'methods'):
        capabilities = analyzer.methods
    
    return {
        "status": analyzer_status, 
        "service": "Robust CTA Focus Analyzer API", 
        "version": "4.0.0",
        "features": [
            "multi_method_url_analysis", 
            "selenium_capture", 
            "playwright_capture",
            "chrome_headless",
            "screenshot_services",
            "image_analysis", 
            "behavioral_insights", 
            "priority_classification",
            "enhanced_ocr"
        ],
        "capabilities": capabilities,
        "analyzer_initialized": analyzer is not None,
        "analyzer_type": ANALYZER_TYPE
    }

@app.route('/debug')
def debug_analyzer():
    """Debug endpoint to check analyzer capabilities"""
    if not analyzer:
        return jsonify({"error": "Analyzer not initialized"})
    
    debug_info = {
        "analyzer_type": ANALYZER_TYPE,
        "methods_available": getattr(analyzer, 'methods', {}),
        "ocr_initialized": hasattr(analyzer, 'ocr'),
        "client_initialized": hasattr(analyzer, 'client'),
        "model": getattr(analyzer, 'model', 'unknown')
    }
    
    return jsonify(debug_info)

@app.route('/download-pdf', methods=['POST'])
def download_pdf():
    """Generate and download analysis results as PDF"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        # Create PDF in memory
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        story = []
        
        # Get styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            textColor=colors.darkblue
        )
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=20,
            textColor=colors.darkblue
        )
        
        # Title
        story.append(Paragraph("CTA Analysis Report", title_style))
        story.append(Spacer(1, 20))
        
        # Goal
        story.append(Paragraph("Your Goal", heading_style))
        story.append(Paragraph(data.get('desired_behavior', 'N/A'), styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Summary
        story.append(Paragraph("Analysis Summary", heading_style))
        summary_data = [
            ['Total CTAs Found', str(data.get('total_ctas', 0))],
            ['Total Conflicts', str(data.get('total_conflicts', 0))],
            ['Conflict Level', data.get('conflict_level', 'N/A')],
            ['Processing Time', f"{data.get('processing_time', 0)}s"]
        ]
        if data.get('source_url'):
            summary_data.append(['Source URL', data.get('source_url')])
        
        summary_table = Table(summary_data, colWidths=[2*inch, 3*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(summary_table)
        story.append(Spacer(1, 20))
        
        # Conflicts
        if data.get('conflicts'):
            story.append(Paragraph("Competing Prompts Found", heading_style))
            for conflict in data.get('conflicts', []):
                conflict_text = f"<b>{conflict.get('priority', 'N/A')} Priority - {conflict.get('element_type', 'N/A')}</b><br/>"
                conflict_text += f"Text: \"{conflict.get('element_text', 'N/A')}\"<br/>"
                conflict_text += f"Context: {conflict.get('context', 'N/A')}<br/>"
                conflict_text += f"Why it competes: {conflict.get('why_competes', 'N/A')}<br/>"
                if conflict.get('behavioral_impact'):
                    conflict_text += f"User Impact: {conflict.get('behavioral_impact', 'N/A')}<br/>"
                conflict_text += f"Severity Score: {conflict.get('severity_score', 'N/A')}/10"
                story.append(Paragraph(conflict_text, styles['Normal']))
                story.append(Spacer(1, 10))
            story.append(Spacer(1, 20))
        
        # Recommendations
        if data.get('recommendations'):
            story.append(Paragraph("Recommendations", heading_style))
            for rec in data.get('recommendations', []):
                rec_text = f"<b>{rec.get('priority', 'N/A')} Priority</b><br/>"
                rec_text += f"Action: {rec.get('action', 'N/A')}<br/>"
                rec_text += f"Rationale: {rec.get('rationale', 'N/A')}<br/>"
                rec_text += f"Expected Impact: {rec.get('expected_impact', 'N/A')}"
                story.append(Paragraph(rec_text, styles['Normal']))
                story.append(Spacer(1, 10))
            story.append(Spacer(1, 20))
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        
        # Generate filename
        filename = f"cta-analysis-{int(time.time())}.pdf"
        
        return send_file(
            buffer,
            as_attachment=True,
            download_name=filename,
            mimetype='application/pdf'
        )
        
    except Exception as e:
        print(f"❌ PDF generation failed: {e}")
        return jsonify({"error": f"PDF generation failed: {str(e)}"}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    
    print("🚀 Starting Robust CTA Analyzer...")
    print(f"📡 Server will run on port {port}")
    print(f"🔧 Debug mode: {debug_mode}")
    print(f"🤖 Analyzer type: {ANALYZER_TYPE}")
    
    if analyzer:
        print("✅ Analyzer ready with multiple URL capture methods!")
        if hasattr(analyzer, 'methods'):
            available_methods = [method for method, status in analyzer.methods.items() if status]
            print(f"🎯 Available capture methods: {', '.join(available_methods)}")
        print("💪 This version handles protected websites and bot detection!")
    else:
        print("❌ Analyzer not initialized - check your configuration")
    
    app.run(host='0.0.0.0', port=port, debug=debug_mode)