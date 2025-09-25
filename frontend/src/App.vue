<script setup lang="ts">
import { onMounted, computed } from 'vue'
import { RouterLink, RouterView, useRouter } from 'vue-router'
import { useAuth } from '@/store/useAuth'
import { LogIn, LogOut, User as UserIcon } from 'lucide-vue-next'

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
  <div class="min-h-dvh bg-gray-50 text-gray-900 overflow-x-hidden antialiased">
    <header class="bg-white border-b shadow-sm sticky top-0 z-50">
      <nav class="container mx-auto px-3 py-2 md:px-6 md:py-3 flex justify-between items-center">
        <!-- bloc gauche -->
        <div class="flex items-center gap-2 md:gap-3 shrink-0">
          VO
          <img src="@/assets/logo.png" alt="Logo" class="h-8 w-8 rounded shrink-0" />
          <!-- <span class="font-semibold text-xs">NudagePrivé</span> -->
        </div>

        <!-- bloc droite -->
        <div class="flex items-center gap-3 md:gap-6 min-w-0">
          <!-- nav liens -->
          <ul class="hidden xs:flex items-center gap-2 text-xs font-medium">
            <li><RouterLink to="/chat" class="hover:text-blue-600">Chat</RouterLink></li>
            <!-- <li><RouterLink to="/profile" class="hover:text-blue-600">Profil</RouterLink></li> -->
          </ul>

          <!-- Zone utilisateur -->
          <div class="flex items-center gap-3 ml-1 min-w-0">
            <template v-if="authStore.isAuthenticated">
              <div class="flex items-center gap-2 text-sm min-w-0">
                <UserIcon class="w-4 h-4 shrink-0" />
                <span class="truncate max-w-[8rem] md:max-w-[12rem]">
                  {{ authStore.activeUsername || '—' }}
                </span>
              </div>

              <button
                @click="handleLogout"
                class="text-xs font-medium text-red-600 hover:text-red-800 relative"
                aria-label="Déconnexion"
              >
                <span class="inline-flex items-center gap-1">
                  <LogOut class="w-4 h-4 md:w-6 md:h-6 shrink-0" />
                  <span
                    class="sr-only md:not-sr-only md:absolute md:left-full md:ml-2 md:px-2 md:py-1 md:text-xs md:text-white md:bg-gray-700 md:rounded md:opacity-0 md:group-hover:opacity-100 md:transition"
                  >
                    Déconnexion
                  </span>
                </span>
              </button>
            </template>

            <template v-else>
              <RouterLink
                to="/login"
                class="text-xs font-medium hover:text-blue-600 inline-flex items-center gap-1"
              >
                <LogIn class="w-4 h-4 md:w-6 md:h-6" />
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
