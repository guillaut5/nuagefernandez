<!-- ChatSidebar.vue -->
<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import { useUserGroupStore } from '@/store/useUserGroupStore'
import { useAuth } from '@/store/useAuth'
import { useMessages } from '@/store/useMessages'
import { formatWhen } from '@/helpers/datehelper'
import { Plus, Search, X, User, Users, Cloud } from 'lucide-vue-next'

const usergroupStore = useUserGroupStore()
const { users, groups, loaded } = storeToRefs(usergroupStore)

const messageStore = useMessages()
const auth = useAuth()
const meId = auth.user?.id
const meInitial = (auth.user?.username || '?').slice(0, 1).toUpperCase()

onMounted(async () => {
  messageStore.fetchConversationsSummary()
  if (!loaded.value) await usergroupStore.fetch()
})

/* ---- Recherche conversations ---- */
const search = ref('')
const filteredConversations = computed(() => {
  const term = search.value.toLowerCase().trim()
  return (messageStore.conversationsSummaries || []).filter((c) =>
    c.label?.toLowerCase().includes(term),
  )
})

function avatarLabel(label: string, type: 'user' | 'group') {
  if (type === 'group') {
    return (label || '?').replace(/[^\p{L}\p{N}]/gu, '').slice(0, 2).toUpperCase()
  }
  return (label || '?').slice(0, 1).toUpperCase()
}

/* ---- Nouvelle discussion ---- */
const showNewDialog = ref(false)
const searchUser = ref('')
const searchGroup = ref('')
const activeNewTab = ref<'users' | 'groups'>('users')

const filteredUsers = computed(() => {
  const list = users.value ?? []
  const term = searchUser.value.toLowerCase().trim()
  return list.filter((u) => u.id !== meId).filter((u) => u.username.toLowerCase().includes(term))
})

const filteredGroups = computed(() => {
  const all = groups.value ?? []
  const term = searchGroup.value.toLowerCase().trim()
  if (!term) return all
  return all.filter((g) => g.groupname.toLowerCase().includes(term))
})

function openNewDialog() {
  const hasUsers = (users.value?.length ?? 0) > 0
  const hasGroups = (groups.value?.length ?? 0) > 0
  if (!hasUsers && !hasGroups) return
  activeNewTab.value = hasUsers ? 'users' : 'groups'
  showNewDialog.value = true
  searchUser.value = ''
  searchGroup.value = ''
}

function startConversation(cid: string) {
  messageStore.openConversation(cid)
}

function startConversationWithUser(u: { id: number }) {
  showNewDialog.value = false
  messageStore.openConversation(`user-${u.id}`)
}
function startConversationWithGroup(g: { id: number }) {
  showNewDialog.value = false
  messageStore.openConversation(`group-${g.id}`)
}
</script>

