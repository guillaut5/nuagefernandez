<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '@/store/useAuth'
import { User, Lock, Eye, EyeOff, Send, LoaderCircle, Cloud } from 'lucide-vue-next'

const username = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')
const showPassword = ref(false)
const auth = useAuth()
const router = useRouter()

async function handleSubmit() {
  loading.value = true
  error.value = ''
  try {
    await auth.login(username.value, password.value)
    router.push('/')
  } catch (e: any) {
    error.value = 'Identifiants incorrects ou connexion impossible.'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="min-h-screen bg-sky-50/40 relative overflow-hidden">
    <!-- fond doux et coloré -->
    <div class="pointer-events-none absolute inset-0">
      <div class="absolute -top-28 -right-24 w-96 h-96 rounded-full bg-sky-50 blur-3xl"></div>
      <div class="absolute -bottom-28 -left-24 w-[28rem] h-[28rem] rounded-full bg-coral-50 blur-3xl"></div>
      <div class="absolute top-16 left-28 w-44 h-44 rounded-full bg-sun-50 blur-2xl opacity-80"></div>
      <div class="absolute bottom-20 right-40 w-56 h-56 rounded-full bg-mint-50 blur-2xl opacity-80"></div>
    </div>

    <div class="relative flex items-center justify-center min-h-screen p-4">
      <form
        @submit.prevent="handleSubmit"
        class="w-full max-w-sm bg-white shadow-[0_20px_50px_rgba(30,50,90,0.12)] border border-gray-100 rounded-[28px] p-7 md:p-8 space-y-6"
      >
        <!-- mascotte nuage -->
        <div class="flex flex-col items-center gap-3">
          <div class="w-[76px] h-[76px] rounded-3xl bg-sky-50 flex items-center justify-center">
            <Cloud class="w-10 h-10 text-sky-500" fill="currentColor" stroke="none" />
          </div>
          <div class="text-center">
            <h1 class="font-display text-2xl font-bold tracking-tight text-gray-900">
              NuageFernandez
            </h1>
            <p class="text-[13.5px] text-gray-500 mt-1">Le petit réseau de la famille ☁️</p>
          </div>
        </div>

        <!-- Username -->
        <div class="space-y-1.5">
          <label for="username" class="block text-[12.5px] font-semibold text-gray-500"
            >Nom d'utilisateur</label
          >
          <div class="relative">
            <span class="absolute inset-y-0 left-0 pl-3.5 flex items-center text-gray-400">
              <User class="w-[18px] h-[18px]" />
            </span>
            <input
              id="username"
              v-model="username"
              type="text"
              autocomplete="username"
              required
              class="w-full rounded-2xl border-[1.5px] border-gray-200 bg-gray-50 pl-11 pr-3 py-3 text-[14.5px] focus:outline-none focus:ring-4 focus:ring-sky-50 focus:border-sky-500"
            />
          </div>
        </div>

        <!-- Password -->
        <div class="space-y-1.5">
          <label for="password" class="block text-[12.5px] font-semibold text-gray-500"
            >Mot de passe</label
          >
          <div class="relative">
            <span class="absolute inset-y-0 left-0 pl-3.5 flex items-center text-gray-400">
              <Lock class="w-[18px] h-[18px]" />
            </span>
            <input
              id="password"
              v-model="password"
              :type="showPassword ? 'text' : 'password'"
              autocomplete="current-password"
              required
              class="w-full rounded-2xl border-[1.5px] border-gray-200 bg-gray-50 pl-11 pr-11 py-3 text-[14.5px] focus:outline-none focus:ring-4 focus:ring-sky-50 focus:border-sky-500"
            />
            <button
              type="button"
              class="absolute inset-y-0 right-0 pr-3.5 flex items-center text-gray-400 hover:text-gray-600"
              @click="showPassword = !showPassword"
              aria-label="Afficher/masquer le mot de passe"
            >
              <Eye v-if="!showPassword" class="w-[18px] h-[18px]" />
              <EyeOff v-else class="w-[18px] h-[18px]" />
            </button>
          </div>
        </div>

        <p v-if="error" class="text-sm text-coral-600 text-center">{{ error }}</p>

        <button
          type="submit"
          :disabled="loading"
          class="w-full inline-flex items-center justify-center gap-2 rounded-2xl bg-coral-500 text-white py-3 text-[15px] font-bold shadow-[0_10px_24px_rgba(230,110,60,0.35)] hover:bg-coral-600 active:scale-[0.99] transition disabled:opacity-60 disabled:cursor-not-allowed"
        >
          <LoaderCircle v-if="loading" class="w-[18px] h-[18px] animate-spin" />
          <Send v-else class="w-[18px] h-[18px]" />
          <span>{{ loading ? 'Connexion…' : 'Se connecter' }}</span>
        </button>

        <p class="text-center text-xs text-gray-400">
          Tout reste à la maison 🏠 — rien ne sort de ce serveur.
        </p>
      </form>
    </div>
  </div>
</template>
