// import InternalDashboard from '../dashboard.vue'
// import FeeWaiverAssessment from '../assessment.vue'
// export default
// {
//     path: '/internal',
//     component:
//     {
//         render(c)
//         {
//             return c('router-view')
//         }
//     },
//     children: [
//         {
//             path: '/',
//             component: InternalDashboard,
//             name:"fee-waiver-dash"
//         },
//         {
//             path: 'fee_waiver',
//             component: {
//                 render(c)
//                 {
//                     return c('router-view')
//                 }
//             },
//             children: [
//                 {
//                     path: ':fee_waiver_id',
//                     component: FeeWaiverAssessment,
//                     name:"fee-waiver-assessment"
//                 },
//             ]
//         },
//     ]
// }

import InternalDashboard from '../dashboard.vue'
import FeeWaiverAssessment from '../assessment.vue'
import { h } from 'vue'
import { RouterView } from 'vue-router'

export default
{
    path: '/internal',
    component:
    {
        render() {
            // Using the h function from Vue 3 to create a RouterView component
            return h(RouterView)
        }
    },
    children: [
        {
            path: '',
            component: InternalDashboard,
            name:"fee-waiver-dash"
        },
        {
            path: 'fee_waiver',
            component: {
                render()
                {
                    return h(RouterView)
                }
            },
            children: [
                {
                    path: ':fee_waiver_id',
                    component: FeeWaiverAssessment,
                    name:"fee-waiver-assessment"
                },
            ]
        },
    ]
}
