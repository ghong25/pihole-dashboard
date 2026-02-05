<template>
  <form @submit.prevent="handleSubmit" class="bg-white rounded-lg shadow-md p-4">
    <div class="flex flex-wrap items-end gap-3">
      <!-- Domain input -->
      <div class="flex-1 min-w-[200px]">
        <label for="domain-input" class="block text-sm font-medium text-gray-700 mb-1">
          Domain
        </label>
        <input
          id="domain-input"
          v-model.trim="form.domain"
          type="text"
          placeholder="example.com"
          required
          class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm"
        />
      </div>

      <!-- Type dropdown -->
      <div class="w-44">
        <label for="type-select" class="block text-sm font-medium text-gray-700 mb-1">
          Type
        </label>
        <select
          id="type-select"
          v-model="form.type"
          class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm bg-white"
        >
          <option value="blacklist">Blacklist</option>
          <option value="whitelist">Whitelist</option>
          <option value="regex_black">Regex Black</option>
          <option value="wildcard">Wildcard</option>
        </select>
      </div>

      <!-- Comment input -->
      <div class="flex-1 min-w-[150px]">
        <label for="comment-input" class="block text-sm font-medium text-gray-700 mb-1">
          Comment
          <span class="text-gray-400 font-normal">(optional)</span>
        </label>
        <input
          id="comment-input"
          v-model.trim="form.comment"
          type="text"
          placeholder="Optional comment"
          class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm"
        />
      </div>

      <!-- Submit button -->
      <div>
        <button
          type="submit"
          :disabled="!form.domain"
          :class="[
            'inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors',
            form.domain
              ? 'bg-blue-600 hover:bg-blue-700 cursor-pointer'
              : 'bg-blue-300 cursor-not-allowed'
          ]"
        >
          <svg class="h-4 w-4 mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          Add Domain
        </button>
      </div>
    </div>
  </form>
</template>

<script setup>
import { reactive } from 'vue'

const emit = defineEmits(['add'])

const form = reactive({
  domain: '',
  type: 'blacklist',
  comment: ''
})

function handleSubmit() {
  if (!form.domain) return

  emit('add', {
    domain: form.domain,
    type: form.type,
    comment: form.comment
  })

  form.domain = ''
  form.comment = ''
}
</script>
