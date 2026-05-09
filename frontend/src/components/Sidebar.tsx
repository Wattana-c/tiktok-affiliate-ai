import { Link, useLocation } from 'react-router-dom';
import { Home, Layers, Clock, Settings } from 'lucide-react';

export default function Sidebar() {
  const location = useLocation();

  const isActive = (path: string) => location.pathname === path ? "bg-indigo-700 text-white" : "text-indigo-100 hover:bg-indigo-600";

  return (
    <div className="flex h-screen flex-col bg-indigo-800 w-64 text-white shrink-0">
      <div className="flex h-16 shrink-0 items-center px-6">
        <h1 className="text-xl font-bold tracking-tight">AI Affiliate Auto</h1>
      </div>
      <div className="flex flex-1 flex-col overflow-y-auto">
        <nav className="flex-1 space-y-1 px-4 py-4">
          <Link to="/" className={`group flex items-center px-2 py-2 text-sm font-medium rounded-md ${isActive('/')}`}>
            <Home className="mr-3 h-5 w-5 flex-shrink-0" />
            หน้าแรก (Dashboard)
          </Link>
          <Link to="/content" className={`group flex items-center px-2 py-2 text-sm font-medium rounded-md ${isActive('/content')}`}>
            <Layers className="mr-3 h-5 w-5 flex-shrink-0" />
            สร้างคอนเทนต์ (Content)
          </Link>
          <Link to="/queue" className={`group flex items-center px-2 py-2 text-sm font-medium rounded-md ${isActive('/queue')}`}>
            <Clock className="mr-3 h-5 w-5 flex-shrink-0" />
            คิวโพสต์ (Post Queue)
          </Link>
          <Link to="/settings" className={`group flex items-center px-2 py-2 text-sm font-medium rounded-md ${isActive('/settings')}`}>
            <Settings className="mr-3 h-5 w-5 flex-shrink-0" />
            ตั้งค่า (Settings)
          </Link>
        </nav>
      </div>
    </div>
  );
}
