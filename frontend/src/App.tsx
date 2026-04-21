import React from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import AppRouter from './routes/AppRouter';
import CartDrawer from './components/Cart/CartDrawer';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

const App: React.FC = () => {
  return (
    <QueryClientProvider client={queryClient}>
      <AppRouter />
      {/* Mount the CartDrawer globally so it can open from anywhere */}
      <CartDrawer />
    </QueryClientProvider>
  );
};

export default App;