import React from 'react';
import clsx from 'clsx';

interface StatusBadgeProps {
  status: string;
  className?: string;
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status, className }) => {
  const normalizedStatus = status.toLowerCase();
  
  let colorClass = 'bg-stone-100 text-stone-800 border-stone-200';
  let dotClass = 'bg-stone-400';

  if (['paid', 'confirmed', 'delivered', 'available', 'success', 'checked_in'].includes(normalizedStatus)) {
    colorClass = 'bg-green-50 text-green-700 border-green-200';
    dotClass = 'bg-green-500';
  } else if (['preparing', 'ready', 'dispatched', 'occupied'].includes(normalizedStatus)) {
    colorClass = 'bg-blue-50 text-blue-700 border-blue-200';
    dotClass = 'bg-blue-500';
  } else if (['pending', 'created', 'pending_payment', 'cleaning', 'partial'].includes(normalizedStatus)) {
    colorClass = 'bg-amber-50 text-amber-700 border-amber-200';
    dotClass = 'bg-amber-500';
  } else if (['maintenance', 'cancelled', 'payment_failed', 'expired', 'failed', 'reversed', 'unpaid'].includes(normalizedStatus)) {
    colorClass = 'bg-red-50 text-red-700 border-red-200';
    dotClass = 'bg-red-500';
  } else if (['checked_out'].includes(normalizedStatus)) {
    colorClass = 'bg-stone-100 text-stone-600 border-stone-300';
    dotClass = 'bg-stone-400';
  }

  const label = normalizedStatus.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());

  return (
    <span className={clsx(`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium border`, colorClass, className)}>
      <span className={clsx(`h-1.5 w-1.5 rounded-full`, dotClass)} aria-hidden="true" />
      {label}
    </span>
  );
};
