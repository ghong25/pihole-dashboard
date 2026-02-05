<template>
  <router-link
    :to="`/devices/${device.mac}`"
    class="block bg-white rounded-lg shadow-md p-5 hover:shadow-lg transition-shadow border border-gray-100 group"
  >
    <div class="flex items-start justify-between">
      <!-- Device info -->
      <div class="flex items-start space-x-3 min-w-0">
        <!-- Icon -->
        <div class="flex-shrink-0 w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center text-blue-600">
          <span v-if="device.icon" class="text-lg">{{ device.icon }}</span>
          <svg v-else class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
          </svg>
        </div>

        <div class="min-w-0">
          <!-- Title: nickname or vendor+MAC fallback -->
          <h3 class="text-sm font-semibold text-gray-900 truncate group-hover:text-blue-600 transition-colors">
            {{ displayName }}
          </h3>

          <!-- IP Address -->
          <p class="text-sm text-gray-600 font-mono mt-0.5">
            {{ device.ip || 'Unknown IP' }}
          </p>

          <!-- Hostname -->
          <p v-if="device.hostname" class="text-xs text-gray-400 truncate mt-0.5">
            {{ device.hostname }}
          </p>
        </div>
      </div>

      <!-- Rename button -->
      <button
        @click.prevent="$emit('rename', device.mac)"
        class="flex-shrink-0 p-1.5 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded-md transition-colors opacity-0 group-hover:opacity-100"
        title="Rename device"
      >
        <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
        </svg>
      </button>
    </div>

    <!-- Stats row -->
    <div class="mt-4 flex items-center justify-between text-xs text-gray-500 border-t border-gray-100 pt-3">
      <div class="flex items-center space-x-1">
        <svg class="h-3.5 w-3.5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 20l4-16m2 16l4-16M6 9h14M4 15h14" />
        </svg>
        <span>{{ formatQueryCount(device.num_queries) }} queries</span>
      </div>

      <div class="flex items-center space-x-1">
        <svg class="h-3.5 w-3.5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <span>{{ relativeTime(device.last_query) }}</span>
      </div>
    </div>

    <!-- First seen -->
    <div v-if="device.first_seen" class="mt-1 text-xs text-gray-400">
      First seen {{ formatAbsoluteDate(device.first_seen) }}
    </div>
  </router-link>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  device: {
    type: Object,
    required: true
  }
})

defineEmits(['rename'])

const displayName = computed(() => {
  if (props.device.nickname) return props.device.nickname
  if (props.device.vendor) return `${props.device.vendor} (${props.device.mac})`
  return props.device.mac || 'Unknown Device'
})

function formatQueryCount(count) {
  if (count == null) return '0'
  if (count >= 1000000) return `${(count / 1000000).toFixed(1)}M`
  if (count >= 1000) return `${(count / 1000).toFixed(1)}k`
  return String(count)
}

function relativeTime(timestamp) {
  if (!timestamp) return 'Never'

  const now = Date.now()
  const then = typeof timestamp === 'number'
    ? (timestamp > 1e12 ? timestamp : timestamp * 1000)
    : new Date(timestamp).getTime()

  const diffMs = now - then
  if (diffMs < 0) return 'Just now'

  const seconds = Math.floor(diffMs / 1000)
  const minutes = Math.floor(seconds / 60)
  const hours = Math.floor(minutes / 60)
  const days = Math.floor(hours / 24)

  if (seconds < 60) return 'Just now'
  if (minutes < 60) return `${minutes}m ago`
  if (hours < 24) return `${hours}h ago`
  if (days < 30) return `${days}d ago`
  return formatAbsoluteDate(timestamp)
}

function formatAbsoluteDate(timestamp) {
  if (!timestamp) return ''
  const date = typeof timestamp === 'number'
    ? new Date(timestamp > 1e12 ? timestamp : timestamp * 1000)
    : new Date(timestamp)
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric'
  })
}
</script>
