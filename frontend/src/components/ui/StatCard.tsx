import React from 'react';
import { m } from 'framer-motion';
import { ArrowUpRight, ArrowDownRight } from 'lucide-react';
import { springs } from './MotionConfig';

interface StatCardProps {
  title: string;
  value: string | number;
  icon: React.ReactNode;
  trend?: {
    value: number;
    isPositive: boolean;
  };
  delay?: number;
}

export const StatCard: React.FC<StatCardProps> = ({ title, value, icon, trend, delay = 0 }) => {
  return (
    <m.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ ...springs.smooth, delay }}
      whileHover={{ y: -2, transition: { duration: 0.2 } }}
      className="bg-white p-6 rounded-2xl shadow-subtle border border-gray-100 flex flex-col"
    >
      <div className="flex justify-between items-start mb-4">
        <div className="p-2.5 bg-brand-light rounded-xl text-brand-orange">
          {icon}
        </div>
        {trend && (
          <span className={`inline-flex items-center gap-1 text-xs font-medium px-2 py-1 rounded-full ${
            trend.isPositive ? 'text-green-700 bg-green-50' : 'text-red-700 bg-red-50'
          }`}>
            {trend.isPositive ? <ArrowUpRight size={14} /> : <ArrowDownRight size={14} />}
            {Math.abs(trend.value)}%
          </span>
        )}
      </div>
      <h3 className="text-3xl font-bold text-brand-dark mb-1">{value}</h3>
      <p className="text-sm font-medium text-gray-500">{title}</p>
    </m.div>
  );
};
