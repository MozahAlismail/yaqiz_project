/**
 * Feedback API service
 * Maps to FastAPI endpoints in api/feedback_router.py
 */

import { get, post, put, del } from './api';

export interface FeedbackRequest {
  case_id: string;
  corrected_incident?: string;
  corrected_severity?: string;
  corrected_unit?: string;
  operator_id?: string;
}

export interface Feedback {
  feedback_id: string;
  case_id: string;
  corrected_incident?: string;
  corrected_severity?: string;
  corrected_unit?: string;
  operator_id: string;
  timestamp: string;
  // Associated case data (when fetched with feedbacks)
  case_transcript?: string;
  ai_incident?: string;
  ai_severity?: string;
  ai_unit?: string;
}

export interface FeedbacksResponse {
  total: number;
  limit: number;
  offset: number;
  count: number;
  feedbacks: Feedback[];
}

export interface FeedbackUpdateData {
  corrected_incident?: string;
  corrected_severity?: string;
  corrected_unit?: string;
  operator_id?: string;
}

/**
 * Submit operator feedback for a case
 * @param data Feedback data with corrections
 */
export async function submitFeedback(
  data: FeedbackRequest
): Promise<{ success: boolean; feedback_id: string }> {
  return post('/api/operator-feedback', data);
}

/**
 * Get a specific feedback by ID
 * @param feedbackId UUID of the feedback to retrieve
 */
export async function getFeedback(feedbackId: string): Promise<Feedback> {
  return get<Feedback>(`/api/feedback/${feedbackId}`);
}

/**
 * Get all feedbacks with pagination
 * @param limit Maximum number of feedbacks to return (1-1000, default: 100)
 * @param offset Number of feedbacks to skip for pagination (default: 0)
 */
export async function getAllFeedbacks(
  limit: number = 100,
  offset: number = 0
): Promise<FeedbacksResponse> {
  return get<FeedbacksResponse>('/api/feedbacks', { limit, offset });
}

/**
 * Update a feedback's information
 * @param feedbackId UUID of the feedback to update
 * @param data Fields to update
 */
export async function updateFeedback(
  feedbackId: string,
  data: FeedbackUpdateData
): Promise<{ success: boolean; updated_fields: string[] }> {
  return put(`/api/feedback/${feedbackId}`, data);
}

/**
 * Delete a feedback
 * @param feedbackId UUID of the feedback to delete
 */
export async function deleteFeedback(
  feedbackId: string
): Promise<{ success: boolean; message: string }> {
  return del(`/api/feedback/${feedbackId}`);
}

export const feedbackService = {
  submitFeedback,
  getFeedback,
  getAllFeedbacks,
  updateFeedback,
  deleteFeedback,
};

export default feedbackService;
