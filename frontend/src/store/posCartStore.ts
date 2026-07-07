import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export type OrderType = 'dine_in' | 'takeaway' | 'room_service';

export interface POSCartItem {
  menu_item_id: string;
  name: string;
  price_kes_cents: number;
  quantity: number;
  special_instructions?: string;
  discount_cents?: number;
  voided?: boolean;
}

interface POSCartState {
  items: POSCartItem[];
  outlet_id: string | null;
  table_id: string | null;
  waiter_id: string | null;
  order_type: OrderType;
  isOpen: boolean;

  toggleCart: () => void;
  openCart: () => void;
  closeCart: () => void;
  
  setOutlet: (outlet_id: string) => void;
  setTable: (table_id: string | null) => void;
  setWaiter: (waiter_id: string | null) => void;
  setOrderType: (type: OrderType) => void;

  addItem: (item: Omit<POSCartItem, 'discount_cents' | 'voided'>) => void;
  removeItem: (menu_item_id: string) => void;
  updateQuantity: (menu_item_id: string, quantity: number) => void;
  applyDiscount: (menu_item_id: string, discount_cents: number) => void;
  voidItem: (menu_item_id: string) => void;

  clearCart: () => void;
  getSubtotalCents: () => number;
  getTotalCents: () => number; // Can include tax logic later
}

export const usePOSCartStore = create<POSCartState>()(
  persist(
    (set, get) => ({
      items: [],
      outlet_id: null,
      table_id: null,
      waiter_id: null,
      order_type: 'dine_in',
      isOpen: false,

      toggleCart: () => set({ isOpen: !get().isOpen }),
      openCart: () => set({ isOpen: true }),
      closeCart: () => set({ isOpen: false }),

      setOutlet: (outlet_id) => set({ outlet_id }),
      setTable: (table_id) => set({ table_id }),
      setWaiter: (waiter_id) => set({ waiter_id }),
      setOrderType: (order_type) => set({ order_type }),

      addItem: (newItem) => {
        const currentItems = get().items;
        const existingItem = currentItems.find((i) => i.menu_item_id === newItem.menu_item_id && !i.voided);

        if (existingItem) {
          set({
            items: currentItems.map((i) =>
              i.menu_item_id === newItem.menu_item_id && !i.voided
                ? { ...i, quantity: i.quantity + newItem.quantity }
                : i
            ),
          });
        } else {
          set({ items: [...currentItems, { ...newItem, discount_cents: 0, voided: false }] });
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

      applyDiscount: (menu_item_id, discount_cents) => {
        set({
          items: get().items.map((i) =>
            i.menu_item_id === menu_item_id ? { ...i, discount_cents } : i
          )
        });
      },

      voidItem: (menu_item_id) => {
        set({
          items: get().items.map((i) =>
            i.menu_item_id === menu_item_id ? { ...i, voided: true } : i
          )
        });
      },

      clearCart: () => set({ items: [], table_id: null, waiter_id: null, order_type: 'dine_in' }),

      getSubtotalCents: () => {
        return get().items.reduce((total, item) => {
          if (item.voided) return total;
          return total + (item.price_kes_cents * item.quantity);
        }, 0);
      },

      getTotalCents: () => {
        return get().items.reduce((total, item) => {
          if (item.voided) return total;
          const itemTotal = (item.price_kes_cents * item.quantity) - (item.discount_cents || 0);
          return total + Math.max(0, itemTotal);
        }, 0);
      },
    }),
    {
      name: 'tablewise-pos-cart',
      partialize: (state) => ({ 
        items: state.items, 
        outlet_id: state.outlet_id, 
        table_id: state.table_id,
        order_type: state.order_type
      }),
    }
  )
);
