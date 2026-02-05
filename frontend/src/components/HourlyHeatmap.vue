<template>
  <div class="bg-white rounded-lg shadow-md p-5">
    <h3 class="text-sm font-semibold text-gray-700 mb-4">Hourly Query Heatmap</h3>

    <div v-if="!data || data.length === 0" class="flex items-center justify-center h-48 text-gray-400 text-sm">
      No data available
    </div>

    <div v-else class="overflow-x-auto relative">
      <!-- Hour labels row -->
      <div class="flex">
        <!-- Spacer for day labels -->
        <div class="w-10 flex-shrink-0"></div>
        <!-- Hour headers -->
        <div class="flex-1 grid grid-cols-24 gap-px">
          <div
            v-for="hour in 24"
            :key="'h-' + hour"
            class="text-center text-[10px] text-gray-400 pb-1"
          >
            {{ hour - 1 }}
          </div>
        </div>
      </div>

      <!-- Heatmap rows -->
      <div v-for="(dayRow, dayIndex) in matrix" :key="'d-' + dayIndex" class="flex items-center mb-px">
        <!-- Day label -->
        <div class="w-10 flex-shrink-0 text-xs text-gray-500 font-medium text-right pr-2">
          {{ dayLabels[dayIndex] }}
        </div>
        <!-- Cells -->
        <div class="flex-1 grid grid-cols-24 gap-px">
          <div
            v-for="(cell, hourIndex) in dayRow"
            :key="'c-' + dayIndex + '-' + hourIndex"
            class="aspect-square rounded-sm cursor-default transition-colors"
            :style="{ backgroundColor: cellColor(cell) }"
            @mouseenter="showTooltip($event, dayIndex, hourIndex, cell)"
            @mouseleave="hideTooltip"
          ></div>
        </div>
      </div>

      <!-- Tooltip -->
      <div
        v-if="tooltip.visible"
        class="absolute z-10 px-2.5 py-1.5 text-xs font-medium text-white bg-gray-900 rounded-md shadow-lg pointer-events-none whitespace-nowrap -translate-x-1/2 -translate-y-full"
        :style="{ left: tooltip.x + 'px', top: tooltip.y + 'px' }"
      >
        {{ tooltip.text }}
        <div class="absolute left-1/2 -translate-x-1/2 top-full w-0 h-0 border-l-4 border-r-4 border-t-4 border-l-transparent border-r-transparent border-t-gray-900"></div>
      </div>

      <!-- Legend -->
      <div class="flex items-center justify-end mt-3 space-x-1.5">
        <span class="text-[10px] text-gray-400">Less</span>
        <div
          v-for="(color, idx) in legendColors"
          :key="'leg-' + idx"
          class="w-3 h-3 rounded-sm"
          :style="{ backgroundColor: color }"
        ></div>
        <span class="text-[10px] text-gray-400">More</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  data: {
    type: Array,
    default: () => []
  }
})

const dayLabels = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']

const tooltip = ref({ visible: false, text: '', x: 0, y: 0 })

function showTooltip(event, dayIndex, hourIndex, count) {
  const rect = event.target.getBoundingClientRect()
  const parent = event.target.closest('.overflow-x-auto').getBoundingClientRect()
  tooltip.value = {
    visible: true,
    text: `${dayLabels[dayIndex]} ${String(hourIndex).padStart(2, '0')}:00 — ${count.toLocaleString()} queries`,
    x: rect.left - parent.left + rect.width / 2,
    y: rect.top - parent.top - 8,
  }
}

function hideTooltip() {
  tooltip.value.visible = false
}

const legendColors = [
  'rgb(241, 245, 249)',
  'rgb(191, 219, 254)',
  'rgb(96, 165, 250)',
  'rgb(37, 99, 235)',
  'rgb(30, 58, 138)'
]

const matrix = computed(() => {
  // Build 7x24 matrix initialized to 0
  const grid = Array.from({ length: 7 }, () => Array(24).fill(0))

  if (props.data && props.data.length > 0) {
    for (const entry of props.data) {
      const day = entry.day_of_week
      const hour = entry.hour
      if (day >= 0 && day < 7 && hour >= 0 && hour < 24) {
        grid[day][hour] = entry.count ?? 0
      }
    }
  }

  return grid
})

const maxCount = computed(() => {
  let max = 0
  for (const row of matrix.value) {
    for (const val of row) {
      if (val > max) max = val
    }
  }
  return max
})

function cellColor(count) {
  if (maxCount.value === 0 || count === 0) {
    return 'rgb(241, 245, 249)' // slate-100
  }

  const intensity = count / maxCount.value

  // Interpolate from light blue to dark blue
  // Level 0: rgb(241, 245, 249) - slate-100
  // Level 1: rgb(191, 219, 254) - blue-200
  // Level 2: rgb(96, 165, 250)  - blue-400
  // Level 3: rgb(37, 99, 235)   - blue-600
  // Level 4: rgb(30, 58, 138)   - blue-900

  if (intensity <= 0.25) {
    return interpolateColor([241, 245, 249], [191, 219, 254], intensity / 0.25)
  } else if (intensity <= 0.5) {
    return interpolateColor([191, 219, 254], [96, 165, 250], (intensity - 0.25) / 0.25)
  } else if (intensity <= 0.75) {
    return interpolateColor([96, 165, 250], [37, 99, 235], (intensity - 0.5) / 0.25)
  } else {
    return interpolateColor([37, 99, 235], [30, 58, 138], (intensity - 0.75) / 0.25)
  }
}

function interpolateColor(c1, c2, t) {
  const r = Math.round(c1[0] + (c2[0] - c1[0]) * t)
  const g = Math.round(c1[1] + (c2[1] - c1[1]) * t)
  const b = Math.round(c1[2] + (c2[2] - c1[2]) * t)
  return `rgb(${r}, ${g}, ${b})`
}
</script>

<style scoped>
.grid-cols-24 {
  grid-template-columns: repeat(24, minmax(0, 1fr));
}
</style>
