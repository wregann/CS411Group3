import { createApp, VueElement } from 'vue'
import App from './App.vue'
import {createRouter, createWebHistory} from 'vue-router'
import Home from '@/components/Home.vue'
import Login from '@/components/Login.vue'
import Search from '@/components/Search.vue'
import axios from 'axios'
VueElement.prototype.$http = axios

const routes = [
    {
        path: '/',
        name: "Home",
        component: Home
    },
    {
        path: '/login',
        name: "Login",
        component: Login
    },
    {
        path: '/search',
        name: "Search",
        component: Search
    }
]

const router = createRouter({
    history: createWebHistory(),
    routes
})

createApp(App).use(router).mount('#app')
