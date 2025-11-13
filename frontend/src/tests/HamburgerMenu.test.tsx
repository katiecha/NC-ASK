import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import HamburgerMenu from '../components/HamburgerMenu';

describe('HamburgerMenu', () => {
  it('renders menu button', () => {
    render(<HamburgerMenu onClick={vi.fn()} />);

    expect(screen.getByRole('button')).toBeInTheDocument();
  });

  it('calls onClick when clicked', async () => {
    const user = userEvent.setup();
    const handleClick = vi.fn();

    render(<HamburgerMenu onClick={handleClick} />);

    const button = screen.getByRole('button');
    await user.click(button);

    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it('has proper aria-label for accessibility', () => {
    render(<HamburgerMenu onClick={vi.fn()} />);

    const button = screen.getByRole('button');
    expect(button).toHaveAttribute('aria-label', 'Open menu');
  });

  it('displays menu icon image', () => {
    render(<HamburgerMenu onClick={vi.fn()} />);

    const image = screen.getByAltText('Menu');
    expect(image).toBeInTheDocument();
    expect(image).toHaveAttribute('src', '/menu.svg');
  });

  it('is keyboard accessible', async () => {
    const user = userEvent.setup();
    const handleClick = vi.fn();

    render(<HamburgerMenu onClick={handleClick} />);

    const button = screen.getByRole('button');
    button.focus();
    expect(button).toHaveFocus();

    await user.keyboard('{Enter}');
    expect(handleClick).toHaveBeenCalled();
  });
});
