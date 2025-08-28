<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { storeToRefs } from 'pinia'
import { useUserGroupStore } from '@/store/useUserGroupStore'
import { useMessages } from '@/store/useMessages'

const store = useMessages()
const usergroupStore = useUserGroupStore()
const router = useRouter()

// Champs du formulaire
const text = ref('')
const recipient = ref<number | ''>('')
const group = ref<number | ''>('')
const imageFile = ref<File | null>(null)
const location = ref({ lat: null as number | null, lng: null as number | null })

// État
const loading = ref(false)
const error = ref('')
const previewUrl = ref<string | null>(null)

// Caméra (desktop/mobile)
const showCamera = ref(false)
const video = ref<HTMLVideoElement | null>(null)
let stream: MediaStream | null = null

// Store users/groups
onMounted(async () => {
  if (!usergroupStore.loaded) {
    await usergroupStore.fetch()
  }

  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition((pos) => {
      location.value.lat = pos.coords.latitude
      location.value.lng = pos.coords.longitude
    })
  }
})

onUnmounted(() => {
  closeCamera()
  if (previewUrl.value) URL.revokeObjectURL(previewUrl.value)
})

const { users, groups } = storeToRefs(usergroupStore)

// ------- Preview helpers -------
function setPreviewFromFile(file: File) {
  if (previewUrl.value) URL.revokeObjectURL(previewUrl.value) // clean ancienne URL
  imageFile.value = file
  previewUrl.value = URL.createObjectURL(file)
}

function clearImage() {
  if (previewUrl.value) URL.revokeObjectURL(previewUrl.value)
  previewUrl.value = null
  imageFile.value = null
}

// ------- Fichier importé -------
function handleFile(e: Event) {
  const files = (e.target as HTMLInputElement).files
  if (files && files[0]) setPreviewFromFile(files[0])
}

// ------- Caméra -------
function openCamera() {
  showCamera.value = true
  navigator.mediaDevices
    .getUserMedia({ video: { facingMode: { ideal: 'environment' } } })
    .then(async (s) => {
      stream = s
      if (video.value) {
        video.value.srcObject = stream
        try {
          await video.value.play()
        } catch {}
      }
    })
    .catch((err) => {
      console.error('Erreur caméra :', err)
      alert("Impossible d'accéder à la caméra")
      showCamera.value = false
    })
}

function closeCamera() {
  showCamera.value = false
  if (stream) {
    stream.getTracks().forEach((t) => t.stop())
    stream = null
  }
}

function capturePhoto() {
  if (!video.value) return
  const w = video.value.videoWidth
  const h = video.value.videoHeight
  const canvas = document.createElement('canvas')
  canvas.width = w
  canvas.height = h
  const ctx = canvas.getContext('2d')
  if (!ctx) return
  ctx.drawImage(video.value, 0, 0, w, h)
  canvas.toBlob(
    (blob) => {
      if (!blob) return
      const file = new File([blob], `photo_${Date.now()}.jpg`, { type: 'image/jpeg' })
      setPreviewFromFile(file)
      closeCamera()
    },
    'image/jpeg',
    0.9,
  )
}

// ------- Envoi -------
async function handleSubmit() {
  loading.value = true
  error.value = ''
  try {
    const form = new FormData()
    form.append('text', text.value)
    if (recipient.value) form.append('recipient', String(recipient.value))
    if (group.value) form.append('recipient_group', String(group.value))
    if (imageFile.value) form.append('image', imageFile.value)
    if (location.value.lat != null) form.append('latitude', String(location.value.lat))
    if (location.value.lng != null) form.append('longitude', String(location.value.lng))

    console.log([...form.entries()])

    await store.sendMessage(form)
    // reset léger après envoi
    text.value = ''
    recipient.value = ''
    group.value = ''
    clearImage()

    router.push('/inbox')
  } catch (e) {
    error.value = "Erreur lors de l'envoi du message."
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="max-w-lg mx-auto bg-white shadow rounded-xl p-6 space-y-5">
    <h1 class="text-xl font-semibold">Envoyer un message</h1>

    <div>
      <label class="block text-sm font-medium mb-1">Texte</label>
      <textarea v-model="text" required rows="5" class="form-textarea w-full"></textarea>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div>
        <label class="block text-sm font-medium mb-1">À un utilisateur</label>
        <select v-model="recipient" class="form-select w-full">
          <option value="">Aucun</option>
          <option v-for="u in users" :key="u.id" :value="u.id">{{ u.username }}</option>
        </select>
      </div>

      <div>
        <label class="block text-sm font-medium mb-1">À un groupe</label>
        <select v-model="group" class="form-select w-full">
          <option value="">Aucun</option>
          <option v-for="g in groups" :key="g.id" :value="g.id">{{ g.groupname }}</option>
        </select>
      </div>
    </div>

    <div>
      <label class="block text-sm font-medium mb-1">Image</label>
      <input
        type="file"
        accept="image/*"
        capture="environment"
        @change="handleFile"
        class="form-input w-full"
      />
      <button @click="openCamera" class="btn-secondary w-full mt-2">📷 Prendre une photo</button>

      <div v-if="showCamera" class="space-y-3 mt-3">
        <video ref="video" autoplay playsinline class="w-full rounded-md"></video>
        <button @click="capturePhoto" class="btn-primary w-full">📸 Capturer</button>
        <button @click="closeCamera" class="btn w-full">❌ Fermer</button>
      </div>

      <!-- Aperçu -->
      <div v-if="previewUrl" class="mt-3">
        <img
          :src="previewUrl"
          alt="Aperçu de l'image"
          class="w-full max-h-64 object-contain rounded-md border"
        />
        <button @click="clearImage" class="btn w-full mt-2">🗑️ Retirer l’image</button>
      </div>
    </div>

    <p v-if="error" class="text-sm text-red-500">{{ error }}</p>

    <button
      :disabled="loading"
      @click="handleSubmit"
      class="btn-primary w-full disabled:opacity-60"
    >
      <span v-if="loading" class="animate-pulse">Envoi…</span>
      <span v-else>Envoyer</span>
    </button>
  </div>
</template>
