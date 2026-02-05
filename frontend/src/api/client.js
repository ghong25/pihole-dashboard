const BASE = import.meta.env.VITE_API_BASE || ''

async function request(path, options = {}) {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options,
  })
  if (!res.ok) {
    const text = await res.text()
    throw new Error(`API error ${res.status}: ${text}`)
  }
  return res.json()
}

export const api = {
  // Dashboard
  getSummary: (hours = 24) => request(`/api/stats/summary?hours=${hours}`),
  getTopDomains: (limit = 10, hours = 24) => request(`/api/stats/top-domains?limit=${limit}&hours=${hours}`),
  getTopBlocked: (limit = 10, hours = 24) => request(`/api/stats/top-blocked?limit=${limit}&hours=${hours}`),
  getOverTime: (hours = 24) => request(`/api/stats/over-time?hours=${hours}`),
  getHourlyPattern: (days = 7) => request(`/api/stats/hourly-pattern?days=${days}`),
  getBlocklistEffectiveness: () => request('/api/stats/blocklist-effectiveness'),

  // Devices
  getDevices: () => request('/api/devices'),
  updateDevice: (mac, data) => request(`/api/devices/${mac}`, { method: 'PATCH', body: JSON.stringify(data) }),
  getDeviceStats: (mac, hours = 24) => request(`/api/devices/${mac}/stats?hours=${hours}`),
  getDeviceActivity: (mac, hours = 24) => request(`/api/devices/${mac}/activity?hours=${hours}`),
  getDeviceTopDomains: (mac, limit = 10) => request(`/api/devices/${mac}/top-domains?limit=${limit}`),
  getDeviceTopBlocked: (mac, limit = 10) => request(`/api/devices/${mac}/top-blocked?limit=${limit}`),

  // Domains
  getDomains: (type) => request(`/api/domains${type ? `?type=${type}` : ''}`),
  addDomain: (data) => request('/api/domains', { method: 'POST', body: JSON.stringify(data) }),
  deleteDomain: (id) => request(`/api/domains/${id}`, { method: 'DELETE' }),
  toggleDomain: (id, enabled) => request(`/api/domains/${id}`, { method: 'PATCH', body: JSON.stringify({ enabled }) }),
  getPresets: () => request('/api/domains/presets'),

  // Timed Blocks
  getTimedBlocks: () => request('/api/timed-blocks'),
  createTimedBlock: (data) => request('/api/timed-blocks', { method: 'POST', body: JSON.stringify(data) }),
  cancelTimedBlock: (id) => request(`/api/timed-blocks/${id}`, { method: 'DELETE' }),

  // Logs
  getLogs: (params = {}) => {
    const qs = new URLSearchParams()
    Object.entries(params).forEach(([k, v]) => { if (v != null && v !== '') qs.set(k, v) })
    return request(`/api/logs?${qs}`)
  },
  searchLogs: (q, hours = 24) => request(`/api/logs/search?q=${encodeURIComponent(q)}&hours=${hours}`),
}
