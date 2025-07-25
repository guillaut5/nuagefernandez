<script setup lang="ts">
import { defineProps, computed } from 'vue'
import { storeToRefs } from 'pinia'
import { useMessages } from '@/store/useMessages'
import { X, Eye } from 'lucide-vue-next'

/** Props */
const props = defineProps<{ statusId: number }>()

/** Emits */
const emit = defineEmits<{
  (e: 'close'): void
  (e: 'mark-read'): void
}>()

/** Store pour retrouver le statut */
const msgStore = useMessages()
const { inbox } = storeToRefs(msgStore)

/** Trouve le statut correspondant */
const status = computed(() => inbox.value.find((s) => s.id === props.statusId))

/** Gère le marquage comme lu */
async function markRead() {
  if (!status.value || status.value.is_read) return
  await msgStore.markAsRead(props.statusId)
  emit('mark-read')
}
</script>

<template>
  <!-- Backdrop -->
  <div
    class="fixed inset-0 bg-black/40 flex items-center justify-center z-50"
    @click.self="emit('close')"
  >
    <!-- Modal card -->
    <div
      class="bg-white rounded-2xl shadow-xl w-full max-w-md p-6 space-y-6 animate-fade"
    >
      <div class="flex justify-between items-center">
        <h2 class="text-xl font-semibold">Détail du message</h2>
        <button @click="emit('close')" class="text-gray-500 hover:text-gray-800">
          <X class="w-5 h-5" />
        </button>
      </div>

      <div v-if="status">
        <p class="text-sm text-gray-500 mb-2">
          De <span class="font-medium">{{ status.message.sender_username }}</span>
          • {{ new Date(status.message.timestamp).toLocaleString() }}
        </p>

        <p class="whitespace-pre-wrap break-words mb-4">{{ status.message.text }}</p>

        <img
          v-if="status.message.image"
          :src="status.message.image"
          alt="image jointe"
          class="rounded-lg max-h-64 object-contain mx-auto"
        />

        <p v-if="status.message.latitude" class="text-xs text-gray-400 mt-3">
          📍 Lat {{ status.message.latitude }}, Lng {{ status.message.longitude }}
        </p>
      </div>

      <div class="flex justify-end gap-4">
        <button @click="emit('close')" class="btn-primary bg-gray-200 text-gray-800">
          Fermer
        </button>
        <button
          v-if="status && !status.is_read"
          @click="markRead"
          class="btn-primary flex items-center gap-1"
        >
          <Eye class="w-4 h-4" /> Marquer comme lu
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
@keyframes fade {
  from {
    opacity: 0;
    transform: translateY(10px);
  }

  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-fade {
  animation: fade 0.25s ease-out;
}
</style>
