<script setup lang="ts">
import { RouterLink, RouterView, useRouter } from 'vue-router'
import { useAuth } from '@/store/useAuth'
import { Mail, Send, LogIn, LogOut } from 'lucide-vue-next'

const auth = useAuth()
const router = useRouter()

function handleLogout() {
  auth.logout()
  router.push('/login')
}
</script>
<template>
  <div class="min-h-screen bg-gray-50 text-gray-900">
    <!-- NAVBAR -->
    <header class="bg-white border-b shadow-sm sticky top-0 z-50">
      <nav class="container mx-auto px-4 py-3 flex justify-between items-center">
        <!-- Logo -->
        <div class="flex items-center gap-3">
          <img src="@/assets/logo.png" alt="Logo" class="h-8 w-8 rounded" />
          <span class="font-semibold text-lg">NuagePrivé</span>
        </div>

        <!-- Menu -->
        <div class="flex items-center gap-6">
          <ul class="flex items-center gap-6 text-sm font-medium">
            <li><RouterLink to="/" class="hover:text-blue-600">Accueil</RouterLink></li>
            <li><RouterLink to="/inbox" class="hover:text-blue-600">Messages</RouterLink></li>
            <li><RouterLink to="/sent" class="hover:text-blue-600">Envoyées</RouterLink></li>
            <li><RouterLink to="/send" class="hover:text-blue-600">Nouveau Message</RouterLink></li>
            <li><RouterLink to="/chat" class="hover:text-blue-600">Chat</RouterLink></li>

            <li><RouterLink to="/profile" class="hover:text-blue-600">Profil</RouterLink></li>
          </ul>

          <!-- Logout -->
          <button
            @click="handleLogout"
            class="text-sm font-medium text-red-600 hover:text-red-800 ml-4"
          >
            Déconnexion
          </button>
        </div>
      </nav>
    </header>

    <!-- CONTENU -->
    <main class="container mx-auto px-4 py-8">
      <RouterView />
    </main>
  </div>
</template>
