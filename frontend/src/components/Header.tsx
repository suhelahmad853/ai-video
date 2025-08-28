import React from 'react';
import { Link, useLocation } from 'react-router-dom';

const Header: React.FC = () => {
  const location = useLocation();

  const isActive = (path: string) => {
    return location.pathname === path ? 'active' : '';
  };

  return (
    <header className="header">
      <div className="container">
        <div className="header-content">
          <Link to="/" className="logo">
            AI Video Creator
          </Link>
          <nav>
            <ul className="nav-menu">
              <li>
                <Link to="/" className={`nav-link ${isActive('/')}`}>
                  Home
                </Link>
              </li>
              <li>
                <Link to="/process" className={`nav-link ${isActive('/process')}`}>
                  Process Video
                </Link>
              </li>
              <li>
                <Link to="/settings" className={`nav-link ${isActive('/settings')}`}>
                  Settings
                </Link>
              </li>
            </ul>
          </nav>
        </div>
      </div>
    </header>
  );
};

export default Header; 