import React from 'react';
import { m } from 'framer-motion';
import { Link } from 'react-router-dom';
import { ArrowRight } from 'lucide-react';
import { springs } from '../ui/MotionConfig';

interface ServiceCardProps {
  title: string;
  description: string;
  icon: React.ReactNode;
  imageUrl: string;
  linkTo: string;
  ctaText: string;
  delay?: number;
}

const ServiceCard: React.FC<ServiceCardProps> = ({ title, description, icon, imageUrl, linkTo, ctaText, delay = 0 }) => {
  return (
    <m.div
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: "-50px" }}
      transition={{ ...springs.smooth, delay }}
      whileHover={{ y: -5 }}
      className="group relative bg-white rounded-3xl overflow-hidden shadow-card hover:shadow-elevated transition-all duration-300 border border-stone-100 flex flex-col h-full"
    >
      <div className="relative h-48 w-full overflow-hidden">
        <div className="absolute inset-0 bg-stone-900/20 group-hover:bg-transparent transition-colors z-10" />
        <img 
          src={imageUrl} 
          alt={title} 
          className="w-full h-full object-cover transform group-hover:scale-105 transition-transform duration-700 ease-out"
        />
        <div className="absolute top-4 left-4 z-20 bg-white/90 backdrop-blur-sm p-3 rounded-2xl shadow-sm text-brand-orange">
          {icon}
        </div>
      </div>
      <div className="p-8 flex flex-col flex-grow">
        <h3 className="text-2xl font-bold text-brand-dark mb-3">{title}</h3>
        <p className="text-stone-500 mb-8 flex-grow">{description}</p>
        <Link 
          to={linkTo}
          className="inline-flex items-center justify-between w-full px-6 py-4 bg-stone-50 hover:bg-brand-orange text-stone-800 hover:text-white rounded-2xl font-semibold transition-all duration-300 group/btn"
        >
          <span>{ctaText}</span>
          <ArrowRight className="w-5 h-5 transform group-hover/btn:translate-x-1 transition-transform" />
        </Link>
      </div>
    </m.div>
  );
};

export default ServiceCard;
