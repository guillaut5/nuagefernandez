import { defineStore } from 'pinia'
import type { Message, MessageStatus, Paginated } from '@/types/api'
import api from '@/api/http' // <-- au lieu de axios

interface MessagesState {
  inbox: MessageStatus[]
  sent: Message[]
  userFilter: number | null
}

export const useMessages = defineStore('messages', {
  state: (): MessagesState => ({
    inbox: [],
    sent: [],

    userFilter: null,
  }),

  actions: {
    async fetchInbox() {
      try {
        const response = await api.get<Paginated<MessageStatus>>('/api/messages/messages/', {
          params: { user: this.userFilter },
        })

        this.inbox = response.data.results
      } catch (error) {
        console.error('Erreur lors du chargement de la boîte de réception :', error)
      }
    },

    async fetchSent() {
      try {
        const response = await api.get<Paginated<Message>>('/api/messages/sent/')
        this.sent = response.data.results
      } catch (error) {
        console.error('Erreur lors du chargement des messages envoyés :', error)
      }
    },
    async markAsRead(statusId: number) {
      try {
        await api.patch<void>(`/api/messages/message-status/${statusId}/`, { is_read: true })

        const found = this.inbox.find((s) => s.id === statusId)
        if (found) {
          found.is_read = true
          found.read_at = new Date().toISOString()
        }
      } catch (error) {
        console.error(`Erreur lors de la mise à jour du statut ${statusId} :`, error)
      }
    },

    async sendMessage(form: FormData) {
      try {
        await api.post<void>('/api/messages/send/', form)
        // Optionnel : tu peux déclencher un rechargement de la boîte "sent"
        // await this.fetchSent()
      } catch (error) {
        console.error('Erreur lors de l’envoi du message :', error)
      }
    },
  },
})
