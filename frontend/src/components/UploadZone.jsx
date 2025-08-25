import React, { useState, useRef } from 'react'
import { Upload, Image as ImageIcon, FileImage } from 'lucide-react'

const UploadZone = ({ onImageUpload }) => {
  const [isDragOver, setIsDragOver] = useState(false)
  const fileInputRef = useRef(null)

  const handleDragEnter = (e) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragOver(true)
  }

  const handleDragLeave = (e) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragOver(false)
  }

  const handleDragOver = (e) => {
    e.preventDefault()
    e.stopPropagation()
  }

  const handleDrop = (e) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragOver(false)

    const files = Array.from(e.dataTransfer.files)
    const imageFile = files.find(file => file.type.startsWith('image/'))
    
    if (imageFile) {
      validateAndUpload(imageFile)
    }
  }

  const handleFileSelect = (e) => {
    const file = e.target.files[0]
    if (file) {
      validateAndUpload(file)
    }
  }

  const validateAndUpload = (file) => {
    // Check file size (max 10MB)
    if (file.size > 10 * 1024 * 1024) {
      alert('File size must be less than 10MB')
      return
    }

    // Check file type
    const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/bmp', 'image/webp']
    if (!allowedTypes.includes(file.type)) {
      alert('Please upload a valid image file (JPEG, PNG, GIF, BMP, WebP)')
      return
    }

    onImageUpload(file)
  }

  const openFileDialog = () => {
    fileInputRef.current?.click()
  }

  return (
    <div className="max-w-4xl mx-auto">
      {/* Hero Section */}
      <div className="text-center mb-12">
        <h2 className="text-4xl font-bold text-white mb-4">
          Analyze Your Design's <span className="text-primary-400">Focus Points</span>
        </h2>
        <p className="text-xl text-navy-300 max-w-2xl mx-auto">
          Upload an image and discover which elements compete for your users' attention. 
          Get actionable insights on CTA positioning and visual hierarchy.
        </p>
      </div>

      {/* Upload Area */}
      <div
        className={`upload-zone ${isDragOver ? 'dragover' : ''} cursor-pointer`}
        onDragEnter={handleDragEnter}
        onDragLeave={handleDragLeave}
        onDragOver={handleDragOver}
        onDrop={handleDrop}
        onClick={openFileDialog}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept="image/*"
          onChange={handleFileSelect}
          className="hidden"
        />
        
        <div className="flex flex-col items-center space-y-4">
          <div className="p-4 bg-primary-600/20 rounded-full">
            <Upload className="h-12 w-12 text-primary-400" />
          </div>
          
          <div className="text-center">
            <h3 className="text-xl font-semibold text-white mb-2">
              Drop your image here or click to browse
            </h3>
            <p className="text-navy-400 mb-4">
              Supports JPEG, PNG, GIF, BMP, WebP • Max 10MB
            </p>
            
            <button className="btn-primary inline-flex items-center space-x-2">
              <FileImage className="h-4 w-4" />
              <span>Choose File</span>
            </button>
          </div>
        </div>
      </div>

      {/* Features */}
      <div className="grid md:grid-cols-3 gap-6 mt-12">
        <div className="card text-center">
          <div className="p-3 bg-green-600/20 rounded-full w-fit mx-auto mb-4">
            <ImageIcon className="h-6 w-6 text-green-400" />
          </div>
          <h3 className="font-semibold text-white mb-2">AI-Powered Detection</h3>
          <p className="text-navy-400 text-sm">
            Uses advanced DETR models to identify interactive elements and potential CTAs
          </p>
        </div>
        
        <div className="card text-center">
          <div className="p-3 bg-blue-600/20 rounded-full w-fit mx-auto mb-4">
            <Zap className="h-6 w-6 text-blue-400" />
          </div>
          <h3 className="font-semibold text-white mb-2">Focus Scoring</h3>
          <p className="text-navy-400 text-sm">
            Calculates attention scores based on size, position, and visual prominence
          </p>
        </div>
        
        <div className="card text-center">
          <div className="p-3 bg-purple-600/20 rounded-full w-fit mx-auto mb-4">
            <FileImage className="h-6 w-6 text-purple-400" />
          </div>
          <h3 className="font-semibold text-white mb-2">Export Reports</h3>
          <p className="text-navy-400 text-sm">
            Generate PDF reports with annotated images and detailed analysis
          </p>
        </div>
      </div>
    </div>
  )
}

export default UploadZone
