/**
 * AgriVision AI 2.0 - Core TypeScript Definitions
 */

export type SupportedCrop = 
  | 'Tomato'
  | 'Potato'
  | 'Rice'
  | 'Cotton'
  | 'Maize'
  | 'Pepper'
  | 'Apple';

export interface BoundingBox {
  id: string;
  box: [number, number, number, number]; // [ymin, xmin, ymax, xmax] normalized (0-1)
  label: string;
  confidence: number;
  color?: string;
}

export interface DiseasePrediction {
  disease_class: string;
  crop: string;
  display_name: string;
  display_name_ta: string;
  confidence: number;
  pathogen: string;
  description: string;
  management: string;
  management_ta: string;
  is_healthy: boolean;
  status: 'confirmed' | 'suspected' | 'uncertain';
  severity_pct?: number;
}

export interface LiveFrameResult {
  has_leaf: boolean;
  leaf_confidence: number;
  crop_identified: string;
  crop_confidence: number;
  disease_name: string;
  disease_name_ta: string;
  confidence: number;
  is_healthy: boolean;
  severity_estimate: string;
  severity_pct: number;
  boxes: BoundingBox[];
  suggested_action: string;
  suggested_action_ta: string;
  canopy_detected: boolean;
  fps: number;
}

export interface InspectionRecord {
  id: string;
  crop_name: string;
  farm_id?: string;
  field_id?: string;
  image_url: string;
  heatmap_url?: string;
  disease_predicted: string;
  disease_predicted_ta: string;
  confidence: number;
  severity_pct: number;
  status: string;
  notes?: string;
  latitude?: number;
  longitude?: number;
  created_at: string;
  management_guidance?: string;
  management_guidance_ta?: string;
  is_synced?: boolean;
}

export interface WeatherCondition {
  temperature_c: number;
  relative_humidity_pct: number;
  precipitation_mm: number;
  wind_speed_kmh: number;
  leaf_wetness_hours: number;
  solar_radiation_mj: number;
  disease_risk_index: number;
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  pathogen_alerts: Array<{
    disease: string;
    pathogen: string;
    risk_level: string;
    favorable_factors: string[];
  }>;
}

export interface FiveDayForecastDay {
  date: string;
  day_name: string;
  temp_min: number;
  temp_max: number;
  humidity_pct: number;
  rain_probability_pct: number;
  overall_risk: 'LOW' | 'MEDIUM' | 'HIGH';
  alert_summary: string;
}

export interface Farm {
  id: string;
  name: string;
  location_name: string;
  total_acres: number;
  crop_types: string[];
  latitude: number;
  longitude: number;
  fields_count: number;
  active_inspections_count: number;
}

export interface Field {
  id: string;
  farm_id: string;
  name: string;
  crop_name: string;
  planting_date: string;
  growth_stage: string;
  acres: number;
  health_status: 'Good' | 'Moderate' | 'Alert';
}

export interface AssistantMessage {
  id: string;
  sender: 'user' | 'assistant';
  text: string;
  audio_url?: string;
  language: 'en' | 'ta';
  timestamp: string;
  suggestions?: string[];
}
