import React, { useState, useEffect } from 'react';
import PrivacyModal from '../components/PrivacyModal';
import SearchInput from '../components/SearchInput';
import ActionButtons from '../components/ActionButtons';
import './Home.css';

const Home: React.FC = () => {
  const [showPrivacyModal, setShowPrivacyModal] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    const hasAcceptedPrivacy = localStorage.getItem('nc-ask-privacy-accepted');
    console.log('Privacy check:', hasAcceptedPrivacy);

    // Temporarily always show the modal for testing
    setShowPrivacyModal(true);

    // Original logic (commented out for testing):
    // if (!hasAcceptedPrivacy) {
    //   setShowPrivacyModal(true);
    // }
  }, []);

  const handlePrivacyAccept = () => {
    localStorage.setItem('nc-ask-privacy-accepted', 'true');
    setShowPrivacyModal(false);
  };

  const handleReadPolicy = () => {
    window.open('/privacy-policy', '_blank');
  };

  const handleSearch = (query: string) => {
    setSearchQuery(query);
    // TODO: Implement search functionality
    console.log('Searching for:', query);
  };

  const handleFileUpload = (file: File) => {
    // TODO: Implement file upload functionality
    console.log('Uploading file:', file.name);
  };

  const handleVoiceInput = () => {
    // TODO: Implement voice input functionality
    console.log('Starting voice input');
  };

  return (
    <div className="home">
      <PrivacyModal
        isOpen={showPrivacyModal}
        onAccept={handlePrivacyAccept}
        onReadPolicy={handleReadPolicy}
      />

      <div className="home-content">
        <SearchInput
          value={searchQuery}
          onChange={setSearchQuery}
          onSearch={handleSearch}
          placeholder="Ask a question about autism resources..."
        />

        <ActionButtons
          onFileUpload={handleFileUpload}
          onVoiceInput={handleVoiceInput}
        />
      </div>
    </div>
  );
};

export default Home;