import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { renderHook } from '@testing-library/react';
import type { ReactNode } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useOrdersWebSocket } from './useOrdersWebSocket';
import { useAuthStore } from '../store/authStore';

class MockWebSocket {
  static instances: MockWebSocket[] = [];
  url: string;
  onopen: (() => void) | null = null;
  onmessage: ((event: MessageEvent) => void) | null = null;
  onclose: ((event: { code: number; reason: string }) => void) | null = null;

  constructor(url: string) {
    this.url = url;
    MockWebSocket.instances.push(this);
  }
  close() {}
}

function wrapper({ children }: { children: ReactNode }) {
  const queryClient = new QueryClient();
  return <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>;
}

describe('useOrdersWebSocket auth-token lookup', () => {
  beforeEach(() => {
    MockWebSocket.instances = [];
    vi.stubGlobal('WebSocket', MockWebSocket);
    useAuthStore.setState({ token: null, user: null });
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it('reads the token from the authStore (single source of truth), not a stale localStorage key', () => {
    useAuthStore.setState({
      token: 'valid-jwt-token',
      user: { id: '1', email: 'staff@tablewise.com', full_name: 'Staff', role: 'owner' },
    });

    renderHook(() => useOrdersWebSocket('outlet-123'), { wrapper });

    expect(MockWebSocket.instances).toHaveLength(1);
    const connectedUrl = new URL(MockWebSocket.instances[0].url);
    expect(connectedUrl.searchParams.get('token')).toBe('valid-jwt-token');
    expect(connectedUrl.pathname).toBe('/ws/orders/outlet-123');
  });

  it('does not open a socket when no token is present in the store', () => {
    const errorSpy = vi.spyOn(console, 'error').mockImplementation(() => {});

    renderHook(() => useOrdersWebSocket('outlet-123'), { wrapper });

    expect(MockWebSocket.instances).toHaveLength(0);
    expect(errorSpy).toHaveBeenCalledWith('WebSocket blocked: Auth token missing');

    errorSpy.mockRestore();
  });
});
