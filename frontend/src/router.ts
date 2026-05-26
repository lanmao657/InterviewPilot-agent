import { createRouter, createWebHistory } from 'vue-router'

import AppShell from '@/components/layout/AppShell.vue'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/login', name: 'login', component: () => import('@/pages/LoginPage.vue') },
    {
      path: '/',
      component: AppShell,
      meta: { requiresAuth: true },
      children: [
        { path: '', redirect: '/dashboard' },
        { path: 'dashboard', name: 'dashboard', component: () => import('@/pages/DashboardPage.vue') },
        { path: 'documents', name: 'documents', component: () => import('@/pages/DocumentsPage.vue') },
        { path: 'questions', name: 'questions', component: () => import('@/pages/QuestionsPage.vue') },
        { path: 'interview', name: 'interview', component: () => import('@/pages/InterviewPage.vue') },
        { path: 'assistant', name: 'assistant', component: () => import('@/pages/AssistantPage.vue') },
        { path: 'reports', name: 'reports', component: () => import('@/pages/ReportsPage.vue') },
        { path: 'settings', name: 'settings', component: () => import('@/pages/SettingsPage.vue') },
      ],
    },
  ],
})

router.beforeEach((to) => {
  const auth = useAuthStore()
  if (to.meta.requiresAuth && !auth.isAuthenticated) return '/login'
  if (to.path === '/login' && auth.isAuthenticated) return '/dashboard'
  return true
})

export default router
