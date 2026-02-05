<template>
  <div class="space-y-6">
    <!-- Header -->
    <h1 class="text-2xl font-bold text-gray-900">Timed Blocking</h1>

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

    <!-- Quick-block presets -->
    <div class="bg-white rounded-lg shadow-md p-6">
      <h2 class="text-lg font-semibold text-gray-900 mb-2">Quick Block</h2>
      <p class="text-sm text-gray-500 mb-4">Instantly block common distractions for a set duration.</p>
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
        <button
          v-for="preset in quickPresets"
          :key="preset.label"
          @click="activateQuickPreset(preset)"
          :disabled="creatingBlock"
          class="relative flex flex-col items-center justify-center p-4 border-2 border-gray-200 rounded-lg hover:border-blue-400 hover:bg-blue-50 transition-all focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed group"
        >
          <span class="text-2xl mb-2">{{ preset.icon }}</span>
          <span class="text-sm font-semibold text-gray-900 group-hover:text-blue-700">{{ preset.label }}</span>
          <span class="text-xs text-gray-500 mt-1">
            {{ preset.domains.length }} domain{{ preset.domains.length === 1 ? '' : 's' }}
          </span>
        </button>
      </div>
    </div>

    <!-- Custom block form -->
    <div class="bg-white rounded-lg shadow-md p-6">
      <h2 class="text-lg font-semibold text-gray-900 mb-4">Custom Block</h2>
      <div class="space-y-4">
        <!-- Domain input -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Domains
          </label>
          <input
            v-model="customDomain"
            type="text"
            placeholder="Enter domain(s), comma-separated (e.g., reddit.com, twitter.com)"
            class="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            @keyup.enter="createCustomBlock"
          />
          <p class="text-xs text-gray-400 mt-1">Separate multiple domains with commas.</p>
        </div>

        <!-- Duration picker -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Duration
          </label>
          <div class="flex flex-wrap gap-2">
            <button
              v-for="dur in durationOptions"
              :key="dur.minutes"
              @click="customDuration = dur.minutes"
              :class="[
                'px-4 py-2 text-sm font-medium rounded-md border transition-colors',
                customDuration === dur.minutes
                  ? 'bg-blue-600 text-white border-blue-600'
                  : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'
              ]"
            >
              {{ dur.label }}
            </button>
          </div>
        </div>

        <!-- Submit button -->
        <div class="pt-2">
          <button
            @click="createCustomBlock"
            :disabled="!customDomain.trim() || creatingBlock"
            class="inline-flex items-center px-6 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <svg v-if="creatingBlock" class="animate-spin -ml-1 mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
            </svg>
            {{ creatingBlock ? 'Blocking...' : 'Start Block' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Active blocks -->
    <div>
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-lg font-semibold text-gray-900">Active Blocks</h2>
        <button
          @click="fetchActiveBlocks"
          class="text-sm text-gray-500 hover:text-gray-700 transition-colors"
        >
          <svg class="h-4 w-4 inline mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          Refresh
        </button>
      </div>

      <div v-if="loadingBlocks" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        <div v-for="n in 3" :key="n" class="bg-white rounded-lg shadow-md p-6 animate-pulse">
          <div class="h-4 bg-gray-200 rounded w-1/2 mb-3"></div>
          <div class="h-8 bg-gray-200 rounded w-2/3 mb-2"></div>
          <div class="h-3 bg-gray-200 rounded w-3/4"></div>
        </div>
      </div>

      <div v-else-if="!activeBlocks || activeBlocks.length === 0" class="bg-white rounded-lg shadow-md p-12 text-center">
        <svg class="mx-auto h-12 w-12 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <p class="mt-3 text-sm text-gray-500">No active timed blocks.</p>
        <p class="text-xs text-gray-400 mt-1">Use the quick block buttons or custom form above to get started.</p>
      </div>

      <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        <TimerCard
          v-for="block in activeBlocks"
          :key="block.id"
          :block="block"
          @cancel="handleCancelBlock(block.id)"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { api } from '../api/client.js'
import TimerCard from '../components/TimerCard.vue'

const quickPresets = [
  {
    label: 'Reddit 30m',
    icon: '📱',
    domains: ['reddit.com', 'www.reddit.com', 'old.reddit.com'],
    duration: 30
  },
  {
    label: 'Social Media 1h',
    icon: '💬',
    domains: ['reddit.com', 'twitter.com', 'instagram.com', 'tiktok.com', 'facebook.com'],
    duration: 60
  },
  {
    label: 'YouTube 1h',
    icon: '🎬',
    domains: ['youtube.com', 'www.youtube.com', 'youtu.be'],
    duration: 60
  },
  {
    label: 'All Video 2h',
    icon: '📺',
    domains: ['youtube.com', 'twitch.tv', 'netflix.com'],
    duration: 120
  }
]

const durationOptions = [
  { label: '15m', minutes: 15 },
  { label: '30m', minutes: 30 },
  { label: '1h', minutes: 60 },
  { label: '2h', minutes: 120 },
  { label: '4h', minutes: 240 }
]

const error = ref(null)
const successMessage = ref('')
const creatingBlock = ref(false)
const loadingBlocks = ref(true)
const activeBlocks = ref([])

const customDomain = ref('')
const customDuration = ref(30)

let refreshInterval = null

async function activateQuickPreset(preset) {
  creatingBlock.value = true
  error.value = null
  try {
    await api.createTimedBlock({
      domains: preset.domains,
      duration_minutes: preset.duration
    })
    successMessage.value = `${preset.label} block activated.`
    await fetchActiveBlocks()
  } catch (err) {
    error.value = err.message || 'Failed to create timed block.'
  } finally {
    creatingBlock.value = false
  }
}

async function createCustomBlock() {
  if (!customDomain.value.trim()) return

  creatingBlock.value = true
  error.value = null

  const domains = customDomain.value
    .split(',')
    .map(d => d.trim())
    .filter(d => d.length > 0)

  if (domains.length === 0) {
    error.value = 'Please enter at least one domain.'
    creatingBlock.value = false
    return
  }

  try {
    await api.createTimedBlock({
      domains,
      duration_minutes: customDuration.value
    })
    successMessage.value = `Blocked ${domains.join(', ')} for ${formatDuration(customDuration.value)}.`
    customDomain.value = ''
    await fetchActiveBlocks()
  } catch (err) {
    error.value = err.message || 'Failed to create timed block.'
  } finally {
    creatingBlock.value = false
  }
}

async function handleCancelBlock(id) {
  error.value = null
  try {
    await api.cancelTimedBlock(id)
    activeBlocks.value = activeBlocks.value.filter(b => b.id !== id)
    successMessage.value = 'Timed block cancelled.'
  } catch (err) {
    error.value = err.message || 'Failed to cancel timed block.'
  }
}

async function fetchActiveBlocks() {
  loadingBlocks.value = activeBlocks.value.length === 0
  try {
    const result = await api.getTimedBlocks()
    activeBlocks.value = Array.isArray(result) ? result : (result.blocks ?? result.timed_blocks ?? [])
  } catch (err) {
    if (activeBlocks.value.length === 0) {
      error.value = err.message || 'Failed to load active blocks.'
    }
  } finally {
    loadingBlocks.value = false
  }
}

function formatDuration(minutes) {
  if (minutes < 60) return `${minutes} minutes`
  const hours = Math.floor(minutes / 60)
  const remaining = minutes % 60
  if (remaining === 0) return `${hours} hour${hours > 1 ? 's' : ''}`
  return `${hours}h ${remaining}m`
}

onMounted(() => {
  fetchActiveBlocks()
  refreshInterval = setInterval(fetchActiveBlocks, 10000)
})

onUnmounted(() => {
  if (refreshInterval) {
    clearInterval(refreshInterval)
  }
})
</script>
