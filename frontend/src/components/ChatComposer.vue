<script setup lang="ts">
import { ref, nextTick, onUnmounted } from 'vue'
import { Camera, Send } from 'lucide-vue-next'

const props = defineProps<{ sending: boolean }>()
const emit = defineEmits<{
  (e: 'send', payload: { text: string; file?: File | null }): void
}>()

// état texte + image
const replyText = ref('')
const imageFile = ref<File | null>(null)
const imagePreview = ref<string | null>(null)

// drag & drop
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
  if (file?.type.startsWith('image/')) setPreviewFromFile(file)
}

// fichier
const fileInput = ref<HTMLInputElement | null>(null)
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

// caméra
const showCamera = ref(false)
const videoRef = ref<HTMLVideoElement | null>(null)
let mediaStream: MediaStream | null = null

async function openCamera() {
  try {
    mediaStream = await navigator.mediaDevices.getUserMedia({
      video: { facingMode: 'user' }, // ou 'environment' pour mobile arrière
    })
    showCamera.value = true
    await nextTick()
    if (videoRef.value) {
      videoRef.value.srcObject = mediaStream
      await videoRef.value.play()
    }
  } catch (err) {
    console.error('Camera error:', err)
    // fallback fichier si refus
    fileInput.value?.click()
  }
}

function closeCamera() {
  mediaStream?.getTracks().forEach((t) => t.stop())
  mediaStream = null
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

onUnmounted(() => {
  closeCamera()
})

// envoyer
function sendMessage() {
  if (!replyText.value.trim() && !imageFile.value) return
  emit('send', { text: replyText.value.trim(), file: imageFile.value })
  replyText.value = ''
  clearImage()
}

// gestion retour ligne / ctrl+enter
function newlineOrSend(mode: 'newline' | 'send') {
  if (mode === 'send') {
    sendMessage()
  } else {
    replyText.value += '\n'
    void nextTick()
  }
}
</script>

<template>
  <div class="p-3 border-t flex flex-col gap-2">
    <!-- Aperçu image -->
    <div v-if="imagePreview" class="flex items-center gap-3">
      <img :src="imagePreview" alt="aperçu" class="h-16 w-16 object-cover rounded-md border" />
      <button @click="clearImage" class="px-2 py-1 text-sm rounded bg-gray-100 hover:bg-gray-200">
        ✕ Retirer
      </button>
    </div>

    <!-- Ligne principale -->
    <div class="flex items-center gap-2">
      <!-- Bouton caméra -->
      <button
        type="button"
        class="flex h-10 w-10 items-center justify-center rounded-full hover:bg-gray-100 border"
        @click="openCamera"
        :disabled="props.sending"
      >
        <Camera class="w-5 h-5" />
      </button>
      <input ref="fileInput" type="file" accept="image/*" class="hidden" @change="handleFile" />

      <!-- Zone texte -->
      <textarea
        v-model="replyText"
        placeholder="Écrire un message…"
        class="flex-1 border rounded-2xl p-2 min-h-[42px] max-h-40 resize-y focus:outline-none"
        @keydown.enter.exact.prevent="newlineOrSend('newline')"
        @keydown.enter.ctrl.prevent="newlineOrSend('send')"
        @keydown.enter.meta.prevent="newlineOrSend('send')"
      ></textarea>

      <!-- Bouton envoyer -->
      <button
        type="button"
        class="flex h-10 w-10 items-center justify-center rounded-full bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-60"
        :disabled="props.sending || (!replyText.trim() && !imageFile)"
        @click="sendMessage"
      >
        <Send class="w-5 h-5" />
      </button>
    </div>

    <!-- Modal caméra -->
    <div
      v-if="showCamera"
      class="fixed inset-0 bg-black/70 z-50 flex items-center justify-center p-4"
    >
      <div class="bg-white rounded-md p-4 w-full max-w-md">
        <video ref="videoRef" autoplay playsinline class="w-full rounded-md"></video>
        <div class="mt-3 flex gap-2">
          <button @click="capturePhoto" class="flex-1 bg-blue-600 text-white rounded py-2">
            📸 Capturer
          </button>
          <button @click="closeCamera" class="flex-1 bg-gray-200 rounded py-2">Fermer</button>
        </div>
      </div>
    </div>
  </div>
</template>
