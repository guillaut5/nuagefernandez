<script setup lang="ts">
import { onMounted } from 'vue'
import { useMessages } from '@/store/useMessages'

const store = useMessages()

onMounted(() => {
  store.fetchSent()
})
</script>

<template>
  <div class="space-y-4">
    <div
      v-for="msg in store.sent"
      :key="msg.id"
      class="rounded-xl shadow p-3 bg-white"
    >
      <p class="font-semibold">
        À :
        <span v-if="msg.recipient?.username">{{ msg.recipient.username }}</span>
        <span v-else-if="msg.recipient_group?.groupname">{{ msg.recipient_group.groupname }} (groupe)</span>
        <span v-else>—</span>
      </p>
      <p class="text-sm text-gray-600 break-words">{{ msg.text }}</p>
      <p class="text-xs text-gray-400 mt-1">
        {{ new Date(msg.timestamp).toLocaleString() }}
      </p>
    </div>


  </div>
</template>

<style scoped></style>
