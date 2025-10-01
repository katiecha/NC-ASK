import React from 'react';
import { Link } from 'react-router-dom';
import './Sidebar.css';

interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
}

const Sidebar: React.FC<SidebarProps> = ({ isOpen, onClose }) => {
  return (
    <aside className={`sidebar ${isOpen ? 'sidebar-open' : ''}`}>
      <nav className="sidebar-nav">
        <Link to="/" className="sidebar-link" onClick={onClose}>
          Home
        </Link>
        <Link to="/about" className="sidebar-link" onClick={onClose}>
          About
        </Link>
      </nav>
    </aside>
  );
};

export default Sidebar;