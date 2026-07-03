import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { fetchAnalyticsOverview } from '../../api/analytics';
import { useAuthStore } from '../../store/authStore';
import { StatCard } from '../../components/ui/StatCard';
import { SkeletonCard, SkeletonTable } from '../../components/ui/Skeleton';
import { EmptyState } from '../../components/ui/EmptyState';
import { PieChart, TrendingUp, DollarSign, Activity, Calendar } from 'lucide-react';

const AnalyticsPage: React.FC = () => {
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

  const isDataEmpty = !data || (data.total_orders === 0 && data.total_revenue_usd_cents === 0);

  if (isDataEmpty) {
    return (
      <div className="space-y-6 relative min-h-[600px]">
        <div className="flex items-center gap-2 mb-6">
          <PieChart className="text-brand-orange" size={28} />
          <h2 className="text-2xl font-bold text-brand-dark">Analytics Dashboard</h2>
        </div>
        
        {/* Faint background skeletons to hint at structure */}
        <div className="absolute inset-0 top-16 opacity-30 pointer-events-none z-0">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
            <SkeletonCard />
            <SkeletonCard />
            <SkeletonCard />
            <SkeletonCard />
          </div>
          <SkeletonTable rows={4} />
        </div>

        {/* Empty State Overlay */}
        <div className="absolute inset-0 top-16 z-10 flex items-center justify-center bg-white/40 backdrop-blur-[2px]">
          <EmptyState 
            theme="light"
            icon={<Calendar size={32} />}
            title="Awaiting data for this period"
            description="There are no recorded transactions or active guests for the selected date range. Data will populate here as soon as orders are placed."
            action={
              <button className="bg-white border border-stone-200 text-brand-dark font-medium px-6 py-2 rounded-lg shadow-sm hover:bg-stone-50 transition-colors">
                Change Date Range
              </button>
            }
          />
        </div>
      </div>
    );
  }

  const overview = data;

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-2 mb-6">
        <PieChart className="text-brand-orange" size={28} />
        <h2 className="text-2xl font-bold text-brand-dark">Analytics Dashboard</h2>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Total Revenue"
          value={`$${(overview.total_revenue_usd_cents / 100).toFixed(2)}`}
          icon={<DollarSign size={24} />}
        />
        <StatCard
          title="Total Orders"
          value={overview.total_orders}
          icon={<TrendingUp size={24} />}
        />
        <StatCard
          title="Active Guests"
          value={overview.active_customers}
          icon={<Activity size={24} />}
        />
        <StatCard
          title="Avg. Occupancy"
          value={`${overview.occupancy_rate}%`}
          icon={<PieChart size={24} />}
        />
      </div>

      <div className="bg-white p-8 rounded-2xl shadow-subtle border border-stone-200 mt-8 min-h-[400px] flex items-center justify-center">
        <div className="text-center">
          <Activity size={48} className="mx-auto mb-4 text-stone-200" />
          <h3 className="text-lg font-bold text-brand-dark">Detailed charts coming soon</h3>
          <p className="text-stone-500">We are integrating a premium charting library.</p>
        </div>
      </div>
    </div>
  );
};

export default AnalyticsPage;