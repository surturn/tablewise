import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { m } from 'framer-motion';
import { login, getMe } from '../../api/auth';
import { useAuthStore } from '../../store/authStore';
import { useToastStore } from '../../store/toastStore';
import { springs } from '../../components/ui/MotionConfig';

const Login: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();
  const { setAuth } = useAuthStore();
  const addToast = useToastStore((state) => state.addToast);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    console.log("Submitting login for:", email);

    try {
      const { access_token } = await login(email, password);
      console.log("Response access_token received");
      
      useAuthStore.getState().setToken(access_token);
      
      const user = await getMe();
      console.log("Auth success for user:", user);
      
      setAuth(access_token, user);
      addToast(`Welcome back, ${user.full_name}!`, 'success');
      navigate('/dashboard');
    } catch (err: any) {
      console.error("Login failed:", err);
      addToast('Invalid email or password', 'error');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-stone-50 py-12 px-4 sm:px-6 lg:px-8">
      <m.div 
        initial={{ opacity: 0, y: 20, scale: 0.95 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        transition={springs.smooth}
        className="max-w-md w-full bg-white p-8 rounded-2xl shadow-elevated border border-stone-100"
      >
        <div>
          <h2 className="mt-2 text-center text-3xl font-black text-brand-dark">
            Table<span className="text-brand-orange">Wise</span> Staff
          </h2>
          <p className="mt-2 text-center text-sm text-stone-500">
            Sign in to access the dashboard
          </p>
        </div>
        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-stone-700 mb-1">Email address</label>
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="appearance-none block w-full px-3 py-3 border border-stone-200 rounded-xl placeholder-stone-400 focus:outline-none focus:ring-2 focus:ring-brand-orange focus:border-transparent transition-all"
                placeholder="staff@tablewise.com"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-stone-700 mb-1">Password</label>
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="appearance-none block w-full px-3 py-3 border border-stone-200 rounded-xl placeholder-stone-400 focus:outline-none focus:ring-2 focus:ring-brand-orange focus:border-transparent transition-all"
                placeholder="••••••••"
              />
            </div>
          </div>

          <div>
            <button
              type="submit"
              disabled={isLoading}
              className="group relative w-full flex justify-center py-3 px-4 border border-transparent text-sm font-bold rounded-xl text-white bg-brand-dark hover:bg-black focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-brand-orange transition-all disabled:opacity-70 disabled:cursor-not-allowed"
            >
              {isLoading ? 'Signing in...' : 'Sign In'}
            </button>
          </div>
        </form>
      </m.div>
    </div>
  );
};

export default Login;