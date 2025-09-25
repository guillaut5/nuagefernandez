<script setup lang="ts">
import { ref } from 'vue'
import { APP_INFO, formatAppInfoLine } from '@/helpers/appInfo'
import { Github } from 'lucide-vue-next'

const open = ref(false)
const line = formatAppInfoLine()
</script>

<template>
  <!-- badge en bas à droite -->
  <button
    class="fixed bottom-3 right-3 z-50 text-[10px] leading-none px-1.5 py-0.5 rounded-full bg-black/70 text-white hover:bg-black/80 focus:outline-none focus:ring"
    @click="open = true"
    aria-label="Informations sur l’application"
  >
    {{ line }}
  </button>

  <!-- modal minimaliste -->
  <div v-if="open" class="fixed inset-0 z-50 flex items-center justify-center">
    <div class="absolute inset-0 bg-black/40" @click="open = false" />
    <div class="relative bg-white rounded-xl shadow-xl p-4 w-[22rem]">
      <h3 class="font-semibold text-lg mb-2">À propos</h3>
      <ul class="text-xs space-y-1">
        <li>
          App : {{ APP_INFO.name }},
          <a
            :href="APP_INFO.repo"
            target="_blank"
            rel="noopener noreferrer"
            class="inline-flex items-center gap-1 text-sm text-blue-600 hover:underline"
          >
            <Github class="w-3.5 h-3.5" aria-hidden="true" />
            GitHub
          </a>
        </li>

        <li><strong>Version</strong> : v{{ APP_INFO.version }}</li>
        <li v-if="APP_INFO.commit"><strong>Commit</strong> : {{ APP_INFO.commit }}</li>
        <li v-if="APP_INFO.branch"><strong>Branche</strong> : {{ APP_INFO.branch }}</li>
        <li><strong>Build</strong> : {{ new Date(APP_INFO.buildDate).toLocaleString() }}</li>
        <li v-if="APP_INFO.repo">
          <strong>Repo</strong> :
          <a
            class="text-blue-600 hover:underline"
            :href="APP_INFO.repo"
            target="_blank"
            rel="noreferrer"
          >
            {{ APP_INFO.repo }}
          </a>
        </li>
      </ul>

      <div class="mt-3 flex gap-2 justify-end">
        <button
          class="px-3 py-1.5 rounded-md border hover:bg-gray-50"
          @click="navigator.clipboard.writeText(JSON.stringify(APP_INFO, null, 2))"
        >
          Copier
        </button>
        <button class="px-3 py-1.5 rounded-md bg-black text-white" @click="open = false">
          Fermer
        </button>
      </div>
    </div>
  </div>
</template>
