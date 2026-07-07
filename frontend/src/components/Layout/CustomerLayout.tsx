import { Outlet, Link } from 'react-router-dom';
import { ShoppingCart, Menu as MenuIcon, User } from 'lucide-react';
import { useCartStore } from '../../store/cartStore';

export default function CustomerLayout() {
  const items = useCartStore((state) => state.items);
  const toggleCart = useCartStore((state) => state.toggleCart);
  const itemCount = items.reduce((acc, item) => acc + item.quantity, 0);

  return (
    <div className="min-h-screen bg-neutral-50 dark:bg-neutral-950 text-neutral-900 dark:text-neutral-50 font-sans transition-colors duration-300">
      {/* Header */}
      <header className="sticky top-0 z-50 bg-white/80 dark:bg-neutral-900/80 backdrop-blur-md border-b border-neutral-200 dark:border-neutral-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-4">
              <button className="md:hidden p-2 text-neutral-500 hover:text-neutral-900 dark:text-neutral-400 dark:hover:text-white">
                <MenuIcon size={24} />
              </button>
              <Link to="/" className="font-bold text-xl tracking-tight">
                TableWise
              </Link>
            </div>
            
            <nav className="hidden md:flex space-x-8">
              <Link to="/menu" className="font-medium text-neutral-600 hover:text-neutral-900 dark:text-neutral-300 dark:hover:text-white transition-colors">Menu</Link>
              <Link to="/book" className="font-medium text-neutral-600 hover:text-neutral-900 dark:text-neutral-300 dark:hover:text-white transition-colors">Book a Room</Link>
              <Link to="/customer/dashboard" className="font-medium text-neutral-600 hover:text-neutral-900 dark:text-neutral-300 dark:hover:text-white transition-colors">Orders</Link>
            </nav>

            <div className="flex items-center gap-4">
              <button
                onClick={toggleCart}
                className="p-2 relative text-neutral-500 hover:text-neutral-900 dark:text-neutral-400 dark:hover:text-white transition-colors"
              >
                <ShoppingCart size={24} />
                {itemCount > 0 && (
                  <span className="absolute -top-0.5 -right-0.5 h-4 w-4 rounded-full bg-brand-orange text-white text-[10px] font-bold flex items-center justify-center border-2 border-white dark:border-neutral-900">
                    {itemCount}
                  </span>
                )}
              </button>
              <Link to="/login" className="p-2 text-neutral-500 hover:text-neutral-900 dark:text-neutral-400 dark:hover:text-white transition-colors">
                <User size={24} />
              </Link>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Outlet />
      </main>

      {/* Footer */}
      <footer className="bg-white dark:bg-neutral-900 border-t border-neutral-200 dark:border-neutral-800 py-8 mt-auto">
        <div className="max-w-7xl mx-auto px-4 text-center text-sm text-neutral-500 dark:text-neutral-400">
          © {new Date().getFullYear()} TableWise. All rights reserved.
        </div>
      </footer>
    </div>
  );
}
