<script setup lang="ts">
import { ref, computed } from 'vue'

const props = defineProps<{
  conversations: Array<{
    id: string
    label: string
    type: 'user' | 'group'
    target: any
    messages: any[]
  }>
  activeId?: string | null

}>()

const emit = defineEmits<{
  (e: 'select', id: string): void
}>()
const search = ref('')

const filteredConversations = computed(() => {
  const term = search.value.toLowerCase().trim()
  return (props.conversations || []).filter((conv) =>
    conv.label?.toLowerCase().includes(term)
  )
})
</script>

<template>
  <div class="w-full md:w-1/3 max-w-xs border-r h-full flex flex-col">
    <div class="p-3 border-b">
      <input
        v-model="search"
        type="text"
        placeholder="Rechercher une discussion…"
        class="w-full p-2 border rounded text-sm"
      />
    </div>

    <ul class="flex-1 overflow-y-auto">
      <li
        v-for="conv in filteredConversations"
        :key="conv.id"
        @click="emit('select', conv.id)"
        :class="['px-3 py-2 cursor-pointer',
          conv.id === props.activeId ? 'bg-blue-50 font-medium' : 'hover:bg-gray-50']">
        <div class="font-semibold text-sm truncate">{{ conv.label }}</div>
        <div class="text-xs text-gray-500 truncate">
          {{ conv.messages.at(-1)?.text || 'Aucun message' }}
        </div>
      </li>
    </ul>
  </div>
</template>

<
