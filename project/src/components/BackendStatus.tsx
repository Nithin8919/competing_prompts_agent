import React, { useState, useEffect } from 'react';
import { apiService } from '../services/api';

export const BackendStatus: React.FC = () => {
  const [status, setStatus] = useState<'checking' | 'connected' | 'error'>('checking');
  const [details, setDetails] = useState<any>(null);

  useEffect(() => {
    const checkBackend = async () => {
      try {
        const health = await apiService.checkHealth();
        setStatus('connected');
        setDetails(health);
      } catch (error) {
        console.error('Backend connection error:', error);
        setStatus('error');
        setDetails({ error: error instanceof Error ? error.message : 'Unknown error' });
      }
    };

    checkBackend();
  }, []);

  if (status === 'checking') {
    return (
      <div className="flex items-center gap-2 text-sm text-gray-600">
        <div className="w-3 h-3 border-2 border-gray-300 border-t-blue-600 rounded-full animate-spin"></div>
        Checking backend connection...
      </div>
    );
  }

  if (status === 'error') {
    return (
      <div className="flex items-center gap-2 text-sm text-red-600">
        <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
        </svg>
        Backend unavailable - {details?.error || 'Connection failed'}
      </div>
    );
  }

  return (
    <div className="flex items-center gap-2 text-sm text-green-600">
      <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
      </svg>
      Backend connected - {details?.version || 'v1.0.0'}
    </div>
  );
};
