import axios, { type AxiosError, type InternalAxiosRequestConfig } from "axios";

export const TOKEN_KEY = "uyimiz_agent_token";

// uyimiz-backend (yagona Django backend): Agent CRM resurslari /api/crm/... ostida,
// login/me/logout esa umumiy /api/auth/... da (barcha rollar uchun bitta login).
//
// Backend manzili.
//   • dev        → bo'sh: vite proxy 127.0.0.1:8000 ga uzatadi
//   • production → Render'dagi backend
// VITE_API_BASE berilsa, u ustun turadi.
const PROD_API_BASE = "https://uyimiz-backend.onrender.com";

const ROOT: string = (() => {
  const fromEnv = (import.meta.env.VITE_API_BASE || "").trim().replace(/\/+$/, "");
  if (fromEnv) return fromEnv;
  return import.meta.env.PROD ? PROD_API_BASE : "";
})();

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
