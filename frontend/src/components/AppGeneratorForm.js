import React, { useState } from 'react';
import './AppGeneratorForm.css';

const AppGeneratorForm = ({ onGenerate, onRecall }) => {
  const [formData, setFormData] = useState({
    project_name: '',
    description: '',
    features: '',
    tech_stack: 'React + FastAPI + PostgreSQL',
    styling: 'TailwindCSS'
  });

  const [isGenerating, setIsGenerating] = useState(false);

  const techStackOptions = [
    'React + FastAPI + PostgreSQL',
    'Vue + Node.js + MongoDB',
    'Next.js + Django + MySQL'
  ];

  const stylingOptions = [
    'TailwindCSS',
    'Bootstrap',
    'Plain CSS'
  ];

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.project_name.trim() || !formData.description.trim() || !formData.features.trim()) {
      alert('Please fill in all required fields');
      return;
    }

    setIsGenerating(true);
    
    try {
      // Convert features string to array
      const featuresArray = formData.features
        .split(',')
        .map(feature => feature.trim())
        .filter(feature => feature.length > 0);

      const payload = {
        ...formData,
        features: featuresArray
      };

      await onGenerate(payload);
    } catch (error) {
      console.error('Error generating app:', error);
    } finally {
      setIsGenerating(false);
    }
  };

  const handleRecall = async () => {
    try {
      await onRecall();
    } catch (error) {
      console.error('Error recalling last app:', error);
    }
  };

  return (
    <div className="app-generator-form">
      <h2>AI App Generator</h2>
      <form onSubmit={handleSubmit} className="form">
        <div className="form-group">
          <label htmlFor="project_name">
            Project Name <span className="required">*</span>
          </label>
          <input
            type="text"
            id="project_name"
            name="project_name"
            value={formData.project_name}
            onChange={handleInputChange}
            placeholder="e.g., MyAwesomeApp"
            className="form-input"
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="description">
            Description <span className="required">*</span>
          </label>
          <textarea
            id="description"
            name="description"
            value={formData.description}
            onChange={handleInputChange}
            placeholder="Describe what your app should do..."
            className="form-textarea"
            rows="3"
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="features">
            Features <span className="required">*</span>
          </label>
          <textarea
            id="features"
            name="features"
            value={formData.features}
            onChange={handleInputChange}
            placeholder="Enter features separated by commas (e.g., User authentication, Task management, Dashboard)"
            className="form-textarea"
            rows="3"
            required
          />
          <small className="form-help">Separate multiple features with commas</small>
        </div>

        <div className="form-row">
          <div className="form-group">
            <label htmlFor="tech_stack">Tech Stack</label>
            <select
              id="tech_stack"
              name="tech_stack"
              value={formData.tech_stack}
              onChange={handleInputChange}
              className="form-select"
            >
              {techStackOptions.map(option => (
                <option key={option} value={option}>
                  {option}
                </option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="styling">Styling Framework</label>
            <select
              id="styling"
              name="styling"
              value={formData.styling}
              onChange={handleInputChange}
              className="form-select"
            >
              {stylingOptions.map(option => (
                <option key={option} value={option}>
                  {option}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div className="form-actions">
          <button
            type="submit"
            className="btn btn-primary"
            disabled={isGenerating}
          >
            {isGenerating ? 'Generating...' : 'Generate App'}
          </button>
          
          <button
            type="button"
            onClick={handleRecall}
            className="btn btn-secondary"
            disabled={isGenerating}
          >
            Recall Last App
          </button>
        </div>
      </form>
    </div>
  );
};

export default AppGeneratorForm;