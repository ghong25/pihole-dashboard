<template>
  <div
    :class="[
      'bg-white rounded-lg shadow-md p-6 border-l-4 transition-shadow hover:shadow-lg',
      borderColorClass
    ]"
  >
    <p class="text-sm font-medium text-gray-500 uppercase tracking-wide">
      {{ title }}
    </p>
    <p :class="['text-3xl font-bold mt-2', valueColorClass]">
      {{ value ?? '--' }}
    </p>
    <p v-if="subtitle" class="text-sm text-gray-400 mt-1">
      {{ subtitle }}
    </p>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  title: {
    type: String,
    required: true
  },
  value: {
    type: [String, Number],
    required: true
  },
  subtitle: {
    type: String,
    default: ''
  },
  color: {
    type: String,
    default: 'blue',
    validator: (val) => ['blue', 'red', 'green', 'yellow'].includes(val)
  }
})

const colorMap = {
  blue: {
    border: 'border-blue-500',
    value: 'text-blue-600'
  },
  red: {
    border: 'border-red-500',
    value: 'text-red-600'
  },
  green: {
    border: 'border-green-500',
    value: 'text-green-600'
  },
  yellow: {
    border: 'border-yellow-500',
    value: 'text-yellow-600'
  }
}

const borderColorClass = computed(() => colorMap[props.color]?.border ?? colorMap.blue.border)
const valueColorClass = computed(() => colorMap[props.color]?.value ?? colorMap.blue.value)
</script>
