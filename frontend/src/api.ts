import axios from 'axios';

export const api = axios.create({ baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api' });
export function setToken(token: string) { api.defaults.headers.common.Authorization = `Bearer ${token}`; localStorage.setItem('northstar_token', token); }
const savedToken = localStorage.getItem('northstar_token');
if (savedToken) setToken(savedToken);
