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

export const getMe = async (token?: string) => {
  const config = token ? { headers: { Authorization: `Bearer ${token}` } } : {};
  const { data } = await apiClient.get('/auth/me', config);
  return data; // Returns User object
};

export const customerRegister = async (data: {
  phone_number: string; full_name: string; email: string; password: string;
}) => {
  const { data: result } = await apiClient.post('/auth/customer/register', data);
  return result; // { access_token, token_type }
};

export const customerLogin = async (email: string, password: string) => {
  const { data: result } = await apiClient.post('/auth/customer/login', { email, password });
  return result; // { access_token, token_type }
};