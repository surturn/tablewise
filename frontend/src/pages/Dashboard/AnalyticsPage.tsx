import React, { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { BrainCircuit, TrendingUp, DollarSign, ShoppingBag, Loader2 } from 'lucide-react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer
} from 'recharts';
import { requestForecast } from '@/api/analytics.ts';

// Mock Data for the chart (In production, this comes from a GET /analytics/sales endpoint)
const mockSalesData =[
  { day: 'Mon', sales: 45000 },
  { day: 'Tue', sales: 52000 },
  { day: 'Wed', sales: 48000 },
  { day: 'Thu', sales: 61000 },
  { day: 'Fri', sales: 85000 },
  { day: 'Sat', sales: 95000 },
  { day: 'Sun', sales: 78000 },
];

const AnalyticsPage: React.FC = () => {
  const [aiMessage, setAiMessage] = useState<string | null>(null);

  // In a real flow, branchId comes from your Zustand auth store
  const testBranchId = "00000000-0000-0000-0000-000000000000";

  const forecastMutation = useMutation({
    mutationFn: requestForecast,
    onSuccess: (data) => {
      // The backend returns a Celery task_id. We display the success message.
      setAiMessage(`AI Engine Queued: ${data.message} (Task ID: ${data.task_id.slice(0, 8)}...)`);

      // Note: To show the actual result, we would need to implement a polling mechanism
      // or WebSocket listener for Celery task completion in a future step.
    },
    onError: () => {
      setAiMessage("Error: Failed to reach the AI Engine.");
    }
  });

  const handleGenerateForecast = () => {
    // Generate a simple summary string based on our mock data to send to OpenAI
    const totalSales = mockSalesData.reduce((acc, curr) => acc + curr.sales, 0);
    const summary = `Last 7 days total sales: ${totalSales} KES. Peak days were Friday and Saturday. Top selling items were Nyama Choma and Pilau.`;

    forecastMutation.mutate({
      branch_id: testBranchId,
      historical_data_summary: summary
    });
  };

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">

      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-brand-dark">Analytics & Insights</h1>
        <p className="text-sm text-gray-500">Track performance and get AI-driven inventory forecasts.</p>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-100 flex items-center gap-4">
          <div className="p-3 bg-orange-100 text-brand-orange rounded-full">
            <DollarSign size={24} />
          </div>
          <div>
            <p className="text-sm text-gray-500">Weekly Revenue</p>
            <p className="text-2xl font-bold text-brand-dark">KES 464,000</p>
          </div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-100 flex items-center gap-4">
          <div className="p-3 bg-green-100 text-green-600 rounded-full">
            <ShoppingBag size={24} />
          </div>
          <div>
            <p className="text-sm text-gray-500">Total Orders</p>
            <p className="text-2xl font-bold text-brand-dark">342</p>
          </div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-100 flex items-center gap-4">
          <div className="p-3 bg-blue-100 text-blue-600 rounded-full">
            <TrendingUp size={24} />
          </div>
          <div>
            <p className="text-sm text-gray-500">Avg. Order Value</p>
            <p className="text-2xl font-bold text-brand-dark">KES 1,356</p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

        {/* Sales Chart */}
        <div className="lg:col-span-2 bg-white p-6 rounded-lg shadow-sm border border-gray-100">
          <h2 className="text-lg font-semibold text-brand-dark mb-4">7-Day Sales Trend</h2>
          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={mockSalesData}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E5E7EB" />
                <XAxis dataKey="day" axisLine={false} tickLine={false} tick={{ fill: '#6B7280' }} />
                <YAxis axisLine={false} tickLine={false} tick={{ fill: '#6B7280' }} tickFormatter={(val) => `Ksh ${val/1000}k`} />
                <Tooltip
                  cursor={{ fill: '#F3F4F6' }}
                  contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                />
                <Bar dataKey="sales" fill="#FF6B00" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* AI Forecasting Module */}
        <div className="bg-gradient-to-br from-brand-dark to-gray-900 p-6 rounded-lg shadow-sm text-white flex flex-col justify-between">
          <div>
            <div className="flex items-center gap-2 mb-4">
              <BrainCircuit className="text-brand-orange" size={28} />
              <h2 className="text-lg font-semibold">AI Inventory Forecaster</h2>
            </div>
            <p className="text-gray-300 text-sm mb-6 leading-relaxed">
              TableWise uses OpenAI to analyze your recent sales trends, local events, and historical data to predict exactly what you need to restock for the upcoming week.
            </p>

            {aiMessage && (
              <div className="bg-white/10 p-4 rounded-md border border-white/20 text-sm mb-6">
                {aiMessage}
              </div>
            )}
          </div>

          <button
            onClick={handleGenerateForecast}
            disabled={forecastMutation.isPending}
            className="w-full flex items-center justify-center gap-2 bg-brand-orange text-white py-3 rounded-md hover:bg-orange-600 transition disabled:opacity-70"
          >
            {forecastMutation.isPending ? (
              <>
                <Loader2 size={18} className="animate-spin" />
                Analyzing Data...
              </>
            ) : (
              <>
                Generate Smart Re-order List
              </>
            )}
          </button>
        </div>

      </div>
    </div>
  );
};

export default AnalyticsPage;