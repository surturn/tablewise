
import AppRouter from './routes/AppRouter';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { MotionProvider } from './components/ui/MotionConfig';
import { ToastContainer } from './components/ui/Toast';
import CartDrawer from './components/Cart/CartDrawer';

const queryClient = new QueryClient();

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <MotionProvider>
        <AppRouter />
        <CartDrawer />
        <ToastContainer />
      </MotionProvider>
    </QueryClientProvider>
  );
}

export default App;