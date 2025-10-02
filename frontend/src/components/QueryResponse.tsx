import React from 'react';
import ReactMarkdown from 'react-markdown';
import { Citation } from '../services/api';
import './QueryResponse.css';

interface QueryResponseProps {
  response: string;
  citations: Citation[];
  crisisDetected: boolean;
}

const QueryResponse: React.FC<QueryResponseProps> = ({ response, citations, crisisDetected }) => {
  return (
    <div className="query-response" role="region" aria-label="Response">
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
