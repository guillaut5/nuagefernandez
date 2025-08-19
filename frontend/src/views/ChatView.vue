
<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import ChatSidebar from '@/components/ChatSidebar.vue'
import ChatMessages from '@/components/ChatMessages.vue'
import { useMessages } from '@/store/useMessages'
import { useAuth } from '@/store/useAuth'

const store = useMessages()

const currentUserName = useAuth().user?.username
const currentUserId = useAuth().user?.id

onMounted(() => store.fetchInbox())

const replyText = ref('')
const activeConversation = ref<any | null>(null)

const conversations = computed(() => {
  const map = new Map()
  for (const msgStatus of store.inbox) {
    const msg = msgStatus.message
    let key = '', label = '', type = '', target = null
    if (msg.recipient_group) {
      key = `group-${msg.recipient_group.id}`
      label = msg.recipient_group.groupname
      type = 'group'
      target = msg.recipient_group
    } else {
      const other = msg.sender.id === currentUserId ? msg.recipient : msg.sender
      key = `user-${other.id}`
      label = other.username
      type = 'user'
      target = other
    }
    if (!map.has(key)) {
      map.set(key, { id: key, label, type, target, messages: [] })
    }
    map.get(key).messages.push(msg)
  }
  return Array.from(map.values()).sort((a, b) =>
    b.messages.at(-1).timestamp.localeCompare(a.messages.at(-1).timestamp)
  )
})


function selectConversation(conv: any) {
  activeConversation.value = conv
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
  replyText.value = ''
}
</script>

<template>
  <div class="flex h-[calc(100vh-60px)]">
    <ChatSidebar
      :conversations="conversations"
      @select="selectConversation"
    />
    <div class="flex flex-col flex-1">
      <ChatMessages
        v-if="activeConversation"
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

