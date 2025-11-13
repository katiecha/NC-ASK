import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { BrowserRouter } from 'react-router-dom';
import Layout from '../components/Layout';
import { DarkModeProvider } from '../contexts/DarkModeContext';

const renderWithProviders = (component: React.ReactElement) => {
  return render(
    <BrowserRouter>
      <DarkModeProvider>
        {component}
      </DarkModeProvider>
    </BrowserRouter>
  );
};

describe('Layout', () => {
  it('renders children content', () => {
    renderWithProviders(
      <Layout>
        <div>Test Content</div>
      </Layout>
    );

    expect(screen.getByText('Test Content')).toBeInTheDocument();
  });

  it('renders hamburger menu', () => {
    renderWithProviders(
      <Layout>
        <div>Content</div>
      </Layout>
    );

    expect(screen.getByLabelText('Open menu')).toBeInTheDocument();
  });

  it('renders dark mode toggle', () => {
    renderWithProviders(
      <Layout>
        <div>Content</div>
      </Layout>
    );

    // Dark mode toggle should be present
    const darkModeButton = screen.getByRole('button', { name: /Switch to/i });
    expect(darkModeButton).toBeInTheDocument();
  });

  it('sidebar is closed by default', () => {
    const { container } = renderWithProviders(
      <Layout>
        <div>Content</div>
      </Layout>
    );

    const sidebar = container.querySelector('.sidebar');
    expect(sidebar).not.toHaveClass('sidebar-open');
  });

  it('opens sidebar when hamburger menu is clicked', async () => {
    const user = userEvent.setup();
    const { container } = renderWithProviders(
      <Layout>
        <div>Content</div>
      </Layout>
    );

    const hamburgerButton = screen.getByLabelText('Open menu');
    await user.click(hamburgerButton);

    const sidebar = container.querySelector('.sidebar');
    expect(sidebar).toHaveClass('sidebar-open');
  });

  it('closes sidebar when sidebar link is clicked', async () => {
    const user = userEvent.setup();
    const { container } = renderWithProviders(
      <Layout>
        <div>Content</div>
      </Layout>
    );

    // Open sidebar
    const hamburgerButton = screen.getByLabelText('Open menu');
    await user.click(hamburgerButton);

    let sidebar = container.querySelector('.sidebar');
    expect(sidebar).toHaveClass('sidebar-open');

    // Click a sidebar link
    const homeLink = screen.getByText('Home');
    await user.click(homeLink);

    sidebar = container.querySelector('.sidebar');
    expect(sidebar).not.toHaveClass('sidebar-open');
  });

  it('shows overlay when sidebar is open', async () => {
    const user = userEvent.setup();
    const { container } = renderWithProviders(
      <Layout>
        <div>Content</div>
      </Layout>
    );

    // Initially no overlay
    let overlay = container.querySelector('.sidebar-overlay');
    expect(overlay).not.toBeInTheDocument();

    // Open sidebar
    const hamburgerButton = screen.getByLabelText('Open menu');
    await user.click(hamburgerButton);

    overlay = container.querySelector('.sidebar-overlay');
    expect(overlay).toBeInTheDocument();
  });

  it('closes sidebar when overlay is clicked', async () => {
    const user = userEvent.setup();
    const { container } = renderWithProviders(
      <Layout>
        <div>Content</div>
      </Layout>
    );

    // Open sidebar
    const hamburgerButton = screen.getByLabelText('Open menu');
    await user.click(hamburgerButton);

    let sidebar = container.querySelector('.sidebar');
    expect(sidebar).toHaveClass('sidebar-open');

    // Click overlay
    const overlay = container.querySelector('.sidebar-overlay');
    if (overlay) {
      await user.click(overlay);
    }

    sidebar = container.querySelector('.sidebar');
    expect(sidebar).not.toHaveClass('sidebar-open');
  });

  it('renders main content area', () => {
    renderWithProviders(
      <Layout>
        <div data-testid="main-content">Main Content</div>
      </Layout>
    );

    expect(screen.getByTestId('main-content')).toBeInTheDocument();
  });
});
