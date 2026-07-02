import React, { useRef, useState } from 'react';
import { motion, Variants } from 'framer-motion';

const springConfig = { type: "spring" as const, stiffness: 400, damping: 30 };

const containerVariants: Variants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
      delayChildren: 0.2,
    }
  }
};

const itemVariants: Variants = {
  hidden: { opacity: 0, y: 40, scale: 0.95 },
  visible: { 
    opacity: 1, 
    y: 0, 
    scale: 1,
    transition: springConfig 
  }
};

interface BentoCardProps {
  title: string;
  description: string;
  imageSrc: string;
  className?: string;
  imageClassName?: string;
}

const BentoCard: React.FC<BentoCardProps> = ({ title, description, imageSrc, className, imageClassName }) => {
  const cardRef = useRef<HTMLDivElement>(null);
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });

  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!cardRef.current) return;
    const rect = cardRef.current.getBoundingClientRect();
    setMousePosition({
      x: e.clientX - rect.left,
      y: e.clientY - rect.top,
    });
  };

  return (
    <motion.div
      variants={itemVariants}
      whileHover={{ scale: 1.01 }}
      ref={cardRef}
      onMouseMove={handleMouseMove}
      className={`relative rounded-3xl bg-zinc-900/40 backdrop-blur-md ring-1 ring-white/10 overflow-hidden group ${className}`}
      style={{
        boxShadow: "inset 0 1px 1px rgba(255, 255, 255, 0.05)",
      }}
    >
      {/* Spotlight effect */}
      <div
        className="pointer-events-none absolute -inset-px rounded-3xl opacity-0 transition duration-300 group-hover:opacity-100 z-10"
        style={{
          background: `radial-gradient(600px circle at ${mousePosition.x}px ${mousePosition.y}px, rgba(255,255,255,0.06), transparent 40%)`,
        }}
      />
      
      <div className="p-8 relative z-20 h-full flex flex-col justify-end">
        <h3 className="text-2xl font-bold text-zinc-100 mb-2">{title}</h3>
        <p className="text-zinc-400 text-sm">{description}</p>
      </div>

      <motion.div 
        className="absolute inset-0 z-0 overflow-visible"
        transition={springConfig}
      >
        <img 
          src={imageSrc} 
          alt={title}
          className={`absolute object-cover transition-transform duration-700 group-hover:scale-105 group-hover:-rotate-1 opacity-60 mix-blend-overlay ${imageClassName}`}
        />
        {/* Noise overlay */}
        <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB2aWV3Qm94PSIwIDAgMjAwIDIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZmlsdGVyIGlkPSJub2lzZUZpbHRlciI+PGZlVHVyYnVsZW5jZSB0eXBlPSJmcmFjdGFsTm9pc2UiIGJhc2VGcmVxdWVuY3k9IjAuNjUiIG51bU9jdGF2ZXM9IjMiIHN0aXRjaFRpbGVzPSJzdGl0Y2giLz48L2ZpbHRlcj48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWx0ZXI9InVybCgibm9pc2VGaWx0ZXIpIiBvcGFjaXR5PSIwLjA1Ii8+PC9zdmc+')] opacity-30 mix-blend-soft-light pointer-events-none" />
      </motion.div>
    </motion.div>
  );
};

export const FeaturedBento: React.FC = () => {
  return (
    <section className="py-24 bg-zinc-950 relative overflow-hidden">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div 
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, amount: 0.2 }}
          variants={containerVariants}
          className="grid grid-cols-1 md:grid-cols-3 gap-6 auto-rows-[300px]"
        >
          <BentoCard 
            title="Masterclass Kitchen"
            description="Witness culinary perfection crafted by world-renowned chefs in our open kitchen."
            imageSrc="/images/landingPage/cooking.jpg"
            className="md:col-span-2"
            imageClassName="w-full h-full object-center top-0 left-0"
          />
          <BentoCard 
            title="Curated Cocktails"
            description="Signature drinks mixed to absolute perfection."
            imageSrc="/images/landingPage/BarSection.jpg"
            className="md:col-span-1"
            imageClassName="w-full h-full object-center top-0 left-0"
          />
          <BentoCard 
            title="Global Cuisines"
            description="Flavors from around the world, delivered to your table."
            imageSrc="/images/landingPage/cuisines.jpg"
            className="md:col-span-1"
            imageClassName="w-full h-full object-center top-0 left-0"
          />
          <BentoCard 
            title="Premium Barbecue"
            description="Smoked meats prepared with uncompromising quality."
            imageSrc="/images/landingPage/barbecue.jpg"
            className="md:col-span-2"
            imageClassName="w-full h-full object-center top-0 left-0"
          />
        </motion.div>
      </div>
    </section>
  );
};
