import { defineStore } from 'pinia'
import api from '@/api/http'
import type { GroupSummary, UserSummary } from '@/types/api'

export const useUserGroupStore = defineStore('user-group-store', {
  state: () => ({
    users: [] as UserSummary[],
    groups: [] as GroupSummary[],
    loaded: false,
  }),

  actions: {
    async fetch() {
      if (this.loaded) return
      const [{ data: users }, { data: groups }] = await Promise.all([
        api.get<UserSummary[]>('/messages/users/'),
        api.get<GroupSummary[]>('/messages/my-groups/'),
      ])
      this.users = users
      this.groups = groups
      this.loaded = true
    },
    getUserById(id: number): UserSummary | undefined {
      return this.users.find((u) => u.id === id)
    },

    getGroupById(id: number): GroupSummary | undefined {
      return this.groups.find((g) => g.id === id)
    },
  },
})
