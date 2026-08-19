export type RiskLevel = "Low Risk" | "Medium Risk" | "High Risk";

export interface FeatureContribution {
  feature: string;
  label: string;
  value: string;
  impact: number;
  direction: "toward_attrition" | "toward_retention";
}

export interface RecommendationItem {
  category: "compensation" | "growth" | "wellbeing" | "engagement" | "environment";
  message: string;
  urgency: number;
}

export interface PredictionResponse {
  employee_id: string;
  risk_level: RiskLevel;
  probability: number;
  confidence: number;
  binary_prediction: number;
  top_features: FeatureContribution[];
  recommendations: RecommendationItem[];
  profile_url: string;
}

export interface BatchPredictionRecord {
  employee_id: string;
  department: string;
  job_role: string;
  risk_level: string;
  probability: number;
  confidence: number;
  key_risk_factors: string[];
  profile_url: string;
}

export interface BatchPredictionResponse {
  batch_id: string;
  total_processed: number;
  high_risk_count: number;
  medium_risk_count: number;
  low_risk_count: number;
  average_attrition_probability: number;
  records: BatchPredictionRecord[];
  download_url: string;
}

export interface EmployeeNote {
  timestamp: string;
  author: string;
  note: string;
}

export interface EmployeeProfileData {
  employee: Record<string, any>; // Raw feature dict
  prediction: PredictionResponse;
  contributions: FeatureContribution[];
  notes: EmployeeNote[];
}

export interface AnalyticsSummary {
  total_predictions: number;
  high_risk_count: number;
  avg_probability: number;
  recent_predictions: PredictionResponse[];
}

// For frontend form input
export interface EmployeePredictionInput {
  EmployeeNumber?: number;
  Age: number;
  BusinessTravel: string;
  DailyRate?: number;
  Department: string;
  DistanceFromHome: number;
  Education: number;
  EducationField: string;
  EmployeeCount?: number;
  EnvironmentSatisfaction: number;
  Gender: string;
  HourlyRate?: number;
  JobInvolvement: number;
  JobLevel: number;
  JobRole: string;
  JobSatisfaction: number;
  MaritalStatus: string;
  MonthlyIncome: number;
  MonthlyRate?: number;
  NumCompaniesWorked: number;
  Over18?: string;
  OverTime: string;
  PercentSalaryHike: number;
  PerformanceRating: number;
  RelationshipSatisfaction: number;
  StandardHours?: number;
  StockOptionLevel: number;
  TotalWorkingYears: number;
  TrainingTimesLastYear: number;
  WorkLifeBalance: number;
  YearsAtCompany: number;
  YearsInCurrentRole: number;
  YearsSinceLastPromotion: number;
  YearsWithCurrManager: number;
}
