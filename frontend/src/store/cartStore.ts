import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export interface CartItem {
  menu_item_id: string;
  name: string;
  price: number;
  quantity: number;
  special_instructions?: string;
}

interface CartState {
  items: CartItem[];
  branch_id: string | null; // Important: A cart should only belong to one branch
  setBranch: (branch_id: string) => void;
  addItem: (item: CartItem) => void;
  removeItem: (menu_item_id: string) => void;
  clearCart: () => void;
  getTotal: () => number;
}

export const useCartStore = create<CartState>()(
  persist(
    (set, get) => ({
      items:[],
      branch_id: null,

      setBranch: (branch_id) => set({ branch_id }),

      addItem: (newItem) => {
        const currentItems = get().items;
        const existingItem = currentItems.find((i) => i.menu_item_id === newItem.menu_item_id);

        if (existingItem) {
          // Update quantity if item already in cart
          set({
            items: currentItems.map((i) =>
              i.menu_item_id === newItem.menu_item_id
                ? { ...i, quantity: i.quantity + newItem.quantity }
                : i
            ),
          });
        } else {
          // Add new item
          set({ items: [...currentItems, newItem] });
        }
      },

      removeItem: (menu_item_id) => {
        set({ items: get().items.filter((i) => i.menu_item_id !== menu_item_id) });
      },

      clearCart: () => set({ items:[], branch_id: null }),

      getTotal: () => {
        return get().items.reduce((total, item) => total + item.price * item.quantity, 0);
      },
    }),
    {
      name: 'tablewise-cart', // Persist cart in local storage
    }
  )
);