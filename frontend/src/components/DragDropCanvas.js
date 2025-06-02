import React, { useState, useRef, useCallback } from 'react';
import { DndProvider, useDrag, useDrop } from 'react-dnd';
import { HTML5Backend } from 'react-dnd-html5-backend';
import './DragDropCanvas.css';

const ItemTypes = {
  COMPONENT: 'component'
};

// Component palette items
const COMPONENT_TYPES = {
  BUTTON: 'button',
  INPUT: 'input',
  TEXT: 'text',
  IMAGE: 'image',
  CARD: 'card',
  LIST: 'list',
  FORM: 'form',
  NAVBAR: 'navbar',
  FOOTER: 'footer',
  SIDEBAR: 'sidebar'
};

// Draggable component from palette
function PaletteItem({ type, label, icon }) {
  const [{ isDragging }, drag] = useDrag(() => ({
    type: ItemTypes.COMPONENT,
    item: { type, label, isNew: true },
    collect: (monitor) => ({
      isDragging: monitor.isDragging()
    })
  }));

  return (
    <div
      ref={drag}
      className={`palette-item ${isDragging ? 'dragging' : ''}`}
      style={{ opacity: isDragging ? 0.5 : 1 }}
    >
      <div className="palette-icon">{icon}</div>
      <div className="palette-label">{label}</div>
    </div>
  );
}

// Draggable component on canvas
function CanvasComponent({ component, index, moveComponent, updateComponent, deleteComponent }) {
  const ref = useRef(null);
  
  const [{ isDragging }, drag] = useDrag({
    type: ItemTypes.COMPONENT,
    item: { index, type: component.type, isNew: false },
    collect: (monitor) => ({
      isDragging: monitor.isDragging()
    })
  });

  const [{ isOver }, drop] = useDrop({
    accept: ItemTypes.COMPONENT,
    hover: (draggedItem) => {
      if (draggedItem.isNew) return;
      if (draggedItem.index === index) return;
      
      moveComponent(draggedItem.index, index);
      draggedItem.index = index;
    },
    collect: (monitor) => ({
      isOver: monitor.isOver()
    })
  });

  drag(drop(ref));

  const handlePropertyChange = (property, value) => {
    updateComponent(index, { ...component, [property]: value });
  };

  const renderComponent = () => {
    const commonProps = {
      style: {
        opacity: isDragging ? 0.5 : 1,
        backgroundColor: isOver ? '#f0f8ff' : 'transparent'
      }
    };

    switch (component.type) {
      case COMPONENT_TYPES.BUTTON:
        return (
          <button 
            {...commonProps} 
            className="canvas-button"
            onClick={(e) => e.preventDefault()}
          >
            {component.text || 'Button'}
          </button>
        );
      case COMPONENT_TYPES.INPUT:
        return (
          <input 
            {...commonProps}
            className="canvas-input"
            type={component.inputType || 'text'}
            placeholder={component.placeholder || 'Enter text...'}
            value={component.value || ''}
            onChange={(e) => handlePropertyChange('value', e.target.value)}
          />
        );
      case COMPONENT_TYPES.TEXT:
        return (
          <div {...commonProps} className="canvas-text">
            {component.text || 'Sample Text'}
          </div>
        );
      case COMPONENT_TYPES.IMAGE:
        return (
          <img 
            {...commonProps}
            src={component.src || 'https://via.placeholder.com/150x100'}
            alt={component.alt || 'Placeholder'}
            className="canvas-image"
          />
        );
      case COMPONENT_TYPES.CARD:
        return (
          <div {...commonProps} className="canvas-card">
            <h3>{component.title || 'Card Title'}</h3>
            <p>{component.content || 'Card content goes here...'}</p>
          </div>
        );
      case COMPONENT_TYPES.LIST:
        return (
          <ul {...commonProps} className="canvas-list">
            {(component.items || ['Item 1', 'Item 2', 'Item 3']).map((item, i) => (
              <li key={i}>{item}</li>
            ))}
          </ul>
        );
      case COMPONENT_TYPES.FORM:
        return (
          <form {...commonProps} className="canvas-form">
            <div className="form-group">
              <label>Name:</label>
              <input type="text" placeholder="Enter name" />
            </div>
            <div className="form-group">
              <label>Email:</label>
              <input type="email" placeholder="Enter email" />
            </div>
            <button type="submit">Submit</button>
          </form>
        );
      case COMPONENT_TYPES.NAVBAR:
        return (
          <nav {...commonProps} className="canvas-navbar">
            <div className="nav-brand">{component.brand || 'Brand'}</div>
            <div className="nav-links">
              <a href="#home">Home</a>
              <a href="#about">About</a>
              <a href="#contact">Contact</a>
            </div>
          </nav>
        );
      case COMPONENT_TYPES.FOOTER:
        return (
          <footer {...commonProps} className="canvas-footer">
            <p>{component.text || '© 2024 Your App. All rights reserved.'}</p>
          </footer>
        );
      case COMPONENT_TYPES.SIDEBAR:
        return (
          <aside {...commonProps} className="canvas-sidebar">
            <ul>
              <li><a href="#dashboard">Dashboard</a></li>
              <li><a href="#profile">Profile</a></li>
              <li><a href="#settings">Settings</a></li>
            </ul>
          </aside>
        );
      default:
        return (
          <div {...commonProps} className="canvas-unknown">
            Unknown Component: {component.type}
          </div>
        );
    }
  };

  return (
    <div ref={ref} className="canvas-component-wrapper">
      <div className="component-controls">
        <button 
          className="control-btn delete-btn"
          onClick={() => deleteComponent(index)}
          title="Delete component"
        >
          ×
        </button>
      </div>
      {renderComponent()}
    </div>
  );
}

