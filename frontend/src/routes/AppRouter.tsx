import React from 'react';
import { BrowserRouter, Routes, Route, Outlet } from 'react-router-dom';

// Public Pages
import HomePage from '../pages/Public/HomePage';
import Menu from '../pages/Public/Menu';
import Login from '../pages/Auth/Login';
import Navbar from '../components/Layout/Navbar';

// Protected Pages & Layouts
import { ProtectedRoute } from '../components/Layout/ProtectedRoute';
import DashboardLayout from '../components/Layout/DashboardLayout';
import DashboardHome from '../pages/Dashboard/DashboardHome';
import OrdersFeed from '../pages/Dashboard/OrdersFeed';
import InventoryManagement from '../pages/Dashboard/InventoryManagement';
import AnalyticsPage from '../pages/Dashboard/AnalyticsPage';
import CustomersManagement from '../pages/Dashboard/CustomersManagement';

// Create a simple Public Layout wrapper that includes the Outlet
const PublicLayout = () => (
  <>
    <Navbar />
    {/* Outlet is CRITICAL! It tells React Router where to render HomePage or Menu */}
    <Outlet />
  </>
);

const AppRouter: React.FC = () => {
  return (
    <BrowserRouter>
      <Routes>
        {/* Public Routes using the PublicLayout */}
        <Route element={<PublicLayout />}>
          <Route path="/" element={<HomePage />} />
          <Route path="/menu" element={<Menu />} />
        </Route>

        {/* Auth Route without Navbar */}
        <Route path="/login" element={<Login />} />

        {/* Protected Dashboard Routes */}
        <Route element={<ProtectedRoute />}>
          <Route path="/dashboard" element={<DashboardLayout />}>
            <Route index element={<DashboardHome />} />
            <Route path="orders" element={<OrdersFeed />} />
            <Route path="inventory" element={<InventoryManagement />} />
            <Route path="customers" element={<CustomersManagement />} />
            <Route path="analytics" element={<AnalyticsPage />} />
          </Route>
        </Route>
      </Routes>
    </BrowserRouter>
  );
};

export default AppRouter;