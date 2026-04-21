import { apiClient } from './client';

// Helper to handle the entire checkout orchestration
export const processCheckout = async (
  phone_number: string,
  fullName: string,
  items: any[]
) => {
  // 1. Get or Create Customer
  const customerRes = await apiClient.post('/customers/', {
    phone_number,
    full_name: fullName,
  });
  const customerId = customerRes.data.id;

  // 2. Get a Branch (For MVP, just grab the first available branch)
  const branchesRes = await apiClient.get('/branches/');
  if (branchesRes.data.length === 0) {
    throw new Error("No active branches found. Please contact support.");
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

  // 4. Trigger M-Pesa STK Push
  const paymentRes = await apiClient.post('/payments/stk-push', {
    order_id: orderId,
    phone_number
  });

  return paymentRes.data;
};