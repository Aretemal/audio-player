import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

import SearchPage from '@/views/SearchPage.vue'
import Login from '@/views/LoginPage.vue'
import Register from '@/views/RegisterPage.vue'
import Logout from '@/views/LogoutPage.vue'
import Songs from '@/views/SongsPage.vue'
import CreateSongPage from '@/views/CreateSongPage.vue'
import Albums from '@/views/AlbumsPage.vue'
import Playlists from '@/views/PlaylistsPage.vue'
import Artists from '@/views/ArtistsPage.vue'
import ArtistDetail from '@/views/ArtistDetailPage.vue'
import ReleaseDetail from '@/views/ReleaseDetailPage.vue'

import { AppRoutes } from '../constants/appRoutes'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: AppRoutes.LOGIN,
      name: 'login',
      component: Login,
      meta: { requiresGuest: true },
    },
    {
      path: AppRoutes.REGISTER,
      component: Register,
      meta: { requiresGuest: true },
    },
    {
      path: AppRoutes.LOGOUT,
      component: Logout,
      meta: { requiresAuth: false },
    },
    {
      path: AppRoutes.HOME,
      name: 'search',
      component: SearchPage,
      meta: { requiresAuth: true },
    },
    {
      path: AppRoutes.SONGS,
      component: Songs,
      meta: { requiresAuth: true },
    },
    {
      path: AppRoutes.CREATE_SONG,
      component: CreateSongPage,
      meta: { requiresAuth: true },
    },
    {
      path: AppRoutes.ALBUMS,
      component: Albums,
      meta: { requiresAuth: true },
    },
    {
      path: AppRoutes.PLAYLISTS,
      component: Playlists,
      meta: { requiresAuth: true },
    },
    {
      path: AppRoutes.ARTISTS,
      component: Artists,
      meta: { requiresAuth: true },
    },
    {
      path: AppRoutes.ARTIST_DETAILS,
      component: ArtistDetail,
      meta: { requiresAuth: true },
    },
    {
      path: AppRoutes.RELEASE_DETAILS,
      component: ReleaseDetail,
      meta: { requiresAuth: true },
    },
  ],
})

router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  if (to.meta.requiresAuth) {
    const isAuthenticated = await authStore.checkAuth()
    if (!isAuthenticated) {
      next({ name: 'login', query: { redirect: to.path } })
      return
    }
  }

  if (to.meta.requiresGuest) {
    const isAuthenticated = await authStore.checkAuth(true)
    if (isAuthenticated) {
      next({ path: AppRoutes.HOME })
      return
    }
  }

  next()
})

export default router
