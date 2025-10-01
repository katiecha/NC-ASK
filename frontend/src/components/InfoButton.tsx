import React from 'react';
import { Link } from 'react-router-dom';
import './InfoButton.css';

const InfoButton: React.FC = () => {
  return (
    <Link to="/about" className="info-button" aria-label="About NC ASK">
      <img src="/info.svg" alt="Info" className="info-icon" />
    </Link>
  );
};

export default InfoButton;