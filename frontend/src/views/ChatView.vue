<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import ChatSidebar from '@/components/ChatSidebar.vue'
import ChatMessages from '@/components/ChatMessages.vue'
import { useMessages } from '@/store/useMessages'
import { useAuth } from '@/store/useAuth'
import { useUserGroupStore } from '@/store/useUserGroupStore'
const ug = useUserGroupStore()

import type { GroupSummary, Message, UserSummary } from '@/types/api'
import { Camera, Send } from 'lucide-vue-next'

const store = useMessages()

// id utilisateur courant (si tu veux qu'il soit réactif, fais-en un computed sur useAuth().user)
const auth = useAuth()
const currentUserId = auth.user?.id ?? 0

const location = ref({ lat: null as number | null, lng: null as number | null })


let timerIntervalId: number | undefined
onMounted(async () => {
  await ug.fetch()
  await store.fetchAllMessages()
  timerIntervalId = window.setInterval(() => {
    store.fetchAllMessages()
  }, 5000)

  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition((pos) => {
      location.value.lat = pos.coords.latitude
      location.value.lng = pos.coords.longitude
    })
  }
})
onUnmounted(() => {
  if (timerIntervalId) clearInterval(timerIntervalId)
  stopCamera()
  if (imagePreview.value) URL.revokeObjectURL(imagePreview.value)
})

const replyText = ref('')
const activeConversationId = ref<string | null>(null)

// ---- état image du composer
const fileInput = ref<HTMLInputElement | null>(null)
const imageFile = ref<File | null>(null)
const imagePreview = ref<string | null>(null)


// ---- état caméra
const showCamera = ref(false)
const videoRef = ref<HTMLVideoElement | null>(null)
let mediaStream: MediaStream | null = null
// ---- helpers image
function setPreviewFromFile(file: File) {
  if (imagePreview.value) URL.revokeObjectURL(imagePreview.value)
  imageFile.value = file
  imagePreview.value = URL.createObjectURL(file)
}
function handleFile(e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (file) setPreviewFromFile(file)
}
function clearImage() {
  imageFile.value = null
  if (imagePreview.value) URL.revokeObjectURL(imagePreview.value)
  imagePreview.value = null
}

// ---- ouverture caméra OU fallback fichier
async function openCameraOrFile() {
  // Support getUserMedia ?
  if (!navigator.mediaDevices?.getUserMedia) {
    // Fallback : explo fichier
    fileInput.value?.click()
    return
  }

  try {
    // On essaye l’objectif arrière si possible
    mediaStream = await navigator.mediaDevices.getUserMedia({
      video: { facingMode: { ideal: 'environment' } },
      audio: false,
    })
    showCamera.value = true
    await nextTick()
    if (videoRef.value) {
      videoRef.value.srcObject = mediaStream
      await videoRef.value.play()
    }
  } catch {
    // Permission refusée / pas de caméra → fallback fichier
    fileInput.value?.click()
  }
}

function stopCamera() {
  mediaStream?.getTracks().forEach(t => t.stop())
  mediaStream = null
}
function closeCamera() {
  stopCamera()
  showCamera.value = false
}

async function capturePhoto() {
  if (!videoRef.value) return
  const w = videoRef.value.videoWidth
  const h = videoRef.value.videoHeight
  const canvas = document.createElement('canvas')
  canvas.width = w
  canvas.height = h
  const ctx = canvas.getContext('2d')!
  ctx.drawImage(videoRef.value, 0, 0, w, h)
  const blob: Blob = await new Promise(res => canvas.toBlob(b => res(b as Blob), 'image/jpeg', 0.9))
  const file = new File([blob], `camera_${Date.now()}.jpg`, { type: 'image/jpeg' })
  setPreviewFromFile(file)
  closeCamera()
}


// ---- drag & drop (optionnel)
const isDragging = ref(false)
function onDragOver(e: DragEvent) {
  e.preventDefault()
  isDragging.value = true
}
function onDragLeave() {
  isDragging.value = false
}
function onDrop(e: DragEvent) {
  e.preventDefault()
  isDragging.value = false
  const file = e.dataTransfer?.files?.[0]
  if (file && file.type.startsWith('image/')) setPreviewFromFile(file)
}

// ---- build des conversations (reçu + envoyé)
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
      if (!other) continue
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

  // trier les messages et calculer lastMessage
  for (const conv of map.values()) {
    conv.messages.sort((a, b) => a.timestamp.localeCompare(b.timestamp))
    const last = conv.messages.at(-1) || null
    conv.lastMessage = last
    conv.lastMessageFromMe = last ? last.sender.id === currentUserId : false
  }

  // trier les conversations par dernier message DESC
  return Array.from(map.values()).sort(
    (a, b) => (b.lastMessage?.timestamp || '').localeCompare(a.lastMessage?.timestamp || '')
  )
})


// gestion de nouvelles converstation
function buildDraftConversationFromId(id: string) {
  if (id.startsWith('user-')) {
    const uid = Number(id.slice(5))
    const user = ug.getUserById(uid)
    if (!user) return null
    return {
      id,
      label: user.username,
      type: 'user' as const,
      target: user,
      messages: [],
      lastMessage: null,
      lastMessageFromMe: false,
      isDraft: true,              // 👈 brouillon
    }
  }
  if (id.startsWith('group-')) {
    const gid = Number(id.slice(6))
    const group = ug.getGroupById(gid)
    if (!group) return null
    return {
      id,
      label: group.name,
      type: 'group' as const,
      target: group,
      messages: [],
      lastMessage: null,
      lastMessageFromMe: false,
      isDraft: true,              // 👈 brouillon

    }
  }
  return null
}

