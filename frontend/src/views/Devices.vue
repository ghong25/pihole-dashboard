<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
      <h1 class="text-2xl font-bold text-gray-900">Devices</h1>
      <div class="flex flex-col sm:flex-row gap-3">
        <!-- Search input -->
        <div class="relative">
          <svg class="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Search devices..."
            class="pl-10 pr-4 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 w-full sm:w-64"
          />
        </div>
        <!-- Sort dropdown -->
        <select
          v-model="sortBy"
          class="px-3 py-2 border border-gray-300 rounded-md text-sm bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        >
          <option value="most_active">Most Active</option>
          <option value="most_blocked">Most Blocked</option>
          <option value="last_seen">Last Seen</option>
        </select>
      </div>
    </div>

    <!-- Error state -->
    <div v-if="error" class="bg-red-50 border border-red-200 rounded-lg p-4">
      <div class="flex items-center">
        <svg class="h-5 w-5 text-red-400 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <p class="text-sm text-red-700">{{ error }}</p>
      </div>
    </div>

    <!-- Loading state -->
    <div v-if="loading" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
      <div v-for="n in 8" :key="n" class="bg-white rounded-lg shadow-md p-6 animate-pulse">
        <div class="flex items-center space-x-3 mb-4">
          <div class="h-10 w-10 bg-gray-200 rounded-full"></div>
          <div class="space-y-2 flex-1">
            <div class="h-4 bg-gray-200 rounded w-3/4"></div>
            <div class="h-3 bg-gray-200 rounded w-1/2"></div>
          </div>
        </div>
        <div class="space-y-2">
          <div class="h-3 bg-gray-200 rounded w-full"></div>
          <div class="h-3 bg-gray-200 rounded w-2/3"></div>
        </div>
      </div>
    </div>

    <!-- Empty state -->
    <div v-else-if="filteredDevices.length === 0 && !loading" class="bg-white rounded-lg shadow-md p-12 text-center">
      <svg class="mx-auto h-12 w-12 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
      </svg>
      <p class="mt-3 text-sm text-gray-500">
        {{ searchQuery ? 'No devices match your search.' : 'No devices found.' }}
      </p>
    </div>

    <!-- Devices grid -->
    <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
      <DeviceCard
        v-for="device in filteredDevices"
        :key="device.mac"
        :device="device"
        @rename="openRenameModal(device)"
        @click="navigateToDevice(device.mac)"
      />
    </div>

    <!-- Rename modal -->
    <div v-if="renameModal.visible" class="fixed inset-0 z-50 overflow-y-auto">
      <div class="flex items-center justify-center min-h-screen px-4">
        <!-- Backdrop -->
        <div class="fixed inset-0 bg-black bg-opacity-50 transition-opacity" @click="closeRenameModal"></div>
        <!-- Modal content -->
        <div class="relative bg-white rounded-lg shadow-xl max-w-md w-full p-6 z-10">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Rename Device</h3>
          <p class="text-sm text-gray-500 mb-1">MAC: {{ renameModal.device?.mac }}</p>
          <p class="text-sm text-gray-500 mb-4">IP: {{ renameModal.device?.ip }}</p>
          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Nickname</label>
              <input
                v-model="renameModal.nickname"
                type="text"
                placeholder="Enter device nickname"
                class="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                @keyup.enter="saveRename"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Icon</label>
              <select
                v-model="renameModal.icon"
                class="w-full px-3 py-2 border border-gray-300 rounded-md text-sm bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="">Default</option>
                <option value="laptop">Laptop</option>
                <option value="phone">Phone</option>
                <option value="tablet">Tablet</option>
                <option value="tv">TV</option>
                <option value="speaker">Speaker</option>
                <option value="camera">Camera</option>
                <option value="server">Server</option>
                <option value="printer">Printer</option>
                <option value="iot">IoT Device</option>
              </select>
            </div>
          </div>
          <div v-if="renameModal.error" class="mt-3 text-sm text-red-600">
            {{ renameModal.error }}
          </div>
          <div class="mt-6 flex justify-end space-x-3">
            <button
              @click="closeRenameModal"
              class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              Cancel
            </button>
            <button
              @click="saveRename"
              :disabled="renameModal.saving"
              class="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {{ renameModal.saving ? 'Saving...' : 'Save' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '../api/client.js'
import DeviceCard from '../components/DeviceCard.vue'

const router = useRouter()

const devices = ref([])
const loading = ref(true)
const error = ref(null)
const searchQuery = ref('')
const sortBy = ref('most_active')

const renameModal = ref({
  visible: false,
  device: null,
  nickname: '',
  icon: '',
  saving: false,
  error: null
})

const filteredDevices = computed(() => {
  let result = [...devices.value]

  // Filter by search query
  if (searchQuery.value.trim()) {
    const q = searchQuery.value.toLowerCase().trim()
    result = result.filter(d =>
      (d.nickname && d.nickname.toLowerCase().includes(q)) ||
      (d.ip && d.ip.toLowerCase().includes(q)) ||
      (d.mac && d.mac.toLowerCase().includes(q)) ||
      (d.vendor && d.vendor.toLowerCase().includes(q))
    )
  }

  // Sort
  result.sort((a, b) => {
    switch (sortBy.value) {
      case 'most_active':
        return (b.total_queries ?? 0) - (a.total_queries ?? 0)
      case 'most_blocked':
        return (b.blocked_queries ?? 0) - (a.blocked_queries ?? 0)
      case 'last_seen':
        return new Date(b.last_seen ?? 0) - new Date(a.last_seen ?? 0)
      default:
        return 0
    }
  })

  return result
})

function navigateToDevice(mac) {
  router.push({ name: 'device-detail', params: { mac } })
}

function openRenameModal(device) {
  renameModal.value = {
    visible: true,
    device,
    nickname: device.nickname || '',
    icon: device.icon || '',
    saving: false,
    error: null
  }
}

function closeRenameModal() {
  renameModal.value.visible = false
}

async function saveRename() {
  renameModal.value.saving = true
  renameModal.value.error = null
  try {
    await api.updateDevice(renameModal.value.device.mac, {
      nickname: renameModal.value.nickname,
      icon: renameModal.value.icon
    })
    // Update local data
    const idx = devices.value.findIndex(d => d.mac === renameModal.value.device.mac)
    if (idx !== -1) {
      devices.value[idx] = {
        ...devices.value[idx],
        nickname: renameModal.value.nickname,
        icon: renameModal.value.icon
      }
    }
    closeRenameModal()
  } catch (err) {
    renameModal.value.error = err.message || 'Failed to update device.'
  } finally {
    renameModal.value.saving = false
  }
}

async function fetchDevices() {
  loading.value = true
  error.value = null
  try {
    const result = await api.getDevices()
    devices.value = Array.isArray(result) ? result : (result.devices ?? [])
  } catch (err) {
    error.value = err.message || 'Failed to load devices.'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchDevices()
})
</script>
