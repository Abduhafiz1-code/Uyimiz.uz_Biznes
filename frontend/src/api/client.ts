import axios, { type AxiosError, type InternalAxiosRequestConfig } from "axios";

export const TOKEN_KEY = "uyimiz_agent_token";

// uyimiz-backend (yagona Django backend): Agent CRM resurslari /api/crm/... ostida,
// login/me/logout esa umumiy /api/auth/... da (barcha rollar uchun bitta login).
//
// VITE_API_BASE — backendning ildiz manzili. Dev'da bo'sh qoldiriladi va
// vite.config.ts dagi proxy 127.0.0.1:8000 ga yo'naltiradi; prod'da
// https://uyimiz-backend.onrender.com qiymati beriladi.
const ROOT = (import.meta.env.VITE_API_BASE || "").replace(/\/+$/, "");

export const API_ROOT = ROOT;

/** Nisbiy media yo'lini (/media/...) to'liq manzilga aylantiradi. */
export function mediaUrl(path?: string | null): string {
  if (!path) return "";
  if (/^https?:\/\//i.test(path)) return path;
  return `${ROOT}${path.startsWith("/") ? "" : "/"}${path}`;
}

const api = axios.create({ baseURL: `${ROOT}/api/crm`, timeout: 60000 });
export const authApi = axios.create({
  baseURL: `${ROOT}/api/auth`,
  timeout: 60000,
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
