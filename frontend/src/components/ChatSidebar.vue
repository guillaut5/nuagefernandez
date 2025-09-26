<!-- ChatSidebar.vue - style macOS -->
<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import { useUserGroupStore } from '@/store/useUserGroupStore'
import { useAuth } from '@/store/useAuth'
import { useMessages } from '@/store/useMessages'
import { formatWhen } from '@/helpers/datehelper'
import { Plus, Search, X, User, Users } from 'lucide-vue-next'

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
  <div
    class="w-full h-full flex flex-col bg-white/60 backdrop-blur-xl shadow-[0_10px_40px_rgba(0,0,0,0.06)]"
  >
    <!-- Header -->
    <div class="px-3 pt-3">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-2">
          <div
            class="size-8 rounded-2xl bg-black text-white grid place-items-center shadow-inner select-none"
            :title="auth.user?.username || 'Moi'"
          >
            {{ meInitial }}
          </div>
          <span class="font-medium">Messages</span>
        </div>

        <button
          v-if="(users && users.length) || (groups && groups.length)"
          class="size-8 grid place-items-center rounded-xl bg-black text-white hover:bg-black/90 active:scale-[0.98] transition"
          title="Nouvelle discussion"
          @click="openNewDialog"
        >
          <Plus class="w-4 h-4" />
        </button>
      </div>

      <!-- Search -->
      <div class="mt-3 relative">
        <span class="absolute inset-y-0 left-0 pl-3 flex items-center text-gray-400">
          <Search class="w-4 h-4" />
        </span>
        <input
          v-model="search"
          type="search"
          placeholder="Rechercher"
          class="w-full rounded-2xl border border-gray-200 bg-white/80 pl-9 pr-3 py-2 text-sm shadow-inner focus:outline-none focus:ring-4 focus:ring-black/5"
        />
      </div>
    </div>

    <!-- List -->
    <ul class="mt-3 px-2 pb-2 overflow-y-auto sidebar-scroll flex-1">
      <li v-for="conv in filteredConversations" :key="conv.id" class="mb-1.5">
        <button
          @click="startConversation(conv.id)"
          class="w-full text-left rounded-2xl px-3 py-2.5 transition group flex items-center gap-3 hover:bg-white/70"
          :class="
            messageStore.activeConversationId === conv.id ? 'bg-red-100 ring-1 ring-red-400' : ''
          "
        >
          <!-- avatar initial -->
          <div
            class="size-9 rounded-2xl bg-gray-200 grid place-items-center text-xs font-semibold text-gray-700"
          >
            {{ (conv.label || '?').slice(0, 1).toUpperCase() }}
          </div>

          <!-- meta -->
          <div class="min-w-0 flex-1">
            <div class="flex items-center gap-2">
              <p class="truncate font-medium text-[13.5px]">{{ conv.label }}</p>
              <span class="ml-auto shrink-0 text-[11px] text-gray-500">{{
                formatWhen(conv.last_message_at)
              }}</span>
            </div>
            <p class="truncate text-[12.5px] text-gray-500">
              {{ conv.preview || '' }}
            </p>
          </div>

          <span
            v-if="conv.unread_count > 0"
            class="ml-2 inline-flex items-center justify-center min-w-5 h-5 px-1 text-[10px] font-bold bg-black text-white rounded-full"
          >
            {{ conv.unread_count }}
          </span>
        </button>
      </li>
    </ul>

    <!-- MODALE : Nouvelle discussion (remplace ton bloc actuel) -->
    <transition name="fade">
      <div
        v-if="showNewDialog"
        class="fixed inset-0 z-50 flex items-center justify-center p-4"
        @click.self="showNewDialog = false"
      >
        <!-- voile -->
        <div class="absolute inset-0 bg-black/40"></div>

        <!-- panneau -->
        <transition
          enter-active-class="transition duration-200 ease-out"
          enter-from-class="opacity-0 translate-y-2 scale-[0.98]"
          enter-to-class="opacity-100 translate-y-0 scale-100"
          leave-active-class="transition duration-150 ease-in"
          leave-from-class="opacity-100 translate-y-0 scale-100"
          leave-to-class="opacity-0 translate-y-2 scale-[0.98]"
        >
          <div
            class="relative w-full max-w-md overflow-hidden backdrop-blur-2xl bg-white/80 border border-white/60 rounded-2xl shadow-[0_20px_60px_rgba(0,0,0,0.20)]"
          >
            <!-- header -->
            <div class="px-4 py-3 border-b flex items-center justify-between">
              <h3 class="font-semibold tracking-tight">Nouvelle discussion</h3>
              <button
                class="size-8 grid place-items-center rounded-xl bg-black text-white hover:bg-black/90"
                aria-label="Fermer"
                @click="showNewDialog = false"
              >
                <X class="w-4 h-4" />
              </button>
            </div>

            <!-- segmented control (onglets) -->
            <div class="px-3 pt-3">
              <div
                class="w-full bg-white/70 border border-gray-200 rounded-2xl p-1 grid grid-cols-2 gap-1"
                role="tablist"
              >
                <button
                  role="tab"
                  :aria-selected="activeNewTab === 'users'"
                  class="rounded-xl py-2 text-sm font-medium transition inline-flex items-center justify-center gap-2"
                  :class="
                    activeNewTab === 'users'
                      ? 'bg-black text-white'
                      : 'text-gray-700 hover:bg-gray-50'
                  "
                  @click="activeNewTab = 'users'"
                >
                  <User class="w-4 h-4" /> Utilisateurs
                </button>
                <button
                  role="tab"
                  :aria-selected="activeNewTab === 'groups'"
                  class="rounded-xl py-2 text-sm font-medium transition inline-flex items-center justify-center gap-2"
                  :class="
                    activeNewTab === 'groups'
                      ? 'bg-black text-white'
                      : 'text-gray-700 hover:bg-gray-50'
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
                <!-- search -->
                <div class="relative">
                  <span class="absolute inset-y-0 left-0 pl-3 flex items-center text-gray-400">
                    <Search class="w-4 h-4" />
                  </span>
                  <input
                    v-model="searchUser"
                    type="text"
                    placeholder="Rechercher un utilisateur…"
                    class="w-full rounded-2xl border border-gray-200 bg-white/80 pl-9 pr-3 py-2 text-sm shadow-inner focus:outline-none focus:ring-4 focus:ring-black/5"
                  />
                </div>

                <!-- liste -->
                <ul class="max-h-64 overflow-y-auto space-y-1 sidebar-scroll mt-2">
                  <li
                    v-for="u in filteredUsers"
                    :key="u.id"
                    @click="startConversationWithUser(u)"
                    class="rounded-xl border border-gray-200 bg-white/70 hover:bg-white active:scale-[0.998] transition px-3 py-2.5 cursor-pointer flex items-center justify-between"
                  >
                    <span class="text-sm">{{ u.username }}</span>
                    <span class="text-[11px] px-2 py-0.5 rounded-full bg-black text-white">
                      user-{{ u.id }}
                    </span>
                  </li>
                  <li
                    v-if="filteredUsers.length === 0"
                    class="py-8 text-center text-sm text-gray-500"
                  >
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
                    class="w-full rounded-2xl border border-gray-200 bg-white/80 pl-9 pr-3 py-2 text-sm shadow-inner focus:outline-none focus:ring-4 focus:ring-black/5"
                  />
                </div>

                <ul class="max-h-64 overflow-y-auto space-y-1 sidebar-scroll mt-2">
                  <li
                    v-for="g in filteredGroups"
                    :key="g.id"
                    @click="startConversationWithGroup(g)"
                    class="rounded-xl border border-gray-200 bg-white/70 hover:bg-white active:scale-[0.998] transition px-3 py-2.5 cursor-pointer flex items-center justify-between"
                  >
                    <span class="text-sm">{{ g.groupname }}</span>
                    <span class="text-[11px] px-2 py-0.5 rounded-full bg-black text-white">
                      group-{{ g.id }}
                    </span>
                  </li>
                  <li
                    v-if="filteredGroups.length === 0"
                    class="py-8 text-center text-sm text-gray-500"
                  >
                    Aucun groupe
                  </li>
                </ul>
              </div>
            </div>

            <!-- footer -->
            <div class="px-4 py-3 border-t flex justify-end gap-2">
              <button
                class="px-3 py-1.5 rounded-xl border hover:bg-gray-50"
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
/* pour la fenertre modale addsicurssion */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.15s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
/* Scrollbar fine façon macOS */

/* scrollbar douce */
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
