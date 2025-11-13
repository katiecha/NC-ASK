import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import ActionButtons from '../components/ActionButtons';

describe('ActionButtons', () => {
  it('renders file upload and voice input buttons', () => {
    render(<ActionButtons onFileUpload={vi.fn()} onVoiceInput={vi.fn()} />);

    expect(screen.getByLabelText('Upload file')).toBeInTheDocument();
    expect(screen.getByLabelText('Voice input')).toBeInTheDocument();
  });

  it('calls onVoiceInput when voice button is clicked', async () => {
    const user = userEvent.setup();
    const handleVoiceInput = vi.fn();

    render(<ActionButtons onFileUpload={vi.fn()} onVoiceInput={handleVoiceInput} />);

    const voiceButton = screen.getByLabelText('Voice input');
    await user.click(voiceButton);

    expect(handleVoiceInput).toHaveBeenCalledTimes(1);
  });

  it('triggers file input when upload button is clicked', async () => {
    const user = userEvent.setup();
    const handleFileUpload = vi.fn();

    render(<ActionButtons onFileUpload={handleFileUpload} onVoiceInput={vi.fn()} />);

    const uploadButton = screen.getByLabelText('Upload file');
    await user.click(uploadButton);

    // File input should be present in the document
    const fileInput = document.querySelector('input[type="file"]');
    expect(fileInput).toBeInTheDocument();
  });

  it('calls onFileUpload with file when file is selected', async () => {
    const user = userEvent.setup();
    const handleFileUpload = vi.fn();
    const file = new File(['test content'], 'test.pdf', { type: 'application/pdf' });

    render(<ActionButtons onFileUpload={handleFileUpload} onVoiceInput={vi.fn()} />);

    const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement;
    expect(fileInput).toBeInTheDocument();

    // Simulate file selection
    await user.upload(fileInput, file);

    expect(handleFileUpload).toHaveBeenCalledWith(file);
  });

  it('accepts correct file types', () => {
    render(<ActionButtons onFileUpload={vi.fn()} onVoiceInput={vi.fn()} />);

    const fileInput = document.querySelector('input[type="file"]');
    expect(fileInput).toHaveAttribute('accept', '.pdf,.doc,.docx,.txt');
  });

  it('hides file input visually', () => {
    render(<ActionButtons onFileUpload={vi.fn()} onVoiceInput={vi.fn()} />);

    const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement;
    expect(fileInput.style.display).toBe('none');
  });

  it('has proper aria-labels for accessibility', () => {
    render(<ActionButtons onFileUpload={vi.fn()} onVoiceInput={vi.fn()} />);

    expect(screen.getByLabelText('Upload file')).toHaveAttribute('aria-label', 'Upload file');
    expect(screen.getByLabelText('Voice input')).toHaveAttribute('aria-label', 'Voice input');
  });

  it('displays correct icons', () => {
    render(<ActionButtons onFileUpload={vi.fn()} onVoiceInput={vi.fn()} />);

    const uploadIcon = screen.getByAltText('Upload file');
    const voiceIcon = screen.getByAltText('Voice input');

    expect(uploadIcon).toHaveAttribute('src', '/note.svg');
    expect(voiceIcon).toHaveAttribute('src', '/mic.svg');
  });

  it('buttons have type="button" to prevent form submission', () => {
    render(<ActionButtons onFileUpload={vi.fn()} onVoiceInput={vi.fn()} />);

    const uploadButton = screen.getByLabelText('Upload file');
    const voiceButton = screen.getByLabelText('Voice input');

    expect(uploadButton).toHaveAttribute('type', 'button');
    expect(voiceButton).toHaveAttribute('type', 'button');
  });
});
