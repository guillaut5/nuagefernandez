<script setup lang="ts">
defineProps<{
  messages: any[]
  currentUserId: number
}>()
</script>


<template>
  <div class="flex-1 p-4 flex flex-col space-y-2 overflow-y-auto h-full">
    <div v-for="msg in messages" :key="msg.id" :class="{
      'text-right': msg.sender.id === currentUserId,
      'text-left': msg.sender.id !== currentUserId
    }">
      <div
        :class="[
          'inline-block px-3 py-2 rounded-xl',
          msg.sender.id === currentUserId ? 'bg-blue-100' : 'bg-gray-100'
        ]"
      >
        {{ msg.text }}
      </div>
    </div>
  </div>
</template>
