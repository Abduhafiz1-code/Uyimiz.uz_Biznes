import axios, { type AxiosError, type InternalAxiosRequestConfig } from "axios";

export const TOKEN_KEY = "uyimiz_agent_token";

// uyimiz-backend (yagona Django backend): Agent CRM resurslari /api/crm/... ostida,
// login/me/logout esa umumiy /api/auth/... da (barcha rollar uchun bitta login).
const api = axios.create({ baseURL: "http://127.0.0.1:8000/api/crm" });
export const authApi = axios.create({
  baseURL: "http://127.0.0.1:8000/api/auth",
});

function attachAuth(config: InternalAxiosRequestConfig) {
  const token = localStorage.getItem(TOKEN_KEY);
  if (token) {
    config.headers.Authorization = `Token ${token}`;
  }
  return config;
}
api.interceptors.request.use(attachAuth);
authApi.interceptors.request.use(attachAuth);

function handle401(error: AxiosError) {
  if (error.response?.status === 401) {
    localStorage.removeItem(TOKEN_KEY);
    if (window.location.pathname !== "/kirish") {
      window.location.href = "/kirish";
    }
  }
  return Promise.reject(error);
}
api.interceptors.response.use((response) => response, handle401);
authApi.interceptors.response.use((response) => response, handle401);

export default api;
