import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '../views/Dashboard.vue'
import Devices from '../views/Devices.vue'
import DeviceDetail from '../views/DeviceDetail.vue'
import Domains from '../views/Domains.vue'
import TimedBlocking from '../views/TimedBlocking.vue'
import Logs from '../views/Logs.vue'

const routes = [
  { path: '/', name: 'Dashboard', component: Dashboard },
  { path: '/devices', name: 'Devices', component: Devices },
  { path: '/devices/:mac', name: 'DeviceDetail', component: DeviceDetail, props: true },
  { path: '/domains', name: 'Domains', component: Domains },
  { path: '/timed-blocking', name: 'TimedBlocking', component: TimedBlocking },
  { path: '/logs', name: 'Logs', component: Logs },
]

export default createRouter({
  history: createWebHistory(),
  routes,
})
