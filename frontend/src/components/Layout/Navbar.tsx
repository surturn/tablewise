import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { ShoppingCart, Menu as MenuIcon, X } from 'lucide-react';
import { useCartStore } from '../../store/cartStore';
import { m, useScroll, useTransform } from 'framer-motion';

const Navbar: React.FC = () => {
  const { items, toggleCart } = useCartStore();
  const totalItems = items.reduce((acc, item) => acc + item.quantity, 0);
  const { scrollY } = useScroll();
  const bgOpacity = useTransform(scrollY, [0, 50], [0, 1]);
  const location = useLocation();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  useEffect(() => {
    setMobileMenuOpen(false);
  }, [location.pathname]);

  return (
    <m.nav 
      className="fixed top-0 inset-x-0 z-50 border-b border-white/10"
      style={{ backgroundColor: `rgba(255, 255, 255, ${bgOpacity.get() * 0.9})`, backdropFilter: `blur(${bgOpacity.get() * 10}px)` }}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-20 items-center">

          <div className="flex-shrink-0 flex items-center">
            <Link to="/" className="text-2xl font-black tracking-tight text-brand-dark">
              Table<span className="text-brand-orange">Wise</span>
            </Link>
          </div>

          <div className="hidden md:flex space-x-8">
            <Link to="/" className="text-stone-600 hover:text-brand-orange transition-colors font-medium text-sm">Home</Link>
            <Link to="/menu" className="text-stone-600 hover:text-brand-orange transition-colors font-medium text-sm">Menu</Link>
            <Link to="/book" className="text-stone-600 hover:text-brand-orange transition-colors font-medium text-sm">Book a Room</Link>
            <Link to="/login" className="text-stone-600 hover:text-brand-orange transition-colors font-medium text-sm">Staff Login</Link>
          </div>

          <div className="flex items-center gap-4">
            <button
              onClick={toggleCart}
              className="relative p-2.5 bg-stone-100 text-stone-600 rounded-full hover:bg-stone-200 hover:text-brand-orange transition-all transform hover:scale-105"
            >
              <ShoppingCart size={20} />
              {totalItems > 0 && (
                <m.span 
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  key={totalItems}
                  className="absolute -top-1 -right-1 flex items-center justify-center min-w-[20px] h-5 px-1 text-[10px] font-bold text-white bg-brand-orange rounded-full border-2 border-white"
                >
                  {totalItems}
                </m.span>
              )}
            </button>
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="md:hidden p-2 text-stone-600 hover:text-brand-orange transition-colors"
            >
              {mobileMenuOpen ? <X size={24} /> : <MenuIcon size={24} />}
            </button>
          </div>

        </div>
      </div>

      <m.div 
        initial={false}
        animate={{ height: mobileMenuOpen ? 'auto' : 0, opacity: mobileMenuOpen ? 1 : 0 }}
        className="md:hidden overflow-hidden bg-white border-b border-stone-100"
      >
        <div className="px-4 pt-2 pb-6 space-y-1">
          <Link to="/" className="block px-3 py-2 rounded-md text-base font-medium text-stone-700 hover:text-brand-orange hover:bg-stone-50">Home</Link>
          <Link to="/menu" className="block px-3 py-2 rounded-md text-base font-medium text-stone-700 hover:text-brand-orange hover:bg-stone-50">Menu</Link>
          <Link to="/book" className="block px-3 py-2 rounded-md text-base font-medium text-stone-700 hover:text-brand-orange hover:bg-stone-50">Book a Room</Link>
          <Link to="/login" className="block px-3 py-2 rounded-md text-base font-medium text-stone-700 hover:text-brand-orange hover:bg-stone-50">Staff Login</Link>
        </div>
      </m.div>
    </m.nav>
  );
};

export default Navbar;