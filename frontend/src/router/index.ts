import {createRouter, createWebHistory} from 'vue-router'



const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'Home',
      component: () => import('../views/HomeView.vue')
    },
    {
      path: '/market',
      name: 'Market',
      component: () => import('../views/MarketView.vue')
    },
    {
        path: '/status',
        name: 'Status',
        component: () => import('../views/StatusView.vue')
    }

  ]
})
export default router