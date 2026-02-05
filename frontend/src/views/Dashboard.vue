<template>
  <div class="space-y-6">
    <!-- Header with time range toggle -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
      <h1 class="text-2xl font-bold text-gray-900">Dashboard</h1>
      <div class="inline-flex rounded-md shadow-sm">
        <button
          v-for="range in timeRanges"
          :key="range.hours"
          @click="selectedHours = range.hours"
          :class="[
            'px-4 py-2 text-sm font-medium border transition-colors',
            selectedHours === range.hours
              ? 'bg-blue-600 text-white border-blue-600 z-10'
              : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50',
            range.hours === 24 ? 'rounded-l-md' : '',
            range.hours === 720 ? 'rounded-r-md' : '',
            range.hours !== 24 ? '-ml-px' : ''
          ]"
        >
          {{ range.label }}
        </button>
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

    <!-- Stat cards row -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <StatsCard
        title="Total Queries"
        :value="loading ? '--' : formatNumber(summary?.total_queries)"
        color="blue"
        :subtitle="`Last ${selectedLabel}`"
      />
      <StatsCard
        title="Blocked"
        :value="loading ? '--' : formatNumber(summary?.blocked_queries)"
        color="red"
        :subtitle="`Last ${selectedLabel}`"
      />
      <StatsCard
        title="Block %"
        :value="loading ? '--' : formatPercent(summary?.blocked_percentage)"
        color="yellow"
        subtitle="Of all queries"
      />
      <StatsCard
        title="Active Devices"
        :value="loading ? '--' : (summary?.unique_clients ?? '--')"
        color="green"
        subtitle="Unique clients"
      />
    </div>

    <!-- Stacked area chart: Blocked vs Allowed over time -->
    <div v-if="loading" class="bg-white rounded-lg shadow-md p-6">
      <div class="h-64 flex items-center justify-center">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    </div>
    <TimeChart v-else :data="overTimeData" title="Query Traffic Over Time" />

    <!-- Two-column layout: Top Queried / Top Blocked -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <BlockedVsAllowedChart :domains="topDomains" title="Top Queried Domains" />
      <BlockedVsAllowedChart :domains="topBlocked" title="Top Blocked Domains" />
    </div>

    <!-- Hourly heatmap -->
    <HourlyHeatmap :data="hourlyData" />
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { api } from '../api/client.js'
import StatsCard from '../components/StatsCard.vue'
import TimeChart from '../components/TimeChart.vue'
import BlockedVsAllowedChart from '../components/BlockedVsAllowedChart.vue'
import HourlyHeatmap from '../components/HourlyHeatmap.vue'

const timeRanges = [
  { label: '24h', hours: 24 },
  { label: '7d', hours: 168 },
  { label: '30d', hours: 720 }
]

const selectedHours = ref(24)
const loading = ref(true)
const initialLoadDone = ref(false)
const error = ref(null)

const summary = ref(null)
const overTimeData = ref([])
const topDomains = ref([])
const topBlocked = ref([])
const hourlyData = ref([])

let refreshInterval = null

const selectedLabel = computed(() => {
  const range = timeRanges.find(r => r.hours === selectedHours.value)
  return range ? range.label : '24h'
})

function formatNumber(val) {
  if (val == null) return '--'
  return Number(val).toLocaleString()
}

function formatPercent(val) {
  if (val == null) return '--'
  return `${Number(val).toFixed(1)}%`
}

async function fetchData(isRefresh = false) {
  if (!isRefresh) {
    loading.value = true
  }
  error.value = null
  try {
    const hours = selectedHours.value
    const [summaryRes, overTimeRes, topDomainsRes, topBlockedRes, hourlyRes] = await Promise.all([
      api.getSummary(hours),
      api.getOverTime(hours),
      api.getTopDomains(10, hours),
      api.getTopBlocked(10, hours),
      api.getHourlyPattern(Math.max(Math.floor(hours / 24), 1))
    ])
    summary.value = summaryRes
    overTimeData.value = overTimeRes
    topDomains.value = topDomainsRes
    topBlocked.value = topBlockedRes
    hourlyData.value = hourlyRes
  } catch (err) {
    if (!isRefresh) {
      error.value = err.message || 'Failed to load dashboard data.'
    }
  } finally {
    loading.value = false
    initialLoadDone.value = true
  }
}

watch(selectedHours, () => {
  fetchData()
})

onMounted(() => {
  fetchData()
  refreshInterval = setInterval(() => fetchData(true), 30000)
})

onUnmounted(() => {
  if (refreshInterval) {
    clearInterval(refreshInterval)
  }
})
</script>
