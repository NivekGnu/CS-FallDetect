import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Index from './pages/Index.jsx';
import LiveVideo from './pages/LiveVideo.jsx';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Index />} />

        <Route path="/live-video" element={<LiveVideo />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
