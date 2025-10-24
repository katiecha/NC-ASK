import React from 'react';
import { ViewType } from '../contexts/ViewContext';
import styles from './ViewSelector.module.css';

interface ViewSelectorProps {
  isOpen: boolean;
  onSelectView: (view: ViewType) => void;
}

/**
 * ViewSelector modal that appears on first visit
 *
 * Forces users to select their view (provider or patient) before
 * they can start using the application. This determines the tone
 * and style of LLM responses.
 */
const ViewSelector: React.FC<ViewSelectorProps> = ({ isOpen, onSelectView }) => {
  if (!isOpen) return null;

  const handleSelectProvider = () => {
    onSelectView('provider');
  };

  const handleSelectPatient = () => {
    onSelectView('patient');
  };

  return (
    <div className={styles.overlay} role="dialog" aria-modal="true" aria-labelledby="view-selector-title">
      <div className={styles.modal}>
        <h2 id="view-selector-title" className={styles.title}>
          Welcome to NC ASK
        </h2>
        <p className={styles.subtitle}>
          Please select how you'll be using NC ASK today
        </p>

        <div className={styles.options}>
          <button
            className={styles.optionButton}
            onClick={handleSelectProvider}
            aria-label="Select Healthcare Provider view"
          >
            <h3 className={styles.optionTitle}>Healthcare Provider</h3>
            <p className={styles.optionDescription}>
              I'm a medical professional seeking clinical information and evidence-based resources
            </p>
          </button>

          <button
            className={styles.optionButton}
            onClick={handleSelectPatient}
            aria-label="Select Patient/Parent view"
          >
            <h3 className={styles.optionTitle}>Parent/Caregiver</h3>
            <p className={styles.optionDescription}>
              I'm a parent or caregiver seeking support, guidance, and easy-to-understand information
            </p>
          </button>
        </div>

        <p className={styles.note}>
          You can use NC ASK in either view. This selection helps us tailor responses to your needs.
        </p>
      </div>
    </div>
  );
};

export default ViewSelector;
