<script setup lang="ts">
import { computed } from 'vue'

type Props = {
  title: string
  subtitle: string
  artworkUrl?: string | null
  durationText?: string
  active?: boolean
}

const props = defineProps<Props>()
const emit = defineEmits<{
  (e: 'click'): void
}>()

const rowClass = computed(() => [
  'song-row flex items-center gap-3 py-2.5 px-2 rounded-lg transition-colors cursor-pointer select-none',
  props.active ? 'bg-stone-800/80' : 'hover:bg-stone-800/60',
])
</script>

<template>
  <div :class="rowClass" @click="emit('click')">
    <div class="shrink-0 w-10 h-10 rounded overflow-hidden bg-stone-700">
      <img
        v-if="artworkUrl"
        :src="artworkUrl"
        :alt="title"
        class="w-full h-full object-cover"
      />
      <div v-else class="w-full h-full flex items-center justify-center text-stone-500 text-lg">♪</div>
    </div>

    <div class="min-w-0 flex-1 flex flex-col justify-center">
      <div class="font-semibold text-stone-100 truncate">{{ title }}</div>
      <div class="text-sm text-stone-400 truncate">{{ subtitle }}</div>
    </div>

    <span v-if="durationText" class="shrink-0 text-sm text-stone-500 tabular-nums">
      {{ durationText }}
    </span>

    <div class="shrink-0" @click.stop>
      <slot name="actions" />
    </div>
  </div>
</template>

<style scoped>
</style>
