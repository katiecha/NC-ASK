import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import ViewIndicator from '../components/ViewIndicator';

describe('ViewIndicator', () => {
  it('renders with provider view', () => {
    render(<ViewIndicator view="provider" />);

    expect(screen.getByText('Healthcare Provider')).toBeInTheDocument();
    expect(screen.getByText('Clinical, evidence-based responses')).toBeInTheDocument();
  });

  it('renders with patient view', () => {
    render(<ViewIndicator view="patient" />);

    expect(screen.getByText('Parent/Caregiver')).toBeInTheDocument();
    expect(screen.getByText('Supportive, easy-to-understand responses')).toBeInTheDocument();
  });

  it('displays "Current View:" label', () => {
    render(<ViewIndicator view="provider" />);

    expect(screen.getByText('Current View:')).toBeInTheDocument();
  });

  it('has proper ARIA attributes for accessibility', () => {
    render(<ViewIndicator view="provider" />);

    const indicator = screen.getByRole('status');
    expect(indicator).toBeInTheDocument();
    expect(indicator).toHaveAttribute('aria-live', 'polite');
  });

  it('shows correct label for provider view', () => {
    render(<ViewIndicator view="provider" />);

    expect(screen.getByText('Healthcare Provider')).toBeInTheDocument();
  });

  it('shows correct label for patient view', () => {
    render(<ViewIndicator view="patient" />);

    expect(screen.getByText('Parent/Caregiver')).toBeInTheDocument();
  });

  it('shows correct description for provider view', () => {
    render(<ViewIndicator view="provider" />);

    expect(screen.getByText('Clinical, evidence-based responses')).toBeInTheDocument();
  });

  it('shows correct description for patient view', () => {
    render(<ViewIndicator view="patient" />);

    expect(screen.getByText('Supportive, easy-to-understand responses')).toBeInTheDocument();
  });
});
