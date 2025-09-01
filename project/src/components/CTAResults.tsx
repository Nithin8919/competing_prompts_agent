import React from 'react';
import { Button } from './ui/button';
import { CTAAnalysisResponse } from '../services/api';

interface CTAResultsProps {
  results: CTAAnalysisResponse;
  onNewAnalysis: () => void;
}

export const CTAResults: React.FC<CTAResultsProps> = ({ results, onNewAnalysis }) => {
  // Debug: Log the results to see what we're getting
  console.log('CTAResults received:', results);
  
  const { ctas, competing_prompts, behavioral_insights, analytics, meta } = results;
  const { conflicts, recommendations } = competing_prompts || {};

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'HIGH': return 'bg-red-100 text-red-800 border-red-200';
      case 'MEDIUM': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'LOW': return 'bg-green-100 text-green-800 border-green-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getConflictLevelColor = (level: string) => {
    switch (level) {
      case 'critical': return 'bg-red-100 text-red-800';
      case 'high': return 'bg-orange-100 text-orange-800';
      case 'medium': return 'bg-yellow-100 text-yellow-800';
      case 'low': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getGoalRoleColor = (role: string) => {
    switch (role) {
      case 'primary': return 'bg-blue-100 text-blue-800';
      case 'supporting': return 'bg-green-100 text-green-800';
      case 'off-goal': return 'bg-red-100 text-red-800';
      case 'neutral': return 'bg-gray-100 text-gray-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  // Safety checks
  if (!results) {
    return (
      <div className="w-full max-w-6xl mx-auto p-8 bg-white rounded-lg shadow-lg">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-red-600 mb-4">No Results Received</h2>
          <Button
            variant="orange"
            onClick={onNewAnalysis}
            className="font-medium"
          >
            ← Try Again
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full max-w-6xl mx-auto p-8 bg-white rounded-lg shadow-lg">
      {/* Header */}
      <div className="text-center mb-8">
        <h2 className="text-3xl font-bold text-gray-900 mb-4">
          Analysis Results
        </h2>
        <div className="flex justify-center gap-4 mb-4">
          <span className={`px-3 py-1 rounded-full text-sm font-medium ${getConflictLevelColor(competing_prompts?.conflict_level || 'unknown')}`}>
            {(competing_prompts?.conflict_level || 'unknown').toUpperCase()} CONFLICT LEVEL
          </span>
          <span className="px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800">
            {analytics?.total_ctas || ctas?.length || 0} CTAs FOUND
          </span>
          <span className="px-3 py-1 rounded-full text-sm font-medium bg-purple-100 text-purple-800">
            {meta?.processing_time || 'N/A'} PROCESSING TIME
          </span>
        </div>
        <Button
          variant="orange"
          onClick={onNewAnalysis}
          className="font-medium"
        >
          ← Analyze Another Design
        </Button>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        <div className="bg-blue-50 p-4 rounded-lg">
          <h3 className="text-sm font-medium text-blue-600 mb-1">Total CTAs</h3>
          <p className="text-2xl font-bold text-blue-900">{analytics?.total_ctas || ctas?.length || 0}</p>
        </div>
        <div className="bg-green-50 p-4 rounded-lg">
          <h3 className="text-sm font-medium text-green-600 mb-1">Primary CTAs</h3>
          <p className="text-2xl font-bold text-green-900">{analytics?.primary_ctas || 0}</p>
        </div>
        <div className="bg-red-50 p-4 rounded-lg">
          <h3 className="text-sm font-medium text-red-600 mb-1">Conflicts</h3>
          <p className="text-2xl font-bold text-red-900">{analytics?.conflicts_found || conflicts?.length || 0}</p>
        </div>
        <div className="bg-purple-50 p-4 rounded-lg">
          <h3 className="text-sm font-medium text-purple-600 mb-1">High Score CTAs</h3>
          <p className="text-2xl font-bold text-purple-900">{analytics?.high_score_ctas || 0}</p>
        </div>
      </div>

      {/* Goal Summary */}
      {competing_prompts.goal_summary && (
        <div className="bg-gray-50 p-6 rounded-lg mb-8">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Goal Analysis</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center">
              <p className="text-2xl font-bold text-blue-600">{competing_prompts.goal_summary.primary_found}</p>
              <p className="text-sm text-gray-600">Primary</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-green-600">{competing_prompts.goal_summary.supporting_found}</p>
              <p className="text-sm text-gray-600">Supporting</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-red-600">{competing_prompts.goal_summary.off_goal_found}</p>
              <p className="text-sm text-gray-600">Off-Goal</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-gray-600">{competing_prompts.goal_summary.neutral_found}</p>
              <p className="text-sm text-gray-600">Neutral</p>
            </div>
          </div>
        </div>
      )}

      {/* CTAs Found */}
      <div className="mb-8">
        <h3 className="text-xl font-semibold text-gray-900 mb-4">CTAs Found</h3>
        <div className="space-y-3">
          {ctas.slice(0, 10).map((cta, index) => (
            <div key={index} className="border border-gray-200 rounded-lg p-4">
              <div className="flex items-center justify-between mb-2">
                <span className="font-medium text-gray-900">"{cta.extracted_text}"</span>
                <div className="flex gap-2">
                  <span className={`px-2 py-1 rounded text-xs font-medium ${getGoalRoleColor(cta.goal_role)}`}>
                    {cta.goal_role}
                  </span>
                  <span className="px-2 py-1 rounded text-xs font-medium bg-gray-100 text-gray-800">
                    {cta.element_type}
                  </span>
                  <span className="px-2 py-1 rounded text-xs font-medium bg-blue-100 text-blue-800">
                    Score: {cta.score}
                  </span>
                </div>
              </div>
              {cta.confidence_estimate && (
                <p className="text-sm text-gray-600">
                  Confidence: {(cta.confidence_estimate * 100).toFixed(1)}% | 
                  Area: {cta.area_percentage?.toFixed(1)}%
                </p>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Competing Prompts - MAIN OUTPUT */}
      {conflicts.length > 0 && (
        <div className="mb-12 bg-white border border-gray-200 rounded-xl p-8 shadow-sm">
          <div className="text-center mb-8">
            <h2 className="text-3xl font-bold text-gray-900 mb-2">Competing Prompts Analysis</h2>
            <p className="text-lg text-gray-600 mb-4">
              {conflicts.length} competing prompt{conflicts.length > 1 ? 's' : ''} detected that may impact conversions
            </p>
            <div className="inline-flex items-center gap-2 bg-blue-50 border border-blue-200 px-4 py-2 rounded-full">
              <span className="text-blue-700 font-semibold">Total Conflicts:</span>
              <span className="text-2xl font-bold text-blue-900">{conflicts.length}</span>
            </div>
          </div>
          
          <div className="space-y-6">
            {conflicts.map((conflict, index) => (
              <div key={index} className="bg-gray-50 border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow duration-300">
                {/* Conflict Header */}
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <span className={`px-3 py-1 rounded-full text-sm font-bold ${getPriorityColor(conflict.priority)}`}>
                      {conflict.priority} PRIORITY
                    </span>
                    <span className="text-sm font-medium text-gray-600 bg-white px-2 py-1 rounded border border-gray-200">
                      {conflict.element_type}
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-medium text-gray-700">Severity:</span>
                    <div className="flex items-center gap-1">
                      {[...Array(10)].map((_, i) => (
                        <div
                          key={i}
                          className={`w-2 h-2 rounded-full ${
                            i < conflict.severity_score ? 'bg-blue-500' : 'bg-gray-300'
                          }`}
                        />
                      ))}
                    </div>
                    <span className="text-sm font-bold text-blue-600">{conflict.severity_score}/10</span>
                  </div>
                </div>
                
                {/* Conflict Title */}
                <h3 className="text-xl font-bold text-gray-900 mb-3 border-b border-gray-200 pb-2">
                  {conflict.element_text}
                </h3>
                
                {/* Conflict Details */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="bg-white border border-gray-200 p-4 rounded-lg">
                    <h4 className="font-semibold text-gray-900 mb-2 flex items-center gap-2">
                      <span className="text-blue-600">🔍</span>
                      Why It Competes
                    </h4>
                    <p className="text-gray-700 leading-relaxed mb-3">{conflict.why_competes}</p>
                    
                    {/* Competing CTAs List */}
                    {conflict.competing_ctas && conflict.competing_ctas.length > 0 && (
                      <div className="mt-4">
                        <h5 className="font-medium text-gray-800 mb-2">Conflicting CTAs:</h5>
                        <div className="space-y-2">
                          {conflict.competing_ctas.map((cta, ctaIndex) => (
                            <div key={ctaIndex} className="flex items-center gap-2 bg-red-50 border border-red-200 rounded-md p-2">
                              <span className="text-red-600 font-medium text-sm">•</span>
                              <span className="text-red-800 font-medium">{cta}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                  
                  <div className="bg-white border border-gray-200 p-4 rounded-lg">
                    <h4 className="font-semibold text-gray-900 mb-2 flex items-center gap-2">
                      <span className="text-green-600">👤</span>
                      User Impact
                    </h4>
                    <p className="text-gray-700 leading-relaxed">{conflict.behavioral_impact}</p>
                  </div>
                </div>
                
                {/* Context Information */}
                {conflict.context && (
                  <div className="mt-4 bg-white border border-gray-200 p-4 rounded-lg">
                    <h4 className="font-semibold text-gray-900 mb-2 flex items-center gap-2">
                      <span className="text-gray-600">📋</span>
                      Context
                    </h4>
                    <p className="text-gray-700">{conflict.context}</p>
                  </div>
                )}
                
                {/* Action Required */}
                <div className="mt-4 bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <h4 className="font-semibold text-blue-900 mb-2 flex items-center gap-2">
                    <span className="text-blue-600">⚡</span>
                    Action Required
                  </h4>
                  <p className="text-blue-800">
                    {conflict.priority === 'HIGH' 
                      ? 'Fix this immediately to prevent conversion loss'
                      : conflict.priority === 'MEDIUM'
                      ? 'Address this soon to improve user experience'
                      : 'Consider addressing this for optimization'
                    }
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Behavioral Insights */}
      {behavioral_insights.length > 0 && (
        <div className="mb-8">
          <h3 className="text-xl font-semibold text-gray-900 mb-4">Behavioral Insights</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {behavioral_insights.map((insight, index) => (
              <div key={index} className="bg-blue-50 p-4 rounded-lg">
                <h4 className="font-medium text-blue-900 mb-2">{insight.insight}</h4>
                <p className="text-sm text-blue-800 mb-2">{insight.description}</p>
                <p className="text-sm text-blue-700"><strong>Recommendation:</strong> {insight.recommendation}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Recommendations */}
      {recommendations.length > 0 && (
        <div className="mb-8">
          <h3 className="text-xl font-semibold text-gray-900 mb-4">Recommendations</h3>
          <div className="space-y-4">
            {recommendations.map((rec, index) => (
              <div key={index} className="border border-gray-200 rounded-lg p-4">
                <div className="flex items-center gap-2 mb-2">
                  <span className={`px-2 py-1 rounded text-xs font-medium ${getPriorityColor(rec.priority)}`}>
                    {rec.priority} PRIORITY
                  </span>
                </div>
                <h4 className="font-medium text-gray-900 mb-1">{rec.action}</h4>
                <p className="text-sm text-gray-700 mb-2">{rec.rationale}</p>
                <p className="text-sm text-green-600 font-medium">Expected Impact: {rec.expected_impact}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Metadata */}
      <div className="bg-gray-50 p-4 rounded-lg text-sm text-gray-600">
        <p><strong>Analysis Version:</strong> {meta.analysis_version}</p>
        <p><strong>Capture Method:</strong> {meta.capture_method}</p>
        {meta.source_url && <p><strong>Source URL:</strong> {meta.source_url}</p>}
        {meta.desired_behavior && <p><strong>Goal:</strong> {meta.desired_behavior}</p>}
      </div>
    </div>
  );
};
