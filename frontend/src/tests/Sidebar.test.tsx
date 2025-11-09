import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { BrowserRouter } from 'react-router-dom';
import Sidebar from '../components/Sidebar';

const renderWithRouter = (component: React.ReactElement) => {
  return render(<BrowserRouter>{component}</BrowserRouter>);
};

describe('Sidebar', () => {
  it('renders navigation links', () => {
    renderWithRouter(<Sidebar isOpen={true} onClose={vi.fn()} />);

    expect(screen.getByText('Home')).toBeInTheDocument();
    expect(screen.getByText('About')).toBeInTheDocument();
  });

  it('applies open class when isOpen is true', () => {
    const { container } = renderWithRouter(<Sidebar isOpen={true} onClose={vi.fn()} />);
    const sidebar = container.querySelector('.sidebar');

    expect(sidebar).toHaveClass('sidebar-open');
  });

  it('does not apply open class when isOpen is false', () => {
    const { container } = renderWithRouter(<Sidebar isOpen={false} onClose={vi.fn()} />);
    const sidebar = container.querySelector('.sidebar');

    expect(sidebar).not.toHaveClass('sidebar-open');
  });

  it('calls onClose when Home link is clicked', async () => {
    const user = userEvent.setup();
    const handleClose = vi.fn();

    renderWithRouter(<Sidebar isOpen={true} onClose={handleClose} />);

    const homeLink = screen.getByText('Home');
    await user.click(homeLink);

    expect(handleClose).toHaveBeenCalledTimes(1);
  });

  it('calls onClose when About link is clicked', async () => {
    const user = userEvent.setup();
    const handleClose = vi.fn();

    renderWithRouter(<Sidebar isOpen={true} onClose={handleClose} />);

    const aboutLink = screen.getByText('About');
    await user.click(aboutLink);

    expect(handleClose).toHaveBeenCalledTimes(1);
  });

  it('has proper navigation structure', () => {
    renderWithRouter(<Sidebar isOpen={true} onClose={vi.fn()} />);

    const nav = screen.getByRole('navigation');
    expect(nav).toBeInTheDocument();
  });

  it('Home link points to correct path', () => {
    renderWithRouter(<Sidebar isOpen={true} onClose={vi.fn()} />);

    const homeLink = screen.getByText('Home').closest('a');
    expect(homeLink).toHaveAttribute('href', '/');
  });

  it('About link points to correct path', () => {
    renderWithRouter(<Sidebar isOpen={true} onClose={vi.fn()} />);

    const aboutLink = screen.getByText('About').closest('a');
    expect(aboutLink).toHaveAttribute('href', '/about');
  });
});
