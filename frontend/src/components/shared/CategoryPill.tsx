import { cn } from './ProductCard';

interface CategoryPillProps {
  label: string;
  isActive?: boolean;
  onClick?: () => void;
  className?: string;
}

export function CategoryPill({ label, isActive = false, onClick, className }: CategoryPillProps) {
  return (
    <button
      onClick={onClick}
      className={cn(
        "px-5 py-2 rounded-full font-medium whitespace-nowrap transition-all duration-200",
        isActive 
          ? "bg-neutral-900 text-white dark:bg-white dark:text-neutral-900 shadow-md"
          : "bg-neutral-100 text-neutral-600 hover:bg-neutral-200 dark:bg-neutral-800 dark:text-neutral-300 dark:hover:bg-neutral-700",
        className
      )}
    >
      {label}
    </button>
  );
}
