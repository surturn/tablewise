import { apiClient } from './client';
import { queueOrderWhenOffline } from '../utils/offlineOrderQueue';

export async function submitCheckoutOrder(payload: unknown) {
  try {
    const { data } = await apiClient.post('/orders/', payload);
    return data;
  } catch (error) {
    if (!navigator.onLine) {
      await queueOrderWhenOffline(payload);
      window.alert('You are offline. Your GrandPlatform order has been queued and will submit automatically when the connection returns.');
    }
    throw error;
  }
}

export async function processCheckout(phoneNumber: string, fullName: string, items: Array<{ menu_item_id: string; quantity: number; outlet_id?: string }>) {
  const outletId = items.find((item) => item.outlet_id)?.outlet_id;
  if (!outletId) throw new Error('Please select an outlet before checkout.');
  const payload = {
    outlet_id: outletId,
    guest: { phone_number: phoneNumber, full_name: fullName },
    items: items.map((item) => ({ menu_item_id: item.menu_item_id, quantity: item.quantity })),
    payment_method: 'stripe',
  };
  return submitCheckoutOrder(payload);
}
