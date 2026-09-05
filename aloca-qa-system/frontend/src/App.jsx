import React, { useState, useEffect } from 'react';
import './index.css';
import Dashboard from './pages/Dashboard';
import TestCases from './pages/TestCases';
import Defects from './pages/Defects';
import Reports from './pages/Reports';
import Search from './pages/Search';

export default function App() {
  const [currentPage, setCurrentPage] = useState('dashboard');
  const [loading, setLoading] = useState(false);

  const menuItems = [
    { id: 'dashboard', label: 'Dashboard', icon: '📊' },
    { id: 'test-cases', label: 'Test Cases', icon: '✓' },
    { id: 'defects', label: 'Defects', icon: '⚠️' },
    { id: 'reports', label: 'Reports', icon: '📄' },
    { id: 'search', label: 'Search', icon: '🔎' },
  ];

  const getPageContent = () => {
    if (loading) {
      return (
        <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
          <div className="spinner"></div>
        </div>
      );
    }

    switch (currentPage) {
      case 'dashboard':
        return <Dashboard />;
      case 'test-cases':
        return <TestCases />;
      case 'defects':
        return <Defects />;
      case 'reports':
        return <Reports />;
      case 'search':
        return <Search />;
      default:
        return <Dashboard />;
    }
  };

  const getPageTitle = () => {
    return menuItems.find(item => item.id === currentPage)?.label || 'Dashboard';
  };

  return (
    <div className="app-container">
      <aside className="sidebar">
        <div className="sidebar-header">
          <div className="sidebar-logo">
            <div className="sidebar-logo-icon">📱</div>
            <span>ALOCA+</span>
          </div>
        </div>
        <nav>
          <ul className="sidebar-nav">
            {menuItems.map(item => (
              <li key={item.id}>
                <a
                  href={`#${item.id}`}
                  className={currentPage === item.id ? 'active' : ''}
                  onClick={(e) => {
                    e.preventDefault();
                    setCurrentPage(item.id);
                  }}
                >
                  <span>{item.icon}</span>
                  <span>{item.label}</span>
                </a>
              </li>
            ))}
          </ul>
        </nav>
      </aside>

      <div className="main-content">
        <header className="header">
          <h1 className="header-title">{getPageTitle()}</h1>
          <div className="header-actions">
            <div style={{ fontSize: '14px', color: '#6b7280' }}>
              Eli Lilly QA System
            </div>
          </div>
        </header>

        <main className="content">
          {getPageContent()}
        </main>
      </div>
    </div>
  );
}
