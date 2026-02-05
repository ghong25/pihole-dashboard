<template>
  <div class="space-y-6">
    <!-- Header -->
    <h1 class="text-2xl font-bold text-gray-900">Query Logs</h1>

    <!-- Error state -->
    <div v-if="error" class="bg-red-50 border border-red-200 rounded-lg p-4">
      <div class="flex items-center justify-between">
        <div class="flex items-center">
          <svg class="h-5 w-5 text-red-400 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <p class="text-sm text-red-700">{{ error }}</p>
        </div>
        <button @click="error = null" class="text-red-400 hover:text-red-600">
          <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
    </div>

    <!-- Success message -->
    <div v-if="successMessage" class="bg-green-50 border border-green-200 rounded-lg p-4">
      <div class="flex items-center justify-between">
        <div class="flex items-center">
          <svg class="h-5 w-5 text-green-400 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
          </svg>
          <p class="text-sm text-green-700">{{ successMessage }}</p>
        </div>
        <button @click="successMessage = ''" class="text-green-400 hover:text-green-600">
          <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
    </div>

    <!-- Search bar -->
    <div class="bg-white rounded-lg shadow-md p-4">
      <div class="flex flex-col sm:flex-row gap-3">
        <div class="relative flex-1">
          <svg class="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Search domains in logs..."
            class="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            @keyup.enter="handleSearch"
          />
        </div>
        <button
          @click="handleSearch"
          class="inline-flex items-center px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-colors"
        >
          Search
        </button>
      </div>
    </div>

    <!-- Filter row -->
    <div class="bg-white rounded-lg shadow-md p-4">
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
        <!-- Status filter -->
        <div>
          <label class="block text-xs font-medium text-gray-500 mb-1">Status</label>
          <select
            v-model="filters.status"
            @change="resetAndFetch"
            class="w-full px-3 py-2 border border-gray-300 rounded-md text-sm bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="">All</option>
            <option value="blocked">Blocked</option>
            <option value="allowed">Allowed</option>
            <option value="cached">Cached</option>
          </select>
        </div>

        <!-- Client filter -->
        <div>
          <label class="block text-xs font-medium text-gray-500 mb-1">Client</label>
          <input
            v-model="filters.client"
            type="text"
            placeholder="IP or hostname"
            class="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            @change="resetAndFetch"
          />
        </div>

        <!-- Date from -->
        <div>
          <label class="block text-xs font-medium text-gray-500 mb-1">From</label>
          <input
            v-model="filters.from"
            type="datetime-local"
            class="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            @change="resetAndFetch"
          />
        </div>

        <!-- Date to -->
        <div>
          <label class="block text-xs font-medium text-gray-500 mb-1">To</label>
          <input
            v-model="filters.to"
            type="datetime-local"
            class="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            @change="resetAndFetch"
          />
        </div>
      </div>

      <!-- Clear filters -->
      <div class="mt-3 flex justify-end">
        <button
          @click="clearFilters"
          class="text-xs text-gray-500 hover:text-gray-700 transition-colors"
        >
          Clear all filters
        </button>
      </div>
    </div>

    <!-- Loading state -->
    <div v-if="loading" class="bg-white rounded-lg shadow-md p-8 text-center">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
      <p class="text-sm text-gray-500 mt-3">Loading logs...</p>
    </div>

    <!-- Empty state -->
    <div v-else-if="logs.length === 0" class="bg-white rounded-lg shadow-md p-12 text-center">
      <svg class="mx-auto h-12 w-12 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-3-3v6m-7 4h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
      </svg>
      <p class="mt-3 text-sm text-gray-500">No log entries found.</p>
      <p class="text-xs text-gray-400 mt-1">Try adjusting your filters or search query.</p>
    </div>

    <!-- Query table -->
    <template v-else>
      <QueryTable
        :logs="logs"
        @block-domain="handleBlockDomain"
      />

      <!-- Pagination controls -->
      <div class="bg-white rounded-lg shadow-md px-4 py-3">
        <div class="flex flex-col sm:flex-row items-center justify-between gap-3">
          <p class="text-sm text-gray-500">
            Page {{ currentPage }} of {{ totalPages }}
            <span v-if="totalCount != null" class="ml-1">({{ totalCount.toLocaleString() }} total)</span>
          </p>
          <div class="flex items-center space-x-1">
            <!-- Previous -->
            <button
              @click="goToPage(currentPage - 1)"
              :disabled="currentPage <= 1"
              class="px-3 py-1.5 text-sm font-medium border border-gray-300 rounded-md bg-white text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              Prev
            </button>

            <!-- Page numbers -->
            <template v-for="page in visiblePages" :key="page">
              <span v-if="page === '...'" class="px-2 py-1.5 text-sm text-gray-400">...</span>
              <button
                v-else
                @click="goToPage(page)"
                :class="[
                  'px-3 py-1.5 text-sm font-medium border rounded-md transition-colors',
                  page === currentPage
                    ? 'bg-blue-600 text-white border-blue-600'
                    : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'
                ]"
              >
                {{ page }}
              </button>
            </template>

            <!-- Next -->
            <button
              @click="goToPage(currentPage + 1)"
              :disabled="currentPage >= totalPages"
              class="px-3 py-1.5 text-sm font-medium border border-gray-300 rounded-md bg-white text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              Next
            </button>
          </div>
        </div>
      </div>
    </template>

    <!-- Block domain confirmation modal -->
    <div v-if="blockModal.visible" class="fixed inset-0 z-50 overflow-y-auto">
      <div class="flex items-center justify-center min-h-screen px-4">
        <div class="fixed inset-0 bg-black bg-opacity-50 transition-opacity" @click="blockModal.visible = false"></div>
        <div class="relative bg-white rounded-lg shadow-xl max-w-md w-full p-6 z-10">
          <h3 class="text-lg font-semibold text-gray-900 mb-2">Block Domain</h3>
          <p class="text-sm text-gray-600 mb-4">
            Add <strong class="font-mono">{{ blockModal.domain }}</strong> to your blacklist?
          </p>
          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 mb-1">Comment (optional)</label>
            <input
              v-model="blockModal.comment"
              type="text"
              placeholder="Reason for blocking"
              class="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
          <div v-if="blockModal.error" class="mb-4 text-sm text-red-600">
            {{ blockModal.error }}
          </div>
          <div class="flex justify-end space-x-3">
            <button
              @click="blockModal.visible = false"
              class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
            >
              Cancel
            </button>
            <button
              @click="confirmBlockDomain"
              :disabled="blockModal.blocking"
              class="px-4 py-2 text-sm font-medium text-white bg-red-600 rounded-md hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {{ blockModal.blocking ? 'Blocking...' : 'Block Domain' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { api } from '../api/client.js'
