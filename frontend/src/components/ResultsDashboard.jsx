import React, { useState } from 'react';
import PDFExport from './PDFExport';
import ConflictVisualizer from './ConflictVisualizer';

const ResultsDashboard = ({ results, onBack }) => {
  const [selectedConflict, setSelectedConflict] = useState(null);
  const [viewMode, setViewMode] = useState('overview'); // 'overview', 'conflicts', 'ctas'

  if (!results) return null;

  const { ctas = [], competing_prompts = {}, meta = {} } = results;
  const conflicts = competing_prompts.primary_conflicts || [];
  const conflictLevel = competing_prompts.conflict_level || 'low';

  const getConflictColor = (level) => {
    switch (level) {
      case 'critical': return 'bg-red-600 text-white';
      case 'high': return 'bg-orange-500 text-white';
      case 'medium': return 'bg-yellow-500 text-black';
      case 'low': return 'bg-green-500 text-white';
      default: return 'bg-gray-500 text-white';
    }
  };

  const getConflictIcon = (level) => {
    switch (level) {
      case 'critical': return '🚨';
      case 'high': return '⚠️';
      case 'medium': return '⚡';
      case 'low': return '✅';
      default: return 'ℹ️';
    }
  };

  const getSeverityScore = (level) => {
    switch (level) {
      case 'critical': return 100;
      case 'high': return 75;
      case 'medium': return 50;
      case 'low': return 25;
      default: return 0;
    }
  };

  const calculateConflictImpact = (conflict) => {
    const severityScore = getSeverityScore(conflict.severity);
    const ctaCount = conflict.cta_indices?.length || 0;
    const proximityBonus = ctaCount > 1 ? 20 : 0;
    return Math.min(100, severityScore + proximityBonus);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 p-6">
      {/* Header */}
      <div className="max-w-7xl mx-auto">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-4xl font-bold text-gray-900 mb-2">
              CTA Conflict Analysis
            </h1>
            <p className="text-lg text-gray-600">
              {ctas.length} CTAs found • {conflicts.length} conflicts detected
            </p>
          </div>
          <div className="flex gap-3">
            <button
              onClick={onBack}
              className="px-6 py-3 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
            >
              ← Back to Upload
            </button>
            <PDFExport results={results} />
          </div>
        </div>

        {/* Navigation Tabs */}
        <div className="flex gap-2 mb-8">
          <button
            onClick={() => setViewMode('overview')}
            className={`px-6 py-3 rounded-lg font-medium transition-all ${
              viewMode === 'overview'
                ? 'bg-blue-600 text-white shadow-lg'
                : 'bg-white text-gray-600 hover:bg-gray-50'
            }`}
          >
            📊 Overview
          </button>
          <button
            onClick={() => setViewMode('conflicts')}
            className={`px-6 py-3 rounded-lg font-medium transition-all ${
              viewMode === 'conflicts'
                ? 'bg-blue-600 text-white shadow-lg'
                : 'bg-white text-gray-600 hover:bg-gray-50'
            }`}
          >
            ⚔️ Conflicts ({conflicts.length})
          </button>
          <button
            onClick={() => setViewMode('ctas')}
            className={`px-6 py-3 rounded-lg font-medium transition-all ${
              viewMode === 'ctas'
                ? 'bg-blue-600 text-white shadow-lg'
                : 'bg-white text-gray-600 hover:bg-gray-50'
            }`}
          >
            🎯 All CTAs ({ctas.length})
          </button>
        </div>

        {/* Overview Mode */}
        {viewMode === 'overview' && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
            {/* Overall Conflict Level */}
            <div className="bg-white rounded-xl shadow-lg p-6 border-l-4 border-blue-500">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-xl font-semibold text-gray-900">Overall Conflict Level</h3>
                <span className={`px-3 py-1 rounded-full text-sm font-medium ${getConflictColor(conflictLevel)}`}>
                  {getConflictIcon(conflictLevel)} {conflictLevel.toUpperCase()}
                </span>
              </div>
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Conflicts Found:</span>
                  <span className="font-semibold">{conflicts.length}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Total Competing:</span>
                  <span className="font-semibold">{competing_prompts.total_competing || 0}</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className={`h-2 rounded-full transition-all duration-500 ${
                      conflictLevel === 'critical' ? 'bg-red-600' :
                      conflictLevel === 'high' ? 'bg-orange-500' :
                      conflictLevel === 'medium' ? 'bg-yellow-500' : 'bg-green-500'
                    }`}
                    style={{ width: `${getSeverityScore(conflictLevel)}%` }}
                  ></div>
                </div>
              </div>
            </div>

            {/* CTA Distribution */}
            <div className="bg-white rounded-xl shadow-lg p-6 border-l-4 border-green-500">
              <h3 className="text-xl font-semibold text-gray-900 mb-4">CTA Distribution</h3>
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Primary CTAs:</span>
                  <span className="font-semibold text-green-600">
                    {ctas.filter(c => c.goal_role === 'primary').length}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Supporting CTAs:</span>
                  <span className="font-semibold text-blue-600">
                    {ctas.filter(c => c.goal_role === 'supporting').length}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Off-Goal CTAs:</span>
                  <span className="font-semibold text-red-600">
                    {ctas.filter(c => c.goal_role === 'off-goal').length}
                  </span>
                </div>
              </div>
            </div>

            {/* Recommendations */}
            <div className="bg-white rounded-xl shadow-lg p-6 border-l-4 border-purple-500">
              <h3 className="text-xl font-semibold text-gray-900 mb-4">Quick Actions</h3>
              <div className="space-y-2">
                {competing_prompts.recommendations?.slice(0, 3).map((rec, idx) => (
                  <div key={idx} className="text-sm text-gray-700 bg-purple-50 p-2 rounded">
                    💡 {rec}
                  </div>
                ))}
                {(!competing_prompts.recommendations || competing_prompts.recommendations.length === 0) && (
                  <div className="text-sm text-gray-500 italic">
                    No specific recommendations available
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Conflicts Mode */}
        {viewMode === 'conflicts' && (
          <ConflictVisualizer conflicts={conflicts} ctas={ctas} />
        )}

        {/* CTAs Mode */}
        {viewMode === 'ctas' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
            {ctas.map((cta, idx) => (
              <div key={idx} className="bg-white rounded-xl shadow-lg overflow-hidden hover:shadow-xl transition-shadow">
                <div className={`p-4 ${getCtaHeaderColor(cta.goal_role)}`}>
                  <div className="flex items-center justify-between">
                    <h3 className="font-semibold text-white truncate">
                      {cta.extracted_text}
                    </h3>
                    <span className="text-sm opacity-90">#{idx}</span>
                  </div>
                </div>
                
                <div className="p-4">
                  <div className="space-y-3">
                    <div className="flex justify-between items-center">
                      <span className="text-gray-600">Score:</span>
                      <div className="flex items-center gap-2">
                        <div className="w-20 bg-gray-200 rounded-full h-2">
                          <div 
                            className="bg-blue-500 h-2 rounded-full transition-all duration-500"
                            style={{ width: `${cta.score}%` }}
                          ></div>
                        </div>
                        <span className="font-semibold text-gray-900">{cta.score}</span>
                      </div>
                    </div>
                    
                    <div className="flex justify-between">
                      <span className="text-gray-600">Role:</span>
                      <span className={`px-2 py-1 rounded text-xs font-medium ${getRoleColor(cta.goal_role)}`}>
                        {cta.goal_role}
                      </span>
                    </div>
                    
                    <div className="flex justify-between">
                      <span className="text-gray-600">Area:</span>
                      <span className="font-medium">{cta.area_percentage}%</span>
                    </div>
                    
                    <div className="flex justify-between">
                      <span className="text-gray-600">Confidence:</span>
                      <span className="font-medium">{(cta.confidence_estimate * 100).toFixed(0)}%</span>
                    </div>
                  </div>
                  
                  <div className="mt-4 p-2 bg-gray-50 rounded text-xs text-gray-600">
                    BBox: [{cta.bbox[0]}, {cta.bbox[1]}, {cta.bbox[2]}, {cta.bbox[3]}]
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

// Helper functions for colors
const getCtaHeaderColor = (role) => {
  switch (role) {
    case 'primary': return 'bg-green-600';
    case 'supporting': return 'bg-blue-600';
    case 'off-goal': return 'bg-red-600';
    default: return 'bg-gray-600';
  }
};

const getRoleColor = (role) => {
  switch (role) {
    case 'primary': return 'bg-green-100 text-green-800';
    case 'supporting': return 'bg-blue-100 text-blue-800';
    case 'off-goal': return 'bg-red-100 text-red-800';
    default: return 'bg-gray-100 text-gray-800';
  }
};

export default ResultsDashboard;
