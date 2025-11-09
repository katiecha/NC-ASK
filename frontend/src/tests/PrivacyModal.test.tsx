import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import PrivacyModal from '../components/PrivacyModal';

describe('PrivacyModal', () => {
  it('does not render when isOpen is false', () => {
    render(
      <PrivacyModal
        isOpen={false}
        onAccept={vi.fn()}
        onReadPolicy={vi.fn()}
      />
    );

    expect(screen.queryByText('Welcome to NC ASK')).not.toBeInTheDocument();
  });

  it('renders when isOpen is true', () => {
    render(
      <PrivacyModal
        isOpen={true}
        onAccept={vi.fn()}
        onReadPolicy={vi.fn()}
      />
    );

    expect(screen.getByText('Welcome to NC ASK')).toBeInTheDocument();
  });

  it('displays the platform description', () => {
    render(
      <PrivacyModal
        isOpen={true}
        onAccept={vi.fn()}
        onReadPolicy={vi.fn()}
      />
    );

    expect(
      screen.getByText(/NC ASK \(North Carolina Autism Support & Knowledge\)/i)
    ).toBeInTheDocument();
    expect(
      screen.getByText(/educational digital platform/i)
    ).toBeInTheDocument();
  });

  it('displays all privacy agreement points', () => {
    render(
      <PrivacyModal
        isOpen={true}
        onAccept={vi.fn()}
        onReadPolicy={vi.fn()}
      />
    );

    expect(
      screen.getByText(/Anonymized data from your session may be collected/i)
    ).toBeInTheDocument();
    expect(
      screen.getByText(/No personal, identifying, or protected health information/i)
    ).toBeInTheDocument();
    expect(
      screen.getByText(/Aggregated, de-identified usage data may be analyzed/i)
    ).toBeInTheDocument();
    expect(
      screen.getByText(/You may stop using NC ASK at any time/i)
    ).toBeInTheDocument();
  });

  it('displays disclaimer', () => {
    render(
      <PrivacyModal
        isOpen={true}
        onAccept={vi.fn()}
        onReadPolicy={vi.fn()}
      />
    );

    expect(screen.getByText(/Disclaimer:/i)).toBeInTheDocument();
    // Use getAllByText since this phrase appears twice in the modal
    const disclaimerText = screen.getAllByText(/not a substitute for medical or legal advice/i);
    expect(disclaimerText.length).toBeGreaterThan(0);
  });

  it('calls onAccept when Accept & Continue button is clicked', async () => {
    const user = userEvent.setup();
    const handleAccept = vi.fn();

    render(
      <PrivacyModal
        isOpen={true}
        onAccept={handleAccept}
        onReadPolicy={vi.fn()}
      />
    );

    const acceptButton = screen.getByRole('button', { name: /Accept & Continue/i });
    await user.click(acceptButton);

    expect(handleAccept).toHaveBeenCalledTimes(1);
  });

  it('calls onReadPolicy when Read Full Privacy Policy button is clicked', async () => {
    const user = userEvent.setup();
    const handleReadPolicy = vi.fn();

    render(
      <PrivacyModal
        isOpen={true}
        onAccept={vi.fn()}
        onReadPolicy={handleReadPolicy}
      />
    );

    const policyButton = screen.getByRole('button', {
      name: /Read Full Privacy Policy & Consent Notice/i,
    });
    await user.click(policyButton);

    expect(handleReadPolicy).toHaveBeenCalledTimes(1);
  });

  it('renders both action buttons', () => {
    render(
      <PrivacyModal
        isOpen={true}
        onAccept={vi.fn()}
        onReadPolicy={vi.fn()}
      />
    );

    expect(
      screen.getByRole('button', { name: /Read Full Privacy Policy & Consent Notice/i })
    ).toBeInTheDocument();
    expect(
      screen.getByRole('button', { name: /Accept & Continue/i })
    ).toBeInTheDocument();
  });

  it('buttons have correct types to prevent form submission', () => {
    render(
      <PrivacyModal
        isOpen={true}
        onAccept={vi.fn()}
        onReadPolicy={vi.fn()}
      />
    );

    const policyButton = screen.getByRole('button', {
      name: /Read Full Privacy Policy & Consent Notice/i,
    });
    const acceptButton = screen.getByRole('button', { name: /Accept & Continue/i });

    expect(policyButton).toHaveAttribute('type', 'button');
    expect(acceptButton).toHaveAttribute('type', 'button');
  });

  it('has proper modal structure with overlay', () => {
    const { container } = render(
      <PrivacyModal
        isOpen={true}
        onAccept={vi.fn()}
        onReadPolicy={vi.fn()}
      />
    );

    expect(container.querySelector('.privacy-modal-overlay')).toBeInTheDocument();
    expect(container.querySelector('.privacy-modal')).toBeInTheDocument();
    expect(container.querySelector('.privacy-content')).toBeInTheDocument();
  });

  it('emphasizes key terms like "Disclaimer"', () => {
    render(
      <PrivacyModal
        isOpen={true}
        onAccept={vi.fn()}
        onReadPolicy={vi.fn()}
      />
    );

    const disclaimerStrong = screen.getByText('Disclaimer:');
    expect(disclaimerStrong.tagName).toBe('STRONG');
  });

  it('displays agreement header', () => {
    render(
      <PrivacyModal
        isOpen={true}
        onAccept={vi.fn()}
        onReadPolicy={vi.fn()}
      />
    );

    expect(
      screen.getByText('By continuing, you acknowledge and agree that:')
    ).toBeInTheDocument();
  });

  it('prevents usage until modal is accepted (blocks when open)', () => {
    render(
      <PrivacyModal
        isOpen={true}
        onAccept={vi.fn()}
        onReadPolicy={vi.fn()}
      />
    );

    // Modal should be present, blocking the UI
    const modalOverlay = document.querySelector('.privacy-modal-overlay');
    expect(modalOverlay).toBeInTheDocument();
  });

  it('allows usage after modal is closed (no blocking when closed)', () => {
    render(
      <PrivacyModal
        isOpen={false}
        onAccept={vi.fn()}
        onReadPolicy={vi.fn()}
      />
    );

    // Modal should not be present
    const modalOverlay = document.querySelector('.privacy-modal-overlay');
    expect(modalOverlay).not.toBeInTheDocument();
  });
});
