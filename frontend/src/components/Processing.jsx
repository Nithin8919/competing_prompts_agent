import React from 'react'
import { Loader2, Brain, Eye, BarChart3 } from 'lucide-react'

const Processing = ({ progress, imageName }) => {
  const getStageInfo = () => {
    if (progress < 30) {
      return {
        icon: Loader2,
        title: 'Uploading Image',
        description: 'Preparing your image for analysis...',
      }
    } else if (progress < 60) {
      return {
        icon: Brain,
        title: 'AI Detection',
        description: 'DETR model is identifying objects and elements...',
      }
    } else if (progress < 90) {
      return {
        icon: Eye,
        title: 'Focus Analysis',
        description: 'Calculating attention scores and visual hierarchy...',
      }
    } else {
      return {
        icon: BarChart3,
        title: 'Generating Results',
        description: 'Preparing your comprehensive analysis report...',
      }
    }
  }

  const stage = getStageInfo()
  const StageIcon = stage.icon

  return (
    <div className="max-w-2xl mx-auto">
      <div className="card text-center">
        {/* Processing Animation */}
        <div className="mb-8">
          <div className="p-6 bg-primary-600/20 rounded-full w-fit mx-auto mb-6">
            <StageIcon className="h-12 w-12 text-primary-400 animate-spin" />
          </div>
          
          <h2 className="text-2xl font-bold text-white mb-2">{stage.title}</h2>
          <p className="text-navy-400">{stage.description}</p>
        </div>

        {/* Progress Bar */}
        <div className="mb-6">
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm text-navy-400">Processing {imageName}</span>
            <span className="text-sm font-medium text-primary-400">{Math.round(progress)}%</span>
          </div>
          
          <div className="w-full bg-navy-700 rounded-full h-3">
            <div 
              className="bg-gradient-to-r from-primary-600 to-primary-500 h-3 rounded-full transition-all duration-300 ease-out"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>

        {/* Processing Steps */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-left">
          <div className={`p-4 rounded-lg border-2 transition-all duration-300 ${
            progress >= 30 ? 'bg-green-900/20 border-green-600' : 'bg-navy-800 border-navy-600'
          }`}>
            <div className="flex items-center space-x-2 mb-2">
              <div className={`w-2 h-2 rounded-full ${
                progress >= 30 ? 'bg-green-400' : 'bg-navy-500'
              }`} />
              <span className="text-sm font-medium text-white">Upload</span>
            </div>
            <p className="text-xs text-navy-400">Image preprocessing</p>
          </div>
          
          <div className={`p-4 rounded-lg border-2 transition-all duration-300 ${
            progress >= 60 ? 'bg-blue-900/20 border-blue-600' : progress >= 30 ? 'bg-yellow-900/20 border-yellow-600' : 'bg-navy-800 border-navy-600'
          }`}>
            <div className="flex items-center space-x-2 mb-2">
              <div className={`w-2 h-2 rounded-full ${
                progress >= 60 ? 'bg-blue-400' : progress >= 30 ? 'bg-yellow-400' : 'bg-navy-500'
              }`} />
              <span className="text-sm font-medium text-white">Detect</span>
            </div>
            <p className="text-xs text-navy-400">Object identification</p>
          </div>
          
          <div className={`p-4 rounded-lg border-2 transition-all duration-300 ${
            progress >= 90 ? 'bg-purple-900/20 border-purple-600' : progress >= 60 ? 'bg-yellow-900/20 border-yellow-600' : 'bg-navy-800 border-navy-600'
          }`}>
            <div className="flex items-center space-x-2 mb-2">
              <div className={`w-2 h-2 rounded-full ${
                progress >= 90 ? 'bg-purple-400' : progress >= 60 ? 'bg-yellow-400' : 'bg-navy-500'
              }`} />
              <span className="text-sm font-medium text-white">Analyze</span>
            </div>
            <p className="text-xs text-navy-400">Score calculation</p>
          </div>
        </div>

        {/* Fun Facts */}
        <div className="mt-8 p-4 bg-navy-800/50 rounded-lg">
          <h3 className="text-sm font-medium text-white mb-2">💡 Did you know?</h3>
          <p className="text-xs text-navy-400">
            The average user spends only 8 seconds on a webpage before deciding to stay or leave. 
            Strategic CTA placement can increase conversion rates by up to 161%!
          </p>
        </div>
      </div>
    </div>
  )
}

export default Processing
