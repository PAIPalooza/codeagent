import React, { useState, useEffect } from 'react';
import './StatusPanel.css';

const StatusPanel = ({ logs, downloadUrl, error, isGenerating, projectId }) => {
  const [streamingLogs, setStreamingLogs] = useState([]);

  useEffect(() => {
    if (projectId && isGenerating) {
      // Set up event source for streaming logs
      const eventSource = new EventSource(`http://localhost:8000/api/v1/projects/${projectId}/logs/stream`);
      
      eventSource.onmessage = (event) => {
        try {
          const logData = JSON.parse(event.data);
          if (logData.status) {
            // Final status message
            setStreamingLogs(prev => [...prev, { 
              message: `Generation ${logData.status}`, 
              level: 'info',
              timestamp: new Date().toISOString()
            }]);
          } else {
            // Regular log message
            setStreamingLogs(prev => [...prev, logData]);
          }
        } catch (e) {
          console.error('Error parsing streaming log:', e);
        }
      };

      eventSource.onerror = (error) => {
        console.error('EventSource failed:', error);
        eventSource.close();
      };

      return () => {
        eventSource.close();
      };
    }
  }, [projectId, isGenerating]);

  // Combine static logs with streaming logs
  const allLogs = [...(logs || []), ...streamingLogs];

  return (
    <div className="status-panel">
      <h3>Generation Status</h3>
      
      {error && (
        <div className="error-message">
          <span className="error-icon">❌</span>
          {error}
        </div>
      )}

      <div className="logs-container">
        {allLogs.length === 0 ? (
          <div className="no-logs">
            {isGenerating ? 'Starting generation...' : 'No logs yet'}
          </div>
        ) : (
          <ul className="logs-list">
            {allLogs.map((log, index) => (
              <li 
                key={log.id || index} 
                className={`log-entry log-${log.level || 'info'}`}
              >
                <span className="log-timestamp">
                  {new Date(log.created_at || log.timestamp || Date.now()).toLocaleTimeString()}
                </span>
                <span className="log-message">{log.message}</span>
                {log.context && (
                  <div className="log-context">
                    {Object.entries(log.context).map(([key, value]) => (
                      <span key={key} className="context-item">
                        {key}: {typeof value === 'object' ? JSON.stringify(value) : value}
                      </span>
                    ))}
                  </div>
                )}
              </li>
            ))}
          </ul>
        )}
      </div>

      {downloadUrl && (
        <div className="download-section">
          <div className="success-message">
            <span className="success-icon">✅</span>
            Generation completed successfully!
          </div>
          <a 
            href={downloadUrl} 
            className="download-btn"
            download
          >
            📥 Download Your App
          </a>
        </div>
      )}

      {isGenerating && (
        <div className="generating-indicator">
          <div className="spinner"></div>
          <span>Generating your app...</span>
        </div>
      )}
    </div>
  );
};

export default StatusPanel;