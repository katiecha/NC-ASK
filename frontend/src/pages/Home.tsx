import React, { useState, useEffect } from 'react';
import PrivacyModal from '../components/PrivacyModal';
import SearchInput from '../components/SearchInput';
import ActionButtons from '../components/ActionButtons';
import QueryResponse from '../components/QueryResponse';
import CrisisBanner from '../components/CrisisBanner';
import { queryKnowledgeBase, QueryResponse as QueryResponseType } from '../services/api';
import './Home.css';

const Home: React.FC = () => {
  const [showPrivacyModal, setShowPrivacyModal] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [response, setResponse] = useState<QueryResponseType | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const hasAcceptedPrivacy = localStorage.getItem('nc-ask-privacy-accepted');

    if (!hasAcceptedPrivacy) {
      setShowPrivacyModal(true);
    }
  }, []);

  const handlePrivacyAccept = () => {
    localStorage.setItem('nc-ask-privacy-accepted', 'true');
    setShowPrivacyModal(false);
  };

  const handleReadPolicy = () => {
    window.open('/privacy-policy', '_blank');
  };

  const handleSearch = async (query: string) => {
    setSearchQuery(query);
    setIsLoading(true);
    setError(null);

    try {
      const result = await queryKnowledgeBase(query);
      setResponse(result);
    } catch (err) {
      console.error('Search error:', err);
      setError(err instanceof Error ? err.message : 'An error occurred. Please try again.');
      setResponse(null);
    } finally {
      setIsLoading(false);
    }
  };

  const handleFileUpload = (file: File) => {
    // File upload not in MVP scope
    console.log('File upload:', file.name);
  };

  const handleVoiceInput = () => {
    // Voice input not in MVP scope
    console.log('Voice input');
  };

  return (
    <div className="home">
      <PrivacyModal
        isOpen={showPrivacyModal}
        onAccept={handlePrivacyAccept}
        onReadPolicy={handleReadPolicy}
      />

      {response?.crisis_detected && (
        <CrisisBanner resources={response.crisis_resources} />
      )}

      <div className="home-content">
        <SearchInput
          value={searchQuery}
          onChange={setSearchQuery}
          onSearch={handleSearch}
          placeholder="Ask a question about autism resources in North Carolina..."
          disabled={isLoading}
        />

        {isLoading && (
          <div className="loading-indicator">
            <p>Finding the best answer for you...</p>
          </div>
        )}

        {error && (
          <div className="error-message" role="alert">
            <p>{error}</p>
          </div>
        )}

        {response && !isLoading && (
          <QueryResponse
            response={response.response}
            citations={response.citations}
            crisisDetected={response.crisis_detected}
          />
        )}
      </div>
    </div>
  );
};

export default Home;