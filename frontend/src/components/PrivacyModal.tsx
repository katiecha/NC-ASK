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
          <h2>Welcome to NC ASK</h2>
          <p>
            NC ASK (North Carolina Autism Support & Knowledge) is an educational digital platform
            that provides information and resources for families, providers, and advocates of
            children with autism spectrum disorder (ASD). It is not a substitute for medical or legal
            advice, diagnosis, or treatment.
          </p>

          <div className="privacy-agreement">
            <p>By continuing, you acknowledge and agree that:</p>
            <ul>
              <li>
                Anonymized data from your session may be collected to improve NC ASK’s accuracy,
                accessibility, and usability, and to support research on autism resources in
                North Carolina.
              </li>
              <li>
                No personal, identifying, or protected health information (PHI) should be entered into
                the platform.
              </li>
              <li>
                Aggregated, de-identified usage data may be analyzed for research, advocacy, and
                policy improvement purposes, but will never include personal identifiers.
              </li>
              <li>
                You may stop using NC ASK at any time, which ends any further data collection.
              </li>
            </ul>
          </div>

          <div className="privacy-actions">
            <button
              className="privacy-link-button"
              onClick={onReadPolicy}
              type="button"
            >
              Read Full Privacy Policy & Consent Notice
            </button>
            <button
              className="privacy-accept-button"
              onClick={onAccept}
              type="button"
            >
              Accept & Continue
            </button>
          </div>

          <footer className="privacy-footer">
            <p className="privacy-disclaimer">
              <strong>Disclaimer:</strong> NC ASK is an educational tool only and not a substitute for
              medical or legal advice.
            </p>
          </footer>
        </div>
      </div>
    </div>
  );
};

export default PrivacyModal;
