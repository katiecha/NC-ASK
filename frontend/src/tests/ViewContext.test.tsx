import { describe, it, expect } from 'vitest';
import { render, screen, renderHook, act } from '@testing-library/react';
import { ViewProvider, useView, ViewType } from '../contexts/ViewContext';

describe('ViewContext', () => {
  describe('ViewProvider', () => {
    it('provides view context to children', () => {
      const TestComponent = () => {
        const { selectedView } = useView();
        return <div>{selectedView || 'No view selected'}</div>;
      };

      render(
        <ViewProvider>
          <TestComponent />
        </ViewProvider>
      );

      expect(screen.getByText('No view selected')).toBeInTheDocument();
    });

    it('initializes with null selectedView', () => {
      const { result } = renderHook(() => useView(), {
        wrapper: ViewProvider,
      });

      expect(result.current.selectedView).toBeNull();
    });

    it('allows setting view to provider', () => {
      const { result } = renderHook(() => useView(), {
        wrapper: ViewProvider,
      });

      act(() => {
        result.current.setSelectedView('provider');
      });

      expect(result.current.selectedView).toBe('provider');
    });

    it('allows setting view to patient', () => {
      const { result } = renderHook(() => useView(), {
        wrapper: ViewProvider,
      });

      act(() => {
        result.current.setSelectedView('patient');
      });

      expect(result.current.selectedView).toBe('patient');
    });

    it('allows changing view from provider to patient', () => {
      const { result } = renderHook(() => useView(), {
        wrapper: ViewProvider,
      });

      act(() => {
        result.current.setSelectedView('provider');
      });

      expect(result.current.selectedView).toBe('provider');

      act(() => {
        result.current.setSelectedView('patient');
      });

      expect(result.current.selectedView).toBe('patient');
    });

    it('does not persist view in localStorage', () => {
      const { result } = renderHook(() => useView(), {
        wrapper: ViewProvider,
      });

      act(() => {
        result.current.setSelectedView('provider');
      });

      // Check that nothing was saved to localStorage
      expect(localStorage.getItem('nc-ask-view')).toBeNull();
      expect(localStorage.getItem('selectedView')).toBeNull();
    });
  });

  describe('useView hook', () => {
    it('throws error when used outside ViewProvider', () => {
      // Suppress console.error for this test
      const originalError = console.error;
      console.error = () => {};

      expect(() => {
        renderHook(() => useView());
      }).toThrow('useView must be used within a ViewProvider');

      console.error = originalError;
    });

    it('returns selectedView and setSelectedView', () => {
      const { result } = renderHook(() => useView(), {
        wrapper: ViewProvider,
      });

      expect(result.current).toHaveProperty('selectedView');
      expect(result.current).toHaveProperty('setSelectedView');
      expect(typeof result.current.setSelectedView).toBe('function');
    });

    it('selectedView is null or ViewType', () => {
      const { result } = renderHook(() => useView(), {
        wrapper: ViewProvider,
      });

      const validValues: (ViewType | null)[] = ['provider', 'patient', null];
      expect(validValues).toContain(result.current.selectedView);
    });
  });

  describe('ViewType', () => {
    it('accepts "provider" as valid ViewType', () => {
      const { result } = renderHook(() => useView(), {
        wrapper: ViewProvider,
      });

      act(() => {
        result.current.setSelectedView('provider' as ViewType);
      });

      expect(result.current.selectedView).toBe('provider');
    });

    it('accepts "patient" as valid ViewType', () => {
      const { result } = renderHook(() => useView(), {
        wrapper: ViewProvider,
      });

      act(() => {
        result.current.setSelectedView('patient' as ViewType);
      });

      expect(result.current.selectedView).toBe('patient');
    });
  });
});
