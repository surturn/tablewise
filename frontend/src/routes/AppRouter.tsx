import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import CartDrawer from '../components/Cart/CartDrawer';
import { ToastContainer } from '../components/ui/Toast';

// Layouts
import CustomerLayout from '../components/Layout/CustomerLayout';
import POSLayout from '../components/Layout/POSLayout';
import StaffLayout from '../components/Layout/StaffLayout';
import DashboardLayout from '../components/Layout/DashboardLayout';
import { ProtectedRoute } from '../components/Layout/ProtectedRoute';

// Public/Customer Pages (Placeholders or existing)
import HomePage from '../pages/Public/HomePage';
import Menu from '../pages/Public/Menu';
import Book from '../pages/Public/Book';
import CustomerDashboard from '../pages/customer/CustomerDashboard';
import DineFlow from '../pages/customer/DineFlow';
import DrinkFlow from '../pages/customer/DrinkFlow';
import StayFlow from '../pages/customer/StayFlow';

// Auth
import Login from '../pages/Auth/Login';
import StaffLogin from '../pages/Auth/StaffLogin';

// Admin / Manager Dashboards
import DashboardHome from '../pages/Dashboard/DashboardHome';
import OrdersFeed from '../pages/Dashboard/OrdersFeed';
import RoomsPage from '../pages/Dashboard/RoomsPage';
import AnalyticsPage from '../pages/Dashboard/AnalyticsPage';
import InventoryManagement from '../pages/Dashboard/InventoryManagement';
import ReservationsPage from '../pages/Dashboard/ReservationsPage';
import HousekeepingPage from '../pages/Dashboard/HousekeepingPage';
import CustomersManagement from '../pages/Dashboard/CustomersManagement';

const AppRouter = () => {
  return (
    <BrowserRouter
      future={{
        v7_startTransition: true,
        v7_relativeSplatPath: true,
      }}
    >
      <Routes>
        {/* Auth Routes */}
        <Route path="/login" element={<Login />} />
        <Route path="/staff/login" element={<StaffLogin />} />

        {/* 1. Public Marketing Flow (CustomerLayout) */}
        <Route path="/" element={<CustomerLayout />}>
          <Route index element={<HomePage />} />
          <Route path="menu" element={<Menu />} />
          <Route path="book" element={<Book />} />
        </Route>

        {/* 1b. Authenticated Customer App Flow.
            These pages each render their own complete chrome via
            <CustomerNavbar/> (nav, cart, profile menu) - they don't nest
            under CustomerLayout because CustomerLayout renders its own
            separate marketing header, which would double up with
            CustomerNavbar on every one of these pages. */}
        <Route path="/customer/dashboard" element={
          <ProtectedRoute roles={['customer']}><CustomerDashboard /></ProtectedRoute>
        } />
        <Route path="/customer/dine" element={
          <ProtectedRoute roles={['customer']}><DineFlow /></ProtectedRoute>
        } />
        <Route path="/customer/drink" element={
          <ProtectedRoute roles={['customer']}><DrinkFlow /></ProtectedRoute>
        } />
        <Route path="/customer/stay" element={
          <ProtectedRoute roles={['customer']}><StayFlow /></ProtectedRoute>
        } />

        {/* 2. Kitchen & FOH Flow (POSLayout) */}
        <Route path="/pos" element={
          <ProtectedRoute roles={['chef', 'waiter', 'bartender', 'owner', 'restaurant_manager']}>
            <POSLayout />
          </ProtectedRoute>
        }>
          <Route index element={<div className="p-8">POS Terminal Catalog</div>} />
          <Route path="tables" element={<div className="p-8">Table Management</div>} />
          <Route path="orders" element={<div className="p-8">KDS / Order Tickets</div>} />
        </Route>

        {/* 3. Front Desk & Delivery Flow (StaffLayout) */}
        <Route path="/staff" element={
          <ProtectedRoute roles={['receptionist', 'rider', 'owner', 'hotel_manager']}>
            <StaffLayout />
          </ProtectedRoute>
        }>
          <Route path="reception" element={<div className="p-8">Receptionist Approval Queue</div>} />
          <Route path="delivery" element={<div className="p-8">Rider Delivery Status</div>} />
        </Route>

        {/* 4. Unified Staff Dashboard (DashboardLayout).
            Every staff role redirects here after login via ROLE_DASHBOARD_MAP
            (see constants/roles.ts + useAuthRedirect.ts) - the outer gate must
            accept every staff role or roles whose target page lives under a
            restricted route would hit a redirect loop (ProtectedRoute sends a
            mismatched role back to its own ROLE_DASHBOARD_MAP target). Finer
            per-role visibility within the dashboard is a follow-up; the
            backend's require_roles checks remain the real authorization
            boundary for these pages' underlying API calls. */}
        <Route path="/dashboard" element={
          <ProtectedRoute roles={['owner', 'hotel_manager', 'restaurant_manager', 'receptionist', 'chef', 'bartender', 'waiter', 'rider']}>
            <DashboardLayout />
          </ProtectedRoute>
        }>
          <Route index element={<DashboardHome />} />
          <Route path="orders" element={<OrdersFeed />} />
          <Route path="rooms" element={<RoomsPage />} />
          <Route path="reservations" element={<ReservationsPage />} />
          <Route path="housekeeping" element={<HousekeepingPage />} />
          <Route path="inventory" element={<InventoryManagement />} />
          <Route path="customers" element={<CustomersManagement />} />
          <Route path="analytics" element={<AnalyticsPage />} />
          <Route path="staff" element={
            <ProtectedRoute roles={['owner']}><div className="p-8">Staff Management</div></ProtectedRoute>
          } />
        </Route>

        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>

      {/* Rendered inside BrowserRouter (not in App.tsx) because CartDrawer calls
          useNavigate(), which throws outside a Router context - it previously
          crashed the whole app to a blank screen on every single page load. */}
      <CartDrawer />
      <ToastContainer />
    </BrowserRouter>
  );
};

export default AppRouter;