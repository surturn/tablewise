import React from 'react';
import { Link } from 'react-router-dom';
import { m, useScroll, useTransform } from 'framer-motion';
import { Utensils, BedDouble, Martini } from 'lucide-react';
import { springs, FadeIn } from '../../components/ui/MotionConfig';
import { useAuth } from '../../contexts/AuthContext';
import ServiceCard from '../../components/customer/ServiceCard';

const HomePage: React.FC = () => {
  const { scrollY } = useScroll();
  const { isAuthenticated, isStaff } = useAuth();
  const y1 = useTransform(scrollY, [0, 1000], [0, 200]);

  return (
    <div className="min-h-screen bg-brand-light font-sans text-brand-dark flex flex-col">
      {/* Hero Section */}
      <section className="relative h-[80vh] min-h-[600px] flex items-center justify-center overflow-hidden">
        <m.div style={{ y: y1 }} className="absolute inset-0 z-0">
          <div className="absolute inset-0 bg-stone-900/40 z-10" />
          <img 
            src="https://images.unsplash.com/photo-1542314831-c6a4d14cd2e1?auto=format&fit=crop&q=80&w=2000" 
            alt="Luxury Hotel" 
            className="w-full h-full object-cover"
          />
        </m.div>

        <div className="relative z-10 max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center mt-20">
          <m.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={springs.gentle}
          >
            <span className="inline-block py-1.5 px-4 rounded-full bg-white/20 backdrop-blur-md border border-white/30 text-white font-semibold text-sm tracking-widest uppercase mb-6 shadow-sm">
              Grand Platform
            </span>
            <h1 className="text-5xl sm:text-7xl font-black text-white mb-6 leading-tight drop-shadow-md">
              Hospitality, <br />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-brand-orange to-amber-300">perfected.</span>
            </h1>
            <p className="text-xl sm:text-2xl text-stone-200 mb-10 max-w-2xl mx-auto font-medium">
              Seamlessly order food, book your stay, and manage your tab all in one place.
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
              {!isAuthenticated ? (
                <>
                  <Link to="/login" className="w-full sm:w-auto bg-brand-orange text-brand-dark font-bold text-lg px-8 py-4 rounded-full shadow-[0_0_20px_rgba(245,158,11,0.2)] hover:bg-amber-400 hover:shadow-[0_0_30px_rgba(245,158,11,0.4)] transition-all transform hover:-translate-y-1">
                    Sign Up
                  </Link>
                  <Link to="/login" className="w-full sm:w-auto bg-white/10 backdrop-blur-md text-white font-bold text-lg px-8 py-4 rounded-full border border-white/30 hover:bg-white/20 transition-all">
                    Log In
                  </Link>
                </>
              ) : (
                <Link to={isStaff() ? "/dashboard" : "/customer/dashboard"} className="w-full sm:w-auto bg-brand-orange text-brand-dark font-bold text-lg px-8 py-4 rounded-full shadow-[0_0_20px_rgba(245,158,11,0.2)] hover:bg-amber-400 transition-all">
                  {isStaff() ? "Staff Dashboard" : "My Dashboard"}
                </Link>
              )}
            </div>
          </m.div>
        </div>
        
        {/* Custom shape divider */}
        <div className="absolute bottom-0 left-0 right-0 z-20 h-16 bg-gradient-to-b from-transparent to-brand-light" />
      </section>

      {/* Services Section */}
      <section className="relative z-20 py-24 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto -mt-16 w-full">
        <FadeIn className="text-center mb-16">
          <h2 className="text-4xl font-black text-brand-dark mb-4">Experience More</h2>
          <p className="text-stone-500 max-w-2xl mx-auto">Choose from our premium services tailored just for you.</p>
        </FadeIn>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <ServiceCard
            title="Dine"
            description="Explore our curated menus. Order directly to your table, room, or pick it up."
            icon={<Utensils size={28} />}
            imageUrl="https://images.unsplash.com/photo-1544148103-0773bf10d330?auto=format&fit=crop&q=80&w=800"
            linkTo="/customer/dine"
            ctaText="Order Food"
            delay={0.1}
          />
          
          <ServiceCard
            title="Stay"
            description="Book your perfect room. Experience luxury and comfort tailored to your needs."
            icon={<BedDouble size={28} />}
            imageUrl="https://images.unsplash.com/photo-1590490360182-c33d57733427?auto=format&fit=crop&q=80&w=800"
            linkTo="/customer/stay"
            ctaText="Book a Room"
            delay={0.2}
          />
          
          <ServiceCard
            title="Drink"
            description="Open a tab at our exclusive bar. Seamlessly add drinks and checkout when ready."
            icon={<Martini size={28} />}
            imageUrl="https://images.unsplash.com/photo-1514362545857-3bc16c4c7d1b?auto=format&fit=crop&q=80&w=800"
            linkTo="/customer/drink"
            ctaText="Open Tab"
            delay={0.3}
          />
        </div>
      </section>
      
      {/* Footer */}
      <footer className="mt-auto py-12 border-t border-stone-200 bg-white text-center text-stone-500 text-sm">
        <p>&copy; {new Date().getFullYear()} Grand Platform. All rights reserved.</p>
      </footer>
    </div>
  );
};

export default HomePage;