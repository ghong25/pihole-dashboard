<template>
  <div class="space-y-6">
    <!-- Header -->
    <h1 class="text-2xl font-bold text-gray-900">Domain Management</h1>

    <!-- Error state -->
    <div v-if="error" class="bg-red-50 border border-red-200 rounded-lg p-4">
      <div class="flex items-center">
        <svg class="h-5 w-5 text-red-400 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <p class="text-sm text-red-700">{{ error }}</p>
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

    <!-- Add domain form -->
    <div class="bg-white rounded-lg shadow-md p-6">
      <h2 class="text-lg font-semibold text-gray-900 mb-4">Add Domain</h2>
      <AddDomainForm
        :active-type="activeTab"
        @submit="handleAddDomain"
        :submitting="addingDomain"
      />
    </div>

    <!-- Tab bar -->
    <div class="border-b border-gray-200">
      <nav class="-mb-px flex space-x-8">
        <button
          v-for="tab in tabs"
          :key="tab.type"
          @click="activeTab = tab.type"
          :class="[
            'py-3 px-1 border-b-2 font-medium text-sm transition-colors whitespace-nowrap',
            activeTab === tab.type
              ? 'border-blue-500 text-blue-600'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
          ]"
        >
          {{ tab.label }}
          <span
            :class="[
              'ml-2 inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium',
              activeTab === tab.type ? 'bg-blue-100 text-blue-600' : 'bg-gray-100 text-gray-600'
            ]"
          >
            {{ getTabCount(tab.type) }}
          </span>
        </button>
      </nav>
    </div>

    <!-- Domain list -->
    <DomainList
      :domains="filteredDomains"
      :loading="loadingDomains"
      @toggle="handleToggle"
      @delete="handleDelete"
    />

    <!-- Presets section -->
    <div class="bg-white rounded-lg shadow-md p-6">
      <h2 class="text-lg font-semibold text-gray-900 mb-2">Domain Presets</h2>
      <p class="text-sm text-gray-500 mb-4">Quickly add common domain lists to your blocklist or whitelist.</p>

      <div v-if="loadingPresets" class="flex items-center justify-center py-8">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>

      <div v-else-if="!presets || presets.length === 0" class="text-center text-gray-400 py-6">
        No presets available.
      </div>

      <div v-else class="space-y-4">
        <div
          v-for="preset in presets"
          :key="preset.name || preset.category"
          class="border border-gray-200 rounded-lg p-4"
        >
          <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
            <div>
              <h3 class="text-sm font-semibold text-gray-900">
                {{ preset.name || preset.category }}
              </h3>
              <p v-if="preset.description" class="text-xs text-gray-500 mt-1">
                {{ preset.description }}
              </p>
              <p class="text-xs text-gray-400 mt-1">
                {{ (preset.domains || []).length }} domain{{ (preset.domains || []).length === 1 ? '' : 's' }}
              </p>
            </div>
            <button
              @click="confirmAddPreset(preset)"
              :disabled="addingPreset === (preset.name || preset.category)"
              class="inline-flex items-center px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <svg v-if="addingPreset === (preset.name || preset.category)" class="animate-spin -ml-1 mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
              </svg>
              {{ addingPreset === (preset.name || preset.category) ? 'Adding...' : 'Add All' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Preset confirmation modal -->
    <div v-if="presetConfirm.visible" class="fixed inset-0 z-50 overflow-y-auto">
      <div class="flex items-center justify-center min-h-screen px-4">
        <div class="fixed inset-0 bg-black bg-opacity-50 transition-opacity" @click="presetConfirm.visible = false"></div>
        <div class="relative bg-white rounded-lg shadow-xl max-w-md w-full p-6 z-10">
          <h3 class="text-lg font-semibold text-gray-900 mb-2">Add Preset Domains?</h3>
          <p class="text-sm text-gray-600 mb-4">
            This will add {{ presetConfirm.preset?.domains?.length || 0 }} domain(s) from
            "<strong>{{ presetConfirm.preset?.name || presetConfirm.preset?.category }}</strong>"
            to your {{ activeTab === 'whitelist' ? 'whitelist' : 'blacklist' }}.
          </p>
          <div class="bg-gray-50 rounded-md p-3 mb-4 max-h-40 overflow-y-auto">
            <ul class="text-xs font-mono text-gray-600 space-y-1">
              <li v-for="domain in (presetConfirm.preset?.domains || [])" :key="domain">
                {{ domain }}
              </li>
            </ul>
          </div>
          <div class="flex justify-end space-x-3">
            <button
              @click="presetConfirm.visible = false"
              class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
            >
              Cancel
            </button>
            <button
              @click="addPresetDomains"
              class="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700"
            >
              Confirm
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { api } from '../api/client.js'
import DomainList from '../components/DomainList.vue'
import AddDomainForm from '../components/AddDomainForm.vue'

const tabs = [
  { label: 'Blacklist', type: 'blacklist' },
  { label: 'Whitelist', type: 'whitelist' },
  { label: 'Regex', type: 'regex_black' }
]

const activeTab = ref('blacklist')
const domains = ref([])
const loadingDomains = ref(true)
const error = ref(null)
const successMessage = ref('')
const addingDomain = ref(false)

const presets = ref([])
const loadingPresets = ref(true)
const addingPreset = ref(null)
const presetConfirm = ref({
  visible: false,
  preset: null
})

const filteredDomains = computed(() => {
  return domains.value.filter(d => d.type === activeTab.value)
})

function getTabCount(type) {
  return domains.value.filter(d => d.type === type).length
}

async function fetchDomains() {
  loadingDomains.value = true
  error.value = null
  try {
    const result = await api.getDomains()
    domains.value = Array.isArray(result) ? result : (result.domains ?? [])
  } catch (err) {
    error.value = err.message || 'Failed to load domains.'
  } finally {
    loadingDomains.value = false
  }
}

async function fetchPresets() {
  loadingPresets.value = true
  try {
    const result = await api.getPresets()
    presets.value = Array.isArray(result) ? result : (result.presets ?? [])
  } catch (err) {
    // Non-critical, just leave empty
    presets.value = []
  } finally {
    loadingPresets.value = false
  }
}

async function handleAddDomain(domainData) {
  addingDomain.value = true
  error.value = null
  try {
    await api.addDomain({
      domain: domainData.domain,
      type: domainData.type || activeTab.value,
      comment: domainData.comment || ''
    })
    successMessage.value = `Domain "${domainData.domain}" added successfully.`
    await fetchDomains()
  } catch (err) {
    error.value = err.message || 'Failed to add domain.'
  } finally {
    addingDomain.value = false
  }
}

async function handleToggle(id, enabled) {
  error.value = null
  try {
    await api.toggleDomain(id, enabled)
    const idx = domains.value.findIndex(d => d.id === id)
    if (idx !== -1) {
      domains.value[idx] = { ...domains.value[idx], enabled }
    }
  } catch (err) {
    error.value = err.message || 'Failed to toggle domain.'
  }
}

async function handleDelete(id) {
  error.value = null
  try {
    await api.deleteDomain(id)
    domains.value = domains.value.filter(d => d.id !== id)
    successMessage.value = 'Domain deleted successfully.'
  } catch (err) {
    error.value = err.message || 'Failed to delete domain.'
  }
}

function confirmAddPreset(preset) {
  presetConfirm.value = {
    visible: true,
    preset
  }
}

async function addPresetDomains() {
  const preset = presetConfirm.value.preset
  presetConfirm.value.visible = false
  if (!preset || !preset.domains) return

  const presetKey = preset.name || preset.category
  addingPreset.value = presetKey
  error.value = null

  try {
    const type = activeTab.value === 'whitelist' ? 'whitelist' : 'blacklist'
    const promises = preset.domains.map(domain =>
      api.addDomain({
        domain,
        type,
        comment: `Added from preset: ${presetKey}`
      })
    )
    await Promise.all(promises)
    successMessage.value = `Added ${preset.domains.length} domain(s) from "${presetKey}".`
    await fetchDomains()
  } catch (err) {
    error.value = err.message || 'Failed to add preset domains.'
  } finally {
    addingPreset.value = null
  }
}

onMounted(() => {
  fetchDomains()
  fetchPresets()
})
</script>
