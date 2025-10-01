import React from 'react';
import { CrisisResource } from '../services/api';
import './CrisisBanner.css';

interface CrisisBannerProps {
  resources: CrisisResource[];
}

const CrisisBanner: React.FC<CrisisBannerProps> = ({ resources }) => {
  return (
    <div className="crisis-banner" role="alert" aria-live="assertive">
      <div className="crisis-banner-content">
        <h2 className="crisis-banner-title">⚠️ Important Crisis Resources</h2>
        <p className="crisis-banner-message">
          If you or someone you know is in crisis, please reach out for immediate help:
        </p>

        <ul className="crisis-resources-list">
          {resources
            .sort((a, b) => a.priority - b.priority)
            .map((resource, index) => (
              <li key={index} className="crisis-resource-item">
                <strong>{resource.name}</strong>
                <div className="resource-phone">
                  <a href={`tel:${resource.phone.replace(/\D/g, '')}`}>
                    {resource.phone}
                  </a>
                </div>
                <p className="resource-description">{resource.description}</p>
                {resource.url && (
                  <a
                    href={resource.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="resource-link"
                  >
                    Learn more
                  </a>
                )}
              </li>
            ))}
        </ul>

        <p className="crisis-banner-footer">
          <strong>You are not alone. Help is available 24/7.</strong>
        </p>
      </div>
    </div>
  );
};

export default CrisisBanner;
