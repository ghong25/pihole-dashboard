<template>
  <div class="bg-white rounded-lg shadow-md overflow-hidden">
    <!-- Loading skeleton -->
    <div v-if="loading" class="p-4 space-y-3">
      <div v-for="n in 8" :key="n" class="animate-pulse flex items-center space-x-4">
        <div class="h-4 bg-gray-200 rounded w-24"></div>
        <div class="h-4 bg-gray-200 rounded w-40"></div>
        <div class="h-4 bg-gray-200 rounded w-28"></div>
        <div class="h-5 bg-gray-200 rounded-full w-16"></div>
        <div class="h-4 bg-gray-200 rounded w-12"></div>
      </div>
    </div>

    <!-- Empty state -->
    <div v-else-if="!rows || rows.length === 0" class="p-8 text-center">
      <svg
        class="mx-auto h-12 w-12 text-gray-300"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M8 16l2.879-2.879m0 0a3 3 0 104.243-4.242 3 3 0 00-4.243 4.242zM21 12a9 9 0 11-18 0 9 9 0 0118 0z"
        />
      </svg>
      <p class="mt-2 text-sm text-gray-500">No queries found.</p>
    </div>

    <!-- Table -->
    <div v-else class="overflow-x-auto">
      <table class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50">
          <tr>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Time
            </th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Domain
            </th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Client
            </th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Status
            </th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Type
            </th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
          <tr v-for="query in rows" :key="query.id" class="hover:bg-gray-50 transition-colors">
            <!-- Time -->
            <td class="px-6 py-3 whitespace-nowrap">
              <span class="text-sm text-gray-600 font-mono">{{ formatTime(query.timestamp) }}</span>
            </td>

            <!-- Domain -->
            <td class="px-6 py-3">
              <button
                class="text-sm text-gray-900 font-mono truncate block max-w-xs hover:text-blue-600 hover:underline text-left"
                :title="'Click to block: ' + query.domain"
                @click="emit('block-domain', query.domain)"
              >
                {{ query.domain }}
              </button>
            </td>

            <!-- Client -->
            <td class="px-6 py-3 whitespace-nowrap">
              <span class="text-sm text-gray-600">{{ query.client }}</span>
            </td>

            <!-- Status badge -->
            <td class="px-6 py-3 whitespace-nowrap">
              <span
                :class="[
                  'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium',
                  statusBadgeClass(query.status)
                ]"
              >
                <span
                  :class="[
                    'w-1.5 h-1.5 rounded-full mr-1.5',
                    statusDotClass(query.status)
                  ]"
                ></span>
                {{ statusLabel(query.status) }}
              </span>
            </td>

            <!-- Type -->
            <td class="px-6 py-3 whitespace-nowrap">
              <span class="text-sm text-gray-500">{{ query.type || '--' }}</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const BLOCKED_STATUSES = [1, 4, 5, 6, 7, 8, 9, 10, 11]
const CACHED_STATUSES = [3]

const props = defineProps({
  queries: {
    type: Array,
    default: () => []
  },
  logs: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['block-domain'])

const rows = computed(() => {
  return props.queries.length > 0 ? props.queries : props.logs
})

function statusLabel(status) {
  if (BLOCKED_STATUSES.includes(status)) return 'Blocked'
  if (CACHED_STATUSES.includes(status)) return 'Cached'
  return 'Allowed'
}

function statusBadgeClass(status) {
  if (BLOCKED_STATUSES.includes(status)) return 'bg-red-100 text-red-800'
  if (CACHED_STATUSES.includes(status)) return 'bg-yellow-100 text-yellow-800'
  return 'bg-green-100 text-green-800'
}

function statusDotClass(status) {
  if (BLOCKED_STATUSES.includes(status)) return 'bg-red-500'
  if (CACHED_STATUSES.includes(status)) return 'bg-yellow-500'
  return 'bg-green-500'
}

function formatTime(timestamp) {
  if (!timestamp) return '--'
  const date = typeof timestamp === 'number'
    ? new Date(timestamp > 1e12 ? timestamp : timestamp * 1000)
    : new Date(timestamp)
  return date.toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false
  })
}
</script>
