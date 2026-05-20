import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import HomePage from '../pages/Public/HomePage';
import Menu from '../pages/Public/Menu';
import Book from '../pages/Public/Book';
import Login from '../pages/Auth/Login';
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
        
        <Route path="/dashboard" element={<ProtectedRoute><DashboardLayout /></ProtectedRoute>}>
          <Route index element={<DashboardHome />} />
          <Route path="orders" element={<OrdersFeed />} />
          <Route path="rooms" element={<RoomsPage />} />
          <Route path="reservations" element={<ReservationsPage />} />
          <Route path="housekeeping" element={<HousekeepingPage />} />
          <Route path="inventory" element={<InventoryManagement />} />
          <Route path="customers" element={<CustomersManagement />} />
          <Route path="analytics" element={<AnalyticsPage />} />
        </Route>

        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
};

export default AppRouter;