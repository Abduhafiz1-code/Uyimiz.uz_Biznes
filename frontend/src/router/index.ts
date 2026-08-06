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

router.beforeEach((to) => {
  const auth = useAuthStore()
  if (!to.meta.public && !auth.isAuthenticated) return { name: 'login' }
  if (to.name === 'login' && auth.isAuthenticated) return { name: 'panel' }
  return true
})

router.afterEach((to) => {
  document.title = to.meta.title ? `${to.meta.title} · Uyimiz Agent` : 'Uyimiz Agent — CRM'
})

export default router
