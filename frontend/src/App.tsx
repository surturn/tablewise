
import AppRouter from './routes/AppRouter';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { MotionProvider } from './components/ui/MotionConfig';
import { AuthProvider } from './contexts/AuthContext';

const queryClient = new QueryClient();

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <MotionProvider>
        <AuthProvider>
          <AppRouter />
        </AuthProvider>
      </MotionProvider>
    </QueryClientProvider>
  );
}

export default App;