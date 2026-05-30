import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';

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

// Auth
import Login from '../pages/Auth/Login';
import StaffLogin from '../pages/Auth/StaffLogin';

// Admin / Manager Dashboards
import DashboardHome from '../pages/Dashboard/DashboardHome';
import OrdersFeed from '../pages/Dashboard/OrdersFeed';
import RoomsPage from '../pages/Dashboard/RoomsPage';
import AnalyticsPage from '../pages/Dashboard/AnalyticsPage';
import InventoryManagement from '../pages/Dashboard/InventoryManagement';

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

        {/* 1. Customer Flow (CustomerLayout) */}
        <Route path="/" element={<CustomerLayout />}>
          <Route index element={<HomePage />} />
          <Route path="menu" element={<Menu />} />
          <Route path="book" element={<Book />} />
          <Route path="customer/dashboard" element={
            <ProtectedRoute roles={['customer']}><CustomerDashboard /></ProtectedRoute>
          } />
          {/* Add Cart/Checkout, Live Tracking, etc. here */}
        </Route>

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

        {/* 4. Manager Flow (DashboardLayout) */}
        <Route path="/manager" element={
          <ProtectedRoute roles={['hotel_manager', 'restaurant_manager', 'owner']}>
            <DashboardLayout />
          </ProtectedRoute>
        }>
          <Route index element={<DashboardHome />} />
          <Route path="orders" element={<OrdersFeed />} />
          <Route path="rooms" element={<RoomsPage />} />
          <Route path="inventory" element={<InventoryManagement />} />
        </Route>

        {/* 5. Owner Flow (DashboardLayout) */}
        <Route path="/owner" element={
          <ProtectedRoute roles={['owner']}>
            <DashboardLayout />
          </ProtectedRoute>
        }>
          <Route index element={<DashboardHome />} />
          <Route path="analytics" element={<AnalyticsPage />} />
          <Route path="staff" element={<div className="p-8">Staff Management</div>} />
        </Route>

        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
};

export default AppRouter;