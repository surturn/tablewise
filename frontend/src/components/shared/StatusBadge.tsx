import { cn } from './ProductCard';

type StatusType = 'pending' | 'preparing' | 'ready' | 'delivered' | 'cancelled' | 'paid';

interface StatusBadgeProps {
  status: StatusType;
  className?: string;
}

const statusConfig: Record<StatusType, { label: string; bg: string; text: string }> = {
  pending: { label: 'Pending', bg: 'bg-orange-100', text: 'text-orange-800' },
  preparing: { label: 'Preparing', bg: 'bg-yellow-100', text: 'text-yellow-800' },
  ready: { label: 'Ready', bg: 'bg-green-100', text: 'text-green-800' },
  delivered: { label: 'Delivered', bg: 'bg-blue-100', text: 'text-blue-800' },
  paid: { label: 'Paid', bg: 'bg-emerald-100', text: 'text-emerald-800' },
  cancelled: { label: 'Cancelled', bg: 'bg-red-100', text: 'text-red-800' },
};

export function StatusBadge({ status, className }: StatusBadgeProps) {
  const config = statusConfig[status];

  return (
    <span
      className={cn(
        "px-2.5 py-0.5 rounded-full text-xs font-semibold tracking-wide",
        config.bg,
        config.text,
        className
      )}
    >
      {config.label}
    </span>
  );
}
