import React from 'react';
import { motion } from 'framer-motion';

export const DeliverySection: React.FC = () => {
  return (
    <section className="py-24 bg-[#1a1c20] border-t border-gray-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
        
        {/* Left Typography */}
        <div>
          <h2 className="text-3xl font-bold text-white mb-4">Food Delivery</h2>
          <div className="flex items-center gap-2 mb-8">
            <div className="h-[1px] w-12 bg-yellow-600/50" />
            <div className="w-2 h-2 rotate-45 border border-yellow-600/50" />
            <div className="h-[1px] w-12 bg-yellow-600/50" />
          </div>

          <p className="text-gray-400 text-sm mb-6 leading-relaxed">
            It is a long established fact that a reader will be distracted by the readable content of a page when looking at its layout. The point of using Lorem Ipsum is that it has a more-or-less normal distribution of letters, as opposed to using 'Content here, content here', making it look like readable English.
          </p>
          <p className="text-gray-400 text-sm mb-10 leading-relaxed">
            Many desktop publishing packages and web page editors now use Lorem Ipsum as their default model text, and a search for 'lorem ipsum'.
          </p>

          <h3 className="text-lg font-bold text-white mb-4">Delivery fee</h3>
          <ul className="space-y-3">
            <li className="text-gray-400 text-sm">
              <span className="text-[#d4af37] font-semibold mr-2">Zone 1,</span>
              Min - $60.00, Fee - $7.00
            </li>
            <li className="text-gray-400 text-sm">
              <span className="text-[#d4af37] font-semibold mr-2">Zone 2,</span>
              Min - $60.00, Fee - $10.00
            </li>
          </ul>
        </div>

        {/* Right Asset (Map) */}
        <motion.div
          initial={{ opacity: 0, x: 50 }}
          whileInView={{ opacity: 1, x: 0 }}
          viewport={{ once: true, amount: 0.3 }}
          transition={{ duration: 0.8 }}
          className="w-full bg-white rounded-md shadow-2xl overflow-hidden h-[400px]"
        >
          {/* Using a placeholder light map image */}
          <div className="w-full h-full bg-gray-100 flex items-center justify-center text-gray-400 relative">
            <img 
              src="https://images.unsplash.com/photo-1524661135-423995f22d0b?auto=format&fit=crop&q=80&w=800" 
              alt="Delivery Map Area" 
              className="absolute inset-0 w-full h-full object-cover opacity-80"
              style={{ filter: 'grayscale(100%) contrast(1.2)' }}
            />
            <div className="absolute inset-0 bg-white/40" />
            <span className="relative z-10 font-medium">Map Area Placeholder</span>
          </div>
        </motion.div>

      </div>
    </section>
  );
};
