import { defineStore } from 'pinia'
import api from '@/api/http'

interface SimpleUser {
  id: number
  username: string
}
interface SimpleGroup {
  id: number
  name: string
}

export const useUserGroupStore = defineStore('user-group-store', {
  state: () => ({
    users: [] as SimpleUser[],
    groups: [] as SimpleGroup[],
    loaded: false,
  }),

  actions: {
    async fetch() {
      if (this.loaded) return
      const [{ data: users }, { data: groups }] = await Promise.all([
        api.get<SimpleUser[]>('/api/messages/users/'),
        api.get<SimpleGroup[]>('/api/messages/groups/'),
      ])
      this.users = users
      this.groups = groups
      this.loaded = true
    },
  },
})
