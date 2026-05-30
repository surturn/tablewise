import { create } from 'zustand';

export interface Order {
  id: string;
  status: 'pending' | 'preparing' | 'ready' | 'delivered' | 'cancelled';
  items: any[]; // refine type later
  table_id?: string;
  room_number?: string;
  created_at: string;
  type: 'dine_in' | 'takeaway' | 'room_service';
}

interface ActiveOrdersState {
  orders: Order[];
  setOrders: (orders: Order[]) => void;
  addOrder: (order: Order) => void;
  updateOrderStatus: (orderId: string, status: Order['status']) => void;
  removeOrder: (orderId: string) => void;
}

export const useActiveOrdersStore = create<ActiveOrdersState>((set) => ({
  orders: [],
  setOrders: (orders) => set({ orders }),
  addOrder: (order) => set((state) => ({ orders: [...state.orders, order] })),
  updateOrderStatus: (orderId, status) =>
    set((state) => ({
      orders: state.orders.map((o) => (o.id === orderId ? { ...o, status } : o)),
    })),
  removeOrder: (orderId) =>
    set((state) => ({
      orders: state.orders.filter((o) => o.id !== orderId),
    })),
}));
