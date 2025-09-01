import React, { useState } from 'react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Textarea } from './ui/textarea';
import { apiService, CTAAnalysisResponse } from '../services/api';
import { BackendStatus } from './BackendStatus';

interface CTAAnalyzerProps {
  onAnalysisComplete: (results: CTAAnalysisResponse) => void;
}

export const CTAAnalyzer: React.FC<CTAAnalyzerProps> = ({ onAnalysisComplete }) => {
  const [url, setUrl] = useState('');
  const [desiredBehavior, setDesiredBehavior] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [inputType, setInputType] = useState<'url' | 'file'>('url');

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      setError('');
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!desiredBehavior.trim()) {
      setError('Please describe your desired user behavior');
      return;
    }

    if (inputType === 'url' && !url.trim()) {
      setError('Please enter a URL to analyze');
      return;
    }

    if (inputType === 'file' && !selectedFile) {
      setError('Please select an image file');
      return;
    }

    setIsLoading(true);
    setError('');

    try {
      let results: CTAAnalysisResponse;
      
      if (inputType === 'url') {
        results = await apiService.analyzeURL(url, desiredBehavior);
      } else {
        results = await apiService.analyzeImage(selectedFile!, desiredBehavior);
      }

      console.log('Analysis completed, results:', results);
      onAnalysisComplete(results);
    } catch (err) {
      console.error('Analysis error:', err);
      setError(err instanceof Error ? err.message : 'Analysis failed');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="w-full max-w-4xl mx-auto p-8 bg-white rounded-lg shadow-lg">
      <div className="text-center mb-8">
        <h2 className="text-3xl font-bold text-gray-900 mb-4">
          CTA Analyzer
        </h2>
        <p className="text-lg text-gray-600 mb-4">
          Analyze your website or design to find competing CTAs that hurt conversions
        </p>
        <div className="flex justify-center items-center gap-4">
          <BackendStatus />
          <button
            onClick={async () => {
              try {
                const health = await apiService.checkHealth();
                console.log('Backend health:', health);
                alert('Backend is working! Check console for details.');
              } catch (error) {
                console.error('Backend test failed:', error);
                alert(`Backend test failed: ${error}`);
              }
            }}
            className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded hover:bg-blue-200"
          >
            Test Connection
          </button>
        </div>
      </div>

      {/* Input Type Toggle */}
      <div className="flex justify-center mb-6">
        <div className="bg-gray-100 rounded-lg p-1">
          <button
            type="button"
            onClick={() => setInputType('url')}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              inputType === 'url'
                ? 'bg-white text-gray-900 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            Analyze URL
          </button>
          <button
            type="button"
            onClick={() => setInputType('file')}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              inputType === 'file'
                ? 'bg-white text-gray-900 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            Upload Image
          </button>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* URL Input */}
        {inputType === 'url' && (
          <div>
            <Label htmlFor="url" className="text-sm font-medium text-gray-700">
              Website URL
            </Label>
            <Input
              id="url"
              type="url"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="https://example.com"
              className="mt-1"
            />
          </div>
        )}

        {/* File Upload */}
        {inputType === 'file' && (
          <div>
            <Label htmlFor="file" className="text-sm font-medium text-gray-700">
              Upload Screenshot or Design
            </Label>
            <div className="mt-1">
              <Input
                id="file"
                type="file"
                accept="image/*"
                onChange={handleFileChange}
                className="file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-medium file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
              />
              {selectedFile && (
                <p className="mt-2 text-sm text-gray-600">
                  Selected: {selectedFile.name}
                </p>
              )}
            </div>
          </div>
        )}

        {/* Desired Behavior */}
        <div>
          <Label htmlFor="behavior" className="text-sm font-medium text-gray-700">
            What do you want users to do?
          </Label>
          <Textarea
            id="behavior"
            value={desiredBehavior}
            onChange={(e) => setDesiredBehavior(e.target.value)}
            placeholder="e.g., Sign up for newsletter, Buy product, Book demo, Download app..."
            rows={3}
            className="mt-1"
          />
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-md p-4">
            <p className="text-sm text-red-600">{error}</p>
          </div>
        )}

        {/* Submit Button */}
        <div className="text-center">
          <Button
            type="submit"
            disabled={isLoading}
            className="bg-gradient-to-r from-[#09c2ff] to-[#0073ff] text-white px-8 py-3 rounded-lg font-medium text-lg hover:opacity-90 disabled:opacity-50"
          >
            {isLoading ? (
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                Analyzing...
              </div>
            ) : (
              'Analyze CTAs'
            )}
          </Button>
        </div>
      </form>

      {/* Features */}
      <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-4 text-center">
        <div className="p-4">
          <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mx-auto mb-3">
            <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <h3 className="font-medium text-gray-900 mb-1">Find Conflicts</h3>
          <p className="text-sm text-gray-600">Identify competing CTAs that confuse users</p>
        </div>
        
        <div className="p-4">
          <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mx-auto mb-3">
            <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
          </div>
          <h3 className="font-medium text-gray-900 mb-1">Boost Conversions</h3>
          <p className="text-sm text-gray-600">Get actionable recommendations to improve results</p>
        </div>
        
        <div className="p-4">
          <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mx-auto mb-3">
            <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
          </div>
          <h3 className="font-medium text-gray-900 mb-1">AI-Powered</h3>
          <p className="text-sm text-gray-600">Advanced OCR and behavioral analysis</p>
        </div>
      </div>
    </div>
  );
};
