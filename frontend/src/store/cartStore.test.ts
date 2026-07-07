import { beforeEach, describe, expect, it } from 'vitest';
import { useCartStore } from './cartStore';

const burger = {
  menu_item_id: 'item-1',
  name: 'Cheeseburger',
  price_kes_cents: 1200,
  quantity: 1,
};

const fries = {
  menu_item_id: 'item-2',
  name: 'Fries',
  price_kes_cents: 400,
  quantity: 1,
};

beforeEach(() => {
  useCartStore.setState({ items: [], outlet_id: null, isOpen: false });
});

describe('cartStore', () => {
  it('adds a new item and opens the cart', () => {
    useCartStore.getState().addItem(burger);

    const { items, isOpen } = useCartStore.getState();
    expect(items).toHaveLength(1);
    expect(items[0].quantity).toBe(1);
    expect(isOpen).toBe(true);
  });

  it('merges quantities when the same menu item is added twice', () => {
    useCartStore.getState().addItem(burger);
    useCartStore.getState().addItem({ ...burger, quantity: 2 });

    const { items } = useCartStore.getState();
    expect(items).toHaveLength(1);
    expect(items[0].quantity).toBe(3);
  });

  it('computes the order total across multiple line items', () => {
    useCartStore.getState().addItem(burger); // 1 x 1200
    useCartStore.getState().addItem({ ...fries, quantity: 2 }); // 2 x 400

    expect(useCartStore.getState().getTotalCents()).toBe(1200 + 2 * 400);
  });

  it('updateQuantity removes the line item once quantity drops to zero', () => {
    useCartStore.getState().addItem(burger);
    useCartStore.getState().updateQuantity(burger.menu_item_id, 0);

    expect(useCartStore.getState().items).toHaveLength(0);
  });

  it('clearCart empties the cart and resets the outlet', () => {
    useCartStore.getState().setOutlet('outlet-1');
    useCartStore.getState().addItem(burger);

    useCartStore.getState().clearCart();

    const { items, outlet_id } = useCartStore.getState();
    expect(items).toHaveLength(0);
    expect(outlet_id).toBeNull();
  });
});
