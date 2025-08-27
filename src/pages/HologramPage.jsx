import React from 'react';
import './HologramPage.css';

const HologramPage = () => {
  return (
    <div className="holo-bg">
      <div className="holo-header">
        <h1>holoGokode</h1>
        <span className="holo-sub">Advanced 3D Interface</span>
        <div className="holo-mode-status">
          <span className="holo-mode">3D Mode</span>
          <span className="holo-online">Online</span>
        </div>
      </div>
      <div className="holo-main">
        <div className="holo-left">
          <div className="holo-card">
            <h2>3D Hologram Interface</h2>
            <p>Interactive AI assistant with advanced holographic visualization</p>
            <div className="holo-face-anim">
              {/* Animated SVG Face */}
              <svg width="220" height="220" viewBox="0 0 220 220">
                <circle cx="110" cy="110" r="90" fill="#22304a" stroke="#3fd2ff" strokeWidth="4" />
                <circle cx="85" cy="100" r="10" fill="#3fd2ff">
                  <animate attributeName="r" values="10;13;10" dur="1.2s" repeatCount="indefinite" />
                </circle>
                <circle cx="135" cy="100" r="10" fill="#3fd2ff">
                  <animate attributeName="r" values="10;13;10" dur="1.2s" repeatCount="indefinite" />
                </circle>
                <rect x="100" y="145" width="20" height="7" rx="3.5" fill="#3fd2ff">
                  <animate attributeName="width" values="20;28;20" dur="1.2s" repeatCount="indefinite" />
                </rect>
                <ellipse cx="110" cy="125" rx="22" ry="10" fill="none" stroke="#3fd2ff" strokeWidth="2" />
                <g>
                  <circle cx="110" cy="110" r="90" fill="none" stroke="#3fd2ff44" strokeWidth="2" />
                  <circle cx="110" cy="110" r="105" fill="none" stroke="#3fd2ff22" strokeWidth="1" />
                </g>
              </svg>
              <div className="holo-ready">Ready</div>
            </div>
            <div className="holo-btn-row">
              <button className="holo-btn neural">Neural Mode</button>
              <button className="holo-btn vision">Vision</button>
              <button className="holo-btn audio">Audio</button>
              <button className="holo-btn boost">Boost</button>
              <button className="holo-btn config">Configure</button>
              <button className="holo-btn reset">Reset</button>
            </div>
          </div>
        </div>
        <div className="holo-right">
          <div className="holo-card status">
            <h3>System Status</h3>
            <div className="holo-status-row">CPU Usage <span className="holo-bar cpu">63%</span></div>
            <div className="holo-status-row">Memory <span className="holo-bar memory">77%</span></div>
            <div className="holo-status-row">AI Confidence <span className="holo-bar ai">94%</span></div>
          </div>
          <div className="holo-card settings">
            <h3>Hologram Settings</h3>
            <div className="holo-settings-tabs">
              <span className="active">Visual</span>
              <span>Behavior</span>
            </div>
            <div className="holo-slider-row">
              <label>Intensity</label>
              <input type="range" min="0" max="100" value="75" readOnly />
              <span>75%</span>
            </div>
            <div className="holo-slider-row">
              <label>Particle Count</label>
              <input type="range" min="0" max="100" value="20" readOnly />
              <span>20 particles</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HologramPage;
