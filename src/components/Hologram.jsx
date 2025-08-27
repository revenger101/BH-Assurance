import React from 'react';
import './Hologram.css';

const Hologram = ({ onClose }) => {
  return (
    <div className="hologram-overlay">
      <div className="hologram-modal" style={{ justifyContent: 'center', alignItems: 'center', minWidth: 'unset', flexDirection: 'column' }}>
        <div className="hologram-header" style={{ position: 'static', textAlign: 'center', marginBottom: '24px' }}>
          <h2>holoGokode</h2>
          <span className="hologram-subtitle">Advanced 3D Interface</span>
        </div>
        <div className="hologram-face" style={{ marginBottom: '0' }}>
          {/* Simple animated SVG face */}
          <svg width="320" height="320" viewBox="0 0 200 200">
            <circle cx="100" cy="100" r="80" fill="#22304a" stroke="#3fd2ff" strokeWidth="4" />
            <circle cx="80" cy="90" r="8" fill="#3fd2ff" />
            <circle cx="120" cy="90" r="8" fill="#3fd2ff" />
            <rect x="90" y="130" width="20" height="6" rx="3" fill="#3fd2ff" />
            <ellipse cx="100" cy="115" rx="18" ry="8" fill="none" stroke="#3fd2ff" strokeWidth="2" />
          </svg>
          <div className="hologram-status">Ready</div>
        </div>
        <button className="hologram-close" onClick={onClose}>×</button>
      </div>
    </div>
  );
};

export default Hologram;
