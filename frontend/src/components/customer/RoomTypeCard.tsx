import React from 'react';
import { m } from 'framer-motion';
import { Wifi, Wind, Coffee, BedDouble } from 'lucide-react';
import { springs } from '../ui/MotionConfig';

interface RoomTypeCardProps {
  id: string;
  name: string;
  description: string;
  capacity: number;
  basePriceKesCents: number;
  availableCount: number;
  amenities: string[];
  photos: string[];
  onSelect: () => void;
  delay?: number;
}

// Map common amenities to icons
const getAmenityIcon = (amenity: string) => {
  const norm = amenity.toLowerCase();
  if (norm.includes('wifi')) return <Wifi size={14} />;
  if (norm.includes('air') || norm.includes('ac')) return <Wind size={14} />;
  if (norm.includes('coffee') || norm.includes('tea')) return <Coffee size={14} />;
  return null;
};

const RoomTypeCard: React.FC<RoomTypeCardProps> = ({ 
  name, description, capacity, basePriceKesCents, availableCount, amenities, photos, onSelect, delay = 0 
}) => {
  const price = (basePriceKesCents / 100).toFixed(2);
  const isAvailable = availableCount > 0;

  return (
    <m.div
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ ...springs.smooth, delay }}
      className="bg-white rounded-3xl border border-stone-100 overflow-hidden shadow-subtle hover:shadow-card transition-all duration-300 flex flex-col md:flex-row"
    >
      <div className="md:w-2/5 h-64 md:h-auto relative">
        <img 
          src={photos.length > 0 ? photos[0] : "https://images.unsplash.com/photo-1611892440504-42a792e24d32?q=80&w=2070&auto=format&fit=crop"} 
          alt={name}
          className="absolute inset-0 w-full h-full object-cover"
        />
        <div className="absolute top-4 left-4 bg-white/90 backdrop-blur-sm px-3 py-1.5 rounded-full shadow-sm text-xs font-bold text-stone-800 flex items-center gap-1.5">
          <BedDouble size={14} className="text-brand-orange" />
          {capacity} Guests
        </div>
      </div>
      <div className="flex-1 p-6 md:p-8 flex flex-col justify-between">
        <div>
          <div className="flex justify-between items-start mb-2">
            <h3 className="font-black text-2xl text-stone-900">{name}</h3>
            {isAvailable ? (
              <span className="bg-green-50 text-green-700 text-xs font-bold px-2.5 py-1 rounded-full border border-green-200">
                {availableCount} Available
              </span>
            ) : (
              <span className="bg-stone-100 text-stone-500 text-xs font-bold px-2.5 py-1 rounded-full">
                Sold Out
              </span>
            )}
          </div>
          <p className="text-stone-500 mb-6 line-clamp-3">{description}</p>
          
          {amenities.length > 0 && (
            <div className="flex flex-wrap gap-2 mb-6">
              {amenities.slice(0, 4).map((amenity, idx) => (
                <span key={idx} className="inline-flex items-center gap-1.5 bg-stone-50 border border-stone-100 text-stone-600 text-xs font-medium px-2.5 py-1 rounded-lg">
                  {getAmenityIcon(amenity)}
                  {amenity}
                </span>
              ))}
              {amenities.length > 4 && (
                <span className="inline-flex items-center bg-stone-50 border border-stone-100 text-stone-500 text-xs font-medium px-2.5 py-1 rounded-lg">
                  +{amenities.length - 4} more
                </span>
              )}
            </div>
          )}
        </div>
        
        <div className="flex items-center justify-between pt-6 border-t border-stone-100">
          <div>
            <span className="text-xs font-bold text-stone-400 uppercase tracking-wider block mb-1">Per Night</span>
            <span className="font-black text-3xl text-brand-dark">KSh {price}</span>
          </div>
          <button
            onClick={onSelect}
            disabled={!isAvailable}
            className="px-8 py-4 bg-brand-dark hover:bg-black text-white font-bold rounded-xl transition-colors focus:outline-none focus:ring-2 focus:ring-brand-orange focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isAvailable ? 'Book Room' : 'Unavailable'}
          </button>
        </div>
      </div>
    </m.div>
  );
};

export default RoomTypeCard;
