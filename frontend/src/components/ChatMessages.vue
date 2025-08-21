<script setup lang="ts">

import type { Message } from "@/types/api";
import { ref, watch, nextTick, onMounted, computed } from "vue"


const props = defineProps<{
  messages: any[]
  currentUserId: number
}>()

// pour les images en grand

// extrait toutes les images de la conversation
const images = computed(() =>
  props.messages.filter(m => m.image).map(m => m.image as string)
)

const currentImageIndex = ref<number | null>(null)

function openImage(msgIndex: number) {
  const img = props.messages[msgIndex].image
  if (!img) return
  // retrouve l’index de l’image dans le tableau "images"
  currentImageIndex.value = images.value.indexOf(img)
}

function closeImage() {
  currentImageIndex.value = null
}

function prevImage() {
  if (currentImageIndex.value !== null && currentImageIndex.value > 0) {
    currentImageIndex.value--
  }
}

function nextImage() {
  if (
    currentImageIndex.value !== null &&
    currentImageIndex.value < images.value.length - 1
  ) {
    currentImageIndex.value++
  }
}

// pour scroller automatiquement en bas
const container = ref<HTMLDivElement | null>(null)

async function scrollToBottom() {
  await nextTick()
  if (container.value) {
    // container.value.scrollTop = container.value.scrollHeight
  }
}

onMounted(() => {
  scrollToBottom()
})

watch(
  () => props.messages,
  () => {
    scrollToBottom()
  },
  { deep: true }
)

/** Format “il y a 30 s / 40 min / 3 h / 2 j”, sinon date ex: “20 mars 25” */
function formatWhen(iso: string): string {
  const now = new Date()
  const then = new Date(iso)
  const diffMs = now.getTime() - then.getTime()

  // bornes
  const sec = Math.floor(diffMs / 1000)
  const min = Math.floor(sec / 60)
  const hour = Math.floor(min / 60)
  const day = Math.floor(hour / 24)

  if (sec < 60) return `il y a ${sec}s`
  if (min < 60) return `il y a ${min} min`
  if (hour < 24) return `il y a ${hour} h`
  if (day < 7) return `il y a ${day} j`

  // Au-delà de 7 jours → date courte en FR (ex: 20 mars 25)
  return new Intl.DateTimeFormat('fr-FR', {
    day: '2-digit',
    month: 'long',
    year: '2-digit'
  }).format(then)
}

/** Affiche le nom de l’auteur (utile même pour tes propres messages dans un groupe) */
function authorName(msg: Message): string {
  return msg.sender?.username ?? ''
}
</script>
<template>
  <div
    ref="container"
    class="flex-1 p-4 flex flex-col space-y-3 overflow-y-auto h-full"
  >
       <div
      v-for="(msg, index) in messages"
      :key="msg.id"
      :class="[
        'flex',
        msg.sender.id === currentUserId ? 'justify-end' : 'justify-start'
      ]"
    >
      <div class="max-w-[70%]">
        <!-- Ligne meta (auteur + quand) -->
        <div
          class="text-xs text-gray-500 mb-1 flex items-center gap-2"
          :class="msg.sender.id === currentUserId ? 'justify-end' : 'justify-start'"
        >
          <span class="font-medium">{{ authorName(msg) }}</span>
          <span>·</span>
          <span>{{ formatWhen(msg.timestamp) }}</span>
        </div>

        <!-- Bulle message -->
        <div
          :class="[
            'inline-block px-3 py-2 rounded-2xl whitespace-pre-wrap break-words',
            msg.sender.id === currentUserId
              ? 'bg-blue-100 text-gray-900'
              : 'bg-gray-100 text-gray-900'
          ]"
        >
          <template v-if="msg.text">{{ msg.text }}</template>

          <!-- optionnel : image si présente -->
          <template v-if="msg.image">
            <img
              :src="msg.image"
              alt="image"
              class="mt-2 rounded-md max-h-32 object-contain cursor-pointer"
              @click="openImage(index)"
            />
          </template>
        </div>
      </div>
    </div>

    <!-- Modal d’affichage grand format avec navigation -->
    <div
      v-if="currentImageIndex !== null"
      class="fixed inset-0 bg-black bg-opacity-90 flex items-center justify-center z-50"
    >
      <!-- Bouton précédent -->
      <button
        v-if="currentImageIndex > 0"
        class="absolute left-4 text-white text-4xl p-2 bg-black bg-opacity-50 rounded-full"
        @click.stop="prevImage"
      >
        ‹
      </button>

      <!-- Image -->
      <img
        :src="images[currentImageIndex]"
        class="max-h-[90%] max-w-[90%] rounded-lg"
      />

      <!-- Bouton suivant -->
      <button
        v-if="currentImageIndex < images.length - 1"
        class="absolute right-4 text-white text-4xl p-2 bg-black bg-opacity-50 rounded-full"
        @click.stop="nextImage"
      >
        ›
      </button>

      <!-- Fermer -->
      <button
        class="absolute top-4 right-4 text-white text-3xl p-2 bg-black bg-opacity-50 rounded-full"
        @click="closeImage"
      >
        ✕
      </button>
    </div>
  </div>
</template>
