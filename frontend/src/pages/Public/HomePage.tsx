import React from 'react';
import { Hero } from '../../components/landing/Hero';
import { MenuSection } from '../../components/landing/MenuSection';
import { DeliverySection } from '../../components/landing/DeliverySection';
import { OpeningHoursSection } from '../../components/landing/OpeningHoursSection';

const HomePage: React.FC = () => {
  return (
    <div className="min-h-screen bg-[#1e2024] font-sans selection:bg-yellow-600/30 selection:text-white flex flex-col">
      <Hero />
      <MenuSection />
      <DeliverySection />
      <OpeningHoursSection />
      
      {/* Footer */}
      <footer className="py-12 border-t border-gray-800 bg-[#15161a] text-center text-gray-500 text-sm mt-auto">
        <p>&copy; {new Date().getFullYear()} Cuisine Wave Restaurant. All rights reserved.</p>
      </footer>
    </div>
  );
};

export default HomePage;