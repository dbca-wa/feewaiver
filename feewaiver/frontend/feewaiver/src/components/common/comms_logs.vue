<template>
    <div class="card mb-3">
        <div class="card-header">
            Logs
        </div>
        <div class="card-body">
            <strong>Communications</strong>
            <div class="row">
                <div class="col-sm-5">
                    <a @click="openCommunicationsLog()" class="actionBtn">Show</a>
                </div>
                <template v-if="!disable_add_entry">
                    <div class="col-sm-1">
                        <span>|</span>
                    </div> 
                    <div class="col-sm-5">
                        <a ref="addCommsBtn" @click="addComm()" class="actionBtn float-end">Add Entry</a>
                    </div>
                </template>
            </div>
            <strong>Actions</strong>
            <div class="row">
                <div class="col-sm-5">
                    <!-- <a tabindex="2" ref="showActionBtn" class="actionBtn">Show</a> -->
                    <a @click="openActionsLog()" class="actionBtn">Show</a>
                </div>
            </div>
        </div>
    </div>
    <AddCommLog
        ref="add_comm"
        :url="comms_add_url"
    />
    <CommunicationsLog
        ref="communications_log"
        :log_url="comms_url"
    />
    <ActionsLog
        ref="actions_log"
        :log_url="logs_url"
    />
</template>

<script>
import AddCommLog from './add_comm_log.vue'
import CommunicationsLog from './communications_log.vue'
import ActionsLog from './actions_log.vue'
import * as bootstrap from 'bootstrap'

export default {
    name: 'CommsLogSection',
    props: {
        comms_url:{
            type: String,
            required: true
        },
        logs_url:{
            type: String,
            required: true
        },
        comms_add_url:{
            type: String,
            required: true
        },
        disable_add_entry: {
            type: Boolean,
            default: true
        }
    },
    data() {
        let vm = this;
        return {

        }
    },
    components:{
        AddCommLog,
        CommunicationsLog,
        ActionsLog
    },
    watch:{
    },
    computed: {
    },
    methods:{
        addComm(){
            this.$refs.add_comm.isModalOpen = true;
        },
        openCommunicationsLog(){
            this.$refs.communications_log.isModalOpen = true;
        },
        openActionsLog(){
            this.$refs.actions_log.isModalOpen = true;
        },
        commaToNewline(value) {
            return value ? value.replace(/,\s*/g, '<br />') : '';
        }
    },
    mounted: function(){
        let vm = this;
        this.$nextTick(() => {

        });
    }
}
</script>

<style scoped>
.top-buffer-s {
    margin-top: 10px;
}
.actionBtn {
    cursor: pointer;
}
</style>
