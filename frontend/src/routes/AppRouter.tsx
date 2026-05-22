import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import HomePage from '../pages/Public/HomePage';
import Menu from '../pages/Public/Menu';
import Book from '../pages/Public/Book';
import Login from '../pages/Auth/Login';
import StaffLogin from '../pages/Auth/StaffLogin';
import DashboardLayout from '../components/Layout/DashboardLayout';
import { ProtectedRoute } from '../components/Layout/ProtectedRoute';
import DashboardHome from '../pages/Dashboard/DashboardHome';
import OrdersFeed from '../pages/Dashboard/OrdersFeed';
import RoomsPage from '../pages/Dashboard/RoomsPage';
import ReservationsPage from '../pages/Dashboard/ReservationsPage';
import HousekeepingPage from '../pages/Dashboard/HousekeepingPage';
import InventoryManagement from '../pages/Dashboard/InventoryManagement';
import CustomersManagement from '../pages/Dashboard/CustomersManagement';
import AnalyticsPage from '../pages/Dashboard/AnalyticsPage';

import CustomerDashboard from '../pages/customer/CustomerDashboard';
import DineFlow from '../pages/customer/DineFlow';
import StayFlow from '../pages/customer/StayFlow';
import DrinkFlow from '../pages/customer/DrinkFlow';

const AppRouter = () => {
  return (
    <BrowserRouter
      future={{
        v7_startTransition: true,
        v7_relativeSplatPath: true,
      }}
    >
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/menu" element={<Menu />} />
        <Route path="/book" element={<Book />} />
        <Route path="/login" element={<Login />} />
        <Route path="/staff/login" element={<StaffLogin />} />
        
        <Route path="/customer">
          <Route path="dashboard" element={<ProtectedRoute roles={['customer']}><CustomerDashboard /></ProtectedRoute>} />
          <Route path="dine" element={<ProtectedRoute roles={['customer']}><DineFlow /></ProtectedRoute>} />
          <Route path="stay" element={<ProtectedRoute roles={['customer']}><StayFlow /></ProtectedRoute>} />
          <Route path="drink" element={<ProtectedRoute roles={['customer']}><DrinkFlow /></ProtectedRoute>} />
        </Route>
        
        <Route path="/dashboard" element={<ProtectedRoute roles={['owner', 'hotel_manager', 'restaurant_manager', 'chef', 'waiter', 'bartender', 'receptionist', 'rider']}><DashboardLayout /></ProtectedRoute>}>
          <Route index element={<ProtectedRoute roles={['owner', 'hotel_manager']}><DashboardHome /></ProtectedRoute>} />
          <Route path="orders" element={<ProtectedRoute roles={['owner', 'hotel_manager', 'restaurant_manager', 'chef', 'waiter', 'bartender', 'rider']}><OrdersFeed /></ProtectedRoute>} />
          <Route path="rooms" element={<ProtectedRoute roles={['owner', 'hotel_manager', 'receptionist']}><RoomsPage /></ProtectedRoute>} />
          <Route path="reservations" element={<ProtectedRoute roles={['owner', 'hotel_manager', 'receptionist']}><ReservationsPage /></ProtectedRoute>} />
          <Route path="housekeeping" element={<ProtectedRoute roles={['owner', 'hotel_manager', 'receptionist']}><HousekeepingPage /></ProtectedRoute>} />
          <Route path="inventory" element={<ProtectedRoute roles={['owner', 'hotel_manager', 'restaurant_manager']}><InventoryManagement /></ProtectedRoute>} />
          <Route path="customers" element={<ProtectedRoute roles={['owner', 'hotel_manager', 'receptionist']}><CustomersManagement /></ProtectedRoute>} />
          <Route path="analytics" element={<ProtectedRoute roles={['owner', 'hotel_manager']}><AnalyticsPage /></ProtectedRoute>} />
        </Route>

        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
};

export default AppRouter;