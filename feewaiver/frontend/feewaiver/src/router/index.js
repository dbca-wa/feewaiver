// import Router from 'vue-router'
import { createRouter, createWebHistory } from 'vue-router'
import external_routes from '@/components/external/routes'
import internal_routes from '@/components/internal/routes'
// Vue.use(Router)

// export default new Router({
//     mode: 'history',
//     routes: [
//         external_routes,
//         internal_routes
//     ]
// })

const router = createRouter({
    history: createWebHistory(),
    routes: [
        external_routes,
        internal_routes
    ]
})

export default router
