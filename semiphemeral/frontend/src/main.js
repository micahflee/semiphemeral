import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'

import App from './App.vue';
import Dashboard from "./pages/Dashboard.vue";
import Tweets from "./pages/Tweets.vue";
import Export from "./pages/Export.vue";
import DirectMessages from "./pages/DirectMessages.vue";
import Settings from "./pages/Settings.vue";

const routes = [
    { path: '/', name: 'dashboard', component: Dashboard },
    { path: '/tweets', name: 'tweets', component: Tweets },
    { path: '/export', name: 'export', component: Export },
    { path: '/dms', name: 'dms', component: DirectMessages },
    { path: '/settings', name: 'settings', component: Settings }
]

const router = createRouter({
    history: createWebHistory(),
    routes
})

const app = createApp(App)
app.use(router)
app.mount('#app')