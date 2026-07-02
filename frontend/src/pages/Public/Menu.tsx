import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { m } from 'framer-motion';
import { useMenuItems } from '../../api/menu';
import { fetchOutlets } from '../../api/outlets';
import { useCartStore } from '../../store/cartStore';
import { useToastStore } from '../../store/toastStore';
import { SkeletonCard } from '../../components/ui/Skeleton';
import { EmptyState } from '../../components/ui/EmptyState';
import { Coffee, ShoppingBag } from 'lucide-react';

const Menu: React.FC = () => {
  const { data: outlets = [] } = useQuery({ queryKey: ['outlets'], queryFn: fetchOutlets });
  const selectedOutletId = outlets[0]?.id;
  const { data: menuItems, isLoading, error } = useMenuItems(selectedOutletId);
  const addItem = useCartStore((state) => state.addItem);
  const setOutlet = useCartStore((state) => state.setOutlet);
  const addToast = useToastStore((state) => state.addToast);

  const handleAddToCart = (item: any) => {
    addItem({
      menu_item_id: item.id,
      name: item.name,
      price_usd_cents: item.price_usd_cents,
      quantity: 1,
      outlet_id: selectedOutletId,
    });
    if (selectedOutletId) setOutlet(selectedOutletId);
    addToast(`Added ${item.name} to cart`, 'success');
  };

  return (
    <div className="min-h-screen bg-stone-50 pt-20 pb-24">

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold text-brand-dark">Our Menu</h1>
          {selectedOutletId && (
            <span className="text-sm font-medium text-stone-500 bg-stone-100 px-3 py-1 rounded-full">
              Ordering from: {outlets[0]?.name}
            </span>
          )}
        </div>

        {error && (
          <div className="mb-8">
            <EmptyState 
              icon={<Coffee />} 
              title="Failed to load menu" 
              description="Is the backend running? Please try again later." 
            />
          </div>
        )}

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {isLoading && Array.from({ length: 8 }).map((_, i) => <SkeletonCard key={i} />)}
          
          {!isLoading && menuItems?.map((item, i) => (
            <m.div 
              key={item.id} 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.05 }}
              whileHover={{ y: -4 }}
              className="bg-white rounded-2xl shadow-subtle overflow-hidden border border-stone-100 flex flex-col"
            >
              {item.image_url ? (
                <img src={item.image_url} alt={item.name} className="w-full h-48 object-cover" />
              ) : (
                <div className="w-full h-48 bg-stone-100 flex items-center justify-center text-stone-400 shrink-0">
                  <Coffee size={32} opacity={0.2} />
                </div>
              )}

              <div className="p-5 flex flex-col flex-1">
                <h3 className="text-lg font-bold text-brand-dark leading-tight">{item.name}</h3>
                <p className="text-sm text-stone-500 mt-2 line-clamp-2 min-h-[40px] flex-1">
                  {item.description || 'Delicious meal prepared fresh.'}
                </p>

                <div className="mt-6 flex items-center justify-between">
                  <span className="text-xl font-black text-brand-orange">
                    ${(item.price_usd_cents / 100).toFixed(2)}
                  </span>
                  <button
                    onClick={() => handleAddToCart(item)}
                    className="p-2.5 bg-brand-dark text-brand-light rounded-full hover:bg-brand-orange transition-colors"
                    aria-label="Add to cart"
                  >
                    <ShoppingBag size={20} />
                  </button>
                </div>
              </div>
            </m.div>
          ))}
        </div>

        {!isLoading && menuItems?.length === 0 && (
          <EmptyState 
            icon={<Coffee />} 
            title="Menu is empty" 
            description="No items available right now at this outlet." 
          />
        )}
      </main>
    </div>
  );
};

export default Menu;