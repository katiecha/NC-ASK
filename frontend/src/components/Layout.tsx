import React, { useState } from 'react';
import HamburgerMenu from './HamburgerMenu';
import Sidebar from './Sidebar';
import DarkModeToggle from './DarkModeToggle';
import './Layout.css';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  const toggleSidebar = () => {
    setIsSidebarOpen(!isSidebarOpen);
  };

  const closeSidebar = () => {
    setIsSidebarOpen(false);
  };

  return (
    <div className="layout">
      <div className="layout-header">
        <HamburgerMenu onClick={toggleSidebar} />
      </div>

      {/* Dark Mode Toggle - Top Right */}
      <DarkModeToggle />

      <Sidebar isOpen={isSidebarOpen} onClose={closeSidebar} />

      <main className="layout-main">
        {children}
      </main>

      {isSidebarOpen && <div className="sidebar-overlay" onClick={closeSidebar} />}
    </div>
  );
};

export default Layout;