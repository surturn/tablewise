import React, { useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';
import gsap from 'gsap';
import HeroScene from '../../components/3d/HeroScene';

const HomePage: React.FC = () => {
  const titleRef = useRef(null);
  const subRef = useRef(null);
  const btnRef = useRef(null);

  useEffect(() => {
    const tl = gsap.timeline();
    tl.fromTo(titleRef.current, { opacity: 0, y: 50 }, { opacity: 1, y: 0, duration: 1, ease: 'power3.out' })
      .fromTo(subRef.current, { opacity: 0, y: 30 }, { opacity: 1, y: 0, duration: 1, ease: 'power3.out' }, "-=0.6")
      .fromTo(btnRef.current, { opacity: 0, scale: 0.9 }, { opacity: 1, scale: 1, duration: 0.5, ease: 'back.out(1.7)' }, "-=0.4");
  },[]);

  return (
    <div className="relative min-h-screen overflow-hidden text-white flex items-center">
      <HeroScene />
      <div className="relative z-10 max-w-7xl mx-auto px-6 w-full mt-20">
        <div className="max-w-2xl">
          <h1 ref={titleRef} className="text-6xl md:text-8xl font-black mb-6 leading-tight">
            Grand <br/><span className="text-[#FF6B00]">Platform.</span>
          </h1>
          <p ref={subRef} className="text-xl md:text-2xl text-gray-300 mb-10 font-light">
            A unified hospitality platform for Juba: rooms, restaurant delivery, bar tabs, offline-first POS, Stripe, cash, and mobile money in USD.
          </p>
          <div ref={btnRef}>
            {/* Make sure this path matches the menu route you previously built */}
            <Link to="/menu" className="inline-block bg-[#FF6B00] text-white font-bold text-lg px-8 py-4 rounded-full shadow-[0_0_20px_rgba(255,107,0,0.4)] hover:bg-[#e66000] transition-transform">
              Explore Menu
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HomePage;