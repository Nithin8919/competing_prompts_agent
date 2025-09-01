// API service for communicating with the CTA Analyzer backend
const API_BASE_URL = process.env.NODE_ENV === 'production' 
  ? 'https://your-backend-url.com' 
  : 'http://localhost:5001';

export interface CTAAnalysisRequest {
  design_url?: string;
  desired_behavior: string;
  image?: File;
}

export interface CTAAnalysisResponse {
  success: boolean;
  ctas: CTA[];
  competing_prompts: CompetingPrompts;
  behavioral_insights: BehavioralInsight[];
  analytics: Analytics;
  meta: Meta;
  error?: string;
}

export interface CTA {
  extracted_text: string;
  bbox: [number, number, number, number];
  score: number;
  goal_role: 'primary' | 'supporting' | 'off-goal' | 'neutral';
  element_type: 'button' | 'link' | 'banner' | 'menu' | 'form';
  confidence_estimate?: number;
  area_percentage?: number;
}

export interface CompetingPrompts {
  conflict_level: 'low' | 'medium' | 'high' | 'critical';
  total_competing: number;
  conflicts: Conflict[];
  behavioral_insights: BehavioralInsight[];
  recommendations: Recommendation[];
  goal_summary: GoalSummary;
}

export interface Conflict {
  priority: 'HIGH' | 'MEDIUM' | 'LOW';
  element_type: string;
  element_text: string;
  context: string;
  why_competes: string;
  behavioral_impact: string;
  severity_score: number;
  competing_ctas?: string[];
}

export interface BehavioralInsight {
  insight: string;
  description: string;
  applies: boolean;
  impact: 'high' | 'medium' | 'low';
  recommendation: string;
}

export interface Recommendation {
  priority: 'HIGH' | 'MEDIUM' | 'LOW';
  action: string;
  rationale: string;
  expected_impact: string;
}

export interface GoalSummary {
  goal: string;
  primary_found: number;
  supporting_found: number;
  off_goal_found: number;
  neutral_found: number;
}

export interface Analytics {
  total_ctas: number;
  high_score_ctas: number;
  primary_ctas: number;
  conflicts_found: number;
  conflict_level: string;
}

export interface Meta {
  processing_time: string;
  desired_behavior?: string;
  analysis_version: string;
  capture_method: string;
  source_url?: string;
  analyzer_type: string;
}

class APIService {
  private baseURL: string;

  constructor() {
    this.baseURL = API_BASE_URL;
  }

  async analyzeURL(design_url: string, desired_behavior: string): Promise<CTAAnalysisResponse> {
    const response = await fetch(`${this.baseURL}/api/analyze-url`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        design_url,
        desired_behavior,
      }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || 'Analysis failed');
    }

    return response.json();
  }

  async analyzeImage(image: File, desired_behavior: string): Promise<CTAAnalysisResponse> {
    const formData = new FormData();
    formData.append('image', image);
    formData.append('desired_behavior', desired_behavior);

    const response = await fetch(`${this.baseURL}/api/analyze`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || 'Analysis failed');
    }

    return response.json();
  }

  async checkHealth(): Promise<any> {
    const response = await fetch(`${this.baseURL}/api/health`);
    if (!response.ok) {
      throw new Error('Backend service unavailable');
    }
    return response.json();
  }
}

export const apiService = new APIService();
