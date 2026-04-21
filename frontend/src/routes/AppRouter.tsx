import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';

// Public Pages
import Home from '../pages/Public/Home';
import Menu from '../pages/Public/Menu';
import Login from '../pages/Auth/Login';
import Navbar from '../components/Layout/Navbar';

// Protected Pages & Layouts
import { ProtectedRoute } from '../components/Layout/ProtectedRoute';
import DashboardLayout from '../components/Layout/DashboardLayout';
import DashboardHome from '../pages/Dashboard/DashboardHome';

const AppRouter: React.FC = () => {
  return (
    <BrowserRouter>
      <Routes>
        {/* Public Routes with Navbar */}
        <Route element={<><Navbar /></>}>
          <Route path="/" element={<Home />} />
          <Route path="/menu" element={<Menu />} />
        </Route>

        {/* Auth Route without Navbar */}
        <Route path="/login" element={<Login />} />

        {/* Protected Dashboard Routes */}
        <Route element={<ProtectedRoute />}>
          <Route path="/dashboard" element={<DashboardLayout />}>
            <Route index element={<DashboardHome />} />
            <Route path="orders" element={<div className="text-gray-500">Orders page coming in next step...</div>} />
            <Route path="inventory" element={<div className="text-gray-500">Inventory page coming soon...</div>} />
            <Route path="customers" element={<div className="text-gray-500">Customers page coming soon...</div>} />
          </Route>
        </Route>
      </Routes>
    </BrowserRouter>
  );
};

export default AppRouter;