// conversation active dérivée
const activeConversation = computed(() => {
  const id = activeConversationId.value
  if (!id) return null
  // essaie d’abord de trouver une vraie conversation
  const real = conversations.value.find(c => c.id === id)
  if (real) return real
  // sinon, fabrique une conversation vide à la volée
  return buildDraftConversationFromId(id)
})
function selectConversation(convid: string) {
  activeConversationId.value = convid
}

const isNewConversation = computed(() =>
  !!activeConversation.value &&
  (activeConversation.value.isDraft || activeConversation.value.messages.length === 0)
)

// ---- composer
const sending = ref(false)
const canSend = computed(() => {
  const hasText = replyText.value.trim().length > 0
  const hasImg = !!imageFile.value
  return (hasText || hasImg) && !!activeConversation.value
})

function newlineOrSend(mode: 'newline' | 'send') {
  if (mode === 'send') {
    void sendMessage()
  } else {
    replyText.value += '\n'
    void nextTick()
  }
}

async function sendMessage() {
  if (!canSend.value || sending.value || !activeConversation.value) return
  sending.value = true
  try {
    const form = new FormData()
    const text = replyText.value.trim()
    if (text) form.append('text', text)

    // cible selon la conversation
    if (activeConversation.value.type === 'group') {
      form.append('recipient_group', String((activeConversation.value.target as GroupSummary).id))
    } else {
      form.append('recipient', String((activeConversation.value.target as UserSummary).id))
    }

    if (imageFile.value) form.append('image', imageFile.value)

    // POST (si tu as déjà store.sendMessage, tu peux l’utiliser ici)
    if (location.value.lat != null) form.append('latitude', String(location.value.lat))
    if (location.value.lng != null) form.append('longitude', String(location.value.lng))
    await store.sendMessage(form)
    // reset composer
    replyText.value = ''
    clearImage()

    // refresh messages
    await store.fetchAllMessages()
  } catch (e) {
    console.error('Erreur envoi message:', e)
  } finally {
    sending.value = false
  }
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
       <!-- Badge "Nouvelle discussion" -->
      <div v-if="isNewConversation" class="px-4 py-2 border-b bg-amber-50 text-amber-800 text-sm">
        <span class="inline-flex items-center gap-2">
          <span class="inline-block px-2 py-0.5 text-xs rounded-full bg-amber-200 font-medium">
            Nouvelle discussion
          </span>
          <span>
            avec <strong>{{ activeConversation?.label }}</strong>. Écrivez votre premier message 👇
          </span>
        </span>
      </div>
      <ChatMessages
        v-if="activeConversation"
        :key="activeConversation.id"
        :messages="activeConversation.messages"
        :current-user-id="currentUserId"
      >
      <div v-if="activeConversation && activeConversation.messages.length === 0"
          class="p-6 text-center text-sm text-gray-500">
        Aucun message pour le moment.
      </div>
      </ChatMessages>

      <!-- Composer -->
      <div
        class="p-3 border-t flex flex-col gap-2"
        @dragover="onDragOver"
        @dragleave="onDragLeave"
        @drop="onDrop"
      >
        <!-- Aperçu image si sélectionnée -->
        <div v-if="imagePreview" class="flex items-center gap-3">
          <img :src="imagePreview" alt="aperçu" class="h-16 w-16 object-cover rounded-md border" />
          <button @click="clearImage" class="px-2 py-1 text-sm rounded bg-gray-100 hover:bg-gray-200">
            ✕ Retirer
          </button>
        </div>

        <!-- Bandeau drag & drop -->
        <div
          v-if="isDragging && !imagePreview"
          class="border-2 border-dashed rounded-md p-3 text-sm text-gray-500"
        >
          Déposez votre image ici…
        </div>

        <div class="flex items-center gap-2">
          <!-- Bouton caméra / fallback fichier -->
          <button
            type="button"
            class="flex h-10 w-10 items-center justify-center rounded-full hover:bg-gray-100 border"
            @click="openCameraOrFile"
            :disabled="sending"
            title="Prendre une photo ou choisir un fichier"
          >
            <Camera class="w-5 h-5" />
          </button>
          <input
            ref="fileInput"
            type="file"
            accept="image/*"
            capture="environment"
            class="hidden"
            @change="handleFile"
          />

          <!-- Zone de saisie -->
          <textarea
            v-model="replyText"
            placeholder="Écrire un message…"
            class="flex-1 border rounded-2xl p-2 min-h-[42px] max-h-40 resize-y focus:outline-none"
            @keydown.enter.exact.prevent="newlineOrSend('newline')"
            @keydown.enter.ctrl.prevent="newlineOrSend('send')"
            @keydown.enter.meta.prevent="newlineOrSend('send')"
          ></textarea>

          <!-- Envoyer -->
          <button
            type="button"
            class="flex h-10 w-10 items-center justify-center rounded-full bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-60"
            :disabled="sending || !canSend"
            @click="sendMessage"
            title="Envoyer (Ctrl/Cmd+Entrée)"
          >
            <Send class="w-5 h-5" />
          </button>
        </div>

        <!-- Modal Caméra -->
        <div
          v-if="showCamera"
          class="fixed inset-0 bg-black/70 z-50 flex items-center justify-center p-4"
        >
          <div class="bg-white rounded-b-full p-4 w-full max-w-md">
            <div class="text-sm text-gray-600 mb-2">Caméra</div>
            <video ref="videoRef" autoplay playsinline class="w-full rounded-md"></video>
            <div class="mt-3 flex gap-2">
              <button @click="capturePhoto" class="btn-primary flex-1">📸 Capturer</button>
              <button @click="closeCamera" class="btn flex-1">❌ Fermer</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

