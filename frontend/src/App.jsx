import React, { useState } from 'react'
import UploadZone from './components/UploadZone'
import Processing from './components/Processing'
import ResultsDashboard from './components/ResultsDashboard'
import { Zap, Github } from 'lucide-react'

function App() {
  const [currentStep, setCurrentStep] = useState('upload') // upload, processing, results
  const [uploadedImage, setUploadedImage] = useState(null)
  const [analysisResults, setAnalysisResults] = useState(null)
  const [processingProgress, setProcessingProgress] = useState(0)

  const handleImageUpload = (file) => {
    setUploadedImage(file)
    setCurrentStep('processing')
    setProcessingProgress(0)
    
    // Simulate processing progress
    const progressInterval = setInterval(() => {
      setProcessingProgress(prev => {
        if (prev >= 90) {
          clearInterval(progressInterval)
          return 90
        }
        return prev + Math.random() * 20
      })
    }, 200)

    // Call API
    const formData = new FormData()
    formData.append('image', file)

    fetch('/api/analyze', {
      method: 'POST',
      body: formData,
    })
    .then(response => response.json())
    .then(data => {
      clearInterval(progressInterval)
      setProcessingProgress(100)
      
      setTimeout(() => {
        setAnalysisResults(data)
        setCurrentStep('results')
      }, 500)
    })
    .catch(error => {
      clearInterval(progressInterval)
      console.error('Analysis failed:', error)
      alert('Analysis failed. Please try again.')
      setCurrentStep('upload')
    })
  }

  const handleReset = () => {
    setCurrentStep('upload')
    setUploadedImage(null)
    setAnalysisResults(null)
    setProcessingProgress(0)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-navy-900 via-navy-800 to-navy-900">
      {/* Header */}
      <header className="border-b border-navy-700 bg-navy-900/50 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-primary-600 rounded-lg">
                <Zap className="h-6 w-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-white">CTA Focus Analyzer</h1>
                <p className="text-navy-400 text-sm">Analyze competing prompts in your designs</p>
              </div>
            </div>
            <a 
              href="https://github.com" 
              target="_blank" 
              rel="noopener noreferrer"
              className="text-navy-400 hover:text-white transition-colors"
            >
              <Github className="h-5 w-5" />
            </a>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {currentStep === 'upload' && (
          <UploadZone onImageUpload={handleImageUpload} />
        )}
        
        {currentStep === 'processing' && (
          <Processing 
            progress={processingProgress}
            imageName={uploadedImage?.name}
          />
        )}
        
        {currentStep === 'results' && (
          <ResultsDashboard 
            results={analysisResults}
            onBack={() => setCurrentStep('upload')}
          />
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-navy-700 bg-navy-900/50 backdrop-blur-sm mt-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="text-center text-navy-400 text-sm">
            <p>Built with React, Flask, and HuggingFace DETR • Deploy on Netlify + Render</p>
          </div>
        </div>
      </footer>
    </div>
  )
}

export default App
