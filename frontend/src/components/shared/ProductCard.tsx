import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

interface ProductCardProps {
  id: string;
  name: string;
  price: number;
  image?: string;
  description?: string;
  onClick?: () => void;
  className?: string;
}

export function ProductCard({ name, price, image, description, onClick, className }: ProductCardProps) {
  return (
    <div 
      onClick={onClick}
      className={cn(
        "flex flex-col cursor-pointer overflow-hidden rounded-2xl transition-all duration-200",
        "bg-white dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-800",
        "hover:shadow-lg hover:-translate-y-1 hover:border-blue-500 dark:hover:border-blue-400",
        className
      )}
    >
      <div className="w-full h-40 bg-neutral-100 dark:bg-neutral-800 overflow-hidden relative">
        {image ? (
          <img src={image} alt={name} className="w-full h-full object-cover" />
        ) : (
          <div className="w-full h-full flex items-center justify-center text-neutral-400">
            No Image
          </div>
        )}
      </div>
      <div className="p-4 flex flex-col flex-1">
        <h3 className="font-semibold text-lg text-neutral-900 dark:text-neutral-100 mb-1 line-clamp-1">{name}</h3>
        {description && (
          <p className="text-sm text-neutral-500 dark:text-neutral-400 line-clamp-2 mb-3 flex-1">{description}</p>
        )}
        <div className="mt-auto pt-2 flex items-center justify-between">
          <span className="font-medium text-blue-600 dark:text-blue-400">
            ${(price / 100).toFixed(2)}
          </span>
          <button className="h-8 w-8 rounded-full bg-blue-100 text-blue-600 dark:bg-blue-900/30 dark:text-blue-400 flex items-center justify-center hover:bg-blue-200 dark:hover:bg-blue-900/50 transition-colors">
            +
          </button>
        </div>
      </div>
    </div>
  );
}
