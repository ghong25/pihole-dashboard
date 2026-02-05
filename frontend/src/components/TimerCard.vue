<template>
  <div class="bg-white rounded-lg shadow-md p-5 border border-gray-100">
    <!-- Header -->
    <div class="flex items-start justify-between">
      <div class="min-w-0 flex-1">
        <h3 class="text-sm font-semibold text-gray-900 truncate">
          {{ block.domain }}
        </h3>
        <p class="text-xs text-gray-400 mt-0.5">
          Created {{ formatTimestamp(block.created_at) }}
        </p>
      </div>

      <!-- Cancel button -->
      <button
        @click="$emit('cancel', block.id)"
        class="flex-shrink-0 ml-3 inline-flex items-center px-2.5 py-1 border border-red-300 text-xs font-medium rounded-md text-red-700 bg-white hover:bg-red-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 transition-colors"
      >
        <svg class="h-3.5 w-3.5 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
        Cancel
      </button>
    </div>

    <!-- Countdown timer -->
    <div class="mt-4">
      <div class="flex items-baseline justify-between mb-1.5">
        <span class="text-2xl font-bold font-mono" :class="timerColorClass">
          {{ formattedTime }}
        </span>
        <span class="text-xs text-gray-400">
          Expires {{ formatTimestamp(block.expires_at) }}
        </span>
      </div>

      <!-- Progress bar -->
      <div class="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
        <div
          class="h-2 rounded-full transition-all duration-1000 ease-linear"
          :class="progressBarColorClass"
          :style="{ width: progressPercent + '%' }"
        ></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'

const props = defineProps({
  block: {
    type: Object,
    required: true
  }
})

defineEmits(['cancel'])

const remaining = ref(props.block.remaining_seconds ?? 0)
let intervalId = null

onMounted(() => {
  intervalId = setInterval(() => {
    if (remaining.value > 0) {
      remaining.value--
    } else {
      clearInterval(intervalId)
    }
  }, 1000)
})

onUnmounted(() => {
  if (intervalId) {
    clearInterval(intervalId)
  }
})

const totalDuration = computed(() => {
  if (!props.block.created_at || !props.block.expires_at) return props.block.remaining_seconds || 1

  const createdMs = typeof props.block.created_at === 'number'
    ? (props.block.created_at > 1e12 ? props.block.created_at : props.block.created_at * 1000)
    : new Date(props.block.created_at).getTime()

  const expiresMs = typeof props.block.expires_at === 'number'
    ? (props.block.expires_at > 1e12 ? props.block.expires_at : props.block.expires_at * 1000)
    : new Date(props.block.expires_at).getTime()

  return Math.max(Math.floor((expiresMs - createdMs) / 1000), 1)
})

const progressPercent = computed(() => {
  if (totalDuration.value <= 0) return 0
  return Math.max(0, Math.min(100, (remaining.value / totalDuration.value) * 100))
})

const formattedTime = computed(() => {
  const total = Math.max(0, remaining.value)
  const hours = Math.floor(total / 3600)
  const minutes = Math.floor((total % 3600) / 60)
  const seconds = total % 60

  if (hours > 0) {
    return `${pad(hours)}:${pad(minutes)}:${pad(seconds)}`
  }
  return `${pad(minutes)}:${pad(seconds)}`
})

const timerColorClass = computed(() => {
  if (remaining.value <= 0) return 'text-gray-400'
  if (remaining.value <= 60) return 'text-red-600'
  if (remaining.value <= 300) return 'text-yellow-600'
  return 'text-blue-600'
})

const progressBarColorClass = computed(() => {
  if (remaining.value <= 0) return 'bg-gray-300'
  if (progressPercent.value <= 10) return 'bg-red-500'
  if (progressPercent.value <= 30) return 'bg-yellow-500'
  return 'bg-blue-500'
})

function pad(num) {
  return String(num).padStart(2, '0')
}

function formatTimestamp(timestamp) {
  if (!timestamp) return ''
  const date = typeof timestamp === 'number'
    ? new Date(timestamp > 1e12 ? timestamp : timestamp * 1000)
    : new Date(timestamp)
  return date.toLocaleString('en-US', {
    month: 'short',
    day: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
    hour12: true
  })
}
</script>
