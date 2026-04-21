import React, { useState } from 'react';
import { X, Plus, Minus, ShoppingBag } from 'lucide-react';
import { useCartStore } from '../../store/cartStore';
import { processCheckout } from '../../api/checkout';

const CartDrawer: React.FC = () => {
  const { isOpen, closeCart, items, updateQuantity, getTotal, clearCart } = useCartStore();

  const [phone, setPhone] = useState('');
  const [name, setName] = useState('');
  const[isLoading, setIsLoading] = useState(false);
  const [statusMsg, setStatusMsg] = useState<{type: 'error'|'success', text: string} | null>(null);

  const handleCheckout = async () => {
    if (!phone || !name) {
      setStatusMsg({ type: 'error', text: 'Please enter your name and M-Pesa number.' });
      return;
    }

    setIsLoading(true);
    setStatusMsg(null);

    try {
      await processCheckout(phone, name, items);
      setStatusMsg({ type: 'success', text: 'M-Pesa prompt sent! Please check your phone to enter your PIN.' });
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
                  <p className="text-brand-orange text-sm font-bold">KES {item.price}</p>
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
              <span className="text-brand-orange">KES {getTotal()}</span>
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
                placeholder="M-Pesa Number (e.g., 0712345678)"
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
                className="w-full border p-3 rounded focus:outline-none focus:ring-2 focus:ring-brand-orange"
              />
              <button
                onClick={handleCheckout}
                disabled={isLoading}
                className="w-full bg-brand-dark hover:bg-black text-white font-bold py-4 rounded transition-colors disabled:opacity-70 flex justify-center items-center"
              >
                {isLoading ? 'Processing...' : 'Pay with M-Pesa'}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default CartDrawer;