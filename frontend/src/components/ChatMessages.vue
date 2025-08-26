<script setup lang="ts">
import type { Message } from '@/types/api'
import { ref, nextTick, onMounted, computed } from 'vue'
import { Trash2, EyeOff } from 'lucide-vue-next' // ← icônes Lucide
import { formatWhen } from '@/helpers/datehelper'
import { useMessages } from '@/store/useMessages'
const props = defineProps<{
  messages: Message[] // doit contenir .deleted_for_all: boolean
  currentUserId: number
}>()

const msgStore = useMessages()
/* ---------------------------
   états locaux (optimistes)
--------------------------- */

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
  <div ref="container" class="flex-1 p-4 flex flex-col space-y-3 overflow-y-auto h-full">
    <div
      v-for="(msg, index) in messages"
      :key="msg.id"
      :class="['flex', msg.sender.id === currentUserId ? 'justify-end' : 'justify-start']"
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
            'inline-block px-3 py-2 rounded-2xl whitespace-pre-wrap break-words relative group',
            msg.sender.id === currentUserId
              ? 'bg-blue-100 text-gray-900'
              : 'bg-gray-100 text-gray-900',
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
            <em class="text-gray-600">Message supprimé (toujours conservé côté serveur)</em>
          </template>

          <!-- Bouton action (Lucide) -->
          <button
            v-if="!msg.deleted_for_all && isMine(msg)"
            class="absolute -top-2 -right-2 hidden group-hover:flex items-center justify-center w-7 h-7 rounded-full bg-gray-300 text-gray-700 hover:bg-gray-400 focus:outline-none focus:ring"
            :title="'Supprimer pour tous'"
            aria-label="Supprimer pour tous"
            @click.stop="deleteForAll(msg)"
          >
            <Trash2 class="w-4 h-4" />
          </button>

          <button
            v-else-if="!msg.deleted_for_all && !isMine(msg)"
            class="absolute -top-2 -right-2 hidden group-hover:flex items-center justify-center w-7 h-7 rounded-full bg-gray-300 text-gray-700 hover:bg-gray-400 focus:outline-none focus:ring"
            :title="'Masquer pour moi'"
            aria-label="Masquer pour moi"
            @click.stop="hideForMe(msg)"
          >
            <EyeOff class="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>

    <!-- Modal d’affichage grand format avec navigation -->
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
