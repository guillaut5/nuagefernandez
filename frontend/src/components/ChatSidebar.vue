<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useUserGroupStore } from '@/store/useUserGroupStore'
const usergroupStore = useUserGroupStore()
import { storeToRefs } from 'pinia'

// Store users/groups
onMounted(async () => {
  if (!usergroupStore.loaded) {
    await usergroupStore.fetch()
  }
}
);
const { users, groups } = storeToRefs(usergroupStore)
type Conversation = {
  id: string
  label: string
  type: 'user' | 'group'
  target: any
  messages: any[]
}
type UserSummary = { id: number; username: string }

const props = defineProps<{
  conversations: Conversation[]
  activeId?: string | null
}>()

const emit = defineEmits<{
  (e: 'select', id: string): void
}>()

const search = ref('')

// Filtre des conversations existantes
const filteredConversations = computed(() => {
  const term = search.value.toLowerCase().trim()
  return (props.conversations || []).filter((conv) =>
    conv.label?.toLowerCase().includes(term)
  )
})

// ---------- Nouvelle discussion ----------
const showNewDialog = ref(false)
const searchUser = ref('')

const filteredUsers = computed(() => {
  const term = searchUser.value.toLowerCase().trim()
  const all = users.value ?? []
  if (!term) return all
  return all.filter(u => u.username.toLowerCase().includes(term))
})

function openNewDialog() {
  if (!users.value || users.value.length === 0) return
  showNewDialog.value = true
  searchUser.value = ''
}

function startConversationWith(user: UserSummary) {
  // On construit l'id conversation attendu par le parent: "user-<id>"
  const convId = `user-${user.id}`
  showNewDialog.value = false
  emit('select', convId)
}
</script>

<template>
  <div class="w-full md:w-1/3 max-w-xs border-r h-full flex flex-col">
    <!-- Header: recherche + bouton + -->
    <div class="p-3 border-b flex items-center gap-2">
      <input
        v-model="search"
        type="text"
        placeholder="Rechercher une discussion…"
        class="w-full p-2 border rounded text-sm"
      />
      <button
        v-if="users && users.length"
        class="h-9 w-9 shrink-0 rounded-full border hover:bg-gray-100"
        title="Nouvelle discussion"
        @click="openNewDialog"
      >
        +
      </button>
    </div>

    <!-- Liste des conversations -->
    <ul class="flex-1 overflow-y-auto">
      <li
        v-for="conv in filteredConversations"
        :key="conv.id"
        @click="emit('select', conv.id)"
        :class="[
          'px-3 py-2 cursor-pointer',
          conv.id === props.activeId ? 'bg-blue-50 font-medium' : 'hover:bg-gray-50'
        ]"
      >
        <div class="font-semibold text-sm truncate">{{ conv.label }}</div>
        <div class="text-xs text-gray-500 truncate">
          {{ conv.messages.at(-1)?.text || 'Aucun message' }}
        </div>
      </li>
    </ul>

    <!-- Modale: démarrer une nouvelle discussion -->
    <div
      v-if="showNewDialog"
      class="fixed inset-0 z-50 bg-black/40 flex items-center justify-center p-4"
      @click.self="showNewDialog = false"
    >
      <div class="bg-white rounded-xl shadow-xl w-full max-w-md">
        <div class="p-4 border-b flex items-center justify-between">
          <h3 class="font-semibold">Nouvelle discussion</h3>
          <button class="text-gray-500 hover:text-gray-800" @click="showNewDialog = false">✕</button>
        </div>

        <div class="p-4 space-y-3">
          <input
            v-model="searchUser"
            type="text"
            placeholder="Rechercher un utilisateur…"
            class="w-full p-2 border rounded text-sm"
          />

          <ul class="max-h-64 overflow-y-auto divide-y">
            <li
              v-for="u in filteredUsers"
              :key="u.id"
              class="py-2 px-1 hover:bg-gray-50 cursor-pointer flex items-center justify-between"
              @click="startConversationWith(u)"
            >
              <span class="text-sm">{{ u.username }}</span>
              <span class="text-xs text-gray-400">user-{{ u.id }}</span>
            </li>
            <li v-if="filteredUsers.length === 0" class="py-6 text-center text-sm text-gray-500">
              Aucun utilisateur
            </li>
          </ul>
        </div>

        <div class="p-3 border-t text-right">
          <button class="px-3 py-1 rounded hover:bg-gray-100" @click="showNewDialog = false">
            Annuler
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
