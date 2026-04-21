import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Home from '../pages/Public/Home';

const AppRouter: React.FC = () => {
  return (
    <BrowserRouter>
      <Routes>
        {/* Public Routes */}
        <Route path="/" element={<Home />} />

        {/* Future Routes will be mounted here (e.g., /dashboard, /menu, /checkout) */}
      </Routes>
    </BrowserRouter>
  );
};

export default AppRouter;