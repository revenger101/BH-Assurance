import './App.css';
import Homepage from './pages/Homepage';
import Chat from './components/Chat';
import { useState } from 'react';

const App = () => {
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [isChatMinimized, setIsChatMinimized] = useState(false);

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


  return (
    <div className="App">
      <Homepage onOpenChat={handleOpenChat} />
      <Chat
        isOpen={isChatOpen}
        onClose={handleCloseChat}
        onMinimize={handleMinimizeChat}
        isMinimized={isChatMinimized}
      />
    </div>
  );
}

export default App;
