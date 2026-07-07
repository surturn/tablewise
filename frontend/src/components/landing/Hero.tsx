import React from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';

export const Hero: React.FC = () => {
  const navigate = useNavigate();

  return (
    <section className="relative min-h-[90vh] flex items-center bg-[#1e2024] overflow-hidden">
      {/* Background Gold Banner */}
      <div className="absolute top-1/2 left-0 right-0 h-40 bg-gradient-to-r from-yellow-700/80 to-yellow-600/80 -translate-y-1/2 opacity-60 pointer-events-none" />
      
      {/* Subtle background texture */}
      <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB2aWV3Qm94PSIwIDAgMjAwIDIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZmlsdGVyIGlkPSJub2lzZUZpbHRlciI+PGZlVHVyYnVsZW5jZSB0eXBlPSJmcmFjdGFsTm9pc2UiIGJhc2VGcmVxdWVuY3k9IjAuNjUiIG51bU9jdGF2ZXM9IjMiIHN0aXRjaFRpbGVzPSJzdGl0Y2giLz48L2ZpbHRlcj48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWx0ZXI9InVybCgibm9pc2VGaWx0ZXIpIiBvcGFjaXR5PSIwLjA1Ii8+PC9zdmc+')] opacity-20 pointer-events-none mix-blend-overlay" />

      {/* Floating Elements (Leaves/Spices) */}
      <motion.div 
        animate={{ y: [0, -20, 0], rotate: [0, 10, 0] }}
        transition={{ duration: 5, repeat: Infinity, ease: "easeInOut" }}
        className="absolute top-[20%] left-[10%] w-8 h-8 bg-red-600 rounded-full blur-[2px] opacity-70"
        style={{ borderRadius: '50% 0 50% 50%' }}
      />
      <motion.div 
        animate={{ y: [0, 30, 0], rotate: [0, -15, 0] }}
        transition={{ duration: 7, repeat: Infinity, ease: "easeInOut", delay: 1 }}
        className="absolute bottom-[20%] right-[10%] w-6 h-6 bg-red-500 rounded-full blur-[1px] opacity-80"
        style={{ borderRadius: '0 50% 50% 50%' }}
      />

      <div className="max-w-7xl mx-auto w-full px-4 sm:px-6 lg:px-8 grid grid-cols-1 lg:grid-cols-2 gap-12 items-center relative z-10">
        
        {/* Left Typography */}
        <motion.div 
          initial={{ opacity: 0, x: -50 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.8, ease: "easeOut" }}
          className="flex flex-col items-start text-left"
        >
          <p className="text-gray-300 text-lg sm:text-xl font-medium tracking-wide mb-2 font-serif italic">
            Taste & Feel the Spirit of Best Quality of
          </p>
          
          <h1 className="text-5xl sm:text-7xl font-black text-white leading-tight tracking-tight mb-8 drop-shadow-lg">
            Cuisine Wave <br/>
            Restaurant
          </h1>

          <div className="flex gap-4">
            <motion.button
              onClick={() => navigate('/menu')}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="px-8 py-3 rounded-md bg-[#e3342f] text-white font-bold tracking-wide shadow-lg hover:bg-red-700 transition-colors"
            >
              View Menu
            </motion.button>
            <motion.button
              onClick={() => navigate('/menu')}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="px-8 py-3 rounded-md bg-[#d4af37] text-gray-900 font-bold tracking-wide shadow-lg hover:bg-yellow-500 transition-colors"
            >
              Order Now
            </motion.button>
          </div>
        </motion.div>

        {/* Right Asset (Food Plate) */}
        <div className="relative w-full h-[500px] flex items-center justify-center">
          <motion.div
            initial={{ opacity: 0, scale: 0.8, rotate: -10 }}
            animate={{ opacity: 1, scale: 1, rotate: 0 }}
            transition={{ duration: 1, type: "spring", bounce: 0.4 }}
            className="w-full max-w-[600px] h-auto relative z-20 drop-shadow-[0_20px_30px_rgba(0,0,0,0.6)]"
          >
            {/* Using the sushi asset as a placeholder for the pizza */}
            <img 
              src="/images/landingPage/assortedSushi.png" 
              alt="Delicious Cuisine" 
              className="w-full h-auto object-contain scale-[1.2] origin-center"
            />
          </motion.div>
        </div>

      </div>
    </section>
  );
};
