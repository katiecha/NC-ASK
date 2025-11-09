import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import SearchInput from '../components/SearchInput';

describe('SearchInput', () => {
  it('renders with default placeholder', () => {
    render(
      <SearchInput
        value=""
        onChange={vi.fn()}
        onSearch={vi.fn()}
      />
    );

    expect(screen.getByPlaceholderText('Ask a question...')).toBeInTheDocument();
  });

  it('renders with custom placeholder', () => {
    render(
      <SearchInput
        value=""
        onChange={vi.fn()}
        onSearch={vi.fn()}
        placeholder="Custom placeholder"
      />
    );

    expect(screen.getByPlaceholderText('Custom placeholder')).toBeInTheDocument();
  });

  it('displays the current value', () => {
    render(
      <SearchInput
        value="Test query"
        onChange={vi.fn()}
        onSearch={vi.fn()}
      />
    );

    expect(screen.getByRole('textbox')).toHaveValue('Test query');
  });

  it('calls onChange when input changes', async () => {
    const user = userEvent.setup();
    const handleChange = vi.fn();

    render(
      <SearchInput
        value=""
        onChange={handleChange}
        onSearch={vi.fn()}
      />
    );

    const input = screen.getByRole('textbox');
    await user.type(input, 'New text');

    expect(handleChange).toHaveBeenCalled();
  });

  it('calls onSearch with trimmed value when form is submitted', async () => {
    const user = userEvent.setup();
    const handleSearch = vi.fn();

    render(
      <SearchInput
        value="  test query  "
        onChange={vi.fn()}
        onSearch={handleSearch}
      />
    );

    const form = screen.getByRole('textbox').closest('form');
    if (form) {
      await user.click(form);
      form.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true }));
    }

    expect(handleSearch).toHaveBeenCalledWith('test query');
  });

  it('does not call onSearch when value is empty or only whitespace', async () => {
    const handleSearch = vi.fn();

    const { rerender } = render(
      <SearchInput
        value="   "
        onChange={vi.fn()}
        onSearch={handleSearch}
      />
    );

    const form = screen.getByRole('textbox').closest('form');
    if (form) {
      form.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true }));
    }

    expect(handleSearch).not.toHaveBeenCalled();

    rerender(
      <SearchInput
        value=""
        onChange={vi.fn()}
        onSearch={handleSearch}
      />
    );

    if (form) {
      form.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true }));
    }

    expect(handleSearch).not.toHaveBeenCalled();
  });

  it('is disabled when disabled prop is true', () => {
    render(
      <SearchInput
        value=""
        onChange={vi.fn()}
        onSearch={vi.fn()}
        disabled={true}
      />
    );

    expect(screen.getByRole('textbox')).toBeDisabled();
  });

  it('has proper aria-label for accessibility', () => {
    render(
      <SearchInput
        value=""
        onChange={vi.fn()}
        onSearch={vi.fn()}
      />
    );

    expect(screen.getByLabelText('Search input')).toBeInTheDocument();
  });

  it('submits form when Enter key is pressed without Shift', async () => {
    const user = userEvent.setup();
    const handleSearch = vi.fn();

    render(
      <SearchInput
        value="test query"
        onChange={vi.fn()}
        onSearch={handleSearch}
      />
    );

    const input = screen.getByRole('textbox');
    await user.click(input);
    await user.keyboard('{Enter}');

    expect(handleSearch).toHaveBeenCalledWith('test query');
  });
});
