import React, { useState } from 'react';

const ConflictVisualizer = ({ conflicts, ctas }) => {
  const [selectedConflict, setSelectedConflict] = useState(null);

  if (!conflicts || conflicts.length === 0) {
    return (
      <div className="bg-white rounded-xl shadow-lg p-8 text-center">
        <div className="text-6xl mb-4">🎉</div>
        <h3 className="text-2xl font-semibold text-gray-900 mb-2">No Conflicts Found!</h3>
        <p className="text-gray-600">Your CTAs are well-optimized and working together harmoniously.</p>
      </div>
    );
  }

  const getConflictColor = (severity) => {
    switch (severity) {
      case 'critical': return 'from-red-500 to-red-700';
      case 'high': return 'from-orange-500 to-orange-700';
      case 'medium': return 'from-yellow-500 to-yellow-700';
      case 'low': return 'from-green-500 to-green-700';
      default: return 'from-gray-500 to-gray-700';
    }
  };

  const getConflictIcon = (severity) => {
    switch (severity) {
      case 'critical': return '🚨';
      case 'high': return '⚠️';
      case 'medium': return '⚡';
      case 'low': return '✅';
      default: return 'ℹ️';
    }
  };

  return (
    <div className="space-y-6">
      <div className="text-center mb-8">
        <h2 className="text-3xl font-bold text-gray-900 mb-2">Conflict Analysis</h2>
        <p className="text-gray-600">Visual breakdown of competing CTAs and their impact</p>
      </div>

      {/* Conflict Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        <div className="bg-white rounded-lg shadow p-4 text-center">
          <div className="text-2xl font-bold text-red-600">{conflicts.length}</div>
          <div className="text-sm text-gray-600">Total Conflicts</div>
        </div>
        <div className="bg-white rounded-lg shadow p-4 text-center">
          <div className="text-2xl font-bold text-orange-600">
            {conflicts.filter(c => c.severity === 'high' || c.severity === 'critical').length}
          </div>
          <div className="text-sm text-gray-600">High Priority</div>
        </div>
        <div className="bg-white rounded-lg shadow p-4 text-center">
          <div className="text-2xl font-bold text-blue-600">
            {conflicts.reduce((sum, c) => sum + (c.cta_indices?.length || 0), 0)}
          </div>
          <div className="text-sm text-gray-600">CTAs Affected</div>
        </div>
      </div>

      {/* Individual Conflicts */}
      <div className="space-y-4">
        {conflicts.map((conflict, idx) => (
          <div
            key={idx}
            className={`bg-white rounded-xl shadow-lg overflow-hidden cursor-pointer transition-all duration-200 hover:shadow-xl ${
              selectedConflict === idx ? 'ring-2 ring-blue-500' : ''
            }`}
            onClick={() => setSelectedConflict(selectedConflict === idx ? null : idx)}
          >
            {/* Conflict Header */}
            <div className={`bg-gradient-to-r ${getConflictColor(conflict.severity)} p-4 text-white`}>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <span className="text-2xl">{getConflictIcon(conflict.severity)}</span>
                  <div>
                    <h3 className="text-lg font-semibold">
                      {conflict.title || `Conflict ${idx + 1}`}
                    </h3>
                    <p className="text-sm opacity-90">
                      {conflict.reason || 'CTA Competition'} • {conflict.severity} severity
                    </p>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-3xl font-bold">
                    {Math.round((getSeverityScore(conflict.severity) + (conflict.cta_indices?.length > 1 ? 20 : 0)))}%
                  </div>
                  <div className="text-sm opacity-90">Impact Score</div>
                </div>
              </div>
            </div>

            {/* Conflict Details */}
            {selectedConflict === idx && (
              <div className="p-6 border-t border-gray-100">
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  {/* Conflict Analysis */}
                  <div>
                    <h4 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                      🔍 Conflict Analysis
                    </h4>
                    <div className="space-y-3">
                      <div className="flex justify-between items-center p-2 bg-gray-50 rounded">
                        <span className="text-gray-600">Type:</span>
                        <span className="font-medium capitalize">{conflict.reason || 'unknown'}</span>
                      </div>
                      <div className="flex justify-between items-center p-2 bg-gray-50 rounded">
                        <span className="text-gray-600">Severity:</span>
                        <span className={`px-3 py-1 rounded-full text-sm font-medium ${getConflictColor(conflict.severity)}`}>
                          {conflict.severity}
                        </span>
                      </div>
                      <div className="flex justify-between items-center p-2 bg-gray-50 rounded">
                        <span className="text-gray-600">CTAs Affected:</span>
                        <span className="font-medium">{conflict.cta_indices?.length || 0}</span>
                      </div>
                    </div>
                    
                    <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                      <p className="text-sm text-blue-800">
                        <strong>Why it's conflicting:</strong> {conflict.explanation || 'Multiple CTAs are competing for user attention'}
                      </p>
                    </div>
                  </div>

                  {/* Affected CTAs */}
                  <div>
                    <h4 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                      🎯 Affected CTAs
                    </h4>
                    <div className="space-y-2">
                      {conflict.cta_indices?.map((ctaIdx, ctaIdx2) => {
                        const cta = ctas[ctaIdx];
                        if (!cta) return null;
                        
                        return (
                          <div key={ctaIdx2} className="p-3 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg border border-blue-200">
                            <div className="flex items-center justify-between mb-2">
                              <span className="font-medium text-blue-900 truncate">{cta.extracted_text}</span>
                              <span className="text-sm text-blue-600 bg-blue-100 px-2 py-1 rounded">
                                Score: {cta.score}
                              </span>
                            </div>
                            <div className="flex items-center justify-between text-xs text-blue-700">
                              <span>Role: {cta.goal_role}</span>
                              <span>Area: {cta.area_percentage}%</span>
                            </div>
                            <div className="mt-2 w-full bg-blue-200 rounded-full h-2">
                              <div 
                                className="bg-blue-600 h-2 rounded-full transition-all duration-500"
                                style={{ width: `${cta.score}%` }}
                              ></div>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                </div>

                {/* Action Recommendations */}
                <div className="mt-6 p-4 bg-gradient-to-r from-yellow-50 to-orange-50 border border-yellow-200 rounded-lg">
                  <h5 className="font-semibold text-yellow-800 mb-3 flex items-center gap-2">
                    🚨 Recommended Actions
                  </h5>
                  <div className="text-sm text-yellow-800 space-y-2">
                    {conflict.severity === 'critical' && (
                      <p>🚨 <strong>Immediate Action Required:</strong> This conflict will significantly hurt your conversion rates. Consider removing or completely redesigning one of the competing CTAs.</p>
                    )}
                    {conflict.severity === 'high' && (
                      <p>⚠️ <strong>High Priority:</strong> This conflict should be addressed within the week. Consider repositioning or redesigning CTAs to reduce competition.</p>
                    )}
                    {conflict.severity === 'medium' && (
                      <p>⚡ <strong>Medium Priority:</strong> This conflict may impact conversion. Consider minor adjustments to CTA positioning or styling.</p>
                    )}
                    {conflict.severity === 'low' && (
                      <p>✅ <strong>Low Priority:</strong> This conflict is minor and may not significantly impact performance, but monitoring is recommended.</p>
                    )}
                  </div>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

// Helper function to get severity score
const getSeverityScore = (severity) => {
  switch (severity) {
    case 'critical': return 100;
    case 'high': return 75;
    case 'medium': return 50;
    case 'low': return 25;
    default: return 0;
  }
};

export default ConflictVisualizer;
