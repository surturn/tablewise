import React, { useEffect, useState } from 'react';
import { m, AnimatePresence } from 'framer-motion';
import { ShoppingBag, ChevronLeft, CheckCircle2, Clock } from 'lucide-react';
import CustomerNavbar from '../../components/customer/CustomerNavbar';
import MenuItemCard from '../../components/customer/MenuItemCard';
import { SkeletonCard } from '../../components/ui/Skeleton';
import { springs } from '../../components/ui/MotionConfig';
import { apiClient as client } from '../../api/client';
import { useAuth } from '../../contexts/AuthContext';
import { useCartStore } from '../../store/cartStore';
import { useToastStore } from '../../store/toastStore';
import { queueOrderWhenOffline } from '../../utils/offlineOrderQueue';

const DineFlow: React.FC = () => {
  const { user } = useAuth();
  const { items, addItem, clearCart } = useCartStore();
  const addToast = useToastStore((state) => state.addToast);
  const [categories, setCategories] = useState<any[]>([]);
  const [menuItems, setMenuItems] = useState<any[]>([]);
  const [activeCategory, setActiveCategory] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [outletId, setOutletId] = useState<string | null>(null);
  
  // Cart & Checkout state
  const [isCartOpen, setIsCartOpen] = useState(false);
  const [isCheckout, setIsCheckout] = useState(false);
  const [isDelivery, setIsDelivery] = useState(false);
  const [tableNumber, setTableNumber] = useState('');
  const [deliveryAddress, setDeliveryAddress] = useState('');
  const [notes, setNotes] = useState('');
  
  // Order tracking
  const [placedOrder, setPlacedOrder] = useState<any>(null);
  const [isPlacing, setIsPlacing] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setIsLoading(true);
        // 1. Get Outlets
        const outletsRes = await client.get('/api/v1/outlets');
        const defaultOutlet = outletsRes.data[0]?.id;
        setOutletId(defaultOutlet);

        if (defaultOutlet) {
          // 2. Get Categories & Items
          const [catRes, itemsRes] = await Promise.all([
            client.get('/api/v1/menu/categories'),
            client.get(`/api/v1/menu/items?outlet_id=${defaultOutlet}`)
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

  const handlePlaceOrder = async () => {
    if (!outletId) return;
    setIsPlacing(true);
    const orderPayload = {
      outlet_id: outletId,
      guest_id: user?.id,
      items: items.map(i => ({
        menu_item_id: i.menu_item_id,
        quantity: i.quantity,
        unit_price: i.price_usd_cents / 100, // ignored by backend but required in schema shape
        special_instructions: ''
      })),
      payment_method: 'cash', // Default stub
      order_type: isDelivery ? 'delivery' : 'dine_in',
      table_number: tableNumber || undefined,
      is_delivery: isDelivery,
      delivery_address: deliveryAddress || undefined,
      notes: notes || undefined
    };
    try {
      const res = await client.post('/api/v1/orders/', orderPayload);
      setPlacedOrder(res.data);
      clearCart();
      setIsCartOpen(false);
      setIsCheckout(false);
    } catch (err) {
      console.error("Failed to place order", err);
      if (!navigator.onLine) {
        await queueOrderWhenOffline(orderPayload);
        addToast('You are offline. Order queued and will submit automatically once reconnected.', 'info');
        clearCart();
        setIsCartOpen(false);
        setIsCheckout(false);
      } else {
        addToast('Failed to place your order. Please try again.', 'error');
      }
    } finally {
      setIsPlacing(false);
    }
  };

  const total = items.reduce((acc, item) => acc + (item.price_usd_cents * item.quantity), 0) / 100;
  const filteredItems = menuItems.filter(item => item.category_id === activeCategory);

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
            <h2 className="text-3xl font-black text-stone-900 mb-2">Order Received!</h2>
            <p className="text-stone-500 mb-8">Your order #{placedOrder.id.split('-')[0]} is being prepared.</p>
            
            <div className="bg-stone-50 rounded-2xl p-6 mb-8 text-left">
              <div className="flex items-center gap-3 mb-4 text-stone-700 font-medium pb-4 border-b border-stone-200">
                <Clock size={20} className="text-brand-orange" />
                <span>Estimated time: 20-30 mins</span>
              </div>
              <div className="relative pl-6 border-l-2 border-brand-orange space-y-6">
                <div className="relative">
                  <div className="absolute -left-[31px] top-1 w-4 h-4 rounded-full bg-brand-orange border-4 border-white" />
                  <p className="font-bold text-stone-900">Received</p>
                  <p className="text-xs text-stone-500">Kitchen is reviewing your order</p>
                </div>
                <div className="relative opacity-40">
                  <div className="absolute -left-[31px] top-1 w-4 h-4 rounded-full bg-stone-300 border-4 border-white" />
                  <p className="font-bold text-stone-900">Preparing</p>
                  <p className="text-xs text-stone-500">Chefs are on it</p>
                </div>
                <div className="relative opacity-40">
                  <div className="absolute -left-[31px] top-1 w-4 h-4 rounded-full bg-stone-300 border-4 border-white" />
                  <p className="font-bold text-stone-900">{isDelivery ? 'On the way' : 'Ready'}</p>
                  <p className="text-xs text-stone-500">Almost there</p>
                </div>
              </div>
            </div>
            
            <button
              onClick={() => setPlacedOrder(null)}
              className="w-full py-4 bg-stone-100 text-stone-800 font-bold rounded-xl hover:bg-stone-200 transition-colors"
            >
              Order Something Else
            </button>
          </m.div>
        </main>
      </div>
    );
  }

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
                      setIsCartOpen(true); 
                    }}
                    delay={i * 0.05}
                  />
                ))
              )}
            </AnimatePresence>
          </div>
        </div>
      </main>

      {/* Cart Drawer Overlay */}
      <AnimatePresence>
        {isCartOpen && (
          <>
            <m.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => { setIsCartOpen(false); setIsCheckout(false); }}
              className="fixed inset-0 bg-stone-900/40 z-50 backdrop-blur-sm"
            />
            <m.div
              initial={{ x: '100%' }}
              animate={{ x: 0 }}
              exit={{ x: '100%' }}
              transition={springs.snappy}
              className="fixed top-0 right-0 h-full w-full sm:w-[400px] bg-white z-50 shadow-2xl flex flex-col"
            >
              {/* Header */}
              <div className="flex items-center p-6 border-b border-stone-100">
                <button onClick={() => { isCheckout ? setIsCheckout(false) : setIsCartOpen(false) }} className="p-2 -ml-2 rounded-full hover:bg-stone-100">
                  <ChevronLeft size={24} />
                </button>
                <h2 className="text-xl font-black ml-2">{isCheckout ? 'Checkout' : 'Your Cart'}</h2>
              </div>

              {/* Body */}
              <div className="flex-1 overflow-y-auto p-6">
                {items.length === 0 ? (
                  <div className="h-full flex flex-col items-center justify-center text-stone-400">
                    <ShoppingBag size={48} className="mb-4 opacity-50" />
                    <p className="font-medium text-lg">Your cart is empty</p>
                  </div>
                ) : !isCheckout ? (
                  <div className="space-y-6">
                    {items.map((item, i) => (
                      <div key={i} className="flex justify-between items-start">
                        <div className="flex gap-3">
                          <div className="w-8 h-8 rounded bg-stone-100 flex items-center justify-center text-sm font-bold text-stone-600 shrink-0">
                            {item.quantity}x
                          </div>
                          <div>
                            <p className="font-bold text-stone-900 leading-tight">{item.name}</p>
                            <p className="text-sm text-brand-orange font-medium mt-1">
                              ${((item.price_usd_cents * item.quantity) / 100).toFixed(2)}
                            </p>
                          </div>
                        </div>
                        <div className="flex gap-2">
                          <button onClick={() => useCartStore.getState().updateQuantity(item.menu_item_id, item.quantity - 1)} className="w-8 h-8 rounded-full bg-stone-100 hover:bg-stone-200 flex items-center justify-center font-bold text-stone-600">-</button>
                          <button onClick={() => useCartStore.getState().updateQuantity(item.menu_item_id, item.quantity + 1)} className="w-8 h-8 rounded-full bg-stone-100 hover:bg-stone-200 flex items-center justify-center font-bold text-stone-600">+</button>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="space-y-6">
                    <div>
                      <h3 className="font-bold text-stone-900 mb-3">Order Type</h3>
                      <div className="flex bg-stone-100 p-1 rounded-xl">
                        <button
                          onClick={() => setIsDelivery(false)}
                          className={`flex-1 py-2 text-sm font-bold rounded-lg transition-all ${!isDelivery ? 'bg-white shadow-sm text-stone-900' : 'text-stone-500 hover:text-stone-700'}`}
                        >
                          Dine In / Pickup
                        </button>
                        <button
                          onClick={() => setIsDelivery(true)}
                          className={`flex-1 py-2 text-sm font-bold rounded-lg transition-all ${isDelivery ? 'bg-white shadow-sm text-stone-900' : 'text-stone-500 hover:text-stone-700'}`}
                        >
                          Delivery
                        </button>
                      </div>
                    </div>

                    {!isDelivery ? (
                      <div>
                        <label className="block text-sm font-bold text-stone-700 mb-2">Table Number (Optional)</label>
                        <input
                          type="text"
                          value={tableNumber}
                          onChange={e => setTableNumber(e.target.value)}
                          className="w-full px-4 py-3 bg-stone-50 border border-stone-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-brand-orange/50 transition-all"
                          placeholder="e.g. 12"
                        />
                      </div>
                    ) : (
                      <div>
                        <label className="block text-sm font-bold text-stone-700 mb-2">Delivery Room / Address</label>
                        <input
                          type="text"
                          value={deliveryAddress}
                          onChange={e => setDeliveryAddress(e.target.value)}
                          className="w-full px-4 py-3 bg-stone-50 border border-stone-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-brand-orange/50 transition-all"
                          placeholder="e.g. Room 402"
                        />
                      </div>
                    )}
                    
                    <div>
                      <label className="block text-sm font-bold text-stone-700 mb-2">Special Instructions</label>
                      <textarea
                        value={notes}
                        onChange={e => setNotes(e.target.value)}
                        className="w-full px-4 py-3 bg-stone-50 border border-stone-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-brand-orange/50 transition-all min-h-[100px]"
                        placeholder="No onions, extra sauce..."
                      />
                    </div>
                  </div>
                )}
              </div>

              {/* Footer */}
              {items.length > 0 && (
                <div className="p-6 bg-white border-t border-stone-100 shadow-[0_-10px_20px_rgba(0,0,0,0.03)] z-10">
                  <div className="flex justify-between items-center mb-4">
                    <span className="font-bold text-stone-600">Total</span>
                    <span className="text-2xl font-black text-brand-dark">${total.toFixed(2)}</span>
                  </div>
                  {!isCheckout ? (
                    <button
                      onClick={() => setIsCheckout(true)}
                      className="w-full py-4 bg-brand-orange text-brand-dark font-bold rounded-xl hover:bg-amber-400 transition-colors shadow-sm"
                    >
                      Go to Checkout
                    </button>
                  ) : (
                    <button
                      onClick={handlePlaceOrder}
                      disabled={isPlacing || (isDelivery && !deliveryAddress)}
                      className="w-full py-4 bg-brand-dark text-white font-bold rounded-xl hover:bg-black transition-colors shadow-sm disabled:opacity-50 flex items-center justify-center gap-2"
                    >
                      {isPlacing ? 'Processing...' : 'Place Order'}
                    </button>
                  )}
                </div>
              )}
            </m.div>
          </>
        )}
      </AnimatePresence>

      {/* Floating Cart Button for mobile (if drawer closed) */}
      <AnimatePresence>
        {!isCartOpen && items.length > 0 && (
          <m.button
            initial={{ y: 100 }}
            animate={{ y: 0 }}
            exit={{ y: 100 }}
            onClick={() => setIsCartOpen(true)}
            className="md:hidden fixed bottom-6 left-4 right-4 bg-brand-dark text-white rounded-2xl p-4 shadow-elevated flex items-center justify-between z-40"
          >
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 bg-white/20 rounded-full flex items-center justify-center font-bold text-sm">
                {items.reduce((acc, i) => acc + i.quantity, 0)}
              </div>
              <span className="font-bold text-lg">View Cart</span>
            </div>
            <span className="font-bold text-lg">${total.toFixed(2)}</span>
          </m.button>
        )}
      </AnimatePresence>

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
