import React from 'react';
import './PrivacyModal.css';

interface PrivacyModalProps {
  isOpen: boolean;
  onAccept: () => void;
  onReadPolicy: () => void;
}

const PrivacyModal: React.FC<PrivacyModalProps> = ({ isOpen, onAccept, onReadPolicy }) => {
  if (!isOpen) return null;

  return (
    <div className="privacy-modal-overlay">
      <div className="privacy-modal">
        <div className="privacy-content">
          <h2>Welcome to NC ASK, an educational platform providing autism-related information and resources.</h2>
          <p>Note: NC ASK is not a substitute for medical or legal advice.</p>
          
          <div className="privacy-agreement">
            <p>By continuing, you acknowledge and agree that:</p>
            <ul>
              <li>Anonymized data from your session may be collected to improve NC ASK and support research.</li>
              <li>You will not enter any personal or identifying information into the platform.</li>
              <li>Aggregated, de-identified usage data may be used for system improvement and research.</li>
            </ul>
          </div>
          
          <div className="privacy-actions">
            <button 
              className="privacy-link-button" 
              onClick={onReadPolicy}
              type="button"
            >
              Read Privacy Policy & Consent Notice
            </button>
            <button 
              className="privacy-accept-button" 
              onClick={onAccept}
              type="button"
            >
              Accept
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PrivacyModal;