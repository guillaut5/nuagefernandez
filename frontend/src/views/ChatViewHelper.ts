// ChartViewHelper.ts
import type { GroupSummary, Message, UserSummary, Conversation } from '@/types/api'

/**
 * Construit les conversations à partir d'une liste de messages
 * - évite les doublons (par id de message)
 * - n'ajoute pas les messages de groupe envoyés par l'utilisateur courant (doublon avec "sent")
 * - trie messages (ASC) et conversations (DESC par dernier message)
 */
export function buildConversations(
  inboxMessages: Message[], // Messages reçus (déjà "plats")
  sentMessages: Message[], // Messages envoyés
  currentUserId: number,
): Conversation[] {
  const map = new Map<string, Conversation>()

  // Fusionne les deux flux
  const all = [...inboxMessages, ...sentMessages]

  for (const msg of all) {
    let key = ''
    let label = ''
    let type: 'user' | 'group'
    let target: any

    if (msg.recipient_group) {
      // Groupe
      key = `group-${msg.recipient_group.id}`
      label = msg.recipient_group.groupname
      type = 'group'
      target = msg.recipient_group

      // Évite de dupliquer mes propres messages de groupe (déjà présents côté "sent")
      //   if (msg.sender.id === currentUserId) continue
    } else {
      // 1-to-1
      const other = msg.sender.id === currentUserId ? msg.recipient : msg.sender
      if (!other) continue
      key = `user-${other.id}`
      label = other.username
      type = 'user'
      target = other
    }

    // Crée la conversation si besoin
    if (!map.has(key)) {
      map.set(key, {
        id: key,
        label,
        type,
        target,
        messages: [],
        lastMessage: null,
        lastMessageFromMe: false,
      })
    }

    const conv = map.get(key)!
    // Pas de doublon
    if (!conv.messages.some((m) => m.id === msg.id)) {
      conv.messages.push(msg)
    }
  }

  // Post-traitement
  for (const conv of map.values()) {
    conv.messages.sort((a, b) => a.timestamp.localeCompare(b.timestamp))
    const last = conv.messages.at(-1) || null
    conv.lastMessage = last
    conv.lastMessageFromMe = last ? last.sender.id === currentUserId : false
  }

  // Trie conversations par dernier message (DESC)
  return Array.from(map.values()).sort((a, b) =>
    (b.lastMessage?.timestamp || '').localeCompare(a.lastMessage?.timestamp || ''),
  )
}

/** Conversation “brouillon” (sans message) à partir d’un id "user-<id>" ou "group-<id>" */
export function buildDraftConversationFromId(
  id: string,
  users: UserSummary[],
  groups: GroupSummary[],
): Conversation | null {
  if (id.startsWith('user-')) {
    const uid = Number(id.slice(5))
    const user = users.find((u) => u.id === uid)
    if (!user) return null
    return {
      id,
      label: user.username,
      type: 'user',
      target: user,
      messages: [],
      lastMessage: null,
      lastMessageFromMe: false,
      isDraft: true,
    }
  }
  if (id.startsWith('group-')) {
    const gid = Number(id.slice(6))
    const group = groups.find((g) => g.id === gid)
    if (!group) return null
    return {
      id,
      label: group.groupname,
      type: 'group',
      target: group,
      messages: [],
      lastMessage: null,
      lastMessageFromMe: false,
      isDraft: true,
    }
  }
  return null
}
