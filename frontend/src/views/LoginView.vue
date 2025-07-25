<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '@/store/useAuth'

const username = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')

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
  <div class="flex items-center justify-center min-h-[70vh] bg-gray-50">
    <form
      @submit.prevent="handleSubmit"
      class="w-full max-w-sm bg-white shadow rounded-xl p-6 space-y-5"
    >
      <h1 class="text-2xl font-semibold text-center">Connexion</h1>

      <div>
        <label for="username" class="block text-sm font-medium text-gray-700 mb-1"
          >Nom d'utilisateur</label
        >
        <input
          id="username"
          v-model="username"
          type="text"
          required
          autocomplete="username"
          class="form-input w-full"
        />
      </div>

      <div>
        <label for="password" class="block text-sm font-medium text-gray-700 mb-1"
          >Mot de passe</label
        >
        <input
          id="password"
          v-model="password"
          type="password"
          required
          autocomplete="current-password"
          class="form-input w-full"
        />
      </div>

      <p v-if="error" class="text-sm text-red-500 text-center">{{ error }}</p>

      <button
        type="submit"
        class="btn-primary w-full flex justify-center disabled:opacity-60"
        :disabled="loading"
      >
        <span v-if="loading" class="animate-pulse">Connexion…</span>
        <span v-else>Se connecter</span>
      </button>
    </form>
  </div>
</template>

<style scoped>
/* Les classes input proviennent de @tailwindcss/forms ; aucun style custom requis */
</style>