import QueryTable from '../components/QueryTable.vue'

const logs = ref([])
const loading = ref(true)
const error = ref(null)
const successMessage = ref('')

const searchQuery = ref('')
const isSearchMode = ref(false)

const currentPage = ref(1)
const perPage = ref(50)
const totalCount = ref(null)
const totalPages = ref(1)

// Default: last 24 hours
function getDefaultFrom() {
  const d = new Date()
  d.setHours(d.getHours() - 24)
  return formatDateTimeLocal(d)
}

function getDefaultTo() {
  return formatDateTimeLocal(new Date())
}

function formatDateTimeLocal(date) {
  const pad = n => String(n).padStart(2, '0')
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}T${pad(date.getHours())}:${pad(date.getMinutes())}`
}

const filters = ref({
  status: '',
  client: '',
  from: getDefaultFrom(),
  to: getDefaultTo()
})

const blockModal = ref({
  visible: false,
  domain: '',
  comment: '',
  blocking: false,
  error: null
})

const visiblePages = computed(() => {
  const pages = []
  const total = totalPages.value
  const current = currentPage.value

  if (total <= 7) {
    for (let i = 1; i <= total; i++) pages.push(i)
    return pages
  }

  // Always show first page
  pages.push(1)

  if (current > 3) {
    pages.push('...')
  }

  // Pages around current
  const start = Math.max(2, current - 1)
  const end = Math.min(total - 1, current + 1)
  for (let i = start; i <= end; i++) {
    pages.push(i)
  }

  if (current < total - 2) {
    pages.push('...')
  }

  // Always show last page
  if (total > 1) {
    pages.push(total)
  }

  return pages
})

function resetAndFetch() {
  currentPage.value = 1
  isSearchMode.value = false
  fetchLogs()
}

function clearFilters() {
  searchQuery.value = ''
  isSearchMode.value = false
  filters.value = {
    status: '',
    client: '',
    from: getDefaultFrom(),
    to: getDefaultTo()
  }
  currentPage.value = 1
  fetchLogs()
}

async function handleSearch() {
  if (!searchQuery.value.trim()) {
    isSearchMode.value = false
    resetAndFetch()
    return
  }
  isSearchMode.value = true
  currentPage.value = 1
  loading.value = true
  error.value = null
  try {
    const result = await api.searchLogs(searchQuery.value.trim(), 24)
    logs.value = Array.isArray(result) ? result : (result.logs ?? result.data ?? [])
    totalCount.value = logs.value.length
    totalPages.value = 1
  } catch (err) {
    error.value = err.message || 'Search failed.'
    logs.value = []
  } finally {
    loading.value = false
  }
}

async function fetchLogs() {
  loading.value = true
  error.value = null
  try {
    const params = {
      page: currentPage.value,
      per_page: perPage.value
    }
    if (filters.value.status) params.status = filters.value.status
    if (filters.value.client) params.client = filters.value.client
    if (filters.value.from) params.from = Math.floor(new Date(filters.value.from).getTime() / 1000)
    if (filters.value.to) params.to = Math.floor(new Date(filters.value.to).getTime() / 1000)

    const result = await api.getLogs(params)

    if (Array.isArray(result)) {
      logs.value = result
      totalCount.value = result.length
      totalPages.value = 1
    } else {
      logs.value = result.items ?? result.logs ?? result.data ?? []
      totalCount.value = result.total ?? result.total_count ?? logs.value.length
      totalPages.value = result.pages ?? result.total_pages ?? Math.ceil((totalCount.value || 1) / perPage.value)
    }
  } catch (err) {
    error.value = err.message || 'Failed to load logs.'
    logs.value = []
  } finally {
    loading.value = false
  }
}

function goToPage(page) {
  if (page < 1 || page > totalPages.value) return
  currentPage.value = page
  if (!isSearchMode.value) {
    fetchLogs()
  }
}

function handleBlockDomain(domain) {
  blockModal.value = {
    visible: true,
    domain,
    comment: '',
    blocking: false,
    error: null
  }
}

async function confirmBlockDomain() {
  blockModal.value.blocking = true
  blockModal.value.error = null
  try {
    await api.addDomain({
      domain: blockModal.value.domain,
      type: 'blacklist',
      comment: blockModal.value.comment || 'Blocked from query logs'
    })
    successMessage.value = `Domain "${blockModal.value.domain}" added to blacklist.`
    blockModal.value.visible = false
  } catch (err) {
    blockModal.value.error = err.message || 'Failed to block domain.'
  } finally {
    blockModal.value.blocking = false
  }
}

onMounted(() => {
  fetchLogs()
})
</script>