// Properties panel for selected component
function PropertiesPanel({ selectedComponent, onUpdate }) {
  if (!selectedComponent) {
    return (
      <div className="properties-panel">
        <h3>Properties</h3>
        <p>Select a component to edit its properties</p>
      </div>
    );
  }

  const handleChange = (property, value) => {
    onUpdate({ ...selectedComponent.component, [property]: value });
  };

  const renderProperties = () => {
    const { type } = selectedComponent.component;
    
    switch (type) {
      case COMPONENT_TYPES.BUTTON:
      case COMPONENT_TYPES.TEXT:
        return (
          <div className="property-group">
            <label>Text:</label>
            <input
              type="text"
              value={selectedComponent.component.text || ''}
              onChange={(e) => handleChange('text', e.target.value)}
            />
          </div>
        );
      case COMPONENT_TYPES.INPUT:
        return (
          <>
            <div className="property-group">
              <label>Type:</label>
              <select
                value={selectedComponent.component.inputType || 'text'}
                onChange={(e) => handleChange('inputType', e.target.value)}
              >
                <option value="text">Text</option>
                <option value="email">Email</option>
                <option value="password">Password</option>
                <option value="number">Number</option>
              </select>
            </div>
            <div className="property-group">
              <label>Placeholder:</label>
              <input
                type="text"
                value={selectedComponent.component.placeholder || ''}
                onChange={(e) => handleChange('placeholder', e.target.value)}
              />
            </div>
          </>
        );
      case COMPONENT_TYPES.IMAGE:
        return (
          <>
            <div className="property-group">
              <label>Image URL:</label>
              <input
                type="text"
                value={selectedComponent.component.src || ''}
                onChange={(e) => handleChange('src', e.target.value)}
              />
            </div>
            <div className="property-group">
              <label>Alt Text:</label>
              <input
                type="text"
                value={selectedComponent.component.alt || ''}
                onChange={(e) => handleChange('alt', e.target.value)}
              />
            </div>
          </>
        );
      case COMPONENT_TYPES.CARD:
        return (
          <>
            <div className="property-group">
              <label>Title:</label>
              <input
                type="text"
                value={selectedComponent.component.title || ''}
                onChange={(e) => handleChange('title', e.target.value)}
              />
            </div>
            <div className="property-group">
              <label>Content:</label>
              <textarea
                value={selectedComponent.component.content || ''}
                onChange={(e) => handleChange('content', e.target.value)}
                rows={3}
              />
            </div>
          </>
        );
      default:
        return <p>No properties available for this component type.</p>;
    }
  };

  return (
    <div className="properties-panel">
      <h3>Properties</h3>
      <div className="component-type">
        Type: {selectedComponent.component.type}
      </div>
      {renderProperties()}
    </div>
  );
}

