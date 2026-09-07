export type UserRole = 'student' | 'admin';

export interface User {
  id: number;
  email: string;
  full_name: string;
  role: UserRole;
  department_id?: number | null;
  department_code?: string | null;
  department_name?: string | null;
  is_active?: boolean;
}

export interface Department {
  id: number;
  code: string;
  name: string;
  description?: string;
  contact_email?: string;
  is_active: boolean;
}

export interface TopPrediction {
  category: string;
  probability: number;
}

export interface ModelPrediction {
  predicted_category: string;
  confidence_score: number;
  is_fallback: boolean;
  raw_predicted_category?: string;
  raw_confidence?: number;
  top_predictions: TopPrediction[];
  inference_time_ms?: number;
}

export interface GrievanceHistory {
  id: number;
  previous_status?: string | null;
  new_status: string;
  remarks?: string | null;
  changed_by_name?: string;
  created_at: string;
}

export interface Grievance {
  id: number;
  ticket_number: string;
  title: string;
  description: string;
  category: string;
  department_id: number;
  department_code?: string;
  department_name?: string;
  priority: 'High' | 'Medium' | 'Low' | string;
  priority_reason?: string;
  status: 'Submitted' | 'Assigned' | 'In Progress' | 'Resolved' | 'Closed' | string;
  is_low_confidence: boolean;
  resolution_remarks?: string | null;
  student_id: number;
  student_name?: string;
  student_email?: string;
  created_at: string;
  updated_at: string;
  prediction?: ModelPrediction;
  history?: GrievanceHistory[];
}

export interface AnalyticsData {
  total_grievances: number;
  status_distribution: Record<string, number>;
  category_distribution: Record<string, number>;
  department_distribution: Record<string, number>;
  priority_distribution: Record<string, number>;
  low_confidence_count: number;
  resolved_count: number;
  avg_resolution_hours?: number | null;
}

export interface ModelPerformanceData {
  training_timestamp: string;
  total_samples: number;
  train_samples: number;
  test_samples: number;
  vocabulary_size: number;
  categories: string[];
  model_architecture: string;
  default_confidence_threshold: number;
  selected_model: string;
  comparison_benchmarks: Record<string, {
    accuracy: number;
    macro_precision: number;
    macro_recall: number;
    macro_f1: number;
    weighted_f1: number;
  }>;
  evaluation_metrics: {
    accuracy: number;
    macro_precision: number;
    macro_recall: number;
    macro_f1: number;
    weighted_f1: number;
  };
  per_class_metrics: Record<string, {
    precision: number;
    recall: number;
    "f1-score": number;
    support: number;
  }>;
  confusion_matrix: {
    matrix: number[][];
    labels: string[];
  };
}

export interface GeneralizationTestResult {
  predicted_category: string;
  confidence: number;
  is_low_confidence: boolean;
  suggested_department: string;
  suggested_priority: string;
  priority_reason: string;
  top_predictions: TopPrediction[];
  raw_predicted_category: string;
  raw_confidence: number;
  cleaned_text: string;
}
