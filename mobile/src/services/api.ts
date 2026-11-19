/**
 * AgriVision AI 2.0 - Central API Service Client
 */

import { API_BASE_URL } from '../constants/config';
import { 
  LiveFrameResult, 
  InspectionRecord, 
  WeatherCondition, 
  FiveDayForecastDay, 
  Farm, 
  AssistantMessage,
  SupportedCrop
} from '../types';

let authToken: string | null = null;

export const setAuthToken = (token: string | null) => {
  authToken = token;
};

const getHeaders = (isFormData: boolean = false) => {
  const headers: Record<string, string> = {};
  if (!isFormData) {
    headers['Content-Type'] = 'application/json';
  }
  if (authToken) {
    headers['Authorization'] = `Bearer ${authToken}`;
  }
  return headers;
};

export const api = {
  // 1. Health & Meta
  async checkHealth(): Promise<{ status: string; version: string }> {
    const res = await fetch(`${API_BASE_URL}/health`);
    return res.json();
  },

  async getSupportedCrops(): Promise<SupportedCrop[]> {
    const res = await fetch(`${API_BASE_URL}/api/v1/crops/supported`);
    const data = await res.json();
    return data.crops || [];
  },

  // 2. Authentication
  async login(phoneOrEmail: string, password: string = 'farmer123') {
    const res = await fetch(`${API_BASE_URL}/api/v1/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username: phoneOrEmail, password })
    });
    const data = await res.json();
    if (data.access_token) {
      setAuthToken(data.access_token);
    }
    return data;
  },

  // 3. Real-Time Camera Live Inspection
  async inspectLiveFrame(base64Image: string, cropHint?: string): Promise<LiveFrameResult> {
    const body: Record<string, string> = { image_base64: base64Image };
    if (cropHint) {
      body.crop_hint = cropHint;
    }

    const res = await fetch(`${API_BASE_URL}/api/v1/live/inspect`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    });

    if (!res.ok) {
      throw new Error(`Live inspect failed: ${res.statusText}`);
    }
    return res.json();
  },

  // 4. Full Inspection Creation (multipart file upload)
  async createInspection(formData: FormData): Promise<InspectionRecord> {
    const res = await fetch(`${API_BASE_URL}/api/v1/inspections/`, {
      method: 'POST',
      headers: getHeaders(true),
      body: formData
    });

    if (!res.ok) {
      throw new Error(`Inspection creation failed: ${res.statusText}`);
    }
    return res.json();
  },

  // 5. Get Inspection by ID
  async getInspection(id: string): Promise<InspectionRecord> {
    const res = await fetch(`${API_BASE_URL}/api/v1/inspections/${id}`, {
      headers: getHeaders()
    });
    return res.json();
  },

  // 6. List Recent Inspections
  async listInspections(limit: number = 20): Promise<InspectionRecord[]> {
    const res = await fetch(`${API_BASE_URL}/api/v1/inspections/?limit=${limit}`, {
      headers: getHeaders()
    });
    const data = await res.json();
    return data.inspections || [];
  },

  // 7. Weather & Disease Risk Forecasting
  async getWeatherRisk(lat: number = 11.0168, lon: number = 76.9558, crop?: string): Promise<{
    current: WeatherCondition;
    forecast: FiveDayForecastDay[];
  }> {
    const url = `${API_BASE_URL}/api/v1/weather/risk?lat=${lat}&lon=${lon}${crop ? `&crop=${crop}` : ''}`;
    const res = await fetch(url, { headers: getHeaders() });
    return res.json();
  },

  // 8. Bilingual AI Farming Assistant (Chat & Voice)
  async askAssistant(message: string, language: 'en' | 'ta' = 'en', crop?: string): Promise<{
    reply: string;
    language: string;
    audio_url?: string;
    disease_detected?: string;
    suggested_actions?: string[];
  }> {
    const res = await fetch(`${API_BASE_URL}/api/v1/assistant/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message, language, crop })
    });
    return res.json();
  },

  // 9. Farms & Fields
  async listFarms(): Promise<Farm[]> {
    const res = await fetch(`${API_BASE_URL}/api/v1/farms/`, { headers: getHeaders() });
    const data = await res.json();
    return data.farms || [];
  },

  async createFarm(farm: { name: string; location_name: string; total_acres: number; latitude: number; longitude: number }): Promise<Farm> {
    const res = await fetch(`${API_BASE_URL}/api/v1/farms/`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify(farm)
    });
    return res.json();
  },

  // 10. Expert Feedback
  async submitFeedback(inspectionId: string, isCorrect: boolean, correctedDisease?: string, notes?: string) {
    const res = await fetch(`${API_BASE_URL}/api/v1/feedback/`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify({
        inspection_id: inspectionId,
        is_correct: isCorrect,
        corrected_disease: correctedDisease,
        notes
      })
    });
    return res.json();
  }
};
