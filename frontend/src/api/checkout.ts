import { apiClient } from './client';

type PaymentMethod = 'stripe' | 'mobile_money' | 'cash';

// Helper to handle the entire checkout orchestration with Stripe, mobile money, or cash fallback.
export const processCheckout = async (
  phone_number: string,
  fullName: string,
  items: any[],
  paymentMethod: PaymentMethod = 'stripe'
) => {
  // 1. Get or Create Customer
  const customerRes = await apiClient.post('/customers/', {
    phone_number,
    full_name: fullName,
  });
  const customerId = customerRes.data.id;

  // 2. Get an Outlet (For MVP, just grab the first available outlet/legacy branch)
  const branchesRes = await apiClient.get('/branches/');
  if (branchesRes.data.length === 0) {
    throw new Error('No active outlets found. Please contact support.');
  }
  const branchId = branchesRes.data[0].id;

  // 3. Create Order
  const orderRes = await apiClient.post('/orders/', {
    branch_id: branchId,
    customer_id: customerId,
    items: items.map(i => ({ menu_item_id: i.menu_item_id, quantity: i.quantity })),
    is_delivery: false // Defaulting to pickup for simplicity right now
  });
  const orderId = orderRes.data.id;

  // 4. Select payment rail; Stripe is primary, cash/mobile-money keep checkout available.
  if (paymentMethod === 'stripe') {
    const paymentRes = await apiClient.post('/payments/stripe/checkout', {
      order_id: orderId,
      success_url: `${window.location.origin}/checkout/success?order_id=${orderId}`,
      cancel_url: `${window.location.origin}/menu?payment=cancelled`,
    });
    return paymentRes.data;
  }

  if (paymentMethod === 'mobile_money') {
    const paymentRes = await apiClient.post('/payments/mobile-money', {
      order_id: orderId,
      phone_number,
      provider: 'africas_talking',
    });
    return paymentRes.data;
  }

  const paymentRes = await apiClient.post('/payments/cash', {
    order_id: orderId,
    collection_note: `Guest checkout for ${fullName}`,
  });
  return paymentRes.data;
};
