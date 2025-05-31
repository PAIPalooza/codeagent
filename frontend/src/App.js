import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [apiStatus, setApiStatus] = useState('checking...');

  useEffect(() => {
    // Check if backend API is running
    const checkApiStatus = async () => {
      try {
        const response = await fetch('http://localhost:8000/health');
        const data = await response.json();
        setApiStatus(data.status === 'healthy' ? '✅ Running' : '❌ Not healthy');
      } catch (error) {
        setApiStatus('❌ Not reachable');
        console.error('Error connecting to API:', error);
      }
    };

    checkApiStatus();
  }, []);

  return (
    <div className="app">
      <header className="app-header">
        <h1>Welcome to CodeAgent</h1>
        <p>Your AI-powered development environment</p>
      </header>
      
      <main className="app-main">
        <section className="status-section">
          <h2>System Status</h2>
          <div className="status-item">
            <span className="status-label">Frontend:</span>
            <span className="status-value">✅ Running</span>
          </div>
          <div className="status-item">
            <span className="status-label">Backend API:</span>
            <span className="status-value">{apiStatus}</span>
          </div>
        </section>

        <section className="cta-section">
          <h2>Get Started</h2>
          <p>Create a new project or explore the documentation to get started.</p>
          <div className="button-group">
            <button className="btn btn-primary">New Project</button>
            <button className="btn btn-secondary">Documentation</button>
          </div>
        </section>
      </main>

      <footer className="app-footer">
        <p>© {new Date().getFullYear()} CodeAgent. All rights reserved.</p>
      </footer>
    </div>
  );
}

export default App;
