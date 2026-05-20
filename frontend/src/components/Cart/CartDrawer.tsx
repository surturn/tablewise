import React, { useState } from 'react';
import { X, Plus, Minus, ShoppingBag, CreditCard, Banknote, Smartphone } from 'lucide-react';
import { m, AnimatePresence } from 'framer-motion';
import { useCartStore } from '../../store/cartStore';
import { useToastStore } from '../../store/toastStore';
import { processCheckout, PaymentProvider } from '../../api/checkout';
import { springs } from '../ui/MotionConfig';

const CartDrawer: React.FC = () => {
  const { isOpen, closeCart, items, updateQuantity, getTotalCents, clearCart } = useCartStore();
  const addToast = useToastStore((state) => state.addToast);

  const [phone, setPhone] = useState('');
  const [name, setName] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [paymentMethod, setPaymentMethod] = useState<PaymentProvider>('cash');

  const handleCheckout = async () => {
    if (!phone || !name) {
      addToast('Please enter your name and phone number.', 'warning');
      return;
    }

    setIsLoading(true);

    try {
      await processCheckout(phone, name, items, paymentMethod);
      addToast('Order created successfully!', 'success');
      setTimeout(() => {
        clearCart();
        closeCart();
      }, 3000);
    } catch (error: any) {
      if (error.message === 'OFFLINE_QUEUED') {
        addToast('You are offline. Order queued for later sync.', 'info');
        clearCart();
        closeCart();
      } else {
        addToast(error.response?.data?.detail || error.message || 'Checkout failed.', 'error');
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <div className="fixed inset-0 z-[100] flex justify-end">
          <m.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="absolute inset-0 bg-black/40 backdrop-blur-sm"
            onClick={closeCart}
          />

          <m.div 
            initial={{ x: '100%' }}
            animate={{ x: 0 }}
            exit={{ x: '100%' }}
            transition={springs.snappy}
            className="w-full max-w-md bg-white h-full shadow-2xl relative flex flex-col"
          >
            <div className="flex items-center justify-between p-6 border-b border-stone-100 shrink-0">
              <h2 className="text-xl font-bold flex items-center gap-2 text-brand-dark">
                <ShoppingBag size={24} className="text-brand-orange" /> Your Cart
              </h2>
              <button onClick={closeCart} className="p-2 hover:bg-stone-100 rounded-full text-stone-400 hover:text-stone-600 transition-colors">
                <X size={20} />
              </button>
            </div>

            <div className="flex-1 overflow-y-auto p-6 space-y-4">
              {items.length === 0 ? (
                <div className="flex flex-col items-center justify-center h-full text-stone-400">
                  <ShoppingBag size={48} className="mb-4 opacity-20" />
                  <p>Your cart is empty.</p>
                </div>
              ) : (
                items.map((item) => (
                  <div key={item.menu_item_id} className="flex justify-between items-center bg-white p-4 rounded-xl shadow-subtle border border-stone-100">
                    <div>
                      <h4 className="font-bold text-brand-dark">{item.name}</h4>
                      <p className="text-brand-orange text-sm font-black">${(item.price_usd_cents / 100).toFixed(2)}</p>
                    </div>
                    <div className="flex items-center gap-3 bg-stone-50 border border-stone-100 rounded-lg p-1">
                      <button onClick={() => updateQuantity(item.menu_item_id, item.quantity - 1)} className="p-1 hover:bg-white rounded text-stone-500 hover:text-brand-dark transition-colors shadow-sm">
                        <Minus size={14} />
                      </button>
                      <span className="w-4 text-center font-bold text-sm">{item.quantity}</span>
                      <button onClick={() => updateQuantity(item.menu_item_id, item.quantity + 1)} className="p-1 hover:bg-white rounded text-stone-500 hover:text-brand-dark transition-colors shadow-sm">
                        <Plus size={14} />
                      </button>
                    </div>
                  </div>
                ))
              )}
            </div>

            {items.length > 0 && (
              <div className="border-t border-stone-100 p-6 bg-stone-50 shrink-0 space-y-4">
                <div className="flex justify-between text-lg font-bold mb-2">
                  <span className="text-brand-dark">Total</span>
                  <span className="text-brand-orange">${(getTotalCents() / 100).toFixed(2)}</span>
                </div>

                <div className="space-y-3">
                  <div>
                    <label className="text-xs font-medium text-stone-500 ml-1">Full Name</label>
                    <input
                      type="text"
                      value={name}
                      onChange={(e) => setName(e.target.value)}
                      className="w-full border border-stone-200 p-3 rounded-lg mt-1 focus:ring-2 focus:ring-brand-orange outline-none"
                    />
                  </div>
                  <div>
                    <label className="text-xs font-medium text-stone-500 ml-1">Phone Number</label>
                    <input
                      type="tel"
                      value={phone}
                      onChange={(e) => setPhone(e.target.value)}
                      className="w-full border border-stone-200 p-3 rounded-lg mt-1 focus:ring-2 focus:ring-brand-orange outline-none"
                    />
                  </div>
                  
                  <div className="grid grid-cols-3 gap-2 pt-2">
                    {[
                      { id: 'stripe', label: 'Card', icon: CreditCard },
                      { id: 'mobile_money', label: 'Mobile', icon: Smartphone },
                      { id: 'cash', label: 'Cash', icon: Banknote },
                    ].map(({ id, label, icon: Icon }) => (
                      <button
                        key={id}
                        type="button"
                        onClick={() => setPaymentMethod(id as PaymentProvider)}
                        className={`border rounded-lg p-3 text-xs font-bold flex flex-col items-center gap-2 transition-all ${paymentMethod === id ? 'border-brand-orange text-brand-orange bg-amber-50 ring-1 ring-brand-orange ring-offset-1' : 'border-stone-200 text-stone-500 bg-white hover:border-stone-300'}`}
                      >
                        <Icon size={18} />
                        {label}
                      </button>
                    ))}
                  </div>
                  
                  <button
                    onClick={handleCheckout}
                    disabled={isLoading}
                    className="w-full mt-4 bg-brand-dark hover:bg-black text-white font-bold py-4 rounded-xl shadow-md transition-all transform hover:-translate-y-0.5 active:translate-y-0 disabled:opacity-70 disabled:hover:translate-y-0 flex justify-center items-center"
                  >
                    {isLoading ? 'Processing...' : 'Place Order'}
                  </button>
                </div>
              </div>
            )}
          </m.div>
        </div>
      )}
    </AnimatePresence>
  );
};

export default CartDrawer;