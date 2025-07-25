<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useMessages } from '@/store/useMessages'
import MessageCard from '@/components/MessageCard.vue'
import MessageDetailModal from '@/components/MessageDetailModal.vue'
import UserFilterSelect from '@/components/UserFilterSelect.vue'

const store = useMessages()
const showModal = ref(false)
const selected = ref<number | null>(null)

onMounted(() => store.fetchInbox())

function openModal(id: number) {
  selected.value = id
  showModal.value = true
}
</script>

<template>
  <div class="p-4 space-y-4">
    <UserFilterSelect
      v-model="store.userFilter"
      @change="store.fetchInbox()"
    />
    <MessageCard
      v-for="status in store.inbox"
      :key="status.id"
      :status="status"
      @click="openModal(status.id)"
    />


    <MessageDetailModal
      v-if="showModal"
      :status-id="selected!"
      @close="showModal = false"
      @mark-read="store.markAsRead(selected!)"
    />
  </div>
</template>
