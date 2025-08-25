# 🎯 CTA Focus Analyzer

An AI-powered web application that analyzes images to identify and score Call-to-Action (CTA) elements, helping designers understand visual hierarchy and competing prompts in their designs.

![CTA Focus Analyzer Demo](https://via.placeholder.com/800x400/1e293b/60a5fa?text=CTA+Focus+Analyzer+Demo)

## ✨ Features

- **AI-Powered Detection**: Uses HuggingFace DETR models to identify interactive elements
- **Focus Scoring**: Calculates attention scores based on size, position, and visual prominence
- **Visual Overlays**: Interactive bounding boxes with color-coded intensity
- **PDF Export**: Generate comprehensive analysis reports
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile
- **Real-time Processing**: Fast analysis with progress tracking

## 🚀 Quick Start (100% Isolated)

### Prerequisites

- Python 3.9+ (system installation)
- Node.js 18+ (system installation)
- npm or yarn

### 🔒 Complete Isolation Setup

This project uses **completely isolated environments** that won't affect your system:
- ✅ Python packages → `.venv/` (isolated virtual environment)
- ✅ Node packages → `frontend/node_modules/` (isolated)
- ✅ No global installations required
- ✅ No system Python/Node modifications

### 1. Clone and Automated Setup

```bash
git clone <your-repo-url>
cd competing-prompts-agent

# Automated isolated setup (recommended)
python3 setup.py
```

The setup script will:
- Create isolated Python virtual environment (`.venv/`)
- Install all Python dependencies in isolation
- Install all Node.js dependencies locally
- Verify isolation is working correctly

### 2. Safe Execution Options

**Option A: Safe Auto-Runner (Recommended)**
```bash
# Automatically activates venv and runs servers safely
python3 activate_and_run.py
```

**Option B: Manual Steps (Full Control)**
```bash
# 1. Activate virtual environment (REQUIRED)
source .venv/bin/activate    # Mac/Linux
# OR
.venv\Scripts\activate       # Windows

# 2. Verify isolation
python -c "import sys; print('✅ Using:', sys.prefix)"
# Should show path ending with .venv

# 3. Start backend
cd backend
python main.py               # Runs on localhost:5000

# 4. In new terminal, start frontend  
cd frontend
npm run dev                  # Runs on localhost:3000
```

### 3. Verification Commands

**Check Virtual Environment:**
```bash
# After activating .venv
which python                 # Should show .venv/bin/python
pip list                     # Shows only project packages
```

**Check Isolation:**
```bash
# Deactivate and check system remains clean
deactivate
pip list                     # Should NOT show project packages
```

### 4. Open Application

Visit `http://localhost:3000` and start analyzing! 🎯

### 🛡️ Safety Features

- **No system modifications**: Everything in `.venv/` and `node_modules/`
- **Easy cleanup**: Delete project folder = complete removal
- **Environment detection**: Setup warns about existing environments
- **Verification**: Scripts confirm isolation is working

### 🔍 Verification & Cleanup

**Verify Complete Isolation:**
```bash
# Check that everything is properly isolated
python3 verify_isolation.py
```

**Complete Cleanup (when done):**
```bash
# Safely remove all dependencies
python3 cleanup.py

# OR manual cleanup
rm -rf .venv frontend/node_modules frontend/dist
```

**Quick Health Check:**
```bash
# Confirm virtual environment is active
source .venv/bin/activate
which python              # Should show .venv/bin/python
pip list                  # Should show project packages only

# Confirm system is clean
deactivate
pip list                  # Should NOT show project packages
```

## 🏗️ Tech Stack

### Backend
- **Flask**: REST API framework
- **HuggingFace Transformers**: DETR object detection model
- **PyTorch**: Deep learning framework
- **Pillow**: Image processing

### Frontend
- **React 18**: UI framework
- **Vite**: Build tool and dev server
- **TailwindCSS**: Utility-first CSS framework
- **Lucide React**: Beautiful icons
- **jsPDF + html2canvas**: PDF generation

### Deployment
- **Netlify**: Frontend hosting
- **Render**: Backend hosting

## 📊 How It Works

1. **Upload**: Drag & drop or select an image file
2. **Detection**: DETR model identifies objects and potential CTAs
3. **Scoring**: Algorithm calculates attention scores based on:
   - **Size Score**: Element area relative to image size
   - **Centrality Score**: Distance from image center
   - **Composite Score**: Weighted average (50% size + 50% centrality)
4. **Visualization**: Interactive overlays with color-coded intensity
5. **Export**: Generate PDF reports with recommendations

## 🔧 Configuration

### Environment Variables

Create `.env` file in backend directory:

```env
# Flask Configuration
FLASK_ENV=development
PORT=5000

# Model Configuration  
MODEL_CONFIDENCE_THRESHOLD=0.7
```

### API Endpoints

- `GET /api/health` - Health check
- `POST /api/analyze` - Analyze image (multipart/form-data)

Example response:
```json
{
  "ctas": [
    {
      "label": "Laptop Interface",
      "bbox": [100, 150, 300, 250],
      "score": 82,
      "confidence": 94.5,
      "type": "interface",
      "area_percentage": 8.5
    }
  ],
  "meta": {
    "processing_time": "1.2s",
    "image_dims": "1200x800",
    "total_ctas_found": 3,
    "confidence_threshold": 0.7
  }
}
```

## 🚀 Deployment

### Frontend (Netlify)

1. **Connect Repository:**
   - Go to [Netlify](https://netlify.com)
   - Click "Add new site" → "Import an existing project"
   - Connect your GitHub repository

2. **Configure Build:**
   - Base directory: `frontend`
   - Build command: `npm run build`
   - Publish directory: `frontend/dist`

3. **Update Backend URL:**
   - Update `netlify.toml` with your Render backend URL
   - Replace `https://your-backend-url.onrender.com` with actual URL

### Backend (Render)

1. **Connect Repository:**
   - Go to [Render](https://render.com)
   - Click "New" → "Web Service"
   - Connect your GitHub repository

2. **Configure Service:**
   - Name: `cta-analyzer-backend`
   - Environment: `Python 3`
   - Build Command: `pip install -r backend/requirements.txt`
   - Start Command: `cd backend && gunicorn main:app`

3. **Environment Variables:**
   - `PYTHON_VERSION`: `3.9.16`
   - `PORT`: `10000`

### Manual Deployment

**Backend (any VPS):**
```bash
# Install dependencies
pip install -r backend/requirements.txt

# Run with Gunicorn
cd backend
gunicorn main:app --bind 0.0.0.0:5000
```

**Frontend (any static host):**
```bash
cd frontend
npm run build
# Upload dist/ folder to your hosting provider
```

## 📁 Project Structure

```
competing-prompts-agent/
├── backend/
│   ├── main.py              # Flask API server
│   ├── analyzer.py          # DETR model & scoring logic
│   ├── requirements.txt     # Python dependencies
│   └── Procfile            # Render deployment config
├── frontend/
│   ├── src/
│   │   ├── components/     # React components
│   │   │   ├── UploadZone.jsx
│   │   │   ├── Processing.jsx
│   │   │   ├── ResultsDashboard.jsx
│   │   │   └── PDFExport.jsx
│   │   ├── App.jsx         # Main app component
│   │   ├── main.jsx        # React entry point
│   │   └── index.css       # Global styles
│   ├── package.json        # Node.js dependencies
│   ├── vite.config.js      # Vite configuration
│   ├── tailwind.config.js  # TailwindCSS config
│   └── netlify.toml        # Netlify deployment config
├── setup.py                # Automated setup script
├── render.yaml             # Render deployment config
├── .gitignore             # Git ignore rules
└── README.md              # This file
```

## 🎨 Customization

### Adding New CTA Types

Edit `backend/analyzer.py`:

```python
def _classify_as_cta(self, class_name):
    cta_mappings = {
        'tv': 'screen',
        'laptop': 'interface',
        'button': 'button',        # Add new mappings
        'form': 'input',           # Add new mappings
        # ... add more
    }
    return cta_mappings.get(class_name)
```

### Customizing Scoring Algorithm

Modify scoring weights in `analyzer.py`:

```python
# Current: 50% size + 50% centrality
composite_score = int((size_score * 0.5 + centrality_score * 0.5))

# Example: 70% size + 30% centrality  
composite_score = int((size_score * 0.7 + centrality_score * 0.3))
```

### UI Theming

Update `frontend/tailwind.config.js` for custom colors:

```javascript
theme: {
  extend: {
    colors: {
      primary: {
        // Add your brand colors
      }
    }
  }
}
```

## 🐛 Troubleshooting

### Virtual Environment Issues

**Virtual environment not activating:**
```bash
# Recreate virtual environment
rm -rf .venv
python3 setup.py

# Verify activation
source .venv/bin/activate
which python  # Should show .venv/bin/python
```

**Packages not found after activation:**
```bash
# Ensure you're in virtual environment
source .venv/bin/activate
python3 verify_isolation.py

# Reinstall if needed
pip install -r backend/requirements.txt
```

**System Python contamination:**
```bash
# Check if accidentally using system Python
python -c "import sys; print(sys.prefix)"
# Should contain '.venv', not system path

# If using wrong Python, deactivate and reactivate
deactivate
source .venv/bin/activate
```

### Common Issues

**Backend not starting:**
```bash
# Ensure virtual environment is activated FIRST
source .venv/bin/activate
which python  # Verify venv is active

# Check Python version in venv
python --version  # Should be 3.9+

# Install dependencies in venv
pip install -r backend/requirements.txt

# Run from correct directory
cd backend
python main.py
```

**Frontend build errors:**
```bash
# Clear and reinstall (from frontend directory)
cd frontend
rm -rf node_modules package-lock.json
npm install

# Check Node.js version
node --version  # Should be 18+
```

**CORS errors:**
- Ensure Flask-CORS is installed in venv: `pip install flask-cors`
- Check backend URL in frontend API calls
- Verify both servers are running

**Model loading errors:**
- First run downloads ~165MB DETR model
- Ensure stable internet connection
- Check available disk space (>2GB recommended)
- Verify torch is installed: `pip list | grep torch`

### Performance Optimization

**Backend:**
- Use GPU if available: Install `torch[cuda]`
- Implement model caching
- Add request rate limiting

**Frontend:**
- Enable image compression before upload
- Implement lazy loading for large result sets
- Add service worker for offline functionality

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 🙋‍♂️ Support

- **Issues**: [GitHub Issues](https://github.com/your-username/competing-prompts-agent/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-username/competing-prompts-agent/discussions)
- **Email**: your-email@example.com

---

**Built with ❤️ by [Your Name]**

*Empowering designers with AI-driven insights for better user experiences.*
