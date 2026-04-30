import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard';
import ContentPreview from './pages/ContentPreview';
import PostQueue from './pages/PostQueue';
import Settings from './pages/Settings';

function App() {
  return (
    <Router>
      <div className="flex h-screen overflow-hidden bg-gray-100">
        <Sidebar />
        <main className="flex-1 overflow-y-auto">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/content" element={<ContentPreview />} />
            <Route path="/queue" element={<PostQueue />} />
            <Route path="/settings" element={<Settings />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
