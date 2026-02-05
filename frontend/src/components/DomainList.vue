<template>
  <div class="bg-white rounded-lg shadow-md overflow-hidden">
    <!-- Loading skeleton -->
    <div v-if="loading" class="p-4 space-y-4">
      <div v-for="n in 5" :key="n" class="animate-pulse flex items-center space-x-4">
        <div class="h-4 bg-gray-200 rounded w-1/4"></div>
        <div class="h-6 bg-gray-200 rounded w-20"></div>
        <div class="h-6 bg-gray-200 rounded-full w-10"></div>
        <div class="h-4 bg-gray-200 rounded w-1/5"></div>
        <div class="h-8 bg-gray-200 rounded w-16"></div>
      </div>
    </div>

    <!-- Empty state -->
    <div v-else-if="!domains || domains.length === 0" class="p-8 text-center">
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
          d="M9 12h6m-3-3v6m-7 4h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
        />
      </svg>
      <p class="mt-2 text-sm text-gray-500">No domains found.</p>
    </div>

    <!-- Table -->
    <div v-else class="overflow-x-auto">
      <table class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50">
          <tr>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Domain
            </th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Type
            </th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Enabled
            </th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Comment
            </th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Actions
            </th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
          <tr v-for="item in domains" :key="item.id" class="hover:bg-gray-50 transition-colors">
            <!-- Domain -->
            <td class="px-6 py-4 whitespace-nowrap">
              <span class="text-sm font-mono text-gray-900">{{ item.domain }}</span>
              <p v-if="item.date_added" class="text-xs text-gray-400 mt-0.5">
                Added {{ formatDate(item.date_added) }}
              </p>
            </td>

            <!-- Type badge -->
            <td class="px-6 py-4 whitespace-nowrap">
              <span :class="['inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium', typeBadgeClass(item.type)]">
                {{ formatType(item.type) }}
              </span>
            </td>

            <!-- Enabled toggle -->
            <td class="px-6 py-4 whitespace-nowrap">
              <button
                @click="$emit('toggle', item.id, !item.enabled)"
                :class="[
                  'relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2',
                  item.enabled ? 'bg-blue-600' : 'bg-gray-200'
                ]"
                role="switch"
                :aria-checked="item.enabled"
              >
                <span
                  :class="[
                    'pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out',
                    item.enabled ? 'translate-x-5' : 'translate-x-0'
                  ]"
                />
              </button>
            </td>

            <!-- Comment -->
            <td class="px-6 py-4">
              <span class="text-sm text-gray-500 max-w-xs truncate block">
                {{ item.comment || '--' }}
              </span>
            </td>

            <!-- Actions -->
            <td class="px-6 py-4 whitespace-nowrap">
              <button
                @click="$emit('delete', item.id)"
                class="inline-flex items-center px-3 py-1.5 border border-red-300 text-sm font-medium rounded-md text-red-700 bg-white hover:bg-red-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 transition-colors"
              >
                <svg class="h-4 w-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
                Delete
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
defineProps({
  domains: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  }
})

defineEmits(['toggle', 'delete'])

function formatType(type) {
  const typeMap = {
    blacklist: 'Blacklist',
    whitelist: 'Whitelist',
    regex_black: 'Regex Black',
    regex_white: 'Regex White',
    wildcard: 'Wildcard'
  }
  return typeMap[type] || type
}

function typeBadgeClass(type) {
  const classMap = {
    blacklist: 'bg-red-100 text-red-800',
    whitelist: 'bg-green-100 text-green-800',
    regex_black: 'bg-orange-100 text-orange-800',
    regex_white: 'bg-teal-100 text-teal-800',
    wildcard: 'bg-purple-100 text-purple-800'
  }
  return classMap[type] || 'bg-gray-100 text-gray-800'
}

function formatDate(timestamp) {
  if (!timestamp) return ''
  const date = typeof timestamp === 'number' ? new Date(timestamp * 1000) : new Date(timestamp)
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}
</script>
