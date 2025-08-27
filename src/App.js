import './App.css';
import Homepage from './pages/Homepage';
import Login from './pages/Login';
import Signup from './pages/Signup';
import Quote from './pages/Quote';
import Chat from './components/Chat';
import { useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';

const App = () => {
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [isChatMinimized, setIsChatMinimized] = useState(false);
  const [isHologramActive, setIsHologramActive] = useState(false);

  const handleOpenChat = () => {
    setIsChatOpen(true);
    setIsChatMinimized(false);
  };

  const handleCloseChat = () => {
    setIsChatOpen(false);
    setIsChatMinimized(false);
  };

  const handleMinimizeChat = () => {
    setIsChatMinimized(!isChatMinimized);
  };

  const handleActivateHologram = () => {
    setIsHologramActive(true);
  };

  const handleDeactivateHologram = () => {
    setIsHologramActive(false);
  };

  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/" element={
            <>
              <Homepage
                onOpenChat={handleOpenChat}
                onActivateHologram={handleActivateHologram}
                isHologramActive={isHologramActive}
                onDeactivateHologram={handleDeactivateHologram}
              />
              {!isHologramActive && (
                <Chat
                  isOpen={isChatOpen}
                  onClose={handleCloseChat}
                  onMinimize={handleMinimizeChat}
                  isMinimized={isChatMinimized}
                />
              )}
            </>
          } />
          <Route path="/login" element={<Login />} />
          <Route path="/signup" element={<Signup />} />
          <Route path="/quote" element={<Quote />} />
        </Routes>
      </div>
    </Router>
  );
};

export default App;