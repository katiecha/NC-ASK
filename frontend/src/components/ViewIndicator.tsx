import React from 'react';
import { ViewType } from '../contexts/ViewContext';
import styles from './ViewIndicator.module.css';

interface ViewIndicatorProps {
  view: ViewType;
}

/**
 * ViewIndicator displays the current active view (provider or patient)
 *
 * Shows a small badge indicating which view mode is active, helping
 * users understand what type of responses they'll receive.
 */
const ViewIndicator: React.FC<ViewIndicatorProps> = ({ view }) => {
  const viewLabel = view === 'provider' ? 'Healthcare Provider' : 'Parent/Caregiver';
  const viewDescription = view === 'provider'
    ? 'Clinical, evidence-based responses'
    : 'Supportive, easy-to-understand responses';

  return (
    <div className={styles.indicator} role="status" aria-live="polite">
      <div className={styles.badge}>
        <span className={styles.label}>Current View:</span>
        <span className={styles.viewName}>{viewLabel}</span>
      </div>
      <p className={styles.description}>{viewDescription}</p>
    </div>
  );
};

export default ViewIndicator;
