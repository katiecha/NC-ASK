/**
 * API service for communicating with NC-ASK backend
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export interface QueryRequest {
  query: string;
  session_id?: string;
}

export interface Citation {
  title: string;
  url: string | null;
  relevance_score: number;
}

export interface CrisisResource {
  name: string;
  phone: string;
  description: string;
  url: string | null;
  priority: number;
}

export interface QueryResponse {
  response: string;
  citations: Citation[];
  crisis_detected: boolean;
  crisis_severity: string | null;
  crisis_resources: CrisisResource[];
  disclaimers?: string[];
}

export interface HealthResponse {
  status: string;
  service: string;
}

/**
 * Generate or retrieve session ID from sessionStorage
 */
function getSessionId(): string {
  let sessionId = sessionStorage.getItem('nc-ask-session-id');

  if (!sessionId) {
    // Generate simple session ID
    sessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    sessionStorage.setItem('nc-ask-session-id', sessionId);
  }

  return sessionId;
}

/**
 * Query the NC-ASK knowledge base
 */
export async function queryKnowledgeBase(query: string): Promise<QueryResponse> {
  const sessionId = getSessionId();

  const response = await fetch(`${API_BASE_URL}/api/query`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      query,
      session_id: sessionId,
    } as QueryRequest),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || 'Failed to process query');
  }

  return response.json();
}

/**
 * Get crisis resources
 */
export async function getCrisisResources(): Promise<CrisisResource[]> {
  const response = await fetch(`${API_BASE_URL}/api/crisis-resources`);

  if (!response.ok) {
    throw new Error('Failed to fetch crisis resources');
  }

  const data = await response.json();
  return data.resources;
}

/**
 * Check API health
 */
export async function checkHealth(): Promise<HealthResponse> {
  const response = await fetch(`${API_BASE_URL}/api/health`);

  if (!response.ok) {
    throw new Error('Health check failed');
  }

  return response.json();
}
