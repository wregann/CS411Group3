import { createApp, VueElement } from 'vue'
import App from './App.vue'
import {createRouter, createWebHistory} from 'vue-router'
import axios from 'axios'
VueElement.prototype.$http = axios

const routes = [
    {
        path: '/',
        name: 'Home',
    }
]
const router = createRouter({
    history: createWebHistory(),
    routes
})

createApp(App).use(router).mount('#app')
