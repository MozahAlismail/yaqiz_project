/**
 * Incidents/Cases API service
 * Maps to FastAPI endpoints in api/case_router.py
 */

import { get, put, post, del } from './api';

export interface Case {
  case_id: string;
  transcript: string;
  detected_language?: string;
  language_confidence?: number;
  ai_incident?: string;
  ai_severity?: string;
  ai_unit?: string;
  incident_confidence?: number;
  severity_confidence?: number;
  dispatch_confidence?: number;
  requires_review?: boolean;
  created_at: string;
  updated_at?: string;
}

export interface CasesResponse {
  total: number;
  limit: number;
  offset: number;
  count: number;
  cases: Case[];
}

export interface CaseUpdateData {
  transcript?: string;
  detected_language?: string;
  language_confidence?: number;
  ai_incident?: string;
  ai_severity?: string;
  ai_unit?: string;
  incident_confidence?: number;
  severity_confidence?: number;
  dispatch_confidence?: number;
  requires_review?: boolean;
}

/**
 * Get all cases with pagination
 * @param limit Maximum number of cases to return (1-1000, default: 100)
 * @param offset Number of cases to skip for pagination (default: 0)
 */
export async function getIncidents(
  limit: number = 100,
  offset: number = 0
): Promise<CasesResponse> {
  return get<CasesResponse>('/api/cases', { limit, offset });
}

/**
 * Get a specific case by ID
 * @param id UUID of the case to retrieve
 */
export async function getIncidentById(id: string): Promise<Case> {
  return get<Case>(`/api/case/${id}`);
}

/**
 * Update a case's information
 * @param id UUID of the case to update
 * @param data Fields to update
 */
export async function updateIncident(
  id: string,
  data: CaseUpdateData
): Promise<{ success: boolean; updated_fields: string[] }> {
  return put(`/api/case/${id}`, data);
}

/**
 * Create a new case
 * @param data Case data
 */
export async function createIncident(
  data: Partial<Case>
): Promise<Case> {
  return post('/api/case', data);
}

/**
 * Delete a case
 * @param id UUID of the case to delete
 */
export async function deleteIncident(
  id: string
): Promise<{ success: boolean; message: string }> {
  return del(`/api/case/${id}`);
}

export const incidentsService = {
  getIncidents,
  getIncidentById,
  updateIncident,
  createIncident,
  deleteIncident,
};

export default incidentsService;
