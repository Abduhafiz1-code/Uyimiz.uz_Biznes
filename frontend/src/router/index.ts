import { createRouter, createWebHistory } from 'vue-router'

import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/kirish',
      name: 'login',
      component: () => import('@/views/LoginView.vue'),
      meta: { public: true, title: 'Kirish' },
    },
    {
      // Agent bo'lish uchun ariza. Kirgan, lekin hali tasdiqlanmagan
      // foydalanuvchilar shu yerga yo'naltiriladi.
      path: '/ariza',
      name: 'apply',
      component: () => import('@/views/ApplyView.vue'),
      meta: { public: true, title: 'Agent bo‘lish' },
    },
    {
      path: '/',
      component: () => import('@/components/CrmLayout.vue'),
      children: [
        { path: '', name: 'panel', component: () => import('@/views/PanelView.vue'), meta: { title: 'Panel' } },
        {
          path: 'mijozlar',
          name: 'clients',
          component: () => import('@/views/ClientsView.vue'),
          meta: { title: 'Mijozlar' },
        },
        {
          path: 'obyektlar',
          name: 'properties',
          component: () => import('@/views/PropertiesView.vue'),
          meta: { title: 'Obyektlar' },
        },
        {
          path: 'obyektlar/:id',
          name: 'property-detail',
          component: () => import('@/views/PropertyDetailView.vue'),
          meta: { title: 'Obyekt' },
          props: true,
        },
        {
          path: 'bitimlar',
          name: 'deals',
          component: () => import('@/views/DealsView.vue'),
          meta: { title: 'Bitimlar' },
        },
        {
          path: 'bitimlar/:id',
          name: 'deal-detail',
          component: () => import('@/views/DealDetailView.vue'),
          meta: { title: 'Bitim' },
          props: true,
        },
        {
          path: 'reyting',
          name: 'rating',
          component: () => import('@/views/RatingView.vue'),
          meta: { title: 'Reyting' },
        },
      ],
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'not-found',
      component: () => import('@/views/NotFoundView.vue'),
      meta: { public: true, title: 'Topilmadi' },
    },
  ],
  scrollBehavior: () => ({ top: 0 }),
})

router.beforeEach(async (to) => {
  const auth = useAuthStore()

  // Kirmagan bo'lsa — login sahifasi.
  if (!to.meta.public && !auth.isAuthenticated) return { name: 'login' }

  if (auth.isAuthenticated) {
    // Sahifa yangilangandan keyin rol/holat bo'sh bo'lishi mumkin —
    // CRM sahifalariga o'tishdan oldin backenddan tekshiramiz.
    if (!auth.role) await auth.refreshStatus()

    // Tasdiqlanmagan agent (yoki umuman agent bo'lmagan) CRM'ga kirmasin.
    if (!to.meta.public && !auth.canEnterCrm) return { name: 'apply' }

    if (to.name === 'login') return auth.canEnterCrm ? { name: 'panel' } : { name: 'apply' }
    if (to.name === 'apply' && auth.canEnterCrm) return { name: 'panel' }
  }

  return true
})

router.afterEach((to) => {
  document.title = to.meta.title ? `${to.meta.title} · Uyimiz Agent` : 'Uyimiz Agent — CRM'
})

export default router
