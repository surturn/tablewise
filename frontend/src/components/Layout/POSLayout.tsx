import React from 'react';
import { Outlet, NavLink } from 'react-router-dom';
import { LayoutGrid, ClipboardList, Utensils, Settings, LogOut } from 'lucide-react';

export default function POSLayout() {
  // POS Layout strictly enforces light mode for maximum contrast and utility
  return (
    <div className="min-h-screen bg-slate-100 text-slate-900 font-sans flex overflow-hidden">
      
      {/* Left Sidebar Navigation */}
      <aside className="w-20 lg:w-64 bg-white border-r border-slate-200 flex flex-col items-center lg:items-start shadow-sm z-10">
        <div className="h-16 flex items-center justify-center lg:justify-start lg:px-6 w-full border-b border-slate-100">
          <span className="font-black text-xl text-blue-600 hidden lg:block">TableWise</span>
          <span className="font-black text-xl text-blue-600 lg:hidden">TW</span>
        </div>
        
        <nav className="flex-1 w-full py-4 space-y-2 px-3">
          <NavLink 
            to="/pos" 
            end
            className={({isActive}) => `flex items-center gap-3 p-3 rounded-lg transition-colors ${isActive ? 'bg-blue-50 text-blue-700 font-semibold' : 'text-slate-600 hover:bg-slate-50'}`}
          >
            <LayoutGrid size={24} />
            <span className="hidden lg:block">Terminal</span>
          </NavLink>
          <NavLink 
            to="/pos/tables" 
            className={({isActive}) => `flex items-center gap-3 p-3 rounded-lg transition-colors ${isActive ? 'bg-blue-50 text-blue-700 font-semibold' : 'text-slate-600 hover:bg-slate-50'}`}
          >
            <Utensils size={24} />
            <span className="hidden lg:block">Tables</span>
          </NavLink>
          <NavLink 
            to="/pos/orders" 
            className={({isActive}) => `flex items-center gap-3 p-3 rounded-lg transition-colors ${isActive ? 'bg-blue-50 text-blue-700 font-semibold' : 'text-slate-600 hover:bg-slate-50'}`}
          >
            <ClipboardList size={24} />
            <span className="hidden lg:block">Orders</span>
          </NavLink>
        </nav>

        <div className="p-4 w-full border-t border-slate-100 space-y-2">
          <button className="flex items-center gap-3 p-3 w-full rounded-lg text-slate-600 hover:bg-slate-50 transition-colors">
            <Settings size={24} />
            <span className="hidden lg:block">Settings</span>
          </button>
          <button className="flex items-center gap-3 p-3 w-full rounded-lg text-red-600 hover:bg-red-50 transition-colors">
            <LogOut size={24} />
            <span className="hidden lg:block">Logout</span>
          </button>
        </div>
      </aside>

      {/* Main Content Area (CSS Grid product catalog goes here via Outlet) */}
      <main className="flex-1 flex flex-col overflow-hidden relative">
        <Outlet />
      </main>

      {/* Right Sidebar - Order Ticket / Cart Summary (placeholder structure, actual content managed by POS pages) */}
      {/* 
        This is a structural placeholder. 
        In actual implementation, the Right Sidebar might be inside the Outlet page itself, 
        or we can pass children/slots if we want it global. 
        Usually for a POS, the right panel is part of the specific terminal page.
      */}
    </div>
  );
}
