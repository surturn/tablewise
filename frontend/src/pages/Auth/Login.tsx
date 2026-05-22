import React, { useState } from 'react';
import { useLocation } from 'react-router-dom';
import { m } from 'framer-motion';
import { customerLogin, customerRegister } from '../../api/auth';
import { useAuth } from '../../contexts/AuthContext';
import { useAuthRedirect } from '../../hooks/useAuthRedirect';
import { useToastStore } from '../../store/toastStore';
import { springs } from '../../components/ui/MotionConfig';

const Login: React.FC = () => {
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [phoneNumber, setPhoneNumber] = useState('');
  
  const [isLoading, setIsLoading] = useState(false);
  const { login: contextLogin } = useAuth();
  const { redirectBasedOnRole } = useAuthRedirect();
  const addToast = useToastStore((state) => state.addToast);
  const location = useLocation();
  const fromPath = location.state?.from;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      if (isLogin) {
        const { access_token } = await customerLogin(email, password);
        const { getMe } = await import('../../api/auth');
        const user = await getMe(access_token);
        
        contextLogin(access_token, user);
        addToast(`Welcome back, ${user.full_name}!`, 'success');
        redirectBasedOnRole(fromPath, 'customer');
      } else {
        const { access_token } = await customerRegister({
          email,
          password,
          full_name: fullName,
          phone_number: phoneNumber
        });
        
        const { getMe } = await import('../../api/auth');
        const user = await getMe(access_token);
        
        contextLogin(access_token, user);
        addToast(`Welcome to TableWise, ${user.full_name}!`, 'success');
        redirectBasedOnRole(fromPath, 'customer');
      }
    } catch (err: any) {
      console.error("Auth failed:", err);
      const message = err.response?.data?.detail || (isLogin ? 'Invalid email or password' : 'Registration failed');
      addToast(message, 'error');
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
            Table<span className="text-brand-orange">Wise</span>
          </h2>
          <p className="mt-2 text-center text-sm text-stone-500">
            {isLogin ? 'Sign in to your account' : 'Create a new account'}
          </p>
        </div>
        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          <div className="space-y-4">
            {!isLogin && (
              <>
                <div>
                  <label className="block text-sm font-medium text-stone-700 mb-1">Full Name</label>
                  <input
                    type="text"
                    required
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    className="appearance-none block w-full px-3 py-3 border border-stone-200 rounded-xl placeholder-stone-400 focus:outline-none focus:ring-2 focus:ring-brand-orange focus:border-transparent transition-all"
                    placeholder="John Doe"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-stone-700 mb-1">Phone Number</label>
                  <input
                    type="tel"
                    required
                    value={phoneNumber}
                    onChange={(e) => setPhoneNumber(e.target.value)}
                    className="appearance-none block w-full px-3 py-3 border border-stone-200 rounded-xl placeholder-stone-400 focus:outline-none focus:ring-2 focus:ring-brand-orange focus:border-transparent transition-all"
                    placeholder="+211..."
                  />
                </div>
              </>
            )}
            <div>
              <label className="block text-sm font-medium text-stone-700 mb-1">Email address</label>
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="appearance-none block w-full px-3 py-3 border border-stone-200 rounded-xl placeholder-stone-400 focus:outline-none focus:ring-2 focus:ring-brand-orange focus:border-transparent transition-all"
                placeholder="you@example.com"
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
              {isLoading ? (isLogin ? 'Signing in...' : 'Creating account...') : (isLogin ? 'Sign In' : 'Create Account')}
            </button>
          </div>
          
          <div className="text-center mt-4">
            <button 
              type="button" 
              onClick={() => setIsLogin(!isLogin)}
              className="text-sm text-brand-orange font-medium hover:text-amber-600 transition-colors"
            >
              {isLogin ? "Don't have an account? Sign Up" : "Already have an account? Sign In"}
            </button>
          </div>
        </form>
      </m.div>
    </div>
  );
};

export default Login;