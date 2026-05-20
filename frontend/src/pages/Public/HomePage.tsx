import React from 'react';
import { Link } from 'react-router-dom';
import { m, useScroll, useTransform } from 'framer-motion';
import { springs, FadeIn } from '../../components/ui/MotionConfig';

const HomePage: React.FC = () => {
  const { scrollY } = useScroll();
  const y1 = useTransform(scrollY, [0, 1000], [0, 200]);
  const y2 = useTransform(scrollY, [0, 1000], [0, -100]);

  return (
    <div className="relative min-h-screen overflow-hidden bg-brand-dark text-white flex flex-col">
      {/* Background Gradients */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <m.div style={{ y: y1 }} className="absolute -top-[20%] -left-[10%] w-[50%] h-[50%] rounded-full bg-brand-orange/20 blur-[120px]" />
        <m.div style={{ y: y2 }} className="absolute top-[40%] -right-[10%] w-[40%] h-[60%] rounded-full bg-stone-700/30 blur-[120px]" />
      </div>

      <div className="relative z-10 max-w-7xl mx-auto px-6 w-full flex-1 flex items-center pt-20">
        <div className="max-w-3xl">
          <m.h1 
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ ...springs.smooth, delay: 0.1 }}
            className="text-6xl md:text-8xl font-black mb-6 leading-tight tracking-tight"
          >
            Table<span className="text-brand-orange">Wise.</span>
          </m.h1>
          <m.p 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ ...springs.smooth, delay: 0.3 }}
            className="text-xl md:text-2xl text-stone-300 mb-10 font-light max-w-2xl leading-relaxed"
          >
            A unified hospitality platform for Juba: rooms, restaurant delivery, bar tabs, offline-first POS, Stripe, cash, and mobile money in USD.
          </m.p>
          <m.div 
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ ...springs.snappy, delay: 0.5 }}
            className="flex flex-wrap gap-4"
          >
            <Link to="/menu" className="inline-block bg-brand-orange text-brand-dark font-bold text-lg px-8 py-4 rounded-full shadow-[0_0_20px_rgba(245,158,11,0.2)] hover:bg-amber-400 hover:shadow-[0_0_30px_rgba(245,158,11,0.4)] transition-all transform hover:-translate-y-1">
              Explore Menu
            </Link>
            <Link to="/book" className="inline-block bg-stone-800 text-white font-bold text-lg px-8 py-4 rounded-full border border-stone-700 hover:bg-stone-700 transition-colors">
              Book a Room
            </Link>
          </m.div>
        </div>
      </div>
      
      <FadeIn delay={1} className="relative z-10 w-full text-center pb-8 text-stone-500 text-sm">
        <p>Scroll to discover</p>
      </FadeIn>
    </div>
  );
};

export default HomePage;