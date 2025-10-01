import React from 'react';
import './HamburgerMenu.css';

interface HamburgerMenuProps {
  onClick: () => void;
}

const HamburgerMenu: React.FC<HamburgerMenuProps> = ({ onClick }) => {
  return (
    <button className="hamburger-menu" onClick={onClick} aria-label="Open menu">
      <img src="/menu.svg" alt="Menu" />
    </button>
  );
};

export default HamburgerMenu;