<template>
  <div class="w-full h-full flex flex-col bg-white">
    <!-- Header -->
    <div class="px-3.5 pt-4">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-2.5">
          <div class="size-9 rounded-2xl bg-sky-50 flex items-center justify-center">
            <Cloud class="w-5 h-5 text-sky-500" fill="currentColor" stroke="none" />
          </div>
          <span class="font-display font-bold text-[15px] text-gray-900">NuageFernandez</span>
        </div>

        <button
          v-if="(users && users.length) || (groups && groups.length)"
          class="size-8 grid place-items-center rounded-[11px] bg-coral-500 text-white hover:bg-coral-600 active:scale-[0.96] transition"
          title="Nouvelle discussion"
          @click="openNewDialog"
        >
          <Plus class="w-4 h-4" />
        </button>
      </div>

      <!-- Search -->
      <div class="mt-3.5 relative">
        <span class="absolute inset-y-0 left-0 pl-3 flex items-center text-gray-400">
          <Search class="w-4 h-4" />
        </span>
        <input
          v-model="search"
          type="search"
          placeholder="Rechercher"
          class="w-full rounded-2xl border-[1.5px] border-gray-200 bg-gray-50 pl-9 pr-3 py-2.5 text-sm focus:outline-none focus:ring-4 focus:ring-sky-50 focus:border-sky-500"
        />
      </div>
    </div>

    <!-- List -->
    <ul class="mt-3 px-2.5 pb-2 overflow-y-auto sidebar-scroll flex-1">
      <li v-for="conv in filteredConversations" :key="conv.id" class="mb-1">
        <button
          @click="startConversation(conv.id)"
          class="w-full text-left rounded-2xl px-2.5 py-2.5 transition flex items-center gap-3 hover:bg-gray-50"
          :class="messageStore.activeConversationId === conv.id ? 'bg-sky-50' : ''"
        >
          <!-- avatar -->
          <div
            class="size-10 rounded-2xl grid place-items-center text-[13px] font-bold text-white shrink-0"
            :class="conv.type === 'group' ? 'bg-grape-500' : 'bg-sky-500'"
          >
            {{ avatarLabel(conv.label, conv.type) }}
          </div>

          <!-- meta -->
          <div class="min-w-0 flex-1">
            <div class="flex items-center gap-2">
              <p class="truncate font-semibold text-[13.5px] text-gray-900">{{ conv.label }}</p>
              <span class="ml-auto shrink-0 text-[11px] text-gray-400">{{
                formatWhen(conv.last_message_at)
              }}</span>
            </div>
            <p class="truncate text-[12.5px] text-gray-500">
              {{ conv.preview || '' }}
            </p>
          </div>

          <span
            v-if="conv.unread_count > 0"
            class="ml-1 inline-flex items-center justify-center min-w-5 h-5 px-1.5 text-[10.5px] font-bold bg-coral-500 text-white rounded-full shrink-0"
          >
            {{ conv.unread_count }}
          </span>
        </button>
      </li>
    </ul>

    <!-- moi -->
    <div class="px-3.5 py-3 border-t border-gray-100 flex items-center gap-2.5">
      <div class="size-8 rounded-[11px] bg-gray-800 text-white grid place-items-center text-xs font-bold">
        {{ meInitial }}
      </div>
      <span class="text-[13px] font-semibold text-gray-700">{{
        auth.user?.username || 'Moi'
      }}</span>
    </div>

    <!-- MODALE : Nouvelle discussion -->
    <transition name="fade">
      <div
        v-if="showNewDialog"
        class="fixed inset-0 z-50 flex items-center justify-center p-4"
        @click.self="showNewDialog = false"
      >
        <div class="absolute inset-0 bg-gray-900/40"></div>

        <transition
          enter-active-class="transition duration-200 ease-out"
          enter-from-class="opacity-0 translate-y-2 scale-[0.98]"
          enter-to-class="opacity-100 translate-y-0 scale-100"
          leave-active-class="transition duration-150 ease-in"
          leave-from-class="opacity-100 translate-y-0 scale-100"
          leave-to-class="opacity-0 translate-y-2 scale-[0.98]"
        >
          <div
            class="relative w-full max-w-md overflow-hidden bg-white border border-gray-100 rounded-[26px] shadow-[0_20px_60px_rgba(0,0,0,0.20)]"
          >
            <!-- header -->
            <div class="px-4 py-3.5 border-b border-gray-100 flex items-center justify-between">
              <h3 class="font-display font-bold text-gray-900">Nouvelle discussion</h3>
              <button
                class="size-8 grid place-items-center rounded-xl bg-gray-100 text-gray-600 hover:bg-gray-200"
                aria-label="Fermer"
                @click="showNewDialog = false"
              >
                <X class="w-4 h-4" />
              </button>
            </div>

            <!-- segmented control (onglets) -->
            <div class="px-3.5 pt-3.5">
              <div
                class="w-full bg-gray-50 border border-gray-200 rounded-2xl p-1 grid grid-cols-2 gap-1"
                role="tablist"
              >
                <button
                  role="tab"
                  :aria-selected="activeNewTab === 'users'"
                  class="rounded-xl py-2 text-sm font-semibold transition inline-flex items-center justify-center gap-2"
                  :class="
                    activeNewTab === 'users' ? 'bg-coral-500 text-white' : 'text-gray-600 hover:bg-white'
                  "
                  @click="activeNewTab = 'users'"
                >
                  <User class="w-4 h-4" /> Utilisateurs
                </button>
                <button
                  role="tab"
                  :aria-selected="activeNewTab === 'groups'"
                  class="rounded-xl py-2 text-sm font-semibold transition inline-flex items-center justify-center gap-2"
                  :class="
                    activeNewTab === 'groups' ? 'bg-coral-500 text-white' : 'text-gray-600 hover:bg-white'
                  "
                  @click="activeNewTab = 'groups'"
                >
                  <Users class="w-4 h-4" /> Groupes
                </button>
              </div>
            </div>

            <!-- contenu -->
            <div class="p-4 space-y-3">
              <!-- Users -->
              <div v-if="activeNewTab === 'users'">
                <div class="relative">
                  <span class="absolute inset-y-0 left-0 pl-3 flex items-center text-gray-400">
                    <Search class="w-4 h-4" />
                  </span>
                  <input
                    v-model="searchUser"
                    type="text"
                    placeholder="Rechercher un utilisateur…"
                    class="w-full rounded-2xl border-[1.5px] border-gray-200 bg-gray-50 pl-9 pr-3 py-2 text-sm focus:outline-none focus:ring-4 focus:ring-sky-50"
                  />
                </div>

                <ul class="max-h-64 overflow-y-auto space-y-1 sidebar-scroll mt-2">
                  <li
                    v-for="u in filteredUsers"
                    :key="u.id"
                    @click="startConversationWithUser(u)"
                    class="rounded-xl border border-gray-100 bg-gray-50 hover:bg-sky-50 active:scale-[0.998] transition px-3 py-2.5 cursor-pointer flex items-center gap-3"
                  >
                    <div class="size-8 rounded-xl bg-sky-500 text-white grid place-items-center text-[11px] font-bold shrink-0">
                      {{ (u.username || '?').slice(0, 1).toUpperCase() }}
                    </div>
                    <span class="text-sm text-gray-800">{{ u.username }}</span>
                  </li>
                  <li v-if="filteredUsers.length === 0" class="py-8 text-center text-sm text-gray-400">
                    Aucun utilisateur
                  </li>
                </ul>
              </div>

              <!-- Groups -->
              <div v-else>
                <div class="relative">
                  <span class="absolute inset-y-0 left-0 pl-3 flex items-center text-gray-400">
                    <Search class="w-4 h-4" />
                  </span>
                  <input
                    v-model="searchGroup"
                    type="text"
                    placeholder="Rechercher un groupe…"
                    class="w-full rounded-2xl border-[1.5px] border-gray-200 bg-gray-50 pl-9 pr-3 py-2 text-sm focus:outline-none focus:ring-4 focus:ring-sky-50"
                  />
                </div>

                <ul class="max-h-64 overflow-y-auto space-y-1 sidebar-scroll mt-2">
                  <li
                    v-for="g in filteredGroups"
                    :key="g.id"
                    @click="startConversationWithGroup(g)"
                    class="rounded-xl border border-gray-100 bg-gray-50 hover:bg-grape-50 active:scale-[0.998] transition px-3 py-2.5 cursor-pointer flex items-center gap-3"
                  >
                    <div class="size-8 rounded-xl bg-grape-500 text-white grid place-items-center text-[11px] font-bold shrink-0">
                      {{ avatarLabel(g.groupname, 'group') }}
                    </div>
                    <span class="text-sm text-gray-800">{{ g.groupname }}</span>
                  </li>
                  <li v-if="filteredGroups.length === 0" class="py-8 text-center text-sm text-gray-400">
                    Aucun groupe
                  </li>
                </ul>
              </div>
            </div>

            <!-- footer -->
            <div class="px-4 py-3 border-t border-gray-100 flex justify-end gap-2">
              <button
                class="px-3.5 py-1.5 rounded-xl border border-gray-200 text-gray-600 hover:bg-gray-50 text-sm font-medium"
                @click="showNewDialog = false"
              >
                Fermer
              </button>
            </div>
          </div>
        </transition>
      </div>
    </transition>
  </div>
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.15s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
.sidebar-scroll::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}
.sidebar-scroll::-webkit-scrollbar-thumb {
  background: rgba(0, 0, 0, 0.08);
  border-radius: 9999px;
}
.sidebar-scroll:hover::-webkit-scrollbar-thumb {
  background: rgba(0, 0, 0, 0.16);
}
</style>
