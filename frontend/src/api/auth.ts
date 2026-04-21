import { apiClient } from './client';

export const login = async (email: string, password: string) => {
  // OAuth2 requires form data
  const formData = new URLSearchParams();
  formData.append('username', email); // FastAPI OAuth2 uses 'username'
  formData.append('password', password);

  const { data } = await apiClient.post('/auth/login', formData, {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
  });
  return data; // Returns { access_token, token_type }
};

export const getMe = async () => {
  const { data } = await apiClient.get('/auth/me');
  return data; // Returns User object
};