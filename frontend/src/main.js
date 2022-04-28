import { createApp, VueElement } from 'vue'
import App from './App.vue'
import {createRouter, createWebHistory} from 'vue-router'
import axios from 'axios'
import BootstrapVue3 from 'bootstrap-vue-3'
import 'bootstrap/dist/css/bootstrap.css'
import 'bootstrap-vue-3/dist/bootstrap-vue-3.css'

VueElement.prototype.$http = axios

// const routes = [
//     {
//         path: '/',
//         name: 'Home',
//     }
// ]
// const router = createRouter({
//     history: createWebHistory(),
//     routes
// })

const app = createApp(App)
//app.use(router)
app.use(BootstrapVue3)
app.mount('#app')