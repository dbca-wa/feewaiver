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
            dateFormat: 'DD/MM/YYYY HH:mm:ss',
            actionsTable: null,
            popoversInitialised: false,
            actionsDtOptions:{
                language: {
                    processing: "<i class='fa fa-4x fa-spinner fa-spin'></i>"
                },
                responsive: true,
                deferRender: true, 
                autowidth: true,
                order: [[3, 'desc']], // order the non-formatted date as a hidden column
                dom:
                    "<'row'<'col-sm-5'l><'col-sm-6'f>>" +
                    "<'row'<'col-sm-12'tr>>" +
                    "<'row'<'col-sm-5'i><'col-sm-7'p>>",
                processing:true,
                ajax: {
                    "url": vm.logs_url, 
                    "dataSrc": '',
                },
                order: [],
                columns:[
                    {
                        data:"who",
                        orderable: false
                    },
                    {
                        data:"what",
                        orderable: false
                    },
                    {
                        data:"when",
                        orderable: false,
                        mRender:function(data,type,full){
                            //return moment(data).format(vm.DATE_TIME_FORMAT)
                            return moment(data).format(vm.dateFormat);
                        }
                    },
                    {
                        title: 'Created',
                        data: 'when',
                        visible: false
                    }
                ]
            },
            commsDtOptions:{
                language: {
                    processing: "<i class='fa fa-4x fa-spinner fa-spin'></i>"
                },
                responsive: true,
                deferRender: true, 
                autowidth: true,
                order: [[8, 'desc']], // order the non-formatted date as a hidden column
                processing:true,
                ajax: {
                    "url": vm.comms_url, 
                    "dataSrc": '',
                },
                columns:[
                    {
                        title: 'Date',
                        data: 'created',
                        render: function (date) {
                            //return moment(date).format("DD-MMM-YYYY HH:mm:ss");
                            //return moment(date).format(vm.DATE_TIME_FORMAT);
                            return moment(date).format(vm.dateFormat);
                        }
                    },
                    {
                        title: 'Type',
                        data: 'type'
                    },
                    /*{
                        title: 'Reference',
                        data: 'reference'
                    },*/
                    {
                        title: 'To',
                        data: 'to',
                        //render: vm.commaToNewline
                        'render': function (value) {
                            var ellipsis = '...',
                                truncated = _.truncate(value, {
                                    length: 25,
                                    omission: ellipsis,
                                    separator: ' '
                                }),
                                result = '<span>' + truncated + '</span>',
                                popTemplate = _.template('<a href="#" ' +
                                    'role="button" ' +
                                    'data-bs-toggle="popover" ' +
                                    'data-bs-trigger="click" ' +
                                    'data-bs-placement="top auto"' +
                                    'data-bs-html="true" ' +
                                    'data-bs-content="<%= text %>" ' +
                                    '>more</a>');
                            if (_.endsWith(truncated, ellipsis)) {
                                result += popTemplate({
                                    text: value
                                });
                            }

                            return result;
                        },
                        'createdCell': function (cell) {
                            //TODO why this is not working?
                            // the call to popover is done in the 'draw' event
                            // $(cell).popover();
                            const popoverElement = $(cell).find('[data-bs-toggle="popover"]')[0];
                            if (popoverElement) {
                                new bootstrap.Popover(popoverElement);
                            }
                        }
                    },
                    {
                        title: 'CC',
                        data: 'cc',
                        //render: vm.commaToNewline
                          'render': function (value) {
                            var ellipsis = '...',
                                truncated = _.truncate(value, {
                                    length: 25,
                                    omission: ellipsis,
                                    separator: ' '
                                }),
                                result = '<span>' + truncated + '</span>',
                                popTemplate = _.template('<a href="#" ' +
                                    'role="button" ' +
                                    'data-bs-toggle="popover" ' +
                                    'data-bs-trigger="click" ' +
                                    'data-bs-placement="top auto"' +
                                    'data-bs-html="true" ' +
                                    'data-bs-content="<%= text %>" ' +
                                    '>more</a>');
                            if (_.endsWith(truncated, ellipsis)) {
                                result += popTemplate({
                                    text: value
                                });
                            }

                            return result;
                        },
                        'createdCell': function (cell) {
                            const popoverElement = $(cell).find('[data-bs-toggle="popover"]')[0];
                            if (popoverElement) {
                                new bootstrap.Popover(popoverElement);
                            }
                        }
                    },
                    {
                        title: 'From',
                        data: 'fromm',
                        render: vm.commaToNewline
                    },
                    {
                        title: 'Subject/Desc.',
                        data: 'subject',
                          'render': function (value) {
                            var ellipsis = '...',
                                truncated = _.truncate(value, {
                                    length: 25,
                                    omission: ellipsis,
                                    separator: ' '
                                }),
                                result = '<span>' + truncated + '</span>',
                                popTemplate = _.template('<a href="#" ' +
                                    'role="button" ' +
                                    'data-bs-toggle="popover" ' +
                                    'data-trigger="click" ' +
                                    'data-placement="top auto"' +
                                    'data-html="true" ' +
                                    'data-content="<%= text %>" ' +
                                    '>more</a>');
                            if (_.endsWith(truncated, ellipsis)) {
                                result += popTemplate({
                                    text: value
                                });
                            }

                            return result;
                        },
                        'createdCell': function (cell) {
                            //TODO why this is not working?
                            // the call to popover is done in the 'draw' event
                            $(cell).popover();
                        }
                    },
                    {
                        title: 'Text',
                        data: 'text',
                        'render': function (value) {
                            var ellipsis = '...',
                                truncated = _.truncate(value, {
                                    length: 100,
                                    omission: ellipsis,
                                    separator: ' '
                                }),
                                result = '<span>' + truncated + '</span>',
                                popTemplate = _.template('<a href="#" ' +
                                    'role="button" ' +
                                    'data-bs-toggle="popover" ' +
                                    'data-bs-trigger="click" ' +
                                    'data-bs-placement="top auto"' +
                                    'data-bs-html="true" ' +
                                    'data-bs-content="<%= text %>" ' +
                                    '>more</a>');
                            if (_.endsWith(truncated, ellipsis)) {
                                result += popTemplate({
                                    text: value
                                });
                            }

                            return result;
                        },
                        'createdCell': function (cell) {
                            //TODO why this is not working?
                            // the call to popover is done in the 'draw' event
                            $(cell).popover();
                        }
                    },
                    {
                        title: 'Documents',
                        data: 'documents',
                        'render': function (values) {
                            var result = '';
                            _.forEach(values, function (value) {
                                // We expect an array [docName, url]
                                // if it's a string it is the url
                                var docName = '',
                                    url = '';
                                if (_.isArray(value) && value.length > 1){
                                    docName = value[0];
                                    url = value[1];
                                }
                                if (typeof s === 'string'){
                                    url = value;
                                    // display the first  chars of the filename
                                    docName = _.last(value.split('/'));
                                    docName = _.truncate(docName, {
                                        length: 18,
                                        omission: '...',
                                        separator: ' '
                                    });
                                }
                                result += '<a href="' + url + '" target="_blank"><p>' + docName+ '</p></a><br>';
                            });
                            return result;
                        }
                    },
                    {
                        title: 'Created',
                        data: 'created',
                        visible: false
                    }
                ]
            },
            commsTable : null,
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
