import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { fetchAnalyticsOverview } from '../../api/analytics';
import { useAuthStore } from '../../store/authStore';
import { StatCard } from '../../components/ui/StatCard';
import { DollarSign, ShoppingBag, Users, CalendarCheck } from 'lucide-react';
import { SkeletonCard } from '../../components/ui/Skeleton';

const DashboardHome: React.FC = () => {
  const { user } = useAuthStore();
  const { data, isLoading } = useQuery({
    queryKey: ['analyticsOverview', user?.outlet_id],
    queryFn: () => fetchAnalyticsOverview(user?.outlet_id),
  });

  if (isLoading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <SkeletonCard />
        <SkeletonCard />
        <SkeletonCard />
        <SkeletonCard />
      </div>
    );
  }

  const overview = data || {
    total_revenue_usd_cents: 0,
    total_orders: 0,
    active_customers: 0,
    occupancy_rate: 0,
  };

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Revenue (Today)"
          value={`$${(overview.total_revenue_usd_cents / 100).toFixed(2)}`}
          icon={<DollarSign size={24} />}
          trend={{ value: 12, isPositive: true }}
          delay={0.1}
        />
        <StatCard
          title="Orders (Today)"
          value={overview.total_orders}
          icon={<ShoppingBag size={24} />}
          trend={{ value: 5, isPositive: true }}
          delay={0.2}
        />
        <StatCard
          title="Active Guests"
          value={overview.active_customers}
          icon={<Users size={24} />}
          delay={0.3}
        />
        <StatCard
          title="Occupancy Rate"
          value={`${overview.occupancy_rate}%`}
          icon={<CalendarCheck size={24} />}
          delay={0.4}
        />
      </div>
    </div>
  );
};

export default DashboardHome;