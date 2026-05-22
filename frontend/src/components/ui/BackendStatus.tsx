import React, { useEffect, useState } from 'react';
import { m, AnimatePresence } from 'framer-motion';
import { Wifi, WifiOff, RefreshCw, Server, Clock, Activity } from 'lucide-react';
import { springs } from './MotionConfig';

interface HealthResponse {
  status: string;
  database: string;
  environment: string;
  project: string;
}

type ConnectionState = 'checking' | 'connected' | 'failed';

/**
 * A polished live status widget that pings the FastAPI /health endpoint.
 * Drop this into any dashboard page to prove backend connectivity to investors.
 *
 * Usage:
 *   import { BackendStatus } from '@/components/ui/BackendStatus';
 *   <BackendStatus />
 */
export const BackendStatus: React.FC = () => {
  const [state, setState] = useState<ConnectionState>('checking');
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [latency, setLatency] = useState<number | null>(null);
  const [error, setError] = useState<string>('');
  const [lastChecked, setLastChecked] = useState<Date | null>(null);

  const API_URL = (
    import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
  ).replace(/\/+$/, '');

  const checkHealth = async () => {
    setState('checking');
    setError('');
    const start = performance.now();

    try {
      const res = await fetch(`${API_URL}/health`, {
        method: 'GET',
        headers: { Accept: 'application/json' },
        signal: AbortSignal.timeout(8000),
      });
      const elapsed = Math.round(performance.now() - start);
      setLatency(elapsed);
      setLastChecked(new Date());

      if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        setState('failed');
        setError(body?.database || `HTTP ${res.status}`);
        return;
      }

      const data: HealthResponse = await res.json();
      setHealth(data);
      setState(data.status === 'healthy' ? 'connected' : 'failed');
      if (data.status !== 'healthy') {
        setError(data.database || 'Unhealthy');
      }
    } catch (err) {
      setLatency(Math.round(performance.now() - start));
      setLastChecked(new Date());
      setState('failed');
      setError(err instanceof Error ? err.message : 'Network error');
    }
  };

  useEffect(() => {
    checkHealth();
    // Re-check every 30s in the background
    const interval = setInterval(checkHealth, 30_000);
    return () => clearInterval(interval);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const statusConfig = {
    checking: {
      bg: 'bg-amber-50 border-amber-200',
      dot: 'bg-amber-400',
      text: 'text-amber-800',
      label: 'Connecting…',
      icon: <RefreshCw size={18} className="animate-spin text-amber-500" />,
    },
    connected: {
      bg: 'bg-emerald-50 border-emerald-200',
      dot: 'bg-emerald-400',
      text: 'text-emerald-800',
      label: 'Connected',
      icon: <Wifi size={18} className="text-emerald-500" />,
    },
    failed: {
      bg: 'bg-red-50 border-red-200',
      dot: 'bg-red-400',
      text: 'text-red-800',
      label: 'Failed',
      icon: <WifiOff size={18} className="text-red-500" />,
    },
  } as const;

  const cfg = statusConfig[state];

  return (
    <m.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={springs.smooth}
      className={`rounded-2xl border p-5 ${cfg.bg} shadow-subtle`}
    >
      {/* ── Header row ── */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2.5">
          <Server size={20} className={cfg.text} />
          <h3 className={`font-semibold text-sm tracking-wide uppercase ${cfg.text}`}>
            Backend Connection
          </h3>
        </div>
        <button
          onClick={checkHealth}
          disabled={state === 'checking'}
          className={`p-1.5 rounded-lg transition-colors hover:bg-white/50 disabled:opacity-40 ${cfg.text}`}
          title="Re-check now"
        >
          <RefreshCw size={16} className={state === 'checking' ? 'animate-spin' : ''} />
        </button>
      </div>

      {/* ── Status pill ── */}
      <AnimatePresence mode="wait">
        <m.div
          key={state}
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0.95 }}
          transition={{ duration: 0.2 }}
          className="flex items-center gap-3 mb-4"
        >
          {cfg.icon}
          <span className={`text-lg font-bold ${cfg.text}`}>
            {cfg.label}
          </span>
          {/* Pulsing dot */}
          <span className="relative flex h-2.5 w-2.5">
            {state === 'connected' && (
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75" />
            )}
            <span className={`relative inline-flex rounded-full h-2.5 w-2.5 ${cfg.dot}`} />
          </span>
        </m.div>
      </AnimatePresence>

      {/* ── Details grid ── */}
      <div className="grid grid-cols-2 gap-3 text-xs">
        {health && state === 'connected' && (
          <>
            <div className="flex items-center gap-1.5 text-gray-600">
              <Activity size={13} />
              <span>Database: <strong className="text-emerald-700">Healthy</strong></span>
            </div>
            <div className="flex items-center gap-1.5 text-gray-600">
              <Server size={13} />
              <span>Env: <strong className="text-gray-800">{health.environment}</strong></span>
            </div>
          </>
        )}

        {latency !== null && (
          <div className="flex items-center gap-1.5 text-gray-600">
            <Clock size={13} />
            <span>Latency: <strong className={latency < 500 ? 'text-emerald-700' : latency < 2000 ? 'text-amber-700' : 'text-red-700'}>{latency}ms</strong></span>
          </div>
        )}

        {lastChecked && (
          <div className="flex items-center gap-1.5 text-gray-500">
            <Clock size={13} />
            <span>Checked: {lastChecked.toLocaleTimeString()}</span>
          </div>
        )}
      </div>

      {/* ── Error details ── */}
      {error && state === 'failed' && (
        <m.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          className="mt-3 p-3 bg-red-100/60 rounded-xl text-xs text-red-700 font-mono break-all"
        >
          {error}
        </m.div>
      )}

      {/* ── Target URL (subtle) ── */}
      <p className="mt-3 text-[10px] text-gray-400 font-mono truncate">
        → {API_URL}/health
      </p>
    </m.div>
  );
};

export default BackendStatus;
