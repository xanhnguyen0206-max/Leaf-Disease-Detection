export interface RecommendationItem {
  title: str;
  description: str;
}

export interface DiagnosisResult {
  id: string;
  plant: string;
  disease: string;
  confidence: number;
  severity: string;
  recommendations: RecommendationItem[];
  image_url?: string;
  heatmap_url?: string;
  created_at: string;
}

export interface CareRecommendation {
  id: string;
  disease_id: string;
  category: string;
  title: string;
  description: string;
  priority: string;
}

export interface Disease {
  id: string;
  name: string;
  plant: string;
  description: string;
  symptoms: string[];
  severity: string;
  image_url?: string;
  recommendations?: CareRecommendation[];
}