// Main canvas area
function Canvas({ components, setComponents, onComponentSelect }) {
  const [{ isOver }, drop] = useDrop(() => ({
    accept: ItemTypes.COMPONENT,
    drop: (item) => {
      if (item.isNew) {
        const newComponent = {
          id: Date.now(),
          type: item.type,
          ...getDefaultProps(item.type)
        };
        setComponents(prev => [...prev, newComponent]);
      }
    },
    collect: (monitor) => ({
      isOver: monitor.isOver()
    })
  }));

  const moveComponent = useCallback((dragIndex, hoverIndex) => {
    setComponents(prev => {
      const newComponents = [...prev];
      const draggedComponent = newComponents[dragIndex];
      newComponents.splice(dragIndex, 1);
      newComponents.splice(hoverIndex, 0, draggedComponent);
      return newComponents;
    });
  }, [setComponents]);

  const updateComponent = useCallback((index, updatedComponent) => {
    setComponents(prev => {
      const newComponents = [...prev];
      newComponents[index] = updatedComponent;
      return newComponents;
    });
  }, [setComponents]);

  const deleteComponent = useCallback((index) => {
    setComponents(prev => prev.filter((_, i) => i !== index));
  }, [setComponents]);

  return (
    <div 
      ref={drop}
      className={`canvas ${isOver ? 'canvas-over' : ''}`}
      style={{ backgroundColor: isOver ? '#f0f8ff' : '#ffffff' }}
    >
      {components.length === 0 ? (
        <div className="canvas-empty">
          <p>Drag components here to start building your UI</p>
        </div>
      ) : (
        components.map((component, index) => (
          <div
            key={component.id}
            onClick={() => onComponentSelect({ component, index })}
            className="canvas-item"
          >
            <CanvasComponent
              component={component}
              index={index}
              moveComponent={moveComponent}
              updateComponent={updateComponent}
              deleteComponent={deleteComponent}
            />
          </div>
        ))
      )}
    </div>
  );
}

// Get default properties for component type
function getDefaultProps(type) {
  switch (type) {
    case COMPONENT_TYPES.BUTTON:
      return { text: 'Button' };
    case COMPONENT_TYPES.INPUT:
      return { placeholder: 'Enter text...', inputType: 'text' };
    case COMPONENT_TYPES.TEXT:
      return { text: 'Sample Text' };
    case COMPONENT_TYPES.IMAGE:
      return { src: 'https://via.placeholder.com/150x100', alt: 'Placeholder' };
    case COMPONENT_TYPES.CARD:
      return { title: 'Card Title', content: 'Card content goes here...' };
    case COMPONENT_TYPES.LIST:
      return { items: ['Item 1', 'Item 2', 'Item 3'] };
    case COMPONENT_TYPES.NAVBAR:
      return { brand: 'Brand' };
    case COMPONENT_TYPES.FOOTER:
      return { text: '© 2024 Your App. All rights reserved.' };
    default:
      return {};
  }
}

// Main drag-drop canvas component
export default function DragDropCanvas({ onSave, initialLayout }) {
  const [components, setComponents] = useState(initialLayout || []);
  const [selectedComponent, setSelectedComponent] = useState(null);

  const handleSave = () => {
    const layout = {
      components,
      timestamp: new Date().toISOString()
    };
    onSave(layout);
  };

  const handleClear = () => {
    setComponents([]);
    setSelectedComponent(null);
  };

  const handlePropertiesUpdate = (updatedComponent) => {
    if (selectedComponent) {
      const newComponents = [...components];
      newComponents[selectedComponent.index] = updatedComponent;
      setComponents(newComponents);
      setSelectedComponent({
        ...selectedComponent,
        component: updatedComponent
      });
    }
  };

  return (
    <DndProvider backend={HTML5Backend}>
      <div className="drag-drop-canvas">
        <div className="canvas-header">
          <h2>Visual UI Builder</h2>
          <div className="canvas-actions">
            <button onClick={handleClear} className="btn btn-secondary">
              Clear Canvas
            </button>
            <button onClick={handleSave} className="btn btn-primary">
              Save Layout
            </button>
          </div>
        </div>
        
        <div className="canvas-content">
          <div className="component-palette">
            <h3>Components</h3>
            <div className="palette-grid">
              <PaletteItem type={COMPONENT_TYPES.BUTTON} label="Button" icon="🔘" />
              <PaletteItem type={COMPONENT_TYPES.INPUT} label="Input" icon="📝" />
              <PaletteItem type={COMPONENT_TYPES.TEXT} label="Text" icon="📄" />
              <PaletteItem type={COMPONENT_TYPES.IMAGE} label="Image" icon="🖼️" />
              <PaletteItem type={COMPONENT_TYPES.CARD} label="Card" icon="🃏" />
              <PaletteItem type={COMPONENT_TYPES.LIST} label="List" icon="📋" />
              <PaletteItem type={COMPONENT_TYPES.FORM} label="Form" icon="📊" />
              <PaletteItem type={COMPONENT_TYPES.NAVBAR} label="Navbar" icon="🧭" />
              <PaletteItem type={COMPONENT_TYPES.FOOTER} label="Footer" icon="⬇️" />
              <PaletteItem type={COMPONENT_TYPES.SIDEBAR} label="Sidebar" icon="📌" />
            </div>
          </div>
          
          <div className="canvas-area">
            <Canvas 
              components={components}
              setComponents={setComponents}
              onComponentSelect={setSelectedComponent}
            />
          </div>
          
          <div className="properties-area">
            <PropertiesPanel
              selectedComponent={selectedComponent}
              onUpdate={handlePropertiesUpdate}
            />
          </div>
        </div>
      </div>
    </DndProvider>
  );
}