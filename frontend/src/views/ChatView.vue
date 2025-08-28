<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import ChatSidebar from '@/components/ChatSidebar.vue'
import ChatMessages from '@/components/ChatMessages.vue'
import { useMessages } from '@/store/useMessages'
import { useAuth } from '@/store/useAuth'
import { useUserGroupStore } from '@/store/useUserGroupStore'
const ug = useUserGroupStore()

import { Camera, Send } from 'lucide-vue-next'

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
onUnmounted(() => {
  stopCamera()
  if (imagePreview.value) URL.revokeObjectURL(imagePreview.value)
})

const replyText = ref('')

const activeConversationId = computed({
  get: () => store.activeConversationId,
  set: (v) => (store.activeConversationId = v),
})

const activeThread = computed(() =>
  activeConversationId.value ? store.threads[activeConversationId.value] : null,
)

// ---- composer
const sending = ref(false)
const canSend = computed(() => {
  const hasText = replyText.value.trim().length > 0
  const hasImg = !!imageFile.value
  return (hasText || hasImg) && !!activeThread.value
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
  if (!canSend.value || sending.value || !activeThread.value) return
  sending.value = true
  try {
    await store.sendMessageToActive(
      replyText.value,
      imageFile.value,
      //String(location.value.lat),
      //String(location.value.lng),
    )
    replyText.value = ''

    clearImage()

    // refresh messages
  } catch (e) {
    console.error('Erreur envoi message:', e)
  } finally {
    sending.value = false
  }
}

// -- Camera stuff

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
  mediaStream?.getTracks().forEach((t) => t.stop())
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
  const blob: Blob = await new Promise((res) =>
    canvas.toBlob((b) => res(b as Blob), 'image/jpeg', 0.9),
  )
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
      <div
        class="p-3 border-t flex flex-col gap-2"
        @dragover="onDragOver"
        @dragleave="onDragLeave"
        @drop="onDrop"
      >
        <!-- Aperçu image si sélectionnée -->
        <div v-if="imagePreview" class="flex items-center gap-3">
          <img :src="imagePreview" alt="aperçu" class="h-16 w-16 object-cover rounded-md border" />
          <button
            @click="clearImage"
            class="px-2 py-1 text-sm rounded bg-gray-100 hover:bg-gray-200"
          >
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
