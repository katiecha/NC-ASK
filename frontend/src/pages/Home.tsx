import React, { useState, useEffect, useRef } from 'react';
import PrivacyModal from '../components/PrivacyModal';
import SearchInput from '../components/SearchInput';
import QueryResponse from '../components/QueryResponse';
import ViewSelector from '../components/ViewSelector';
import ViewIndicator from '../components/ViewIndicator';
import { useView } from '../contexts/ViewContext';
import { queryKnowledgeBase, QueryResponse as QueryResponseType } from '../services/api';
import './Home.css';

interface Message {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  response?: QueryResponseType;
}

const Home: React.FC = () => {
  const { selectedView, setSelectedView } = useView();
  const [showPrivacyModal, setShowPrivacyModal] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // commenting out for demo purposes
    // const hasAcceptedPrivacy = localStorage.getItem('nc-ask-privacy-accepted');

    setShowPrivacyModal(true);
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handlePrivacyAccept = () => {
    // localStorage.setItem('nc-ask-privacy-accepted', 'true');
    setShowPrivacyModal(false);
  };

  const handleReadPolicy = () => {
    window.open('/privacy-policy', '_blank');
  };

  const handleSearch = async (query: string) => {
    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: query
    };

    setMessages(prev => [...prev, userMessage]);
    setSearchQuery('');
    setIsLoading(true);
    setError(null);

    try {
      // Pass the selected view to the API (defaults to 'patient' if not selected)
      const result = await queryKnowledgeBase(query, selectedView || 'patient');
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: result.response,
        response: result
      };
      setMessages(prev => [...prev, assistantMessage]);
    } catch (err) {
      console.error('Search error:', err);
      setError(err instanceof Error ? err.message : 'An error occurred. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="home">
      <ViewSelector
        isOpen={selectedView === null}
        onSelectView={setSelectedView}
      />

      <PrivacyModal
        isOpen={showPrivacyModal && selectedView !== null}
        onAccept={handlePrivacyAccept}
        onReadPolicy={handleReadPolicy}
      />

      <div className="home-content">
        {selectedView && <ViewIndicator view={selectedView} />}

        <div className="messages-container">
          {messages.length === 0 && (
            <div className="welcome-message">
              <h2>Welcome to NC Ask</h2>
              <p>Ask any question about autism resources in North Carolina</p>
            </div>
          )}

          {messages.map((message) => (
            <div key={message.id} className={`message ${message.type}`}>
              {message.type === 'user' ? (
                <div className="user-message">
                  <p>{message.content}</p>
                </div>
              ) : (
                <QueryResponse
                  response={message.response!.response}
                  citations={message.response!.citations}
                  crisisDetected={message.response!.crisis_detected}
                  crisisResources={message.response!.crisis_resources}
                />
              )}
            </div>
          ))}

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

          <div ref={messagesEndRef} />
        </div>

        <div className="input-container">
          <SearchInput
            value={searchQuery}
            onChange={setSearchQuery}
            onSearch={handleSearch}
            placeholder="Ask a question about autism resources in North Carolina..."
            disabled={isLoading}
          />
        </div>
      </div>
    </div>
  );
};

export default Home;