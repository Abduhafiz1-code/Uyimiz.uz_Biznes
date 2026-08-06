import axios from 'axios'

export const TOKEN_KEY = 'uyimiz_agent_token'

const api = axios.create({ baseURL: '/api' })

api.interceptors.request.use((config) => {
  const token = localStorage.getItem(TOKEN_KEY)
  if (token) {
    config.headers.Authorization = `Token ${token}`
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem(TOKEN_KEY)
      if (window.location.pathname !== '/kirish') {
        window.location.href = '/kirish'
      }
    }
    return Promise.reject(error)
  },
)

export default api
