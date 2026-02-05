<template>
  <div class="bg-white rounded-lg shadow-md p-5">
    <h3 class="text-sm font-semibold text-gray-700 mb-4">{{ title }}</h3>

    <div v-if="!data || data.length === 0" class="flex items-center justify-center h-48 text-gray-400 text-sm">
      No data available
    </div>

    <div v-else class="relative" style="height: 300px;">
      <Line :data="chartData" :options="chartOptions" />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Line } from 'vue-chartjs'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js'

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, Filler)

const props = defineProps({
  data: {
    type: Array,
    default: () => []
  },
  title: {
    type: String,
    default: 'Queries Over Time'
  }
})

const chartData = computed(() => {
  if (!props.data || props.data.length === 0) {
    return { labels: [], datasets: [] }
  }

  const labels = props.data.map((item) => formatBucketLabel(item.bucket))

  return {
    labels,
    datasets: [
      {
        label: 'Allowed',
        data: props.data.map((item) => item.allowed ?? 0),
        borderColor: 'rgb(34, 197, 94)',
        backgroundColor: 'rgba(34, 197, 94, 0.2)',
        fill: true,
        tension: 0.3,
        pointRadius: 0,
        pointHoverRadius: 4,
        borderWidth: 2,
        order: 2
      },
      {
        label: 'Blocked',
        data: props.data.map((item) => item.blocked ?? 0),
        borderColor: 'rgb(239, 68, 68)',
        backgroundColor: 'rgba(239, 68, 68, 0.2)',
        fill: true,
        tension: 0.3,
        pointRadius: 0,
        pointHoverRadius: 4,
        borderWidth: 2,
        order: 1
      }
    ]
  }
})

const chartOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
  interaction: {
    mode: 'index',
    intersect: false
  },
  plugins: {
    legend: {
      position: 'top',
      align: 'end',
      labels: {
        usePointStyle: true,
        pointStyle: 'circle',
        boxWidth: 6,
        padding: 16,
        font: {
          size: 12
        }
      }
    },
    tooltip: {
      backgroundColor: 'rgba(0, 0, 0, 0.8)',
      padding: 10,
      cornerRadius: 6,
      titleFont: { size: 12 },
      bodyFont: { size: 12 }
    }
  },
  scales: {
    x: {
      grid: {
        display: false
      },
      ticks: {
        font: { size: 11 },
        color: '#9ca3af',
        maxRotation: 0,
        autoSkip: true,
        maxTicksLimit: 12
      }
    },
    y: {
      stacked: true,
      beginAtZero: true,
      grid: {
        color: 'rgba(0, 0, 0, 0.05)'
      },
      ticks: {
        font: { size: 11 },
        color: '#9ca3af',
        precision: 0
      }
    }
  }
}))

function formatBucketLabel(bucket) {
  if (!bucket) return ''
  const date = typeof bucket === 'number'
    ? new Date(bucket > 1e12 ? bucket : bucket * 1000)
    : new Date(bucket)
  return date.toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit',
    hour12: false
  })
}
</script>
