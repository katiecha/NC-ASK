import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import ViewSelector from '../components/ViewSelector';

describe('ViewSelector', () => {
  it('renders when isOpen is true', () => {
    render(<ViewSelector isOpen={true} onSelectView={vi.fn()} />);

    expect(screen.getByText('Welcome to NC ASK')).toBeInTheDocument();
  });

  it('does not render when isOpen is false', () => {
    render(<ViewSelector isOpen={false} onSelectView={vi.fn()} />);

    expect(screen.queryByText('Welcome to NC ASK')).not.toBeInTheDocument();
  });

  it('displays both view options', () => {
    render(<ViewSelector isOpen={true} onSelectView={vi.fn()} />);

    expect(screen.getByText('Healthcare Provider')).toBeInTheDocument();
    expect(screen.getByText('Parent/Caregiver')).toBeInTheDocument();
  });

  it('calls onSelectView with "provider" when provider button is clicked', async () => {
    const user = userEvent.setup();
    const handleSelectView = vi.fn();

    render(<ViewSelector isOpen={true} onSelectView={handleSelectView} />);

    const providerButton = screen.getByLabelText('Select Healthcare Provider view');
    await user.click(providerButton);

    expect(handleSelectView).toHaveBeenCalledWith('provider');
  });

  it('calls onSelectView with "patient" when patient button is clicked', async () => {
    const user = userEvent.setup();
    const handleSelectView = vi.fn();

    render(<ViewSelector isOpen={true} onSelectView={handleSelectView} />);

    const patientButton = screen.getByLabelText('Select Patient/Parent view');
    await user.click(patientButton);

    expect(handleSelectView).toHaveBeenCalledWith('patient');
  });

  it('has proper ARIA attributes for modal', () => {
    render(<ViewSelector isOpen={true} onSelectView={vi.fn()} />);

    const modal = screen.getByRole('dialog');
    expect(modal).toHaveAttribute('aria-modal', 'true');
    expect(modal).toHaveAttribute('aria-labelledby', 'view-selector-title');
  });

  it('displays subtitle message', () => {
    render(<ViewSelector isOpen={true} onSelectView={vi.fn()} />);

    expect(screen.getByText("Please select how you'll be using NC ASK today")).toBeInTheDocument();
  });

  it('displays provider option description', () => {
    render(<ViewSelector isOpen={true} onSelectView={vi.fn()} />);

    expect(
      screen.getByText("I'm a medical professional seeking clinical information and evidence-based resources")
    ).toBeInTheDocument();
  });

  it('displays patient option description', () => {
    render(<ViewSelector isOpen={true} onSelectView={vi.fn()} />);

    expect(
      screen.getByText("I'm a parent or caregiver seeking support, guidance, and easy-to-understand information")
    ).toBeInTheDocument();
  });

  it('displays note about view flexibility', () => {
    render(<ViewSelector isOpen={true} onSelectView={vi.fn()} />);

    expect(
      screen.getByText('You can use NC ASK in either view. This selection helps us tailor responses to your needs.')
    ).toBeInTheDocument();
  });

  it('has proper aria-labels for accessibility', () => {
    render(<ViewSelector isOpen={true} onSelectView={vi.fn()} />);

    expect(screen.getByLabelText('Select Healthcare Provider view')).toBeInTheDocument();
    expect(screen.getByLabelText('Select Patient/Parent view')).toBeInTheDocument();
  });
});
