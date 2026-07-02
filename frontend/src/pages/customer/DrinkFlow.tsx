import React, { useEffect, useState } from 'react';
import { m, AnimatePresence } from 'framer-motion';
import { Martini, CreditCard, CheckCircle2, ChevronRight } from 'lucide-react';
import CustomerNavbar from '../../components/customer/CustomerNavbar';
import MenuItemCard from '../../components/customer/MenuItemCard';
import { SkeletonCard } from '../../components/ui/Skeleton';
import { AnimatedPage, springs } from '../../components/ui/MotionConfig';
import { apiClient as client } from '../../api/client';
import { useAuth } from '../../contexts/AuthContext';

const DrinkFlow: React.FC = () => {
  const { user } = useAuth();
  
  // Local "Tab" State
  // We use local state since there is no backend endpoint to incrementally add items to an order.
  const [tabItems, setTabItems] = useState<{item: any, quantity: number}[]>([]);
  const [isTabOpen, setIsTabOpen] = useState(false);
  const [isCheckout, setIsCheckout] = useState(false);
  const [placedOrder, setPlacedOrder] = useState<any>(null);
  const [isPlacing, setIsPlacing] = useState(false);

  // Menu State
  const [menuItems, setMenuItems] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [outletId, setOutletId] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setIsLoading(true);
        const outletsRes = await client.get('/api/v1/outlets');
        const defaultOutlet = outletsRes.data[0]?.id;
        setOutletId(defaultOutlet);

        if (defaultOutlet) {
          // Typically we'd filter for "Drinks" or "Bar" category if backend supported it natively by name.
          // For now, we fetch all items and simulate it.
          const itemsRes = await client.get(`/api/v1/menu/items?outlet_id=${defaultOutlet}`);
          setMenuItems(itemsRes.data);
        }
      } catch (err) {
        console.error("Failed to load menu", err);
      } finally {
        setIsLoading(false);
      }
    };
    fetchData();
  }, []);

  const addToTab = (menuItem: any) => {
    if (!isTabOpen) setIsTabOpen(true);
    setTabItems(prev => {
      const existing = prev.find(i => i.item.id === menuItem.id);
      if (existing) {
        return prev.map(i => i.item.id === menuItem.id ? { ...i, quantity: i.quantity + 1 } : i);
      }
      return [...prev, { item: menuItem, quantity: 1 }];
    });
  };

  const handleCloseTab = async () => {
    if (!outletId || tabItems.length === 0) return;
    setIsPlacing(true);
    try {
      const payload = {
        outlet_id: outletId,
        guest_id: user?.id,
        items: tabItems.map(i => ({
          menu_item_id: i.item.id,
          quantity: i.quantity,
          unit_price: i.item.price_usd_cents / 100,
          special_instructions: ''
        })),
        payment_method: 'cash', // TODO: wire up real M-Pesa STK push for this flow (see CartDrawer.tsx)
        order_type: 'dine_in',
        is_delivery: false,
      };
      
      const res = await client.post('/api/v1/orders/', payload);
      setPlacedOrder(res.data);
      setTabItems([]);
      setIsTabOpen(false);
      setIsCheckout(false);
    } catch (err) {
      console.error("Failed to close tab", err);
    } finally {
      setIsPlacing(false);
    }
  };

  const total = tabItems.reduce((acc, i) => acc + (i.item.price_usd_cents * i.quantity), 0) / 100;

  if (placedOrder) {
    return (
      <div className="min-h-screen bg-brand-light font-sans text-brand-dark flex flex-col">
        <CustomerNavbar />
        <main className="flex-1 max-w-2xl mx-auto w-full px-4 py-12 flex flex-col items-center justify-center">
          <m.div
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={springs.snappy}
            className="bg-white p-8 rounded-3xl shadow-card text-center w-full"
          >
            <div className="w-20 h-20 bg-green-50 rounded-full flex items-center justify-center mx-auto mb-6">
              <CheckCircle2 size={40} className="text-green-500" />
            </div>
            <h2 className="text-3xl font-black text-stone-900 mb-2">Payment Successful</h2>
            <p className="text-stone-500 mb-8">Your tab has been closed and paid in full.</p>
            
            <div className="bg-stone-50 rounded-2xl p-6 mb-8 text-left border border-stone-100 flex justify-between items-center">
              <div>
                <p className="text-xs font-bold text-stone-400 uppercase tracking-wider mb-1">Amount Paid</p>
                <p className="font-black text-2xl text-brand-dark">${(placedOrder.total_usd_cents / 100).toFixed(2)}</p>
              </div>
              <div className="bg-white p-3 rounded-xl shadow-sm">
                <CreditCard className="text-stone-400" />
              </div>
            </div>
            
            <button
              onClick={() => setPlacedOrder(null)}
              className="w-full py-4 bg-brand-orange text-brand-dark font-bold rounded-xl hover:bg-amber-400 transition-colors shadow-sm"
            >
              Open New Tab
            </button>
          </m.div>
        </main>
      </div>
    );
  }

  if (isCheckout) {
    return (
      <div className="min-h-screen bg-brand-light font-sans text-brand-dark flex flex-col">
        <CustomerNavbar />
        <main className="flex-1 max-w-2xl mx-auto w-full px-4 py-12">
          <AnimatedPage className="bg-white p-8 rounded-3xl shadow-elevated border border-stone-100">
            <h2 className="text-2xl font-black text-stone-900 mb-6 flex items-center gap-2">
              <Martini className="text-brand-orange" /> Close Tab
            </h2>
            
            <div className="space-y-4 mb-8">
              {tabItems.map((item, i) => (
                <div key={i} className="flex justify-between items-center py-2 border-b border-stone-100 last:border-0">
                  <div>
                    <p className="font-bold text-stone-800">{item.item.name}</p>
                    <p className="text-sm text-stone-500">Qty: {item.quantity}</p>
                  </div>
                  <span className="font-bold">${((item.item.price_usd_cents * item.quantity) / 100).toFixed(2)}</span>
                </div>
              ))}
            </div>
            
            <div className="bg-stone-50 p-6 rounded-2xl mb-8 flex justify-between items-center">
              <span className="font-bold text-stone-600">Total Amount</span>
              <span className="text-3xl font-black text-brand-dark">${total.toFixed(2)}</span>
            </div>

            {/* TODO: wire up real M-Pesa STK push for this flow (see CartDrawer.tsx) */}
            <div className="mb-8">
              <p className="text-sm font-bold text-stone-700 mb-3">Payment Method</p>
              <div className="border border-brand-orange bg-amber-50/30 p-4 rounded-xl flex items-center gap-3">
                <div>
                  <p className="font-bold text-stone-900 text-sm">Pay with cash at the bar</p>
                </div>
                <div className="ml-auto w-5 h-5 rounded-full bg-brand-orange text-white flex items-center justify-center">
                  <CheckCircle2 size={12} />
                </div>
              </div>
            </div>

            <div className="flex gap-4">
              <button
                onClick={() => setIsCheckout(false)}
                className="flex-1 py-4 bg-stone-100 text-stone-800 font-bold rounded-xl hover:bg-stone-200 transition-colors"
              >
                Back to Bar
              </button>
              <button
                onClick={handleCloseTab}
                disabled={isPlacing}
                className="flex-[2] py-4 bg-brand-dark text-white font-bold rounded-xl hover:bg-black transition-colors shadow-sm disabled:opacity-50 flex items-center justify-center"
              >
                {isPlacing ? 'Processing...' : `Pay $${total.toFixed(2)}`}
              </button>
            </div>
          </AnimatedPage>
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-brand-light font-sans text-brand-dark flex flex-col relative">
      <CustomerNavbar />

      <main className="flex-1 max-w-7xl mx-auto w-full px-4 sm:px-6 lg:px-8 py-8 flex flex-col md:flex-row gap-8 relative">
        <div className="flex-1">
          <div className="mb-8 flex justify-between items-end">
            <div>
              <h1 className="text-3xl md:text-4xl font-black text-brand-dark mb-2">The Lounge Bar</h1>
              <p className="text-stone-500 font-medium">Add drinks to your tab.</p>
            </div>
            
            {/* Tab Status Badge */}
            <div className={`px-4 py-2 rounded-full font-bold text-sm flex items-center gap-2 ${isTabOpen ? 'bg-green-50 text-green-700 border border-green-200' : 'bg-stone-100 text-stone-500'}`}>
              <div className={`w-2 h-2 rounded-full ${isTabOpen ? 'bg-green-500 animate-pulse' : 'bg-stone-400'}`} />
              {isTabOpen ? 'Tab Open' : 'Tab Closed'}
            </div>
          </div>

          {/* Menu Items Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pb-32">
            <AnimatePresence mode="popLayout">
              {isLoading ? (
                [1, 2, 3, 4].map(i => <div key={i}><SkeletonCard /></div>)
              ) : (
                menuItems.map((item, i) => (
                  <MenuItemCard
                    key={item.id}
                    id={item.id}
                    name={item.name}
                    description={item.description}
                    priceUsdCents={item.price_usd_cents}
                    imageUrl={item.image_url}
                    isAvailable={item.is_available}
                    onAdd={() => addToTab(item)}
                    delay={i * 0.05}
                  />
                ))
              )}
            </AnimatePresence>
          </div>
        </div>
      </main>

      {/* Persistent Bottom Tab Summary */}
      <AnimatePresence>
        {isTabOpen && (
          <m.div
            initial={{ y: 100 }}
            animate={{ y: 0 }}
            exit={{ y: 100 }}
            transition={springs.snappy}
            className="fixed bottom-0 left-0 right-0 bg-white border-t border-stone-200 shadow-[0_-10px_20px_rgba(0,0,0,0.05)] z-40"
          >
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-24 flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 bg-amber-50 rounded-full flex items-center justify-center border border-brand-orange/20">
                  <Martini className="text-brand-orange" />
                </div>
                <div>
                  <p className="font-bold text-stone-900">Current Tab</p>
                  <p className="text-sm text-stone-500 font-medium">{tabItems.reduce((acc, i) => acc + i.quantity, 0)} drinks</p>
                </div>
              </div>
              
              <div className="flex items-center gap-6">
                <div className="text-right hidden sm:block">
                  <p className="text-xs font-bold text-stone-400 uppercase tracking-wider">Total</p>
                  <p className="font-black text-2xl text-brand-dark">${total.toFixed(2)}</p>
                </div>
                <button
                  onClick={() => setIsCheckout(true)}
                  className="px-6 sm:px-8 py-3.5 bg-brand-dark text-white font-bold rounded-xl hover:bg-black transition-colors shadow-sm flex items-center gap-2"
                >
                  Close Tab <ChevronRight size={18} />
                </button>
              </div>
            </div>
          </m.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default DrinkFlow;
