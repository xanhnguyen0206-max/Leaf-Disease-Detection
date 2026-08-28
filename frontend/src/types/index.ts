export interface BoundingBox {
  x1: number;
  y1: number;
  x2: number;
  y2: number;
}

export interface DetectionItem {
  class_id: number;
  disease: string;
  confidence: number;
  bbox: BoundingBox;
}

export interface RecommendationItem {
  title: string;
  description: string;
}

export interface DetectedDiseaseGroup {
  disease: string;
  disease_name: string;
  plant: string;
  disease_id?: string;
  max_confidence: number;
  detection_count: number;
  severity: string;
  confidence_level: string; // 'Độ tin cậy cao' | 'Độ tin cậy trung bình' | 'Dấu hiệu cần kiểm tra thêm'
  description?: string;
  symptoms?: string[];
  recommendations?: RecommendationItem[];
  detections: DetectionItem[];
}

export interface DiagnosisResult {
  id: string;
  plant: string;
  disease: string;
  primary_disease?: string;
  confidence: number;
  severity: string;
  status?: string; // 'detected' | 'no_detection'
  recommendations: RecommendationItem[];
  image_url?: string;
  heatmap_url?: string;
  created_at: string;
  detections?: DetectionItem[];
  detected_diseases?: DetectedDiseaseGroup[];
  is_multi_disease?: boolean;
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
  scientific_name?: string;
  english_name?: string;
  severity: string;
  description: string;
  overview?: string;
  pathogen?: string;
  favorable_conditions?: string;
  transmission?: string[];
  risk_level_explanation?: string;
  
  symptoms: string[];
  early_symptoms?: string[];
  mid_symptoms?: string[];
  severe_symptoms?: string[];
  similar_diseases_diff?: string[];

  prevention_before_planting?: string[];
  prevention_during_growth?: string[];
  water_management?: string;
  nutrition_management?: string;
  density_management?: string;
  field_sanitation?: string;
  pruning_guide?: string;
  crop_rotation_guide?: string;
  biological_control?: string[];
  chemical_control_principles?: string[];
  aftercare_monitoring?: string[];
  common_mistakes?: string[];
  when_to_seek_help?: string;
  safety_notes?: string;
  sources?: string[];
  image_url?: string;
  recommendations?: CareRecommendation[];
}

