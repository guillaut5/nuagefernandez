<script setup lang="ts">
import { onMounted, computed } from 'vue'
import { RouterLink, RouterView, useRouter } from 'vue-router'
import { useAuth } from '@/store/useAuth'
import { LogIn, LogOut, User as UserIcon, Cloud } from 'lucide-vue-next'
import AppInfoBadge from '@/components/AppInfoBadge.vue'

const authStore = useAuth() // <-- renommé
const router = useRouter()

// Computed simple : lit le username depuis le store (réactif)
const username = computed(() => authStore.user?.username || '')
onMounted(() => {
  authStore.initialize()
})
function handleLogout() {
  authStore.logout()
  router.push('/login')
}
</script>
<template>
  <div class="min-h-dvh bg-sky-50/30 text-gray-900 overflow-x-hidden antialiased">
    <header class="bg-white border-b border-gray-100 sticky top-0 z-50">
      <nav class="container mx-auto px-3 py-2.5 md:px-6 md:py-3 flex justify-between items-center">
        <!-- bloc gauche -->
        <RouterLink to="/chat" class="flex items-center gap-2 shrink-0">
          <div class="w-8 h-8 rounded-xl bg-sky-50 flex items-center justify-center">
            <Cloud class="w-4.5 h-4.5 text-sky-500" fill="currentColor" stroke="none" />
          </div>
          <span class="font-display font-bold text-[14px] text-gray-900 hidden xs:inline">
            NuageFernandez
          </span>
        </RouterLink>

        <!-- bloc droite -->
        <div class="flex items-center gap-3 md:gap-6 min-w-0">
          <!-- nav liens -->
          <ul class="hidden xs:flex items-center gap-3 text-xs font-semibold text-gray-500">
            <li><RouterLink to="/chat" class="hover:text-sky-600">Chat</RouterLink></li>
            <li><a href="/admin" rel="noopener" class="hover:text-sky-600">Admin</a></li>
          </ul>

          <!-- Zone utilisateur -->
          <div class="flex items-center gap-3 ml-1 min-w-0">
            <template v-if="authStore.isAuthenticated">
              <div class="flex items-center gap-2 text-sm min-w-0">
                <UserIcon class="w-4 h-4 shrink-0 text-gray-400" />
                <span class="truncate max-w-[8rem] md:max-w-[12rem] font-medium">
                  {{ authStore.activeUsername || '—' }}
                </span>
              </div>

              <button
                @click="handleLogout"
                class="text-xs font-semibold text-coral-600 hover:text-coral-700 relative"
                aria-label="Déconnexion"
              >
                <span class="inline-flex items-center gap-1">
                  <LogOut class="w-4 h-4 md:w-5 md:h-5 shrink-0" />
                  <span class="hidden md:inline">Déconnexion</span>
                </span>
              </button>
            </template>

            <template v-else>
              <RouterLink
                to="/login"
                class="text-xs font-semibold text-gray-600 hover:text-sky-600 inline-flex items-center gap-1"
              >
                <LogIn class="w-4 h-4 md:w-5 md:h-5" />
                Connexion
              </RouterLink>
            </template>
          </div>
        </div>
      </nav>
    </header>

    <main class="container mx-auto px-3 py-3 md:px-6 md:py-8">
      <!-- le wrapper min-w-0 évite que du contenu interne force un débordement -->
      <div class="min-w-0">
        <RouterView />
        <AppInfoBadge />
      </div>
    </main>
  </div>
</template>

<style>
/* Global, volontairement non-scopé : évite le scroll horizontal fantôme */
html,
body {
  overflow-x: hidden;
}

/* (optionnel) si tu as des images dans le contenu du <RouterView> */
img {
  max-width: 100%;
  height: auto;
}
</style>
