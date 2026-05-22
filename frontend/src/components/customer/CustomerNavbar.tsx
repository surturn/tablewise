import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { ShoppingCart, LogOut, Menu as MenuIcon, X } from 'lucide-react';
import { useCartStore } from '../../store/cartStore';
import { useAuth } from '../../contexts/AuthContext';
import { m, AnimatePresence } from 'framer-motion';
import { springs } from '../ui/MotionConfig';

const CustomerNavbar: React.FC = () => {
  const { items, toggleCart } = useCartStore();
  const { user, logout } = useAuth();
  const location = useLocation();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [isProfileMenuOpen, setIsProfileMenuOpen] = useState(false);

  const totalItems = items.reduce((acc, item) => acc + item.quantity, 0);

  const navLinks = [
    { name: 'Dashboard', path: '/customer/dashboard' },
    { name: 'Dine', path: '/customer/dine' },
    { name: 'Stay', path: '/customer/stay' },
    { name: 'Drink', path: '/customer/drink' },
  ];

  return (
    <nav className="sticky top-0 z-50 bg-white/70 backdrop-blur-md border-b border-stone-200 shadow-sm transition-all duration-300">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-20">
          <div className="flex items-center">
            <Link to="/customer/dashboard" className="flex-shrink-0 flex items-center">
              <h1 className="text-2xl font-black text-brand-dark tracking-tight">
                Table<span className="text-brand-orange">Wise</span>
              </h1>
            </Link>
          </div>

          <div className="hidden md:flex space-x-8 items-center">
            {navLinks.map((link) => (
              <Link 
                key={link.name} 
                to={link.path} 
                className={`transition-colors font-medium text-sm ${location.pathname === link.path ? 'text-brand-orange' : 'text-stone-600 hover:text-brand-orange'}`}
              >
                {link.name}
              </Link>
            ))}
          </div>

          <div className="flex items-center gap-4">
            <button
              onClick={toggleCart}
              className="relative p-2.5 bg-stone-100 text-stone-600 rounded-full hover:bg-stone-200 hover:text-brand-orange transition-all transform hover:scale-105"
            >
              <ShoppingCart size={20} />
              <AnimatePresence>
                {totalItems > 0 && (
                  <m.span
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    exit={{ scale: 0 }}
                    className="absolute -top-1 -right-1 bg-brand-orange text-white text-[10px] font-bold h-5 w-5 rounded-full flex items-center justify-center border-2 border-white"
                  >
                    {totalItems}
                  </m.span>
                )}
              </AnimatePresence>
            </button>

            <div className="relative hidden md:block">
              <button 
                onClick={() => setIsProfileMenuOpen(!isProfileMenuOpen)}
                className="flex items-center gap-2 focus:outline-none"
              >
                <div className="w-10 h-10 rounded-full bg-brand-orange text-white flex items-center justify-center font-bold text-sm shadow-sm ring-2 ring-white">
                  {user?.full_name?.charAt(0).toUpperCase() || 'U'}
                </div>
              </button>
              
              <AnimatePresence>
                {isProfileMenuOpen && (
                  <m.div
                    initial={{ opacity: 0, y: 10, scale: 0.95 }}
                    animate={{ opacity: 1, y: 0, scale: 1 }}
                    exit={{ opacity: 0, y: 10, scale: 0.95 }}
                    transition={springs.snappy}
                    className="absolute right-0 mt-2 w-48 bg-white rounded-xl shadow-elevated border border-stone-100 py-1"
                  >
                    <div className="px-4 py-3 border-b border-stone-100">
                      <p className="text-sm font-medium text-stone-900 truncate">{user?.full_name}</p>
                      <p className="text-xs text-stone-500 truncate">{user?.email}</p>
                    </div>
                    <button
                      onClick={() => { logout(); setIsProfileMenuOpen(false); }}
                      className="w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50 flex items-center gap-2 transition-colors"
                    >
                      <LogOut size={16} />
                      Log out
                    </button>
                  </m.div>
                )}
              </AnimatePresence>
            </div>

            <div className="md:hidden flex items-center">
              <button
                onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
                className="p-2 rounded-md text-stone-600 hover:text-brand-orange hover:bg-stone-100 focus:outline-none"
              >
                {isMobileMenuOpen ? <X size={24} /> : <MenuIcon size={24} />}
              </button>
            </div>
          </div>
        </div>
      </div>

      <AnimatePresence>
        {isMobileMenuOpen && (
          <m.div 
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="md:hidden overflow-hidden bg-white border-b border-stone-200"
          >
            <div className="px-4 pt-2 pb-6 space-y-1">
              <div className="flex items-center gap-3 px-3 py-4 border-b border-stone-100 mb-2">
                <div className="w-10 h-10 rounded-full bg-brand-orange text-white flex items-center justify-center font-bold text-sm shadow-sm">
                  {user?.full_name?.charAt(0).toUpperCase() || 'U'}
                </div>
                <div>
                  <p className="text-sm font-medium text-stone-900">{user?.full_name}</p>
                  <p className="text-xs text-stone-500">{user?.email}</p>
                </div>
              </div>
              
              {navLinks.map((link) => (
                <Link 
                  key={link.name} 
                  to={link.path} 
                  className={`block px-3 py-2 rounded-md text-base font-medium transition-colors ${location.pathname === link.path ? 'text-brand-orange bg-brand-orange/10' : 'text-stone-700 hover:text-brand-orange hover:bg-stone-50'}`}
                  onClick={() => setIsMobileMenuOpen(false)}
                >
                  {link.name}
                </Link>
              ))}
              
              <div className="border-t border-stone-100 my-2 pt-2">
                <button
                  onClick={() => { logout(); setIsMobileMenuOpen(false); }}
                  className="w-full text-left px-3 py-2 rounded-md text-base font-medium text-red-600 hover:bg-red-50 flex items-center gap-2"
                >
                  <LogOut size={18} />
                  Log out
                </button>
              </div>
            </div>
          </m.div>
        )}
      </AnimatePresence>
    </nav>
  );
};

export default CustomerNavbar;
