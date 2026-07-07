import React from 'react';
import { m } from 'framer-motion';
import { Plus } from 'lucide-react';
import { springs } from '../ui/MotionConfig';

interface MenuItemCardProps {
  id: string;
  name: string;
  description?: string;
  priceKesCents: number;
  imageUrl?: string;
  isAvailable: boolean;
  onAdd: () => void;
  delay?: number;
}

const MenuItemCard: React.FC<MenuItemCardProps> = ({ 
  name, description, priceKesCents, imageUrl, isAvailable, onAdd, delay = 0 
}) => {
  const price = (priceKesCents / 100).toFixed(2);

  return (
    <m.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ ...springs.smooth, delay }}
      className={`bg-white rounded-2xl border border-stone-100 overflow-hidden shadow-subtle hover:shadow-card transition-all duration-300 flex ${!isAvailable ? 'opacity-60 grayscale' : ''}`}
    >
      <div className="flex-1 p-5 flex flex-col justify-between">
        <div>
          <h3 className="font-bold text-stone-900 text-lg mb-1">{name}</h3>
          {description && (
            <p className="text-sm text-stone-500 line-clamp-2 mb-3">{description}</p>
          )}
        </div>
        <div className="flex items-center justify-between mt-4">
          <span className="font-bold text-brand-dark">KSh {price}</span>
          <button
            onClick={onAdd}
            disabled={!isAvailable}
            className="flex items-center justify-center w-8 h-8 rounded-full bg-stone-100 text-stone-700 hover:bg-brand-orange hover:text-white transition-colors disabled:opacity-50 disabled:cursor-not-allowed focus:outline-none focus:ring-2 focus:ring-brand-orange focus:ring-offset-2"
            aria-label="Add to cart"
          >
            <Plus size={18} strokeWidth={2.5} />
          </button>
        </div>
      </div>
      {imageUrl && (
        <div className="w-32 sm:w-40 h-full min-h-[140px] relative">
          <img 
            src={imageUrl} 
            alt={name}
            className="absolute inset-0 w-full h-full object-cover"
          />
        </div>
      )}
    </m.div>
  );
};

export default MenuItemCard;
