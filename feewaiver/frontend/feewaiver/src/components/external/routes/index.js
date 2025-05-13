import FeeWaiverForm from '../../feewaiver_form.vue'
import FeeWaiverSubmit from '../feewaiver_submit.vue'
import { h } from 'vue'
import { RouterView } from 'vue-router'

export default
{
    path: '/external',
    component: {
        render() {
            // Using the h function from Vue 3 to create a RouterView component
            return h(RouterView)
        }
    },
    children: [
        {
            path: '',
            component: FeeWaiverForm,
            name: 'external-feewaiver-form'
        },
        {
            path: 'submit',
            component: FeeWaiverSubmit,
            name: "submit_feewaiver"
        }
    ]
}
