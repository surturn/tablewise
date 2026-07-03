import React from 'react';
import { motion } from 'framer-motion';

const menuItems = [
  { id: 1, title: 'Vegetable Dishes', image: '/images/landingPage/Pasta.png' },
  { id: 2, title: 'Rice Dishes', image: '/images/landingPage/drumsticks.jpg' },
  { id: 3, title: 'Tandoori Breads', image: '/images/landingPage/friedFish.jpg' },
  { id: 4, title: 'Desserts', image: '/images/landingPage/pancakes.png' },
];

export const MenuSection: React.FC = () => {
  return (
    <section className="py-24 bg-[#1e2024]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {/* Section Header */}
        <div className="text-center mb-16">
          <h2 className="text-3xl font-bold text-white mb-4">Our Menu</h2>
          <div className="flex items-center justify-center gap-2">
            <div className="h-[1px] w-12 bg-yellow-600/50" />
            <div className="w-2 h-2 rotate-45 border border-yellow-600/50" />
            <div className="h-[1px] w-12 bg-yellow-600/50" />
          </div>
        </div>

        {/* Menu Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8">
          {menuItems.map((item, index) => (
            <motion.div 
              key={item.id}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, amount: 0.2 }}
              transition={{ delay: index * 0.1, duration: 0.6 }}
              className="flex flex-col items-center"
            >
              <div className="relative w-full aspect-[4/5] bg-[#2a2c33] rounded-t-[100px] rounded-b-md flex flex-col items-center pt-8 pb-6 px-4 shadow-lg hover:bg-[#32353d] transition-colors cursor-pointer group">
                {/* Circular Image Container */}
                <div className="w-40 h-40 rounded-full overflow-hidden shadow-xl mb-6 ring-4 ring-[#1e2024] group-hover:scale-105 transition-transform duration-300">
                  <img 
                    src={item.image} 
                    alt={item.title} 
                    className="w-full h-full object-cover"
                  />
                </div>
                
                {/* Subtle Gold Pattern Divider */}
                <div className="w-16 h-4 bg-[url('data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI0IiBoZWlnaHQ9IjQiPjxyZWN0IHdpZHRoPSI0IiBoZWlnaHQ9IjQiIGZpbGw9IiNkNGFmMzciIGZpbGwtb3BhY2l0eT0iMC4yIi8+PC9zdmc+')] mb-4" />
                
                <h3 className="text-lg font-bold text-white mt-auto text-center">{item.title}</h3>
              </div>
            </motion.div>
          ))}
        </div>

      </div>
    </section>
  );
};
