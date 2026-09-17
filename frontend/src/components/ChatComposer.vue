<script setup lang="ts">
import { ref, nextTick, onUnmounted, onMounted } from 'vue'
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

onMounted(() => {
  // si on perd le focus, on force le close camera
  window.addEventListener('blur', closeCamera)
})
onUnmounted(() => {
  window.addEventListener('blur', closeCamera)

  closeCamera()
})

// envoyer
function sendMessage() {
  const text = replyText.value.trim()
  const file = imageFile.value

  if (!text && !file) return // rien du tout

  emit('send', { text, file })
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
  <div class="p-3.5 border-t border-gray-100 flex flex-col gap-2.5">
    <!-- Aperçu image -->
    <div v-if="imagePreview" class="flex items-center gap-3">
      <img :src="imagePreview" alt="aperçu" class="h-16 w-16 object-cover rounded-xl border border-gray-200" />
      <button
        @click="clearImage"
        class="px-2.5 py-1 text-sm rounded-full bg-gray-100 text-gray-600 hover:bg-gray-200"
      >
        ✕ Retirer
      </button>
    </div>

    <!-- Ligne principale -->
    <div class="flex items-center gap-2.5">
      <!-- Bouton caméra -->
      <button
        type="button"
        class="flex h-[42px] w-[42px] shrink-0 items-center justify-center rounded-2xl bg-sun-50 text-sun-600 hover:brightness-95 transition"
        @click="openCamera"
        :disabled="props.sending"
      >
        <Camera class="w-[19px] h-[19px]" />
      </button>
      <input ref="fileInput" type="file" accept="image/*" class="hidden" @change="handleFile" />

      <!-- Zone texte -->
      <textarea
        v-model="replyText"
        placeholder="Écrire un message…"
        class="flex-1 border-[1.5px] border-gray-200 bg-gray-50 rounded-2xl px-4 py-3 min-h-[42px] max-h-40 resize-y text-[14px] focus:outline-none focus:ring-4 focus:ring-sky-50 focus:border-sky-500"
        @keydown.enter.exact.prevent="newlineOrSend('newline')"
        @keydown.enter.ctrl.prevent="newlineOrSend('send')"
        @keydown.enter.meta.prevent="newlineOrSend('send')"
      ></textarea>

      <!-- Bouton envoyer -->
      <button
        type="button"
        class="flex h-[42px] w-[42px] shrink-0 items-center justify-center rounded-2xl bg-coral-500 text-white hover:bg-coral-600 shadow-[0_8px_18px_rgba(230,110,60,0.35)] disabled:opacity-50 disabled:shadow-none transition"
        :disabled="props.sending || (!replyText.trim() && !imageFile)"
        @click="sendMessage"
      >
        <Send class="w-[18px] h-[18px]" />
      </button>
    </div>

    <!-- Modal caméra -->
    <div
      v-if="showCamera"
      class="fixed inset-0 bg-gray-900/70 z-50 flex items-center justify-center p-4"
    >
      <div class="bg-white rounded-2xl p-4 w-full max-w-md">
        <video ref="videoRef" autoplay playsinline class="w-full rounded-xl"></video>
        <div class="mt-3 flex gap-2">
          <button
            @click="capturePhoto"
            class="flex-1 inline-flex items-center justify-center gap-2 bg-coral-500 text-white rounded-xl py-2.5 font-semibold hover:bg-coral-600"
          >
            <Camera class="w-4 h-4" /> Capturer
          </button>
          <button
            @click="closeCamera"
            class="flex-1 bg-gray-100 text-gray-700 rounded-xl py-2.5 font-semibold hover:bg-gray-200"
          >
            Fermer
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
