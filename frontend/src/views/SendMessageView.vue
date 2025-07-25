<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { storeToRefs } from 'pinia'
import { useUserGroupStore } from '@/store/useUserGroupStore'
import { useMessages } from '@/store/useMessages'

const store = useMessages()
const usergroup = useUserGroupStore()
const router = useRouter()

// Champs du formulaire
const text = ref('')
const recipient = ref<number | ''>('')
const group = ref<number | ''>('')
const imageFile = ref<File | null>(null)
const location = ref({ lat: null as number | null, lng: null as number | null })

// État de chargement et erreurs
const loading = ref(false)
const error = ref('')
const usergroupLoaded = ref(false)


// Campera pour  PC

const showCamera = ref(false)
const video = ref<HTMLVideoElement | null>(null)

let stream: MediaStream | null = null

function openCamera() {
  showCamera.value = true
  navigator.mediaDevices.getUserMedia({ video: true })
    .then(s => {
      stream = s
      if (video.value) {
        video.value.srcObject = stream
      }
    })
    .catch(err => {
      console.error('Erreur caméra :', err)
      alert("Impossible d'accéder à la caméra")
      showCamera.value = false
    })
}

function capturePhoto() {
  if (!video.value) return

  const canvas = document.createElement('canvas')
  canvas.width = video.value.videoWidth
  canvas.height = video.value.videoHeight
  const ctx = canvas.getContext('2d')
  if (ctx) {
    ctx.drawImage(video.value, 0, 0)
    canvas.toBlob(blob => {
      if (blob) {
        imageFile.value = new File([blob], 'photo.jpg', { type: blob.type })
        closeCamera()
      }
    }, 'image/jpeg')
  }
}

function closeCamera() {
  showCamera.value = false
  if (stream) {
    stream.getTracks().forEach(t => t.stop())
    stream = null
  }
}


// Initialisation
onMounted(async () => {
  if (!usergroup.loaded) {
    await usergroup.fetch()
  }
  usergroupLoaded.value = true

  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition((pos) => {
      location.value.lat = pos.coords.latitude
      location.value.lng = pos.coords.longitude
    })
  }
})
onUnmounted(() => closeCamera())

const { users, groups } = storeToRefs(usergroup)

function handleFile(e: Event) {
  const files = (e.target as HTMLInputElement).files
  if (files && files[0]) imageFile.value = files[0]
}

async function handleSubmit() {
  loading.value = true
  error.value = ''
  try {
    const form = new FormData()
    form.append('text', text.value)
    if (recipient.value) form.append('recipient', String(recipient.value))
    if (group.value) form.append('recipient_group', String(group.value))
    if (imageFile.value) form.append('image', imageFile.value)
    if (location.value.lat) form.append('latitude', String(location.value.lat))
    if (location.value.lng) form.append('longitude', String(location.value.lng))

    await store.sendMessage(form)
    router.push('/inbox')
  } catch {
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
          <option v-for="g in groups" :key="g.id" :value="g.id">{{ g.name }}</option>
        </select>
      </div>
    </div>

    <div>
      <label class="block text-sm font-medium mb-1">Image  dqssdq</label>
      <input
        type="file"
        accept="image/*"
        capture="environment"
        @change="handleFile"
        class="form-input w-full"
      />
      <button @click="openCamera" class="btn-secondary w-full">📷 Prendre une photo</button>
<div v-if="showCamera" class="space-y-3">
  <video ref="video" autoplay class="w-full rounded-md"></video>
  <button @click="capturePhoto" class="btn-primary w-full">📸 Capturer</button>
  <button @click="closeCamera" class="btn w-full">❌ Fermer</button>
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

<style scoped></style>
