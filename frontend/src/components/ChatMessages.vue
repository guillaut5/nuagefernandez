<script setup lang="ts">
import type { Message } from '@/types/api'
import { ref, nextTick, onMounted, computed } from 'vue'
import { Trash2, EyeOff, Eye, Ghost } from 'lucide-vue-next'
import { formatWhen } from '@/helpers/datehelper'
import { useMessages } from '@/store/useMessages'
const props = defineProps<{
  messages: Message[] // doit contenir .deleted_for_all: boolean
  currentUserId: number
}>()

const msgStore = useMessages()
/* ---------------------------
   trace "vu par le serveur" (repliée par défaut)
--------------------------- */
const expandedTrace = ref<Set<number>>(new Set())
function toggleTrace(id: number) {
  const next = new Set(expandedTrace.value)
  next.has(id) ? next.delete(id) : next.add(id)
  expandedTrace.value = next
}

/* ---------------------------
   images (sur la liste affichée)
--------------------------- */
const images = computed(() => props.messages.filter((m) => m.image).map((m) => m.image as string))

const currentImageIndex = ref<number | null>(null)

function openImage(msgIndex: number) {
  const img = props.messages[msgIndex].image
  if (!img) return
  currentImageIndex.value = images.value.indexOf(img)
}
function closeImage() {
  currentImageIndex.value = null
}
function prevImage() {
  if (currentImageIndex.value !== null && currentImageIndex.value > 0) currentImageIndex.value--
}
function nextImage() {
  if (currentImageIndex.value !== null && currentImageIndex.value < images.value.length - 1)
    currentImageIndex.value++
}

/* ---------------------------
   scroll auto en bas
--------------------------- */
const container = ref<HTMLDivElement | null>(null)
async function scrollToBottom() {
  await nextTick()
  if (container.value) container.value.scrollTop = container.value.scrollHeight
}
onMounted(() => {
  scrollToBottom()
})

/* ---------------------------
   helpers
--------------------------- */
function authorName(msg: Message): string {
  return msg.sender?.username ?? ''
}
function isMine(msg: Message) {
  return msg.sender?.id === props.currentUserId
}

/* ---------------------------
   actions API
--------------------------- */
async function deleteForAll(msg: Message) {
  msgStore.deleteForAll(msg.id)
}

async function hideForMe(msg: Message) {
  msgStore.hideMessage(msg.id)
}
</script>

<template>
  <div ref="container" class="flex-1 p-4 flex flex-col space-y-4 overflow-y-auto h-full">
    <div
      v-for="(msg, index) in messages"
      :key="msg.id"
      :class="['flex flex-col gap-1', msg.sender.id === currentUserId ? 'items-end' : 'items-start']"
    >
      <div class="max-w-[70%] flex flex-col gap-1" :class="msg.sender.id === currentUserId ? 'items-end' : 'items-start'">
        <!-- Ligne meta (auteur + quand) -->
        <div class="text-[11.5px] text-gray-400 flex items-center gap-2">
          <span class="font-semibold text-gray-500">{{ authorName(msg) }}</span>
          <span>·</span>
          <span>{{ formatWhen(msg.timestamp) }}</span>
        </div>

        <!-- Bulle message -->
        <div
          :class="[
            'inline-block px-3.5 py-2.5 whitespace-pre-wrap break-words relative group text-[14px] leading-snug',
            msg.deleted_for_all
              ? 'bg-coral-50 text-coral-600 italic border-[1.5px] border-dashed border-coral-500 rounded-2xl'
              : msg.sender.id === currentUserId
                ? 'bg-sky-500 text-white rounded-2xl rounded-br-md'
                : 'bg-gray-100 text-gray-900 rounded-2xl rounded-bl-md',
          ]"
        >
          <!-- contenu normal vs placeholder supprimé global -->
          <template v-if="!msg.deleted_for_all">
            <template v-if="msg.text">{{ msg.text }}</template>

            <template v-if="msg.image">
              <img
                :src="msg.image"
                alt="image"
                class="mt-2 rounded-md max-h-32 object-contain cursor-pointer"
                @click="openImage(index)"
              />
            </template>
          </template>
          <template v-else>
            <span class="inline-flex items-center gap-2">
              <Ghost class="w-4 h-4 shrink-0" />
              Supprimé… mais toujours dans les archives du serveur
            </span>
          </template>

          <!-- Bouton action -->
          <button
            v-if="!msg.deleted_for_all && isMine(msg)"
            class="absolute -top-2 -right-2 hidden group-hover:flex items-center justify-center w-7 h-7 rounded-full bg-white text-gray-500 shadow border border-gray-200 hover:bg-gray-50 focus:outline-none"
            :title="'Supprimer pour tous'"
            aria-label="Supprimer pour tous"
            @click.stop="deleteForAll(msg)"
          >
            <Trash2 class="w-3.5 h-3.5" />
          </button>

          <button
            v-else-if="!msg.deleted_for_all && !isMine(msg)"
            class="absolute -top-2 -right-2 hidden group-hover:flex items-center justify-center w-7 h-7 rounded-full bg-white text-gray-500 shadow border border-gray-200 hover:bg-gray-50 focus:outline-none"
            :title="'Masquer pour moi'"
            aria-label="Masquer pour moi"
            @click.stop="hideForMe(msg)"
          >
            <EyeOff class="w-3.5 h-3.5" />
          </button>
        </div>

        <!-- Badge pédagogique : ce que le serveur garde de ce message -->
        <button
          v-if="!msg.deleted_for_all"
          class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-sun-50 text-sun-600 text-[10.5px] font-bold hover:brightness-95 transition"
          @click="toggleTrace(msg.id)"
        >
          <Eye class="w-3 h-3" />
          vu par le serveur
        </button>

        <div
          v-if="expandedTrace.has(msg.id)"
          class="w-56 rounded-xl border-[1.5px] border-dashed border-sun-500 bg-sun-50 px-3 py-2.5 text-left"
        >
          <p class="text-[10.5px] font-bold text-sun-600 mb-1.5">🪪 Carte d'identité du message</p>
          <ul class="text-[11px] text-gray-600 leading-relaxed space-y-0.5">
            <li>🕒 Heure exacte : {{ formatWhen(msg.timestamp) }}</li>
            <li v-if="msg.latitude != null && msg.longitude != null">
              📍 Position enregistrée ({{ msg.latitude.toFixed(2) }}, {{ msg.longitude.toFixed(2) }})
            </li>
            <li v-else>📍 Pas de position transmise cette fois</li>
            <li>🌐 Adresse IP et appareil aussi gardés, visibles par un adulte dans l'admin</li>
          </ul>
        </div>
      </div>
    </div>

    <!-- Modal d'affichage grand format avec navigation -->
    <div
      v-if="currentImageIndex !== null"
      class="fixed inset-0 bg-black bg-opacity-90 flex items-center justify-center z-50"
    >
      <button
        v-if="currentImageIndex > 0"
        class="absolute left-4 text-white text-4xl p-2 bg-black bg-opacity-50 rounded-full"
        @click.stop="prevImage"
      >
        ‹
      </button>

      <img :src="images[currentImageIndex]" class="max-h-[90%] max-w-[90%] rounded-lg" />

      <button
        v-if="currentImageIndex < images.length - 1"
        class="absolute right-4 text-white text-4xl p-2 bg-black bg-opacity-50 rounded-full"
        @click.stop="nextImage"
      >
        ›
      </button>

      <button
        class="absolute top-4 right-4 text-white text-3xl p-2 bg-black bg-opacity-50 rounded-full"
        @click="closeImage"
      >
        ✕
      </button>
    </div>
  </div>
</template>
