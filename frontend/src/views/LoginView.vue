<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '@/store/useAuth'
import { User, Lock, Eye, EyeOff, LogIn, LoaderCircle } from 'lucide-vue-next'

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
    router.push('/') // redirige vers l'inbox après connexion
  } catch (e: any) {
    error.value = 'Identifiants incorrects ou connexion impossible.'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="min-h-screen bg-[#f5f7fb] relative overflow-hidden">
    <!-- fond doux façon iOS -->
    <div class="pointer-events-none absolute inset-0">
      <div
        class="absolute -top-24 -right-24 w-96 h-96 rounded-full bg-indigo-200/40 blur-3xl"
      ></div>
      <div
        class="absolute -bottom-24 -left-24 w-[28rem] h-[28rem] rounded-full bg-pink-200/40 blur-3xl"
      ></div>
    </div>

    <div class="relative flex items-center justify-center min-h-screen p-4">
      <form
        @submit.prevent="handleSubmit"
        class="w-full max-w-sm backdrop-blur-xl bg-white/70 shadow-[0_10px_40px_rgba(0,0,0,0.08)] border border-white/60 rounded-2xl p-6 md:p-7 space-y-5"
      >
        <!-- logo / avatar -->
        <img
          src="@/assets/logo.png"
          alt="Logo"
          class="mx-auto w-12 h-12 rounded-2xl text-white flex items-center justify-center shadow-inner shrink-0"
        />
        <!-- <span class="font-semibold text-xs">NudagePrivé</span> -->

        <div class="text-center">
          <h1 class="text-xl md:text-2xl font-semibold tracking-tight">Cloud Nuage</h1>
          <!-- <p class="text-sm text-gray-500 mt-1">Accédez à votre </p> -->
        </div>

        <!-- Username -->
        <div class="space-y-1.5">
          <label for="username" class="block text-[13px] text-gray-600">Nom d’utilisateur</label>
          <div class="relative">
            <span class="absolute inset-y-0 left-0 pl-3 flex items-center text-gray-400">
              <User class="w-4.5 h-4.5" />
            </span>
            <input
              id="username"
              v-model="username"
              type="text"
              autocomplete="username"
              required
              class="w-full rounded-xl border border-gray-200 bg-white/80 pl-10 pr-3 py-2.5 text-[15px] shadow-inner focus:outline-none focus:ring-4 focus:ring-black/5 focus:border-gray-300"
            />
          </div>
        </div>

        <!-- Password -->
        <div class="space-y-1.5">
          <label for="password" class="block text-[13px] text-gray-600">Mot de passe</label>
          <div class="relative">
            <span class="absolute inset-y-0 left-0 pl-3 flex items-center text-gray-400">
              <Lock class="w-4.5 h-4.5" />
            </span>
            <input
              id="password"
              v-model="password"
              :type="showPassword ? 'text' : 'password'"
              autocomplete="current-password"
              required
              class="w-full rounded-xl border border-gray-200 bg-white/80 pl-10 pr-10 py-2.5 text-[15px] shadow-inner focus:outline-none focus:ring-4 focus:ring-black/5 focus:border-gray-300"
            />
            <button
              type="button"
              class="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 hover:text-gray-600"
              @click="showPassword = !showPassword"
              aria-label="Afficher/masquer le mot de passe"
            >
              <Eye v-if="!showPassword" class="w-4.5 h-4.5" />
              <EyeOff v-else class="w-4.5 h-4.5" />
            </button>
          </div>
        </div>

        <p v-if="error" class="text-sm text-red-500 text-center">{{ error }}</p>

        <button
          type="submit"
          :disabled="loading"
          class="w-full inline-flex items-center justify-center gap-2 rounded-xl bg-black text-white py-2.5 text-[15px] font-medium shadow hover:bg-black/90 active:scale-[0.99] transition disabled:opacity-60 disabled:cursor-not-allowed"
        >
          <LoaderCircle v-if="loading" class="w-4.5 h-4.5 animate-spin" />
          <LogIn v-else class="w-4.5 h-4.5" />
          <span>{{ loading ? 'Connexion…' : 'Se connecter' }}</span>
        </button>

        <div class="text-center text-xs text-gray-500">
          En vous connectant, vous acceptez les conditions d’utilisation.
        </div>
      </form>
    </div>
  </div>
</template>

<style scoped>
/* tailles 4.5 remappées (12px ~ 18px) pour une finesse iOS */
.w-4\.5 {
  width: 1.125rem;
}
.h-4\.5 {
  height: 1.125rem;
}
</style>
