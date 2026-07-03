import { Outlet } from 'react-router-dom';
import { Bell, User } from 'lucide-react';

export default function StaffLayout() {
  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 font-sans">
      <header className="bg-white border-b border-slate-200 sticky top-0 z-40 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-4">
              <span className="font-bold text-xl text-blue-600">TableWise Staff</span>
            </div>
            
            <div className="flex items-center gap-4">
              <button className="p-2 relative text-slate-500 hover:text-slate-900 transition-colors">
                <Bell size={20} />
              </button>
              <div className="h-8 w-8 rounded-full bg-slate-200 flex items-center justify-center text-slate-600">
                <User size={16} />
              </div>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Outlet />
      </main>
    </div>
  );
}
