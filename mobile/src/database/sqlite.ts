/**
 * AgriVision AI 2.0 - Offline SQLite Storage & Sync Queue
 * Implements local-first data caching and offline inspection persistence.
 */

import * as SQLite from 'expo-sqlite';
import { InspectionRecord } from '../types';

let db: SQLite.SQLiteDatabase | null = null;

export const initOfflineDatabase = async () => {
  try {
    db = await SQLite.openDatabaseAsync('agrivision_offline.db');
    
    // Create inspections table
    await db.execAsync(`
      CREATE TABLE IF NOT EXISTS local_inspections (
        id TEXT PRIMARY KEY,
        crop_name TEXT NOT NULL,
        disease_predicted TEXT NOT NULL,
        disease_predicted_ta TEXT,
        confidence REAL NOT NULL,
        severity_pct REAL DEFAULT 0.0,
        image_uri TEXT NOT NULL,
        heatmap_uri TEXT,
        management_guidance TEXT,
        management_guidance_ta TEXT,
        created_at TEXT NOT NULL,
        is_synced INTEGER DEFAULT 0,
        sync_attempts INTEGER DEFAULT 0
      );
      
      CREATE TABLE IF NOT EXISTS sync_queue (
        id TEXT PRIMARY KEY,
        action TEXT NOT NULL,
        payload TEXT NOT NULL,
        created_at TEXT NOT NULL
      );
    `);
    
    console.log('[SQLite] Local database initialized successfully.');
  } catch (error) {
    console.warn('[SQLite] SQLite not available in current environment (e.g. web fallback):', error);
  }
};

export const saveLocalInspection = async (inspection: InspectionRecord, isSynced: boolean = false) => {
  if (!db) return;
  try {
    await db.runAsync(
      `INSERT OR REPLACE INTO local_inspections 
      (id, crop_name, disease_predicted, disease_predicted_ta, confidence, severity_pct, image_uri, heatmap_uri, management_guidance, management_guidance_ta, created_at, is_synced)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
      [
        inspection.id,
        inspection.crop_name,
        inspection.disease_predicted,
        inspection.disease_predicted_ta || '',
        inspection.confidence,
        inspection.severity_pct || 0.0,
        inspection.image_url,
        inspection.heatmap_url || '',
        inspection.management_guidance || '',
        inspection.management_guidance_ta || '',
        inspection.created_at,
        isSynced ? 1 : 0
      ]
    );
  } catch (err) {
    console.error('[SQLite] Failed to save local inspection:', err);
  }
};

export const getLocalInspections = async (): Promise<InspectionRecord[]> => {
  if (!db) return [];
  try {
    const rows = await db.getAllAsync<any>(
      `SELECT * FROM local_inspections ORDER BY created_at DESC LIMIT 50`
    );
    return rows.map((r: any) => ({
      id: r.id,
      crop_name: r.crop_name,
      disease_predicted: r.disease_predicted,
      disease_predicted_ta: r.disease_predicted_ta,
      confidence: r.confidence,
      severity_pct: r.severity_pct,
      image_url: r.image_uri,
      heatmap_url: r.heatmap_uri,
      management_guidance: r.management_guidance,
      management_guidance_ta: r.management_guidance_ta,
      created_at: r.created_at,
      status: 'saved',
      is_synced: r.is_synced === 1
    }));
  } catch (err) {
    console.error('[SQLite] Error reading local inspections:', err);
    return [];
  }
};

export const getUnsyncedCount = async (): Promise<number> => {
  if (!db) return 0;
  try {
    const result = await db.getFirstAsync<{ count: number }>(
      `SELECT COUNT(*) as count FROM local_inspections WHERE is_synced = 0`
    );
    return result?.count || 0;
  } catch {
    return 0;
  }
};
