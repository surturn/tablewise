import React, { useState } from 'react';
import { X, Plus, Minus, ShoppingBag, CreditCard, Banknote, Smartphone } from 'lucide-react';
import { useCartStore } from '../../store/cartStore';
import { processCheckout } from '../../api/checkout';

const CartDrawer: React.FC = () => {
  const { isOpen, closeCart, items, updateQuantity, getTotal, clearCart } = useCartStore();

  const [phone, setPhone] = useState('');
  const [name, setName] = useState('');
  const[isLoading, setIsLoading] = useState(false);
  const [paymentMethod, setPaymentMethod] = useState<'stripe' | 'mobile_money' | 'cash'>('stripe');
  const [statusMsg, setStatusMsg] = useState<{type: 'error'|'success', text: string} | null>(null);

  const handleCheckout = async () => {
    if (!phone || !name) {
      setStatusMsg({ type: 'error', text: 'Please enter your name and phone number.' });
      return;
    }

    setIsLoading(true);
    setStatusMsg(null);

    try {
      const result = await processCheckout(phone, name, items, paymentMethod);
      if (result.checkout_url) {
        window.location.href = result.checkout_url;
        return;
      }
      setStatusMsg({ type: 'success', text: result.message || 'Order placed. Payment instructions are confirmed.' });
      setTimeout(() => {
        clearCart();
        closeCart();
        setStatusMsg(null);
      }, 5000);
    } catch (error: any) {
      setStatusMsg({ type: 'error', text: error.response?.data?.detail || error.message || 'Checkout failed.' });
    } finally {
      setIsLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-[100] flex justify-end">
      {/* Overlay */}
      <div
        className="fixed inset-0 bg-black/50 transition-opacity"
        onClick={closeCart}
      />

      {/* Drawer */}
      <div className="w-full max-w-md bg-white h-full shadow-2xl relative flex flex-col animate-[slideIn_0.3s_ease-out]">

        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b">
          <h2 className="text-xl font-bold flex items-center gap-2">
            <ShoppingBag size={24} /> Your Cart
          </h2>
          <button onClick={closeCart} className="p-2 hover:bg-gray-100 rounded-full">
            <X size={24} />
          </button>
        </div>

        {/* Items */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {items.length === 0 ? (
            <p className="text-center text-gray-500 mt-10">Your cart is empty.</p>
          ) : (
            items.map((item) => (
              <div key={item.menu_item_id} className="flex justify-between items-center bg-gray-50 p-3 rounded-lg border">
                <div>
                  <h4 className="font-semibold">{item.name}</h4>
                  <p className="text-brand-orange text-sm font-bold">USD {item.price}</p>
                </div>
                <div className="flex items-center gap-3 bg-white border rounded-md p-1">
                  <button onClick={() => updateQuantity(item.menu_item_id, item.quantity - 1)} className="p-1 hover:bg-gray-100 rounded">
                    <Minus size={16} />
                  </button>
                  <span className="w-4 text-center font-medium">{item.quantity}</span>
                  <button onClick={() => updateQuantity(item.menu_item_id, item.quantity + 1)} className="p-1 hover:bg-gray-100 rounded">
                    <Plus size={16} />
                  </button>
                </div>
              </div>
            ))
          )}
        </div>

        {/* Checkout Section */}
        {items.length > 0 && (
          <div className="border-t p-4 bg-gray-50 space-y-4">
            <div className="flex justify-between text-lg font-bold">
              <span>Total:</span>
              <span className="text-brand-orange">USD {getTotal()}</span>
            </div>

            {statusMsg && (
              <div className={`p-3 rounded text-sm font-medium ${statusMsg.type === 'error' ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700'}`}>
                {statusMsg.text}
              </div>
            )}

            <div className="space-y-3">
              <input
                type="text"
                placeholder="Full Name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="w-full border p-3 rounded focus:outline-none focus:ring-2 focus:ring-brand-orange"
              />
              <input
                type="tel"
                placeholder="Phone Number (SMS/payment updates)"
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
                className="w-full border p-3 rounded focus:outline-none focus:ring-2 focus:ring-brand-orange"
              />
              <div className="grid grid-cols-3 gap-2">
                {[
                  { id: 'stripe', label: 'Card', icon: CreditCard },
                  { id: 'mobile_money', label: 'Mobile', icon: Smartphone },
                  { id: 'cash', label: 'Cash', icon: Banknote },
                ].map(({ id, label, icon: Icon }) => (
                  <button
                    key={id}
                    type="button"
                    onClick={() => setPaymentMethod(id as 'stripe' | 'mobile_money' | 'cash')}
                    className={`border rounded p-3 text-sm font-semibold flex flex-col items-center gap-1 ${paymentMethod === id ? 'border-brand-orange text-brand-orange bg-orange-50' : 'border-gray-200 text-gray-600 bg-white'}`}
                  >
                    <Icon size={18} />
                    {label}
                  </button>
                ))}
              </div>
              <button
                onClick={handleCheckout}
                disabled={isLoading}
                className="w-full bg-brand-dark hover:bg-black text-white font-bold py-4 rounded transition-colors disabled:opacity-70 flex justify-center items-center"
              >
                {isLoading ? 'Processing...' : paymentMethod === 'stripe' ? 'Pay with Card' : paymentMethod === 'mobile_money' ? 'Pay with Mobile Money' : 'Place Cash Order'}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default CartDrawer;