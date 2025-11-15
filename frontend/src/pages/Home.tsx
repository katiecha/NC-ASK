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

  // --- Export helpers ---
  const filenameForExport = () => {
    const now = new Date();
    return `nc-ask-transcript-${now.toISOString().slice(0,19).replace(/[:T]/g,'-')}.md`;
  };

  const stripHtml = (html: string) => {
    const tmp = document.createElement('div');
    tmp.innerHTML = html;
    return tmp.textContent || tmp.innerText || '';
  };

  const buildMarkdownFromMessages = (msgs: Message[], view?: string) => {
    const lines: string[] = [];
    lines.push(`# NC ASK Transcript`);
    lines.push(`- View: ${view || 'unspecified'}`);
    lines.push(`- Exported: ${new Date().toLocaleString()}`);
    lines.push('');
    for (const m of msgs) {
      const who = m.type === 'user' ? 'User' : 'Assistant';
      // try to interpret id as timestamp if possible
      let timeStr = '';
      const n = Number(m.id);
      if (!Number.isNaN(n)) {
        timeStr = ` — ${new Date(n).toLocaleString()}`;
      }
      lines.push(`## ${who}${timeStr}`);
      lines.push('');
      if (m.type === 'user') {
        lines.push(m.content);
        lines.push('');
      } else {
        const assistantText = typeof m.content === 'string' ? m.content : (m.response?.response ?? '');
        lines.push(stripHtml(String(assistantText)));
        lines.push('');
        if (m.response?.citations && m.response.citations.length > 0) {
          lines.push('**Citations**:');
          for (const c of m.response.citations) {
            if (typeof c === 'string') {
              lines.push(`- ${c}`);
            } else {
              const title = (c as any).title ?? (c as any).text ?? 'Source';
              const url = (c as any).url ?? '';
              lines.push(url ? `- [${title}](${url})` : `- ${title}`);
            }
          }
          lines.push('');
        }
      }
      lines.push('---');
      lines.push('');
    }
    return lines.join('\n');
  };

  const downloadTextFile = (filename: string, content: string, mime = 'text/markdown') => {
    const blob = new Blob([content], { type: mime + ';charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
  };

  const handleExportMarkdown = () => {
    if (!messages || messages.length === 0) {
      // small UX: alert, can be replaced with nicer toast
      alert('No messages to export.');
      return;
    }
    const md = buildMarkdownFromMessages(messages, selectedView ?? 'unspecified');
    const filename = filenameForExport();
    downloadTextFile(filename, md, 'text/markdown');
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
        <div className="top-controls">
          {selectedView && <ViewIndicator view={selectedView} />}
          <button className="export-btn" onClick={handleExportMarkdown} title="Download chat transcript" aria-label="Download chat transcript">
            {/* Download icon (arrow into a tray) */}
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
              <polyline points="7 10 12 15 17 10" />
              <line x1="12" y1="15" x2="12" y2="3" />
            </svg>
          </button>
        </div>

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