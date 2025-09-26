<!-- chatView.vue -->
<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import ChatSidebar from '@/components/ChatSidebar.vue'
import ChatMessages from '@/components/ChatMessages.vue'
import ChatComposer from '@/components/ChatComposer.vue'
import { ArrowLeft } from 'lucide-vue-next'

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
  <div class="flex h-[calc(100vh-100px)] overflow-hidden">
    <!-- MOBILE : sidebar en plein écran si pas de conv -->
    <aside v-if="!activeConversationId" class="md:hidden w-full">
      <ChatSidebar :active-id="activeConversationId" />
    </aside>

    <!-- DESKTOP : sidebar fixe, toujours visible -->
    <aside
      class="hidden md:flex w-80 flex-shrink-0 bg-white/60 backdrop-blur-xl border-r shadow-[0_10px_40px_rgba(0,0,0,0.06)]"
    >
      <ChatSidebar :active-id="activeConversationId" />
    </aside>
    <!-- ================= CHAT VIEW ================= -->
    <div v-if="activeThread" class="flex flex-col flex-1">
      <!-- Header avec bouton retour (mobile only) -->
      <div class="h-12 flex items-center px-4 border-b bg-white/70 backdrop-blur sticky top-0 z-10">
        <button class="md:hidden mr-2 text-gray-600" @click="activeConversationId = null">
          <ArrowLeft class="w-6 h-6" />
        </button>
        <span class="font-medium truncate">
          {{ activeThread?.label || 'Conversation' }}
        </span>
      </div>

      <!-- Badge "Nouvelle discussion" -->
      <div
        v-if="activeThread?.messages.length == 0"
        class="px-4 py-2 border-b bg-amber-50 text-amber-800 text-sm"
      >
        <span class="inline-flex items-center gap-2">
          <span class="inline-block px-2 py-0.5 text-xs rounded-full bg-amber-200 font-medium">
            Nouvelle discussion
          </span>
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
          class="p-6 text-center text-sm text-gray-500"
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
  </div>
</template>
