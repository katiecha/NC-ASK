import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { render, screen, renderHook, act } from '@testing-library/react';
import { DarkModeProvider, useDarkMode } from '../contexts/DarkModeContext';

describe('DarkModeContext', () => {
  beforeEach(() => {
    // Clear localStorage before each test
    localStorage.clear();
    // Clear dark-mode class from document
    document.documentElement.classList.remove('dark-mode');
  });

  afterEach(() => {
    localStorage.clear();
    document.documentElement.classList.remove('dark-mode');
  });

  describe('DarkModeProvider', () => {
    it('provides dark mode context to children', () => {
      const TestComponent = () => {
        const { isDarkMode } = useDarkMode();
        return <div>{isDarkMode ? 'Dark' : 'Light'}</div>;
      };

      render(
        <DarkModeProvider>
          <TestComponent />
        </DarkModeProvider>
      );

      expect(screen.getByText('Light')).toBeInTheDocument();
    });

    it('initializes with light mode by default', () => {
      const { result } = renderHook(() => useDarkMode(), {
        wrapper: DarkModeProvider,
      });

      expect(result.current.isDarkMode).toBe(false);
    });

    it('initializes with saved preference from localStorage', () => {
      localStorage.setItem('nc-ask-dark-mode', JSON.stringify(true));

      const { result } = renderHook(() => useDarkMode(), {
        wrapper: DarkModeProvider,
      });

      expect(result.current.isDarkMode).toBe(true);
    });

    it('toggles dark mode when toggleDarkMode is called', () => {
      const { result } = renderHook(() => useDarkMode(), {
        wrapper: DarkModeProvider,
      });

      expect(result.current.isDarkMode).toBe(false);

      act(() => {
        result.current.toggleDarkMode();
      });

      expect(result.current.isDarkMode).toBe(true);

      act(() => {
        result.current.toggleDarkMode();
      });

      expect(result.current.isDarkMode).toBe(false);
    });

    it('adds dark-mode class to document when dark mode is enabled', () => {
      const { result } = renderHook(() => useDarkMode(), {
        wrapper: DarkModeProvider,
      });

      expect(document.documentElement.classList.contains('dark-mode')).toBe(false);

      act(() => {
        result.current.toggleDarkMode();
      });

      expect(document.documentElement.classList.contains('dark-mode')).toBe(true);
    });

    it('removes dark-mode class from document when dark mode is disabled', () => {
      localStorage.setItem('nc-ask-dark-mode', JSON.stringify(true));

      const { result } = renderHook(() => useDarkMode(), {
        wrapper: DarkModeProvider,
      });

      expect(document.documentElement.classList.contains('dark-mode')).toBe(true);

      act(() => {
        result.current.toggleDarkMode();
      });

      expect(document.documentElement.classList.contains('dark-mode')).toBe(false);
    });

    it('saves dark mode preference to localStorage', () => {
      const { result } = renderHook(() => useDarkMode(), {
        wrapper: DarkModeProvider,
      });

      act(() => {
        result.current.toggleDarkMode();
      });

      expect(localStorage.getItem('nc-ask-dark-mode')).toBe('true');

      act(() => {
        result.current.toggleDarkMode();
      });

      expect(localStorage.getItem('nc-ask-dark-mode')).toBe('false');
    });
  });

  describe('useDarkMode hook', () => {
    it('throws error when used outside DarkModeProvider', () => {
      // Suppress console.error for this test
      const originalError = console.error;
      console.error = () => {};

      expect(() => {
        renderHook(() => useDarkMode());
      }).toThrow('useDarkMode must be used within a DarkModeProvider');

      console.error = originalError;
    });

    it('returns isDarkMode and toggleDarkMode', () => {
      const { result } = renderHook(() => useDarkMode(), {
        wrapper: DarkModeProvider,
      });

      expect(result.current).toHaveProperty('isDarkMode');
      expect(result.current).toHaveProperty('toggleDarkMode');
      expect(typeof result.current.isDarkMode).toBe('boolean');
      expect(typeof result.current.toggleDarkMode).toBe('function');
    });
  });
});
