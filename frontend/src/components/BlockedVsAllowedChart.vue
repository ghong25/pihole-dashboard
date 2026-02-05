<template>
  <div class="bg-white rounded-lg shadow-md p-5">
    <h3 class="text-sm font-semibold text-gray-700 mb-4">{{ title }}</h3>

    <div v-if="!domains || domains.length === 0" class="flex items-center justify-center h-48 text-gray-400 text-sm">
      No data available
    </div>

    <div v-else class="relative" :style="{ height: chartHeight + 'px' }">
      <Bar :data="chartData" :options="chartOptions" />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Bar } from 'vue-chartjs'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js'

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend)

const props = defineProps({
  domains: {
    type: Array,
    default: () => []
  },
  title: {
    type: String,
    default: 'Top Domains'
  }
})

const chartHeight = computed(() => {
  const count = props.domains?.length || 0
  return Math.max(200, count * 32 + 60)
})

const chartData = computed(() => {
  if (!props.domains || props.domains.length === 0) {
    return { labels: [], datasets: [] }
  }

  const sorted = [...props.domains].sort((a, b) => (b.count ?? 0) - (a.count ?? 0))

  return {
    labels: sorted.map((item) => truncateDomain(item.domain)),
    datasets: [
      {
        label: 'Queries',
        data: sorted.map((item) => item.count ?? 0),
        backgroundColor: generateColors(sorted.length),
        borderColor: generateBorderColors(sorted.length),
        borderWidth: 1,
        borderRadius: 3,
        barThickness: 20
      }
    ]
  }
})

const chartOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
  indexAxis: 'y',
  plugins: {
    legend: {
      display: false
    },
    tooltip: {
      backgroundColor: 'rgba(0, 0, 0, 0.8)',
      padding: 10,
      cornerRadius: 6,
      titleFont: { size: 12 },
      bodyFont: { size: 12 },
      callbacks: {
        title: (items) => {
          if (!items.length) return ''
          const idx = items[0].dataIndex
          const sorted = [...props.domains].sort((a, b) => (b.count ?? 0) - (a.count ?? 0))
          return sorted[idx]?.domain || ''
        }
      }
    }
  },
  scales: {
    x: {
      beginAtZero: true,
      grid: {
        color: 'rgba(0, 0, 0, 0.05)'
      },
      ticks: {
        font: { size: 11 },
        color: '#9ca3af',
        precision: 0
      }
    },
    y: {
      grid: {
        display: false
      },
      ticks: {
        font: { size: 11, family: 'ui-monospace, monospace' },
        color: '#374151'
      }
    }
  }
}))

function truncateDomain(domain) {
  if (!domain) return ''
  return domain.length > 30 ? domain.substring(0, 27) + '...' : domain
}

function generateColors(count) {
  const palette = [
    'rgba(59, 130, 246, 0.7)',
    'rgba(16, 185, 129, 0.7)',
    'rgba(245, 158, 11, 0.7)',
    'rgba(239, 68, 68, 0.7)',
    'rgba(139, 92, 246, 0.7)',
    'rgba(236, 72, 153, 0.7)',
    'rgba(20, 184, 166, 0.7)',
    'rgba(249, 115, 22, 0.7)',
    'rgba(99, 102, 241, 0.7)',
    'rgba(34, 197, 94, 0.7)'
  ]
  const colors = []
  for (let i = 0; i < count; i++) {
    colors.push(palette[i % palette.length])
  }
  return colors
}

function generateBorderColors(count) {
  const palette = [
    'rgba(59, 130, 246, 1)',
    'rgba(16, 185, 129, 1)',
    'rgba(245, 158, 11, 1)',
    'rgba(239, 68, 68, 1)',
    'rgba(139, 92, 246, 1)',
    'rgba(236, 72, 153, 1)',
    'rgba(20, 184, 166, 1)',
    'rgba(249, 115, 22, 1)',
    'rgba(99, 102, 241, 1)',
    'rgba(34, 197, 94, 1)'
  ]
  const colors = []
  for (let i = 0; i < count; i++) {
    colors.push(palette[i % palette.length])
  }
  return colors
}
</script>
