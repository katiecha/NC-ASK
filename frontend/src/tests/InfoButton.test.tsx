import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import InfoButton from '../components/InfoButton';

const renderWithRouter = (component: React.ReactElement) => {
  return render(<BrowserRouter>{component}</BrowserRouter>);
};

describe('InfoButton', () => {
  it('renders info button link', () => {
    renderWithRouter(<InfoButton />);

    const link = screen.getByRole('link');
    expect(link).toBeInTheDocument();
  });

  it('links to about page', () => {
    renderWithRouter(<InfoButton />);

    const link = screen.getByRole('link');
    expect(link).toHaveAttribute('href', '/about');
  });

  it('has proper aria-label for accessibility', () => {
    renderWithRouter(<InfoButton />);

    const link = screen.getByRole('link');
    expect(link).toHaveAttribute('aria-label', 'About NC ASK');
  });

  it('displays info icon image', () => {
    renderWithRouter(<InfoButton />);

    const svg = screen.getByRole('link').querySelector('svg');
    expect(svg).toBeInTheDocument();
    expect(svg).toHaveClass('info-icon');
  });

  it('has correct CSS class', () => {
    renderWithRouter(<InfoButton />);

    const link = screen.getByRole('link');
    expect(link).toHaveClass('info-button');
  });

  it('is keyboard accessible', () => {
    renderWithRouter(<InfoButton />);

    const link = screen.getByRole('link');
    link.focus();
    expect(link).toHaveFocus();
  });
});
