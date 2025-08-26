import { defineStore } from 'pinia'
import type {
  Message,
  MessageStatus,
  Paginated,
  ConversationDetail,
  ConversationSummary,
} from '@/types/api'
import api from '@/api/http' // <-- au lieu de axios
import { useAuth } from '@/store/useAuth'
import { useUserGroupStore } from '@/store/useUserGroupStore'

interface MessagesState {
  conversationsSummaries: ConversationSummary[] // sidebar
  threads: Record<string, ConversationDetail> // cache par convId
  inbox: MessageStatus[]
  sent: Message[]
  userFilter: number | null
  activeConversationId: string | null // pratique
  _pending: Set<string> // évite doubles clics
}

export const useMessages = defineStore('messages', {
  state: (): MessagesState => ({
    conversationsSummaries: [],
    threads: {},
    inbox: [],
    sent: [],
    userFilter: null,
    activeConversationId: null,
    _pending: new Set<string>(),
  }),

  actions: {
    resetThread(convId: string) {
      // supprime proprement la clé du cache (réactif en Vue 3)
      delete this.threads[convId]
    },
    resetStore() {
      this.$reset()
    },

    // ---------------------------
    // SUPPRIMER POUR TOUS
    // ---------------------------
    async deleteForAll(messageId: number, opts: { convId?: string } = {}) {
      const pendingKey = `delete_for_all:${messageId}`
      if (this._pending.has(pendingKey)) return
      this._pending.add(pendingKey)

      // Optimistic: on marque le message comme supprimé globalement
      const snapshots: Array<{ convId: string; index: number; before: Message }> = []
      const convIds = opts.convId ? [opts.convId] : Object.keys(this.threads)

      for (const cid of convIds) {
        const thr = this.threads[cid]
        if (!thr) continue
        const idx = thr.messages.findIndex((m) => m.id === messageId)
        if (idx === -1) continue
        const before = { ...thr.messages[idx] }
        snapshots.push({ convId: cid, index: idx, before })
        thr.messages[idx] = { ...thr.messages[idx], deleted_for_all: true } as Message
        // lastMessage reste cohérent (le message reste dans la timeline)
      }

      try {
        await api.post(`/api/messages/messages/${messageId}/delete_for_all/`)
      } catch (e) {
        // rollback si erreur
        for (const s of snapshots) {
          const thr = this.threads[s.convId]
          if (thr && thr.messages[s.index]) thr.messages[s.index] = s.before
        }
        this._pending.delete(pendingKey)
        throw e
      }

      this._pending.delete(pendingKey)
    },

    // ---------------------------
    // MASQUER POUR MOI
    // ---------------------------
    async hideMessage(messageId: number, opts: { convId?: string } = {}) {
      const pendingKey = `hide:${messageId}`
      if (this._pending.has(pendingKey)) return
      this._pending.add(pendingKey)

      // Optimistic: on enlève le message de MES threads (il disparaît pour moi)
      const removed: Array<{ convId: string; index: number; msg: Message }> = []
      const convIds = opts.convId ? [opts.convId] : Object.keys(this.threads)

      const recompute = (cid: string) => {
        const thr = this.threads[cid]
        if (!thr) return
        const last = thr.messages.at(-1) ?? null
        const me = useAuth().user?.id
        thr.lastMessage = last
        thr.lastMessageFromMe = !!(last && me && last.sender?.id === me)
      }

      for (const cid of convIds) {
        const thr = this.threads[cid]
        if (!thr) continue
        const idx = thr.messages.findIndex((m) => m.id === messageId)
        if (idx === -1) continue
        const msg = thr.messages[idx]
        removed.push({ convId: cid, index: idx, msg })
        thr.messages.splice(idx, 1)
        recompute(cid)
      }

      try {
        await api.post(`/api/messages/messages/${messageId}/hide/`)
      } catch (e) {
        // rollback si erreur
        for (const r of removed) {
          const thr = this.threads[r.convId]
          if (!thr) continue
          thr.messages.splice(r.index, 0, r.msg)
          recompute(r.convId)
        }
        this._pending.delete(pendingKey)
        throw e
      }

      this._pending.delete(pendingKey)
    },

    // 1) Sidebar
    async fetchConversationsSummary() {
      const { data } = await api.get<ConversationSummary[]>('/api/messages/conversations-summary/')
      // tri desc
      this.conversationsSummaries = data.sort((a, b) =>
        (b.last_message_at || '').localeCompare(a.last_message_at || ''),
      )
    },
    getConversationSummary(convId: string) {
      return this.conversationsSummaries.find((s) => s.id === convId) ?? null
    },
    async openConversation(convId: string) {
      this.activeConversationId = convId

      // 1) refresh des summaries (badges à jour)
      await this.fetchConversationsSummary()

      // 2) si la conv a des unread -> reset cache + refetch du thread
      const summary = this.conversationsSummaries.find((s) => s.id === convId)
      if (!summary || (summary.unread_count ?? 0) > 0) {
        this.resetThread(convId)
      }

      // si summay et null => c'est forcement la demande d'un converstation qui n'existe pas dans la base,
      // c'est donc un demande de converstation,
      // créer un squelette immédiatement pour l’UI
      if (!summary) {
        this.ensureEmptyThread(convId)
      } else {
        // c'est un thread reel... donc on recharge, si besoin
        // 3) (re)charger le thread (soit depuis zéro si reset, soit pour être sûr d'être frais)
        await this.fetchThread(convId)
      }
    },

    async ensureEmptyThread(convId: string) {
      const ug = useUserGroupStore()

      // Charger users/groups si pas encore fait
      if (!ug.loaded) {
        try {
          await ug.fetch()
        } catch (_) {
          /* noop */
        }
      }

      // Déterminer type + id numérique
      const isUser = convId.startsWith('user-')
      const idStr = convId.slice(isUser ? 5 : 6) // "user-"=5, "group-"=6
      const id = Number(idStr)

      // Trouver un label par défaut (si pas fourni par summary)
      let fallbackLabel = convId
      if (isUser) {
        const u = ug.getUserById(id)
        fallbackLabel = u?.username ?? `Utilisateur ${id}`
      } else {
        const g = ug.getGroupById(id)
        fallbackLabel = g?.groupname ?? `Groupe ${id}`
      }

      const label = fallbackLabel
      const type: 'user' | 'group' = isUser ? 'user' : 'group'

      this.threads[convId] = {
        id: convId,
        type,
        label,
        messages: [],
        lastMessage: null,
        lastMessageFromMe: false,
      }
    },

    // 2) Détail d’un thread (user ou group)
    // change la signature
    async fetchThread(convId: string, opts: { force?: boolean } = {}) {
      if (!opts.force && this.threads[convId]) return // garde le cache sauf si force

      if (convId.startsWith('user-')) {
        const uid = Number(convId.slice(5))
        const { data } = await api.get<Message[]>('/api/messages/thread/', {
          params: { user: uid, mark_read: true },
        })
        this._setThreadFromMessages(convId, 'user', data)
      } else if (convId.startsWith('group-')) {
        const gid = Number(convId.slice(6))
        const { data } = await api.get<Message[]>('/api/messages/thread/', {
          params: { group: gid, mark_read: true },
        })
        this._setThreadFromMessages(convId, 'group', data)
      }
    },

    _setThreadFromMessages(convId: string, type: 'user' | 'group', msgs: Message[]) {
      msgs.sort((a, b) => a.timestamp.localeCompare(b.timestamp))
      const last = msgs.at(-1) ?? null
      const label = this.conversationsSummaries.find((s) => s.id === convId)?.label || convId
      this.threads[convId] = {
        id: convId,
        type,
        label,
        messages: msgs,
        lastMessage: last,
        lastMessageFromMe: last ? last.sender.id === useAuth().user?.id : false,
      }
    },

    // Envoi d’un message en utilisant activeConversationId
    async sendMessageToActive(
      text: string,
      image?: File | null,
      latitude?: string | null,
      longitude?: string | null,
    ) {
      if (!this.activeConversationId) return
      const fd = new FormData()
      if (text.trim()) fd.append('text', text.trim())
      if (image) fd.append('image', image)
      if (latitude) fd.append('latitude', latitude)
      if (longitude) fd.append('longitude', longitude)

      const convId = this.activeConversationId
      if (convId.startsWith('user-')) {
        fd.append('recipient', convId.slice(5))
      } else {
        fd.append('recipient_group', convId.slice(6))
      }

      await api.post('/api/messages/send/', fd)
      // Refresh juste le thread et la liste
      delete this.threads[convId] // simple: on invalide le cache
      await Promise.all([this.fetchThread(convId), this.fetchConversationsSummary()])
    },

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

    async fetchAllMessages() {
      try {
        await Promise.all([this.fetchInbox(), this.fetchSent()])
      } catch (error) {
        console.error('Erreur lors du chargement des messages :', error)
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
