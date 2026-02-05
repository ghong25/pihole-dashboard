<template>
  <div class="space-y-6">
    <!-- Back button -->
    <button
      @click="$router.back()"
      class="inline-flex items-center text-sm text-gray-600 hover:text-gray-900 transition-colors"
    >
      <svg class="h-4 w-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
      </svg>
      Back to Devices
    </button>

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
    <div v-if="loading" class="space-y-6">
      <div class="bg-white rounded-lg shadow-md p-6 animate-pulse">
        <div class="flex items-center space-x-4">
          <div class="h-16 w-16 bg-gray-200 rounded-full"></div>
          <div class="space-y-3 flex-1">
            <div class="h-6 bg-gray-200 rounded w-1/3"></div>
            <div class="h-4 bg-gray-200 rounded w-1/2"></div>
            <div class="h-4 bg-gray-200 rounded w-1/4"></div>
          </div>
        </div>
      </div>
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div v-for="n in 4" :key="n" class="bg-white rounded-lg shadow-md p-6 animate-pulse">
          <div class="h-4 bg-gray-200 rounded w-1/2 mb-3"></div>
          <div class="h-8 bg-gray-200 rounded w-2/3"></div>
        </div>
      </div>
    </div>

    <!-- Device content -->
    <template v-if="!loading">
      <!-- Device header -->
      <div class="bg-white rounded-lg shadow-md p-6">
        <div class="flex flex-col sm:flex-row sm:items-center gap-4">
          <div class="flex-shrink-0">
            <div class="h-16 w-16 bg-blue-100 rounded-full flex items-center justify-center">
              <svg class="h-8 w-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
              </svg>
            </div>
          </div>
          <div class="flex-1 min-w-0">
            <h1 class="text-2xl font-bold text-gray-900 truncate">
              {{ device?.nickname || device?.ip || mac }}
            </h1>
            <div class="mt-1 flex flex-wrap gap-x-4 gap-y-1 text-sm text-gray-500">
              <span v-if="device?.ip">
                <span class="font-medium text-gray-600">IP:</span> {{ device.ip }}
              </span>
              <span>
                <span class="font-medium text-gray-600">MAC:</span> {{ mac }}
              </span>
              <span v-if="device?.vendor">
                <span class="font-medium text-gray-600">Vendor:</span> {{ device.vendor }}
              </span>
            </div>
            <div class="mt-1 flex flex-wrap gap-x-4 gap-y-1 text-sm text-gray-400">
              <span v-if="device?.first_seen">
                First seen: {{ formatDateTime(device.first_seen) }}
              </span>
              <span v-if="device?.last_seen">
                Last seen: {{ formatDateTime(device.last_seen) }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- Stats cards row -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatsCard
          title="Total Queries"
          :value="formatNumber(stats?.total_queries)"
          color="blue"
          subtitle="Last 24 hours"
        />
        <StatsCard
          title="Blocked"
          :value="formatNumber(stats?.blocked_queries)"
          color="red"
          subtitle="Last 24 hours"
        />
        <StatsCard
          title="Block %"
          :value="formatPercent(stats?.block_percentage)"
          color="yellow"
          subtitle="Of this device's queries"
        />
        <StatsCard
          title="Unique Domains"
          :value="formatNumber(stats?.unique_domains)"
          color="green"
          subtitle="Distinct domains queried"
        />
      </div>

      <!-- Activity timeline -->
      <div class="bg-white rounded-lg shadow-md p-6">
        <h2 class="text-lg font-semibold text-gray-900 mb-4">Activity Timeline</h2>
        <div v-if="!activityData || activityData.length === 0" class="h-64 flex items-center justify-center text-gray-400">
          No activity data available.
        </div>
        <TimeChart v-else :data="activityData" class="h-64" />
      </div>

      <!-- Two columns: Top queried + Top blocked -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div class="bg-white rounded-lg shadow-md p-6">
          <h2 class="text-lg font-semibold text-gray-900 mb-4">Top Queried Domains</h2>
          <div v-if="!topDomains || topDomains.length === 0" class="text-center text-gray-400 py-8">
            No domain data available.
          </div>
          <BlockedVsAllowedChart v-else :data="topDomains" type="queried" />
        </div>
        <div class="bg-white rounded-lg shadow-md p-6">
          <h2 class="text-lg font-semibold text-gray-900 mb-4">Top Blocked Domains</h2>
          <div v-if="!topBlocked || topBlocked.length === 0" class="text-center text-gray-400 py-8">
            No blocked domain data available.
          </div>
          <BlockedVsAllowedChart v-else :data="topBlocked" type="blocked" />
        </div>
      </div>

      <!-- Recent queries -->
      <div class="bg-white rounded-lg shadow-md p-6">
        <h2 class="text-lg font-semibold text-gray-900 mb-4">Recent Queries</h2>
        <div v-if="logsLoading" class="flex items-center justify-center py-8">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
        <div v-else-if="!recentLogs || recentLogs.length === 0" class="text-center text-gray-400 py-8">
          No recent query data available.
        </div>
        <QueryTable v-else :logs="recentLogs" />
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { api } from '../api/client.js'
import StatsCard from '../components/StatsCard.vue'
import TimeChart from '../components/TimeChart.vue'
import BlockedVsAllowedChart from '../components/BlockedVsAllowedChart.vue'
import QueryTable from '../components/QueryTable.vue'

const route = useRoute()
const mac = route.params.mac

const loading = ref(true)
const logsLoading = ref(true)
const error = ref(null)

const device = ref(null)
const stats = ref(null)
const activityData = ref([])
const topDomains = ref([])
const topBlocked = ref([])
const recentLogs = ref([])

function formatNumber(val) {
  if (val == null) return '--'
  return Number(val).toLocaleString()
}

function formatPercent(val) {
  if (val == null) return '--'
  return `${Number(val).toFixed(1)}%`
}

function formatDateTime(timestamp) {
  if (!timestamp) return ''
  const date = typeof timestamp === 'number' ? new Date(timestamp * 1000) : new Date(timestamp)
  return date.toLocaleString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

async function fetchDeviceData() {
  loading.value = true
  error.value = null
  try {
    // Fetch devices list to find this device's info
    const devicesResult = await api.getDevices()
    const devicesList = Array.isArray(devicesResult) ? devicesResult : (devicesResult.devices ?? [])
    device.value = devicesList.find(d => d.mac === mac) || null

    // Fetch device stats and activity in parallel
    const [statsRes, activityRes, topDomainsRes, topBlockedRes] = await Promise.all([
      api.getDeviceStats(mac, 24),
      api.getDeviceActivity(mac, 24),
      api.getDeviceTopDomains(mac, 10),
      api.getDeviceTopBlocked(mac, 10)
    ])

    stats.value = statsRes
    activityData.value = activityRes
    topDomains.value = topDomainsRes
    topBlocked.value = topBlockedRes
  } catch (err) {
    error.value = err.message || 'Failed to load device details.'
  } finally {
    loading.value = false
  }

  // Fetch recent logs for this device (uses IP, not MAC)
  await fetchRecentLogs()
}

async function fetchRecentLogs() {
  logsLoading.value = true
  try {
    const clientIp = device.value?.ip || ''
    if (clientIp) {
      const now = new Date()
      const dayAgo = new Date(now.getTime() - 24 * 60 * 60 * 1000)
      const logsRes = await api.getLogs({
        client: clientIp,
        per_page: 50,
        page: 1,
        from: dayAgo.toISOString(),
        to: now.toISOString()
      })
      recentLogs.value = Array.isArray(logsRes) ? logsRes : (logsRes.logs ?? logsRes.data ?? [])
    }
  } catch (err) {
    // Non-critical error, just leave logs empty
    recentLogs.value = []
  } finally {
    logsLoading.value = false
  }
}

onMounted(() => {
  fetchDeviceData()
})
</script>
