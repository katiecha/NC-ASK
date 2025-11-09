import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import QueryResponse from '../components/QueryResponse';
import { Citation, CrisisResource } from '../services/api';

describe('QueryResponse', () => {
  const mockCitations: Citation[] = [
    {
      title: 'Test Document 1',
      url: 'https://example.com/doc1',
      relevance_score: 0.95,
    },
    {
      title: 'Test Document 2',
      url: null,
      relevance_score: 0.87,
    },
  ];

  const mockCrisisResources: CrisisResource[] = [
    {
      name: '988 Suicide & Crisis Lifeline',
      phone: '988',
      description: '24/7 free and confidential support',
      url: 'https://988lifeline.org',
      priority: 1,
    },
    {
      name: 'Crisis Text Line',
      phone: '741741',
      description: 'Text HOME to 741741',
      url: null,
      priority: 2,
    },
  ];

  it('renders response text', () => {
    render(
      <QueryResponse
        response="This is a test response"
        citations={[]}
        crisisDetected={false}
      />
    );

    expect(screen.getByText('This is a test response')).toBeInTheDocument();
  });

  it('renders markdown in response', () => {
    render(
      <QueryResponse
        response="# Heading\n\nThis is **bold** text"
        citations={[]}
        crisisDetected={false}
      />
    );

    // ReactMarkdown renders the heading, check that it exists
    expect(screen.getByRole('heading', { level: 1 })).toBeInTheDocument();
    // Check that bold text is rendered as a strong element
    expect(screen.getByText('bold')).toBeInTheDocument();
    const boldElement = screen.getByText('bold');
    expect(boldElement.tagName).toBe('STRONG');
  });

  it('renders citations when provided', () => {
    render(
      <QueryResponse
        response="Test response"
        citations={mockCitations}
        crisisDetected={false}
      />
    );

    expect(screen.getByText('Sources')).toBeInTheDocument();
    expect(screen.getByText('Test Document 1')).toBeInTheDocument();
    expect(screen.getByText('Test Document 2')).toBeInTheDocument();
    expect(screen.getByText('(Relevance: 95%)')).toBeInTheDocument();
    expect(screen.getByText('(Relevance: 87%)')).toBeInTheDocument();
  });

  it('renders citation links when URL is provided', () => {
    render(
      <QueryResponse
        response="Test response"
        citations={mockCitations}
        crisisDetected={false}
      />
    );

    const links = screen.getAllByText('View source');
    expect(links).toHaveLength(1); // Only one citation has a URL
    expect(links[0]).toHaveAttribute('href', 'https://example.com/doc1');
    expect(links[0]).toHaveAttribute('target', '_blank');
    expect(links[0]).toHaveAttribute('rel', 'noopener noreferrer');
  });

  it('does not render Sources section when citations are empty', () => {
    render(
      <QueryResponse
        response="Test response"
        citations={[]}
        crisisDetected={false}
      />
    );

    expect(screen.queryByText('Sources')).not.toBeInTheDocument();
  });

  it('displays crisis alert when crisis is detected', () => {
    render(
      <QueryResponse
        response="Test response"
        citations={[]}
        crisisDetected={true}
        crisisResources={mockCrisisResources}
      />
    );

    expect(screen.getByText('Crisis Support Available')).toBeInTheDocument();
  });

  it('does not display crisis alert when crisis is not detected', () => {
    render(
      <QueryResponse
        response="Test response"
        citations={[]}
        crisisDetected={false}
      />
    );

    expect(screen.queryByText('Crisis Support Available')).not.toBeInTheDocument();
  });

  it('crisis resources dropdown starts closed', () => {
    render(
      <QueryResponse
        response="Test response"
        citations={[]}
        crisisDetected={true}
        crisisResources={mockCrisisResources}
      />
    );

    expect(screen.queryByText('988 Suicide & Crisis Lifeline')).not.toBeInTheDocument();
  });

  it('toggles crisis resources dropdown when button is clicked', async () => {
    const user = userEvent.setup();

    render(
      <QueryResponse
        response="Test response"
        citations={[]}
        crisisDetected={true}
        crisisResources={mockCrisisResources}
      />
    );

    const toggleButton = screen.getByRole('button', { name: /resources/i });

    // Initially closed
    expect(screen.queryByText('988 Suicide & Crisis Lifeline')).not.toBeInTheDocument();

    // Click to open
    await user.click(toggleButton);
    expect(screen.getByText('988 Suicide & Crisis Lifeline')).toBeInTheDocument();
    expect(screen.getByText('24/7 free and confidential support')).toBeInTheDocument();

    // Click to close
    await user.click(toggleButton);
    expect(screen.queryByText('988 Suicide & Crisis Lifeline')).not.toBeInTheDocument();
  });

  it('renders crisis resources with correct information', async () => {
    const user = userEvent.setup();

    render(
      <QueryResponse
        response="Test response"
        citations={[]}
        crisisDetected={true}
        crisisResources={mockCrisisResources}
      />
    );

    const toggleButton = screen.getByRole('button', { name: /resources/i });
    await user.click(toggleButton);

    // Check first resource
    expect(screen.getByText('988 Suicide & Crisis Lifeline')).toBeInTheDocument();
    expect(screen.getByText('988')).toBeInTheDocument();
    expect(screen.getByText('24/7 free and confidential support')).toBeInTheDocument();

    // Check phone link
    const phoneLink = screen.getByText('988').closest('a');
    expect(phoneLink).toHaveAttribute('href', 'tel:988');

    // Check resource link
    const resourceLinks = screen.getAllByText('Learn more');
    expect(resourceLinks[0]).toHaveAttribute('href', 'https://988lifeline.org');
    expect(resourceLinks[0]).toHaveAttribute('target', '_blank');
  });

  it('handles crisis resources without URLs', async () => {
    const user = userEvent.setup();

    render(
      <QueryResponse
        response="Test response"
        citations={[]}
        crisisDetected={true}
        crisisResources={mockCrisisResources}
      />
    );

    const toggleButton = screen.getByRole('button', { name: /resources/i });
    await user.click(toggleButton);

    // Second resource has no URL
    expect(screen.getByText('Crisis Text Line')).toBeInTheDocument();
    expect(screen.getByText('Text HOME to 741741')).toBeInTheDocument();

    // Should have 1 "Learn more" link (only for resource with URL)
    const learnMoreLinks = screen.getAllByText('Learn more');
    expect(learnMoreLinks).toHaveLength(1);
  });

  it('has proper ARIA attributes for accessibility', () => {
    render(
      <QueryResponse
        response="Test response"
        citations={[]}
        crisisDetected={false}
      />
    );

    expect(screen.getByRole('region', { name: 'Response' })).toBeInTheDocument();
  });

  it('has proper ARIA attributes for crisis dropdown', () => {
    render(
      <QueryResponse
        response="Test response"
        citations={[]}
        crisisDetected={true}
        crisisResources={mockCrisisResources}
      />
    );

    const toggleButton = screen.getByRole('button', { name: /resources/i });
    expect(toggleButton).toHaveAttribute('aria-expanded', 'false');
  });

  it('applies crisis styling when crisis is detected', () => {
    const { container } = render(
      <QueryResponse
        response="Test response"
        citations={[]}
        crisisDetected={true}
        crisisResources={mockCrisisResources}
      />
    );

    const responseElement = container.querySelector('.query-response');
    expect(responseElement).toHaveClass('crisis-response');
  });
});
