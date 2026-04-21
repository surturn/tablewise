import React from 'react';
import { useMenuItems } from '../../api/menu';
import { useCartStore } from '../../store/cartStore';
import Navbar from '../../components/Layout/Navbar';

const Menu: React.FC = () => {
  const { data: menuItems, isLoading, error } = useMenuItems();
  const addItem = useCartStore((state) => state.addItem);

  const handleAddToCart = (item: any) => {
    addItem({
      menu_item_id: item.id,
      name: item.name,
      price: item.price,
      quantity: 1,
    });
  };

  return (
    <div className="min-h-screen bg-brand-light">
      <Navbar />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <h1 className="text-3xl font-bold text-brand-dark mb-8">Our Menu</h1>

        {isLoading && <p className="text-gray-500 text-center">Loading menu...</p>}
        {error && <p className="text-red-500 text-center">Failed to load menu. Is the backend running?</p>}

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8">
          {menuItems?.map((item) => (
            <div key={item.id} className="bg-white rounded-xl shadow-sm overflow-hidden border border-gray-100 hover:shadow-md transition-shadow">
              {item.image_url ? (
                <img src={item.image_url} alt={item.name} className="w-full h-48 object-cover" />
              ) : (
                <div className="w-full h-48 bg-gray-200 flex items-center justify-center text-gray-400">
                  No Image
                </div>
              )}

              <div className="p-5">
                <h3 className="text-lg font-bold text-brand-dark">{item.name}</h3>
                <p className="text-sm text-gray-500 mt-1 line-clamp-2 min-h-[40px]">
                  {item.description || 'Delicious meal prepared fresh.'}
                </p>

                <div className="mt-4 flex items-center justify-between">
                  <span className="text-xl font-bold text-brand-orange">KES {item.price}</span>
                  <button
                    onClick={() => handleAddToCart(item)}
                    className="px-4 py-2 bg-brand-dark text-white text-sm font-medium rounded hover:bg-brand-orange transition-colors"
                  >
                    Add to Cart
                  </button>
                </div>
              </div>
            </div>
          ))}

          {menuItems?.length === 0 && (
            <p className="col-span-full text-center text-gray-500 py-10">No items available right now.</p>
          )}
        </div>
      </main>
    </div>
  );
};

export default Menu;