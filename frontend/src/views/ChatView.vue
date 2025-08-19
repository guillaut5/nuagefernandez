
<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import ChatSidebar from '@/components/ChatSidebar.vue'
import ChatMessages from '@/components/ChatMessages.vue'
import { useMessages } from '@/store/useMessages'
import { useAuth } from '@/store/useAuth'
import type { GroupSummary, Message, UserSummary } from '@/types/api'

const store = useMessages()

const currentUserId = useAuth().user?.id

onMounted(async () => {
  await Promise.all([
    store.fetchInbox(),
    store.fetchSent(),
  ])
})

const replyText = ref('')
const activeConversationId = ref<string | null>(null)

const conversations = computed(() => {
  const map = new Map<string, {
    id: string
    label: string
    type: 'user' | 'group'
    target: UserSummary | GroupSummary
    messages: Message[]
    lastMessage: Message | null
    lastMessageFromMe: boolean
  }>()

  const allMessages = [
    ...store.inbox.map(ms => ms.message), // Inbox = MessageStatus -> Message
    ...store.sent,                        // Sent = Message[]
  ]

  for (const msg of allMessages) {
    let key = '', label = '', type: 'user' | 'group', target: any

    if (msg.recipient_group) {
      key = `group-${msg.recipient_group.id}`
      label = msg.recipient_group.groupname
      type = 'group'
      target = msg.recipient_group
    } else {
      const other = msg.sender.id === currentUserId ? msg.recipient : msg.sender
      if (!other) continue // sécurité si null

      key = `user-${other.id}`
      label = other.username
      type = 'user'
      target = other
    }

    if (!map.has(key)) {
      map.set(key, { id: key, label, type, target, messages: [], lastMessage: null, lastMessageFromMe: false })
    }

    map.get(key)!.messages.push(msg)
  }

  for (const conv of map.values()) {
    // Trier messages ASC
    conv.messages.sort((a, b) => a.timestamp.localeCompare(b.timestamp))

    // Mettre à jour lastMessage et le flag
    const last = conv.messages.at(-1) || null
    conv.lastMessage = last
    conv.lastMessageFromMe = last ? last.sender.id === currentUserId : false
  }

  // Trier conversations par dernier message DESC
  return Array.from(map.values()).sort(
    (a, b) => (b.lastMessage?.timestamp || '').localeCompare(a.lastMessage?.timestamp || '')
  )
})

// la conversation active est dérivée de la liste + l'id
const activeConversation = computed(() =>
  conversations.value.find(c => c.id === activeConversationId.value) ?? null
)

function selectConversation(convid: any) {
  activeConversationId.value = convid
}

async function sendMessage() {
  if (!activeConversation.value || !replyText.value.trim()) return

  const form = new FormData()
  form.append('text', replyText.value)
  if (activeConversation.value.type === 'group') {
    form.append('recipient_group', activeConversation.value.target.id)
  } else {
    form.append('recipient', activeConversation.value.target.id)
  }

  await store.sendMessage(form)
  await store.fetchInbox()
  await store.fetchSent()
  replyText.value = ''
}
</script>

<template>
  <div class="flex h-[calc(100vh-100px)]">
<ChatSidebar
  :conversations="conversations"
  :active-id="activeConversationId"
  @select="selectConversation"
/>
    <div class="flex flex-col flex-1">
      <ChatMessages
  v-if="activeConversation"
  :key="activeConversation.id"
  :messages="activeConversation.messages"
  :current-user-id="currentUserId"
/>
      <div class="p-2 border-t flex gap-2">
        <input
          v-model="replyText"
          placeholder="Écrire un message…"
          class="flex-1 border rounded p-2"
          @keydown.enter="sendMessage"
        />
        <button @click="sendMessage" class="btn-primary">Envoyer</button>
      </div>
    </div>
  </div>
</template>

