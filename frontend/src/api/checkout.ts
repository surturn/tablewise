import { apiClient } from './client';
import { queueOrderWhenOffline } from '../utils/offlineOrderQueue';

export type PaymentProvider = 'cash' | 'mobile_money' | 'stripe';

export interface CheckoutPayload {
  outlet_id: string;
  guest: {
    phone_number: string;
    full_name: string;
  };
  items: Array<{ menu_item_id: string; quantity: number }>;
  payment_method: PaymentProvider;
  notes?: string;
  order_type: 'dine_in' | 'delivery' | 'takeaway' | 'room_service';
  is_delivery: boolean;
  delivery_address?: string;
}

export async function submitCheckoutOrder(payload: CheckoutPayload) {
  try {
    const { data } = await apiClient.post('/orders/', payload);
    return data;
  } catch (error) {
    if (!navigator.onLine) {
      await queueOrderWhenOffline(payload);
      // We'll throw an offline-specific error that the UI can catch to show a Toast
      throw new Error('OFFLINE_QUEUED');
    }
    throw error;
  }
}

export async function processCheckout(
  phoneNumber: string, 
  fullName: string, 
  items: Array<{ menu_item_id: string; quantity: number; outlet_id?: string }>,
  paymentMethod: PaymentProvider = 'cash',
  notes?: string
) {
  const outletId = items.find((item) => item.outlet_id)?.outlet_id;
  if (!outletId) throw new Error('Please select an outlet before checkout.');
  
  const payload: CheckoutPayload = {
    outlet_id: outletId,
    guest: { phone_number: phoneNumber, full_name: fullName },
    items: items.map((item) => ({ menu_item_id: item.menu_item_id, quantity: item.quantity })),
    payment_method: paymentMethod,
    notes,
    order_type: 'takeaway',
    is_delivery: false
  };
  
  return submitCheckoutOrder(payload);
}
