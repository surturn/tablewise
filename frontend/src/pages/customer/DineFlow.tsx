import React, { useEffect, useState } from 'react';
import { AnimatePresence } from 'framer-motion';
import CustomerNavbar from '../../components/customer/CustomerNavbar';
import MenuItemCard from '../../components/customer/MenuItemCard';
import { SkeletonCard } from '../../components/ui/Skeleton';
import { apiClient as client } from '../../api/client';
import { useCartStore } from '../../store/cartStore';
import { useToastStore } from '../../store/toastStore';

const DineFlow: React.FC = () => {
  const addItem = useCartStore((state) => state.addItem);
  const addToast = useToastStore((state) => state.addToast);
  const [categories, setCategories] = useState<any[]>([]);
  const [menuItems, setMenuItems] = useState<any[]>([]);
  const [activeCategory, setActiveCategory] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [outletId, setOutletId] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setIsLoading(true);
        // 1. Get Outlets
        const outletsRes = await client.get('/outlets');
        const defaultOutlet = outletsRes.data[0]?.id;
        setOutletId(defaultOutlet);

        if (defaultOutlet) {
          // 2. Get Categories & Items
          const [catRes, itemsRes] = await Promise.all([
            client.get('/menu/categories'),
            client.get(`/menu/items?outlet_id=${defaultOutlet}`)
          ]);
          setCategories(catRes.data);
          setMenuItems(itemsRes.data);
          if (catRes.data.length > 0) setActiveCategory(catRes.data[0].id);
        }
      } catch (err) {
        console.error("Failed to load menu", err);
        addToast('Could not load the menu. Please check your connection and try again.', 'error');
      } finally {
        setIsLoading(false);
      }
    };
    fetchData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const filteredItems = menuItems.filter(item => item.category_id === activeCategory);

  return (
    <div className="min-h-screen bg-brand-light font-sans text-brand-dark flex flex-col relative">
      <CustomerNavbar />

      <main className="flex-1 max-w-7xl mx-auto w-full px-4 sm:px-6 lg:px-8 py-8 flex flex-col md:flex-row gap-8 relative">
        <div className="flex-1">
          <div className="mb-8">
            <h1 className="text-3xl md:text-4xl font-black text-brand-dark mb-2">Dine with us</h1>
            <p className="text-stone-500 font-medium">Explore the menu and order directly.</p>
          </div>

          {/* Categories Tab Bar */}
          <div className="flex overflow-x-auto pb-4 mb-6 hide-scrollbar gap-2 sticky top-20 z-30 bg-brand-light/90 backdrop-blur pt-2">
            {isLoading ? (
              [1, 2, 3, 4].map(i => <div key={i} className="h-10 w-24 bg-stone-200 rounded-full animate-pulse flex-shrink-0" />)
            ) : (
              categories.map(cat => (
                <button
                  key={cat.id}
                  onClick={() => setActiveCategory(cat.id)}
                  className={`px-6 py-2.5 rounded-full text-sm font-bold whitespace-nowrap transition-all ${
                    activeCategory === cat.id
                      ? 'bg-brand-dark text-white shadow-md transform scale-105'
                      : 'bg-white text-stone-600 border border-stone-200 hover:bg-stone-50'
                  }`}
                >
                  {cat.name}
                </button>
              ))
            )}
          </div>

          {/* Menu Items Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <AnimatePresence mode="popLayout">
              {isLoading ? (
                [1, 2, 3, 4].map(i => <div key={i}><SkeletonCard /></div>)
              ) : (
                filteredItems.map((item, i) => (
                  <MenuItemCard
                    key={item.id}
                    id={item.id}
                    name={item.name}
                    description={item.description}
                    priceUsdCents={item.price_usd_cents}
                    imageUrl={item.image_url}
                    isAvailable={item.is_available}
                    onAdd={() => {
                      addItem({
                        menu_item_id: item.id,
                        name: item.name,
                        price_usd_cents: item.price_usd_cents,
                        quantity: 1,
                        outlet_id: outletId || undefined
                      });
                      addToast(`Added ${item.name} to cart`, 'success');
                    }}
                    delay={i * 0.05}
                  />
                ))
              )}
            </AnimatePresence>
          </div>
        </div>
      </main>

      <style>{`
        .hide-scrollbar::-webkit-scrollbar {
          display: none;
        }
        .hide-scrollbar {
          -ms-overflow-style: none;
          scrollbar-width: none;
        }
      `}</style>
    </div>
  );
};

export default DineFlow;
