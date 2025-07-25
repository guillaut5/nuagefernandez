<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import { useUserGroupStore } from '@/store/useUserGroupStore'

/*
 * Usage :
 * <UserFilterSelect v-model="store.userFilter" />
 */
interface Props {
  modelValue: number | null
}
const props = defineProps<Props>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: number | null): void
  (e: 'change', value: number | null): void
}>()

// ▶️ Pinia store centralisé (users & groups)
const userandgroup = useUserGroupStore()
const { users, loaded } = storeToRefs(userandgroup)

onMounted(() => {
  if (!loaded.value) userandgroup.fetch()
})

// v-model bridge
const selected = computed<number | ''>({
  get: () => (props.modelValue === null ? '' : props.modelValue),
  set: (val) => {
    const value = val === '' ? null : Number(val)
    emit('update:modelValue', value)
    emit('change', value)
  },
})
</script>

<template>
  <div>
    <label class="block text-sm font-medium mb-1">Filtrer par utilisateur</label>
    <select v-model="selected" class="form-select w-full">
      <option :value="''">Tous</option>
      <option v-for="u in users" :key="u.id" :value="u.id">{{ u.username }}</option>
    </select>
  </div>
</template>

<style scoped></style>
