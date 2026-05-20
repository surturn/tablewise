import React, { ReactNode } from 'react';
import { m } from 'framer-motion';
import { springs } from './MotionConfig';

interface EmptyStateProps {
  icon: ReactNode;
  title: string;
  description: string;
  action?: ReactNode;
}

export const EmptyState: React.FC<EmptyStateProps> = ({ icon, title, description, action }) => {
  return (
    <m.div 
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={springs.smooth}
      className="flex flex-col items-center justify-center p-10 text-center bg-white border border-dashed border-gray-200 rounded-2xl"
    >
      <div className="w-16 h-16 bg-brand-light rounded-full flex items-center justify-center text-brand-orange mb-4">
        {icon}
      </div>
      <h3 className="text-lg font-semibold text-brand-dark mb-2">{title}</h3>
      <p className="text-sm text-gray-500 max-w-sm mb-6 leading-relaxed">
        {description}
      </p>
      {action && <div>{action}</div>}
    </m.div>
  );
};
