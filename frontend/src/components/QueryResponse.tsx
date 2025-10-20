import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import { Citation, CrisisResource } from '../services/api';
import './QueryResponse.css';

interface QueryResponseProps {
  response: string;
  citations: Citation[];
  crisisDetected: boolean;
  crisisResources?: CrisisResource[];
}

const QueryResponse: React.FC<QueryResponseProps> = ({ response, citations, crisisDetected, crisisResources }) => {
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);

  return (
    <div className={`query-response ${crisisDetected ? 'crisis-response' : ''}`} role="region" aria-label="Response">
      {crisisDetected && (
        <div className="crisis-alert">
          <div className="crisis-alert-header">
            <span className="crisis-title">Crisis Support Available</span>
            <button
              className="crisis-dropdown-toggle"
              onClick={() => setIsDropdownOpen(!isDropdownOpen)}
              aria-expanded={isDropdownOpen}
              aria-label={isDropdownOpen ? "Hide crisis resources" : "Show crisis resources"}
            >
              {isDropdownOpen ? '▼' : '▶'} Resources
            </button>
          </div>
          {isDropdownOpen && crisisResources && crisisResources.length > 0 && (
            <div className="crisis-resources-dropdown">
              {crisisResources.map((resource, index) => (
                <div key={index} className="crisis-resource-item">
                  <div className="resource-header">
                    <h4 className="resource-name">{resource.name}</h4>
                    <a
                      href={`tel:${resource.phone.replace(/\D/g, '')}`}
                      className="crisis-phone-link"
                    >
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
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      <div className="response-content">
        <div className="response-text">
          <ReactMarkdown>{response}</ReactMarkdown>
        </div>
      </div>

      {citations.length > 0 && (
        <div className="citations-section">
          <h3>Sources</h3>
          <ul className="citations-list">
            {citations.map((citation, index) => (
              <li key={index} className="citation-item">
                <strong>{citation.title}</strong>
                {citation.url && (
                  <>
                    {' - '}
                    <a
                      href={citation.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="citation-link"
                    >
                      View source
                    </a>
                  </>
                )}
                <span className="relevance-score">
                  {' '}(Relevance: {Math.round(citation.relevance_score * 100)}%)
                </span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default QueryResponse;
