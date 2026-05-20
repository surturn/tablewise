import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export interface CartItem {
  menu_item_id: string;
  name: string;
  price_usd_cents: number;
  quantity: number;
  special_instructions?: string;
  outlet_id?: string;
}

interface CartState {
  items: CartItem[];
  outlet_id: string | null;
  isOpen: boolean;
  toggleCart: () => void;
  openCart: () => void;
  closeCart: () => void;
  setOutlet: (outlet_id: string) => void;
  addItem: (item: CartItem) => void;
  removeItem: (menu_item_id: string) => void;
  updateQuantity: (menu_item_id: string, quantity: number) => void;
  clearCart: () => void;
  getTotalCents: () => number;
}

export const useCartStore = create<CartState>()(
  persist(
    (set, get) => ({
      items: [],
      outlet_id: null,
      isOpen: false,

      toggleCart: () => set({ isOpen: !get().isOpen }),
      openCart: () => set({ isOpen: true }),
      closeCart: () => set({ isOpen: false }),
      setOutlet: (outlet_id) => set({ outlet_id }),

      addItem: (newItem) => {
        const currentItems = get().items;
        const existingItem = currentItems.find((i) => i.menu_item_id === newItem.menu_item_id);

        if (existingItem) {
          set({
            items: currentItems.map((i) =>
              i.menu_item_id === newItem.menu_item_id
                ? { ...i, quantity: i.quantity + newItem.quantity }
                : i
            ),
          });
        } else {
          set({ items: [...currentItems, newItem] });
        }
        set({ isOpen: true });
      },

      removeItem: (menu_item_id) => {
        set({ items: get().items.filter((i) => i.menu_item_id !== menu_item_id) });
      },

      updateQuantity: (menu_item_id, quantity) => {
        if (quantity <= 0) {
          get().removeItem(menu_item_id);
          return;
        }
        set({
          items: get().items.map((i) =>
            i.menu_item_id === menu_item_id ? { ...i, quantity } : i
          )
        });
      },

      clearCart: () => set({ items: [], outlet_id: null }),

      getTotalCents: () => {
        return get().items.reduce((total, item) => total + item.price_usd_cents * item.quantity, 0);
      },
    }),
    {
      name: 'tablewise-cart',
      partialize: (state) => ({ items: state.items, outlet_id: state.outlet_id }),
    }
  )
);