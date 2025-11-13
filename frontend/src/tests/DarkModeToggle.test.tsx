import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import DarkModeToggle from '../components/DarkModeToggle';
import { DarkModeProvider } from '../contexts/DarkModeContext';

describe('DarkModeToggle', () => {
  it('renders toggle button', () => {
    render(
      <DarkModeProvider>
        <DarkModeToggle />
      </DarkModeProvider>
    );

    expect(screen.getByRole('button')).toBeInTheDocument();
  });

  it('shows moon icon in light mode', () => {
    render(
      <DarkModeProvider>
        <DarkModeToggle />
      </DarkModeProvider>
    );

    const button = screen.getByRole('button');
    expect(button).toHaveAttribute('aria-label', 'Switch to dark mode');
  });

  it('toggles dark mode when clicked', async () => {
    const user = userEvent.setup();

    render(
      <DarkModeProvider>
        <DarkModeToggle />
      </DarkModeProvider>
    );

    const button = screen.getByRole('button');

    // Initially in light mode
    expect(button).toHaveAttribute('aria-label', 'Switch to dark mode');

    // Click to toggle to dark mode
    await user.click(button);
    expect(button).toHaveAttribute('aria-label', 'Switch to light mode');

    // Click to toggle back to light mode
    await user.click(button);
    expect(button).toHaveAttribute('aria-label', 'Switch to dark mode');
  });

  it('has proper accessibility labels', () => {
    render(
      <DarkModeProvider>
        <DarkModeToggle />
      </DarkModeProvider>
    );

    const button = screen.getByRole('button');
    expect(button).toHaveAttribute('aria-label');
    expect(button).toHaveAttribute('title');
  });

  it('updates document class when toggled', async () => {
    const user = userEvent.setup();

    render(
      <DarkModeProvider>
        <DarkModeToggle />
      </DarkModeProvider>
    );

    const button = screen.getByRole('button');

    // Initially no dark-mode class
    expect(document.documentElement.classList.contains('dark-mode')).toBe(false);

    // Click to enable dark mode
    await user.click(button);
    expect(document.documentElement.classList.contains('dark-mode')).toBe(true);

    // Click to disable dark mode
    await user.click(button);
    expect(document.documentElement.classList.contains('dark-mode')).toBe(false);
  });
});
