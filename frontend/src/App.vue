<template>
  <div class="min-h-screen bg-gray-100">
    <nav class="bg-gray-900 text-white shadow-lg">
      <div class="max-w-7xl mx-auto px-4">
        <div class="flex items-center justify-between h-14">
          <router-link to="/" class="flex items-center gap-2 font-bold text-lg">
            <span class="text-red-400">&#9679;</span> Pi-hole Dashboard
          </router-link>
          <div class="flex gap-1">
            <router-link
              v-for="link in navLinks" :key="link.to"
              :to="link.to"
              class="px-3 py-2 rounded text-sm hover:bg-gray-700 transition-colors"
              active-class="bg-gray-700"
            >
              {{ link.label }}
            </router-link>
          </div>
        </div>
      </div>
    </nav>
    <main class="max-w-7xl mx-auto px-4 py-6">
      <router-view />
    </main>
  </div>
</template>

<script setup>
const navLinks = [
  { to: '/', label: 'Dashboard' },
  { to: '/devices', label: 'Devices' },
  { to: '/domains', label: 'Domains' },
  { to: '/timed-blocking', label: 'Timed Blocking' },
  { to: '/logs', label: 'Logs' },
]
</script>
