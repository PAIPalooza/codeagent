import React, { useState, useEffect } from 'react';
import AppGeneratorForm from './components/AppGeneratorForm';
import StatusPanel from './components/StatusPanel';
import DragDropCanvas from './components/DragDropCanvas';
import './App.css';

function App() {
  const [apiStatus, setApiStatus] = useState('checking...');
  const [currentView, setCurrentView] = useState('home'); // 'home', 'generator', or 'canvas'
  const [logs, setLogs] = useState([]);
  const [downloadUrl, setDownloadUrl] = useState('');
  const [error, setError] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [projectId, setProjectId] = useState('');

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

  const handleGenerate = async (appSpec) => {
    setError('');
    setLogs([]);
    setDownloadUrl('');
    setIsGenerating(true);
    
    try {
      const response = await fetch('http://localhost:8000/api/v1/generate-app', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(appSpec),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Generation failed');
      }

      const data = await response.json();
      setProjectId(data.project_id);
      setLogs(data.logs || []);
      
      // Poll for completion
      pollProjectStatus(data.project_id);
      
    } catch (err) {
      setError(err.message);
      setIsGenerating(false);
    }
  };

  const pollProjectStatus = async (projectId) => {
    const maxAttempts = 60; // 5 minutes max
    let attempts = 0;
    
    const poll = async () => {
      try {
        const response = await fetch(`http://localhost:8000/api/v1/projects/${projectId}`);
        const project = await response.json();
        
        if (project.status === 'completed') {
          setIsGenerating(false);
          setDownloadUrl(project.download_url);
        } else if (project.status === 'failed') {
          setIsGenerating(false);
          setError('Generation failed. Check logs for details.');
        } else if (attempts < maxAttempts) {
          attempts++;
          setTimeout(poll, 5000); // Poll every 5 seconds
        } else {
          setIsGenerating(false);
          setError('Generation timed out');
        }
      } catch (err) {
        console.error('Error polling project status:', err);
        if (attempts < maxAttempts) {
          attempts++;
          setTimeout(poll, 5000);
        } else {
          setIsGenerating(false);
          setError('Lost connection to server');
        }
      }
    };
    
    poll();
  };

  const handleRecall = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/recall-last-app');
      if (response.ok) {
        const data = await response.json();
        // Pre-fill form would happen here
        console.log('Recalled app spec:', data);
        alert('Recalled last app spec (check console for details)');
      } else {
        alert('No previous app found');
      }
    } catch (err) {
      console.error('Error recalling app:', err);
      alert('Error recalling last app');
    }
  };

  const showGenerator = () => {
    setCurrentView('generator');
    setError('');
    setLogs([]);
    setDownloadUrl('');
    setIsGenerating(false);
    setProjectId('');
  };

  const handleCanvasSave = async (layout) => {
    try {
      setIsGenerating(true);
      setError('');
      
      const response = await fetch('http://localhost:8000/api/v1/canvas/generate-code', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: 'Visual UI Project',
          description: 'Project created with visual builder',
          canvas_layout: layout,
          tech_stack: 'React + FastAPI + PostgreSQL',
          styling: 'Tailwind CSS'
        }),
      });

      if (response.ok) {
        const result = await response.json();
        setIsGenerating(false);
        
        // Show generated code in a modal or new view
        console.log('Generated files:', result.files);
        alert(`Code generated successfully! ${result.components_count} components processed. Check console for code.`);
        
        // You could set a state here to show the generated code
        // setGeneratedCode(result.files);
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to generate code from canvas');
        setIsGenerating(false);
      }
    } catch (err) {
      console.error('Error generating code from canvas:', err);
      setError('Error generating code from canvas');
      setIsGenerating(false);
    }
  };

  if (currentView === 'canvas') {
    return (
      <div className="app">
        <header className="app-header">
          <h1>Visual UI Builder</h1>
          <button 
            onClick={() => setCurrentView('home')} 
            className="btn btn-secondary"
            style={{ marginTop: '1rem' }}
          >
            ← Back to Home
          </button>
        </header>
        
        <main className="app-main" style={{ padding: 0, height: 'calc(100vh - 120px)' }}>
          <DragDropCanvas onSave={handleCanvasSave} />
          {isGenerating && (
            <div style={{
              position: 'fixed',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              background: 'rgba(0,0,0,0.5)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              zIndex: 1000
            }}>
              <div style={{
                background: 'white',
                padding: '2rem',
                borderRadius: '8px',
                textAlign: 'center'
              }}>
                <div>Generating code from canvas...</div>
                <div style={{ margin: '1rem 0' }}>🔄</div>
              </div>
            </div>
          )}
          {error && (
            <div style={{
              position: 'fixed',
              top: '20px',
              right: '20px',
              background: '#f8d7da',
              color: '#721c24',
              padding: '1rem',
              borderRadius: '4px',
              border: '1px solid #f1aeb5',
              maxWidth: '300px',
              zIndex: 1001
            }}>
              <strong>Error:</strong> {error}
              <button 
                onClick={() => setError('')}
                style={{
                  float: 'right',
                  background: 'none',
                  border: 'none',
                  fontSize: '1.2rem',
                  cursor: 'pointer',
                  marginLeft: '10px'
                }}
              >
                ×
              </button>
            </div>
          )}
        </main>
      </div>
    );
  }

  if (currentView === 'generator') {
    return (
      <div className="app">
        <header className="app-header">
          <h1>AI App Generator</h1>
          <button 
            onClick={() => setCurrentView('home')} 
            className="btn btn-secondary"
            style={{ marginTop: '1rem' }}
          >
            ← Back to Home
          </button>
        </header>
        
        <main className="app-main">
          <AppGeneratorForm 
            onGenerate={handleGenerate}
            onRecall={handleRecall}
          />
          <StatusPanel 
            logs={logs}
            downloadUrl={downloadUrl}
            error={error}
            isGenerating={isGenerating}
            projectId={projectId}
          />
        </main>
      </div>
    );
  }

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
            <button className="btn btn-primary" onClick={showGenerator}>
              New Project
            </button>
            <button className="btn btn-primary" onClick={() => setCurrentView('canvas')}>
              Visual Builder
            </button>
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
