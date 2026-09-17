<!-- chatView.vue -->
<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import ChatSidebar from '@/components/ChatSidebar.vue'
import ChatMessages from '@/components/ChatMessages.vue'
import ChatComposer from '@/components/ChatComposer.vue'
import { ArrowLeft, Cloud } from 'lucide-vue-next'

import { useMessages } from '@/store/useMessages'
import { useAuth } from '@/store/useAuth'
import { useUserGroupStore } from '@/store/useUserGroupStore'

const ug = useUserGroupStore()
const store = useMessages()
const auth = useAuth()

const currentUserId = auth.user?.id ?? 0

const location = ref({ lat: null as number | null, lng: null as number | null })

onMounted(async () => {
  await ug.fetch()
  await store.fetchConversationsSummary()

  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition((pos) => {
      location.value.lat = pos.coords.latitude
      location.value.lng = pos.coords.longitude
    })
  }
})

const activeConversationId = computed({
  get: () => store.activeConversationId,
  set: (v) => (store.activeConversationId = v),
})

const activeThread = computed(() =>
  activeConversationId.value ? store.threads[activeConversationId.value] : null,
)

const sending = ref(false)
</script>

<template>
  <div class="p-3 md:p-5 h-[calc(100vh-100px)]">
    <div
      class="flex h-full overflow-hidden bg-white rounded-[28px] shadow-[0_20px_50px_rgba(30,50,90,0.10)] border border-gray-100"
    >
      <!-- MOBILE : sidebar en plein écran si pas de conv -->
      <aside v-if="!activeConversationId" class="md:hidden w-full">
        <ChatSidebar :active-id="activeConversationId" />
      </aside>

      <!-- DESKTOP : sidebar fixe, toujours visible -->
      <aside class="hidden md:flex w-80 flex-shrink-0 border-r border-gray-100">
        <ChatSidebar :active-id="activeConversationId" />
      </aside>

      <!-- ================= CHAT VIEW ================= -->
      <div v-if="activeThread" class="flex flex-col flex-1 min-w-0">
        <!-- Header avec bouton retour (mobile only) -->
        <div class="h-14 flex items-center px-4 md:px-5 border-b border-gray-100 shrink-0">
          <button
            class="md:hidden mr-2 text-gray-500"
            @click="activeConversationId = null"
          >
            <ArrowLeft class="w-6 h-6" />
          </button>
          <span class="font-display font-bold text-[15px] text-gray-900 truncate">
            {{ activeThread?.label || 'Conversation' }}
          </span>
        </div>

        <!-- Bandeau pédagogique -->
        <div class="mx-4 md:mx-5 mt-3.5 px-3.5 py-2 rounded-2xl bg-mint-50 flex items-center gap-2 shrink-0">
          <span class="text-[13px]">🕵️</span>
          <span class="text-[12px] font-semibold text-mint-600">
            Rien n'est jamais totalement supprimé sur Internet — regarde ce que le serveur garde
            de chaque message.
          </span>
        </div>

        <!-- Badge "Nouvelle discussion" -->
        <div v-if="activeThread?.messages.length == 0" class="mx-4 md:mx-5 mt-3 shrink-0">
          <span class="inline-flex items-center gap-2 px-3 py-2 rounded-2xl bg-sun-50 text-sun-600 text-sm">
            <span class="px-2 py-0.5 text-xs rounded-full bg-white font-bold">Nouvelle discussion</span>
            <span>
              avec <strong>{{ activeThread?.label }}</strong
              >. Écrivez votre premier message 👇
            </span>
          </span>
        </div>

        <!-- Messages -->
        <ChatMessages
          :key="activeThread.id"
          :messages="activeThread.messages"
          :current-user-id="currentUserId"
        >
          <div
            v-if="activeThread && activeThread.messages.length === 0"
            class="p-6 text-center text-sm text-gray-400"
          >
            Aucun message pour le moment.
          </div>
        </ChatMessages>

        <!-- Composer -->
        <ChatComposer
          :sending="sending"
          @send="({ text, file }) => store.sendMessageToActive(text, file)"
        />
      </div>

      <!-- Empty state desktop -->
      <div v-else class="hidden md:flex flex-1 flex-col items-center justify-center gap-3 text-center px-6">
        <div class="w-16 h-16 rounded-3xl bg-sky-50 flex items-center justify-center">
          <Cloud class="w-9 h-9 text-sky-500" fill="currentColor" stroke="none" />
        </div>
        <p class="text-sm text-gray-400 max-w-xs">
          Choisis une conversation à gauche, ou lance une nouvelle discussion.
        </p>
      </div>
    </div>
  </div>
</template>
