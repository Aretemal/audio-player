<script setup lang="ts">
type Props = {
  title: string
  subtitle?: string
  artworkUrl?: string | null
  clickable?: boolean
}

defineProps<Props>()
const emit = defineEmits<{
  (e: 'click'): void
}>()
</script>

<template>
  <div class="album-card w-40">
    <div
      :class="[
        'relative w-40 h-40 rounded-xl overflow-hidden bg-stone-700/60 border border-stone-600',
        clickable ? 'cursor-pointer hover:border-stone-500' : ''
      ]"
      @click="clickable && emit('click')"
    >
      <img
        v-if="artworkUrl"
        :src="artworkUrl"
        :alt="title"
        class="w-full h-full object-cover"
        loading="lazy"
      />
      <div v-else class="w-full h-full flex items-center justify-center text-stone-500 text-2xl">♪</div>

      <div class="absolute top-2 right-2">
        <slot name="badge" />
      </div>
    </div>

    <div class="mt-2 min-w-0">
      <div class="text-sm font-semibold text-stone-100 truncate">{{ title }}</div>
      <div v-if="subtitle" class="text-xs text-stone-400 truncate">{{ subtitle }}</div>
    </div>
  </div>
</template>

<style scoped>
</style>
