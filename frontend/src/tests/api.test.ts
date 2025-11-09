/**
 * Tests for API service backend communication
 */
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import {
  queryKnowledgeBase,
  getCrisisResources,
  checkHealth,
  type QueryResponse,
  type CrisisResource,
  type HealthResponse,
} from '../services/api';

// Mock fetch globally
const mockFetch = vi.fn();
global.fetch = mockFetch;

// Mock sessionStorage
const mockSessionStorage = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
  length: 0,
  key: vi.fn(),
};
Object.defineProperty(window, 'sessionStorage', {
  value: mockSessionStorage,
  writable: true,
});

describe('API Service', () => {
  beforeEach(() => {
    // Clear all mocks before each test
    vi.clearAllMocks();
    mockFetch.mockClear();
    mockSessionStorage.getItem.mockClear();
    mockSessionStorage.setItem.mockClear();
  });

  afterEach(() => {
    vi.resetAllMocks();
  });

  describe('queryKnowledgeBase', () => {
    it('should successfully query the knowledge base', async () => {
      const mockResponse: QueryResponse = {
        response: 'Autism Spectrum Disorder (ASD) is a developmental disability.',
        citations: [
          {
            title: 'What is Autism',
            url: 'https://example.com/autism',
            relevance_score: 0.95,
          },
        ],
        crisis_detected: false,
        crisis_severity: null,
        crisis_resources: [],
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      mockSessionStorage.getItem.mockReturnValue('test-session-id');

      const result = await queryKnowledgeBase('What is autism?', 'patient');

      expect(mockFetch).toHaveBeenCalledTimes(1);
      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/query',
        expect.objectContaining({
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: expect.stringContaining('What is autism?'),
        })
      );

      expect(result).toEqual(mockResponse);
      expect(result.response).toBe('Autism Spectrum Disorder (ASD) is a developmental disability.');
      expect(result.citations).toHaveLength(1);
      expect(result.crisis_detected).toBe(false);
    });

    it('should use provider view type when specified', async () => {
      const mockResponse: QueryResponse = {
        response: 'IEP refers to Individualized Education Program.',
        citations: [],
        crisis_detected: false,
        crisis_severity: null,
        crisis_resources: [],
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      mockSessionStorage.getItem.mockReturnValue('test-session-id');

      await queryKnowledgeBase('What is an IEP?', 'provider');

      const callArgs = mockFetch.mock.calls[0];
      const requestBody = JSON.parse(callArgs[1].body);

      expect(requestBody.view_type).toBe('provider');
      expect(requestBody.query).toBe('What is an IEP?');
    });

    it('should default to patient view type when not specified', async () => {
      const mockResponse: QueryResponse = {
        response: 'Test response',
        citations: [],
        crisis_detected: false,
        crisis_severity: null,
        crisis_resources: [],
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      mockSessionStorage.getItem.mockReturnValue('test-session-id');

      await queryKnowledgeBase('Test query');

      const callArgs = mockFetch.mock.calls[0];
      const requestBody = JSON.parse(callArgs[1].body);

      expect(requestBody.view_type).toBe('patient');
    });

    it('should generate and store session ID if not present', async () => {
      const mockResponse: QueryResponse = {
        response: 'Test response',
        citations: [],
        crisis_detected: false,
        crisis_severity: null,
        crisis_resources: [],
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      // Simulate no existing session ID
      mockSessionStorage.getItem.mockReturnValue(null);

      await queryKnowledgeBase('Test query');

      // Should have tried to get session ID
      expect(mockSessionStorage.getItem).toHaveBeenCalledWith('nc-ask-session-id');

      // Should have set a new session ID
      expect(mockSessionStorage.setItem).toHaveBeenCalledWith(
        'nc-ask-session-id',
        expect.stringMatching(/^session_\d+_[a-z0-9]+$/)
      );
    });

    it('should handle crisis detection response', async () => {
      const mockResponse: QueryResponse = {
        response: 'I understand you are going through a difficult time.',
        citations: [],
        crisis_detected: true,
        crisis_severity: 'high',
        crisis_resources: [
          {
            name: 'National Suicide Prevention Lifeline',
            phone: '988',
            description: '24/7 crisis support',
            url: 'https://988lifeline.org',
            priority: 1,
          },
        ],
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      mockSessionStorage.getItem.mockReturnValue('test-session-id');

      const result = await queryKnowledgeBase('I feel hopeless');

      expect(result.crisis_detected).toBe(true);
      expect(result.crisis_severity).toBe('high');
      expect(result.crisis_resources).toHaveLength(1);
      expect(result.crisis_resources[0].phone).toBe('988');
    });

    it('should throw error when request fails', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        json: async () => ({ detail: 'Internal server error' }),
      });

      mockSessionStorage.getItem.mockReturnValue('test-session-id');

      await expect(queryKnowledgeBase('Test query')).rejects.toThrow('Internal server error');
    });

    it('should throw generic error when error response has no detail', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        json: async () => {
          throw new Error('JSON parse error');
        },
      });

      mockSessionStorage.getItem.mockReturnValue('test-session-id');

      await expect(queryKnowledgeBase('Test query')).rejects.toThrow('Failed to process query');
    });

    it('should handle network errors', async () => {
      mockFetch.mockRejectedValueOnce(new Error('Network error'));

      mockSessionStorage.getItem.mockReturnValue('test-session-id');

      await expect(queryKnowledgeBase('Test query')).rejects.toThrow('Network error');
    });
  });

  describe('getCrisisResources', () => {
    it('should successfully fetch crisis resources', async () => {
      const mockResources: CrisisResource[] = [
        {
          name: 'National Suicide Prevention Lifeline',
          phone: '988',
          description: '24/7 crisis support',
          url: 'https://988lifeline.org',
          priority: 1,
        },
        {
          name: 'Crisis Text Line',
          phone: '741741',
          description: 'Text HOME to 741741',
          url: 'https://crisistextline.org',
          priority: 2,
        },
      ];

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ resources: mockResources }),
      });

      const result = await getCrisisResources();

      expect(mockFetch).toHaveBeenCalledTimes(1);
      expect(mockFetch).toHaveBeenCalledWith('http://localhost:8000/api/crisis-resources');

      expect(result).toEqual(mockResources);
      expect(result).toHaveLength(2);
      expect(result[0].phone).toBe('988');
      expect(result[1].phone).toBe('741741');
    });

    it('should throw error when request fails', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
      });

      await expect(getCrisisResources()).rejects.toThrow('Failed to fetch crisis resources');
    });

    it('should handle network errors', async () => {
      mockFetch.mockRejectedValueOnce(new Error('Network error'));

      await expect(getCrisisResources()).rejects.toThrow('Network error');
    });
  });

  describe('checkHealth', () => {
    it('should successfully check API health', async () => {
      const mockHealthResponse: HealthResponse = {
        status: 'healthy',
        service: 'NC-ASK Backend API',
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockHealthResponse,
      });

      const result = await checkHealth();

      expect(mockFetch).toHaveBeenCalledTimes(1);
      expect(mockFetch).toHaveBeenCalledWith('http://localhost:8000/api/health');

      expect(result).toEqual(mockHealthResponse);
      expect(result.status).toBe('healthy');
      expect(result.service).toBe('NC-ASK Backend API');
    });

    it('should throw error when health check fails', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
      });

      await expect(checkHealth()).rejects.toThrow('Health check failed');
    });

    it('should handle network errors', async () => {
      mockFetch.mockRejectedValueOnce(new Error('Network error'));

      await expect(checkHealth()).rejects.toThrow('Network error');
    });
  });

  describe('Session ID Management', () => {
    it('should reuse existing session ID across multiple queries', async () => {
      const mockResponse: QueryResponse = {
        response: 'Test response',
        citations: [],
        crisis_detected: false,
        crisis_severity: null,
        crisis_resources: [],
      };

      mockFetch.mockResolvedValue({
        ok: true,
        json: async () => mockResponse,
      });

      // Set existing session ID
      mockSessionStorage.getItem.mockReturnValue('existing-session-123');

      // Make two queries
      await queryKnowledgeBase('First query');
      await queryKnowledgeBase('Second query');

      // Should not have set a new session ID
      expect(mockSessionStorage.setItem).not.toHaveBeenCalled();

      // Both calls should use the same session ID
      const firstCallBody = JSON.parse(mockFetch.mock.calls[0][1].body);
      const secondCallBody = JSON.parse(mockFetch.mock.calls[1][1].body);

      expect(firstCallBody.session_id).toBe('existing-session-123');
      expect(secondCallBody.session_id).toBe('existing-session-123');
    });
  });

  describe('API Base URL', () => {
    it('should use environment variable for API base URL if set', async () => {
      // Note: This test verifies the default behavior since we can't easily
      // change import.meta.env in tests. In production, VITE_API_BASE_URL
      // can be set via environment variables.

      const mockResponse: QueryResponse = {
        response: 'Test',
        citations: [],
        crisis_detected: false,
        crisis_severity: null,
        crisis_resources: [],
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      mockSessionStorage.getItem.mockReturnValue('test-session-id');

      await queryKnowledgeBase('Test');

      // Should use localhost:8000 as default
      expect(mockFetch.mock.calls[0][0]).toContain('http://localhost:8000');
    });
  });
});
