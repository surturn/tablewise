import React, { useState } from 'react';
import { Outlet, Link, useNavigate, useLocation } from 'react-router-dom';
import { LayoutDashboard, ShoppingBag, Package, Users, LogOut, PieChart, BedDouble, CalendarCheck, SprayCan, Menu, X } from 'lucide-react';
import { m, AnimatePresence } from 'framer-motion';
import { useAuthStore } from '../../store/authStore';
import { AnimatedPage } from '../ui/MotionConfig';

const DashboardLayout: React.FC = () => {
  const user = useAuthStore((state) => state.user);
  const logout = useAuthStore((state) => state.logout);
  const navigate = useNavigate();
  const location = useLocation();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const navItems = [
    { name: 'Overview', path: '/dashboard', icon: LayoutDashboard },
    { name: 'Orders (POS)', path: '/dashboard/orders', icon: ShoppingBag },
    { name: 'Rooms', path: '/dashboard/rooms', icon: BedDouble },
    { name: 'Bookings', path: '/dashboard/reservations', icon: CalendarCheck },
    { name: 'Housekeeping', path: '/dashboard/housekeeping', icon: SprayCan },
    { name: 'Inventory', path: '/dashboard/inventory', icon: Package },
    { name: 'Guests', path: '/dashboard/customers', icon: Users },
    { name: 'Analytics', path: '/dashboard/analytics', icon: PieChart },
  ];

  return (
    <div className="flex h-screen bg-stone-50 overflow-hidden text-brand-dark">
      <div className="hidden md:flex w-64 bg-white border-r border-stone-200 flex-col relative z-20">
        <div className="h-16 flex items-center px-6 border-b border-stone-100">
          <span className="text-xl font-black tracking-tight">
            Table<span className="text-brand-orange">Wise</span>
          </span>
        </div>

        <div className="flex-1 overflow-y-auto py-6 px-4 space-y-1">
          {navItems.map((item) => {
            const isActive = location.pathname === item.path || (item.path !== '/dashboard' && location.pathname.startsWith(item.path));
            const Icon = item.icon;
            return (
              <Link
                key={item.name}
                to={item.path}
                className={`relative flex items-center px-3 py-2.5 text-sm font-bold rounded-xl transition-colors ${
                  isActive ? 'text-brand-orange' : 'text-stone-500 hover:bg-stone-50 hover:text-brand-dark'
                }`}
              >
                {isActive && (
                  <m.div 
                    layoutId="activeNavTab"
                    className="absolute inset-0 bg-amber-50 rounded-xl -z-10"
                    transition={{ type: "spring", stiffness: 300, damping: 30 }}
                  />
                )}
                <Icon className={`mr-3 h-5 w-5 ${isActive ? 'text-brand-orange' : 'text-stone-400'}`} />
                {item.name}
              </Link>
            );
          })}
        </div>

        <div className="p-4 border-t border-stone-100 bg-stone-50/50">
          <div className="flex items-center mb-4 px-2">
            <div className="flex-1 min-w-0">
              <p className="text-sm font-bold text-brand-dark truncate">{user?.full_name}</p>
              <p className="text-xs font-medium text-stone-500 truncate capitalize">{user?.role?.replace('_', ' ')}</p>
            </div>
          </div>
          <button
            onClick={handleLogout}
            className="flex w-full items-center justify-center px-4 py-2.5 text-sm font-bold text-red-600 bg-red-50 rounded-xl hover:bg-red-100 transition-colors"
          >
            <LogOut className="mr-2 h-4 w-4" />
            Logout
          </button>
        </div>
      </div>

      <div className="flex-1 flex flex-col overflow-hidden relative z-10">
        <header className="h-16 bg-white/80 backdrop-blur-md border-b border-stone-200 flex items-center justify-between px-4 sm:px-8 shrink-0 z-20">
          <div className="flex items-center">
            <button onClick={() => setMobileMenuOpen(true)} className="md:hidden mr-4 p-2 -ml-2 text-stone-500 hover:text-brand-dark">
              <Menu size={20} />
            </button>
            <h1 className="text-xl font-bold text-brand-dark capitalize">
              {navItems.find(item => location.pathname === item.path || (item.path !== '/dashboard' && location.pathname.startsWith(item.path)))?.name || 'Overview'}
            </h1>
          </div>
          
          <div className="flex items-center gap-3">
            {user?.outlet_id && (
              <span className="hidden sm:inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-stone-100 text-stone-600">
                Outlet: {user.outlet_id.slice(0, 8)}
              </span>
            )}
            <div className="w-8 h-8 rounded-full bg-brand-orange text-white flex items-center justify-center font-bold shadow-sm">
              {user?.full_name?.charAt(0).toUpperCase() || 'U'}
            </div>
          </div>
        </header>
        
        <main className="flex-1 overflow-y-auto p-4 sm:p-8 bg-stone-50/50">
          <AnimatePresence mode="wait">
            <AnimatedPage key={location.pathname} className="h-full">
              <Outlet />
            </AnimatedPage>
          </AnimatePresence>
        </main>
      </div>
      
      <AnimatePresence>
        {mobileMenuOpen && (
          <div className="md:hidden fixed inset-0 z-50 flex">
            <m.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 bg-black/40 backdrop-blur-sm"
              onClick={() => setMobileMenuOpen(false)}
            />
            <m.div
              initial={{ x: '-100%' }}
              animate={{ x: 0 }}
              exit={{ x: '-100%' }}
              transition={{ type: "spring", stiffness: 300, damping: 30 }}
              className="relative w-64 bg-white h-full shadow-2xl flex flex-col"
            >
              <div className="h-16 flex items-center justify-between px-6 border-b border-stone-100 shrink-0">
                <span className="text-xl font-black tracking-tight">
                  Table<span className="text-brand-orange">Wise</span>
                </span>
                <button onClick={() => setMobileMenuOpen(false)} className="p-1 -mr-2 text-stone-400 hover:text-stone-600">
                  <X size={20} />
                </button>
              </div>
              <div className="flex-1 overflow-y-auto py-4 px-2 space-y-1">
                {navItems.map((item) => {
                  const isActive = location.pathname === item.path || (item.path !== '/dashboard' && location.pathname.startsWith(item.path));
                  const Icon = item.icon;
                  return (
                    <Link
                      key={item.name}
                      to={item.path}
                      onClick={() => setMobileMenuOpen(false)}
                      className={`flex items-center px-4 py-3 text-sm font-bold rounded-xl ${
                        isActive ? 'bg-amber-50 text-brand-orange' : 'text-stone-600'
                      }`}
                    >
                      <Icon className={`mr-3 h-5 w-5 ${isActive ? 'text-brand-orange' : 'text-stone-400'}`} />
                      {item.name}
                    </Link>
                  );
                })}
              </div>
            </m.div>
          </div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default DashboardLayout;