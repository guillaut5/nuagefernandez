export interface UserSummary {
  id: number
  username: string
}

export interface GroupSummary {
  id: number
  groupname: string
}

export interface ConversationSummary {
  id: string // "user-12" | "group-5"
  label: string
  type: 'user' | 'group'
  last_message_at: string // ISO
  unread_count: number
  isDraft?: boolean
}

export interface ConversationDetail {
  id: string
  type: 'user' | 'group'
  label: string
  messages: Message[] // ← tes messages habituels
  lastMessage: Message | null
  lastMessageFromMe: boolean
}

export interface Message {
  id: number
  text: string
  image: string | null
  timestamp: string
  latitude: number | null
  longitude: number | null
  sender: UserSummary
  recipient: UserSummary | null
  recipient_group: GroupSummary | null
}

export interface MessageStatus {
  id: number
  message: Message
  is_read: boolean
  is_deleted: boolean
  read_at: string | null
}

export interface Paginated<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}

export interface TokenPair {
  access: string
  refresh: string
}
