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
  <div class="min-h-screen bg-gray-50 text-gray-900">
    <header class="bg-white border-b shadow-sm sticky top-0 z-50">
      <nav class="container mx-auto px-4 py-3 flex justify-between items-center">
        <div class="flex items-center gap-3">
          <img src="@/assets/logo.png" alt="Logo" class="h-8 w-8 rounded" />
          <!-- <span class="font-semibold text-xs">NudagePrivé</span>-->
        </div>

        <div class="flex items-center gap-6">
          <ul class="flex items-center gap-2 text-xs font-medium">
            <li><RouterLink to="/chat" class="hover:text-blue-600">Chat</RouterLink></li>
            <li><RouterLink to="/profile" class="hover:text-blue-600">Profil</RouterLink></li>
          </ul>

          <!-- Zone utilisateur -->
          <div class="flex items-center gap-4 ml-2">
            <template v-if="authStore.isAuthenticated">
              <div class="flex items-center gap-2 text-sm">
                <UserIcon class="w-4 h-4" />
                <span class="truncate max-w-[12rem]">
                  {{ authStore.activeUsername || '—' }}
                </span>
              </div>
              <button
                @click="handleLogout"
                class="text-xs font-medium text-red-600 hover:text-red-800"
              >
                <span class="inline-flex items-center gap-1 group relative">
                  <LogOut class="w-4 h-4 md:w-6 md:h-6" />
                  <span
                    class="absolute left-full ml-2 px-2 py-1 text-xs text-white bg-gray-700 rounded opacity-0 group-hover:opacity-100 transition"
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
                <LogIn class="w-4 h-4 md:w-6 md:h-6 text-xs md:text-base" /> Connection
              </RouterLink>
            </template>
          </div>
        </div>
      </nav>
    </header>

    <main class="container mx-auto px-2 py-2 md:px-4 md:py-8">
      <RouterView />
    </main>
  </div>
</template>
