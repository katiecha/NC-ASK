import React, { useRef } from 'react';
import './ActionButtons.css';

interface ActionButtonsProps {
  onFileUpload: (file: File) => void;
  onVoiceInput: () => void;
}

const ActionButtons: React.FC<ActionButtonsProps> = ({ onFileUpload, onVoiceInput }) => {
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileUploadClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      onFileUpload(file);
    }
  };

  return (
    <div className="action-buttons">
      <button 
        className="action-button file-upload-button"
        onClick={handleFileUploadClick}
        aria-label="Upload file"
        type="button"
      >
        <img src="/note.svg" alt="Upload file" className="action-icon" />
      </button>
      
      <button 
        className="action-button voice-input-button"
        onClick={onVoiceInput}
        aria-label="Voice input"
        type="button"
      >
        <img src="/mic.svg" alt="Voice input" className="action-icon" />
      </button>
      
      <input
        ref={fileInputRef}
        type="file"
        onChange={handleFileChange}
        style={{ display: 'none' }}
        accept=".pdf,.doc,.docx,.txt"
      />
    </div>
  );
};

export default ActionButtons;