<script setup lang="ts">
import type { MessageStatus } from '@/types/api'
import { Eye, EyeOff } from 'lucide-vue-next'

defineProps<{ status: MessageStatus }>()
defineEmits(['click']) // 👈 autorise l'écoute de @click au niveau parent

</script>

<template>

  Mon message
  <div
    class="rounded-xl shadow p-3 bg-white flex justify-between items-center cursor-pointer"
    @click="$emit('click')" >
    <div>
      <p class="font-semibold">{{ status.message.sender_username }}</p>
      <p class="text-sm text-gray-600 truncate">{{ status.message.text }}</p>
    </div>
    <EyeOff v-if="!status.is_read" class="w-5 h-5 text-red-500" />
    <Eye v-else class="w-5 h-5 text-gray-400" />
  </div>
</template>
