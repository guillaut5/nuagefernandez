export interface UserSummary {
  id: number
  username: string
}

export interface GroupSummary {
  id: number
  groupname: string
}

export type Conversation = {
  id: string
  label: string
  type: 'user' | 'group'
  target: UserSummary | GroupSummary
  messages: Message[]
  lastMessage: Message | null
  lastMessageFromMe: boolean
  isDraft?: boolean
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
