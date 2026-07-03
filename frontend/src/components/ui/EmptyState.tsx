import React, { ReactNode } from 'react';
import { m, Variants } from 'framer-motion';
import clsx from 'clsx';

interface EmptyStateProps {
  icon?: ReactNode;
  illustration?: ReactNode;
  title: string;
  description: string;
  action?: ReactNode;
  theme?: 'light' | 'dark';
}

const springConfig = { type: "spring" as const, stiffness: 400, damping: 30 };

const containerVariants: Variants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
      delayChildren: 0.05
    }
  }
};

const itemVariants: Variants = {
  hidden: { opacity: 0, y: 15, scale: 0.95 },
  visible: { 
    opacity: 1, 
    y: 0, 
    scale: 1,
    transition: springConfig
  }
};

export const EmptyState: React.FC<EmptyStateProps> = ({ 
  icon, 
  illustration, 
  title, 
  description, 
  action,
  theme = 'light' 
}) => {
  const isDark = theme === 'dark';
  const displayGraphic = illustration || icon;

  return (
    <m.div 
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className={clsx(
        "flex flex-col items-center justify-center p-10 text-center rounded-2xl w-full",
        isDark 
          ? "bg-zinc-950/50 backdrop-blur-xl ring-1 ring-white/10 shadow-[inset_0_0_20px_rgba(255,255,255,0.02)]" 
          : "bg-white border border-stone-200 shadow-sm"
      )}
    >
      {displayGraphic && (
        <m.div variants={itemVariants} className="mb-6">
          <div className={clsx(
            "w-20 h-20 rounded-full flex items-center justify-center relative",
            isDark ? "bg-white/5 text-white ring-1 ring-white/10" : "bg-stone-50 text-stone-400 border border-stone-100"
          )}>
            {/* Diffused Glow in dark mode */}
            {isDark && (
              <div className="absolute inset-0 rounded-full bg-brand-orange/20 blur-xl -z-10" />
            )}
            {displayGraphic}
          </div>
        </m.div>
      )}
      
      <m.h3 variants={itemVariants} className={clsx(
        "text-xl font-bold mb-2 tracking-tight",
        isDark ? "text-white" : "text-brand-dark"
      )}>
        {title}
      </m.h3>
      
      <m.p variants={itemVariants} className={clsx(
        "text-sm max-w-sm mb-8 leading-relaxed",
        isDark ? "text-zinc-400" : "text-stone-500"
      )}>
        {description}
      </m.p>
      
      {action && (
        <m.div variants={itemVariants}>
          {action}
        </m.div>
      )}
    </m.div>
  );
};
