import { createRouter, createWebHistory } from 'vue-router'
import Home from '../pages/home.vue'
import About from '../pages/about.vue'
import FirstAdminRegister from '../pages/firstAdminRegister.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home,
  },
  {
    path: '/about',
    name: 'About',
    component: About,
  },
  {
    path: '/firstAdminRegister',
    name: 'FirstAdminRegister',
    component: FirstAdminRegister,
  },
]
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: routes,
})

export default router
