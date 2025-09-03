<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import ChatSidebar from '@/components/ChatSidebar.vue'
import ChatMessages from '@/components/ChatMessages.vue'
import { useMessages } from '@/store/useMessages'
import { useAuth } from '@/store/useAuth'
import { useUserGroupStore } from '@/store/useUserGroupStore'
const ug = useUserGroupStore()

import ChatComposer from '@/components/ChatComposer.vue'

const store = useMessages()

// id utilisateur courant (si tu veux qu'il soit réactif, fais-en un computed sur useAuth().user)
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

// ---- composer
const sending = ref(false)
</script>

<template>
  <div class="flex h-[calc(100vh-100px)]">
    <ChatSidebar :active-id="activeConversationId" />

    <div class="flex flex-col flex-1">
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

      <div
        class="h-9 flex items-center justify-center text-[16px] font-medium tracking-tight text-neutral-700 dark:text-neutral-200 select-none truncate"
        title="{{ activeThread?.label }}"
      >
        {{ activeThread?.label || 'Conversation' }}
      </div>

      <ChatMessages
        v-if="activeThread"
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
