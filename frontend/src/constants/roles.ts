export const STAFF_ROLES = [
  'owner', 'hotel_manager', 'restaurant_manager',
  'receptionist', 'chef', 'bartender', 'waiter', 'rider'
] as const;

export type StaffRole = typeof STAFF_ROLES[number];
export type UserRole = StaffRole | 'customer';

export const ROLE_DASHBOARD_MAP: Record<StaffRole, string> = {
  owner: '/dashboard',
  hotel_manager: '/dashboard',
  restaurant_manager: '/dashboard/inventory', // Or specific start page if needed
  chef: '/dashboard/orders',
  waiter: '/dashboard/orders',
  receptionist: '/dashboard/rooms',
  bartender: '/dashboard/orders',
  rider: '/dashboard/orders',
};

export const isStaffRole = (role: string): role is StaffRole =>
  (STAFF_ROLES as readonly string[]).includes(role);
