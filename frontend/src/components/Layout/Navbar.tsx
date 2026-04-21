import React from 'react';
import { Link } from 'react-router-dom';
import { ShoppingCart } from 'lucide-react';
import { useCartStore } from '../../store/cartStore';

const Navbar: React.FC = () => {
  const { items, toggleCart } = useCartStore();
  const totalItems = items.reduce((acc, item) => acc + item.quantity, 0);

  return (
    <nav className="bg-white shadow-sm sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16 items-center">

          <div className="flex-shrink-0">
            <Link to="/" className="text-2xl font-bold text-brand-dark">
              Table<span className="text-brand-orange">Wise</span>
            </Link>
          </div>

          <div className="flex space-x-8">
            <Link to="/" className="text-gray-700 hover:text-brand-orange px-3 py-2 rounded-md font-medium">Home</Link>
            <Link to="/menu" className="text-gray-700 hover:text-brand-orange px-3 py-2 rounded-md font-medium">Menu</Link>
          </div>

          <div className="flex items-center">
            {/* Call toggleCart here! */}
            <button
              onClick={toggleCart}
              className="relative p-2 text-gray-600 hover:text-brand-orange transition-colors"
            >
              <ShoppingCart size={24} />
              {totalItems > 0 && (
                <span className="absolute top-0 right-0 inline-flex items-center justify-center px-2 py-1 text-xs font-bold leading-none text-white transform translate-x-1/4 -translate-y-1/4 bg-brand-orange rounded-full">
                  {totalItems}
                </span>
              )}
            </button>
          </div>

        </div>
      </div>
    </nav>
  );
};

export default Navbar;