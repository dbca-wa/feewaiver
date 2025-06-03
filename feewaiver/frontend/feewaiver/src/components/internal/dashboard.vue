<template id="proposal_dashboard">
    <div class="container">
        <FormSection :formCollapse="false" label="Fee Waiver Requests" Index="fee_waiver_requests">
            <div class="row">
                <div class="col-md-3">
                        <label for="lodged_from" class="pt-2 pr-2">Lodged From：</label>
                        <input
                            id="lodged_from"
                            v-model="filterFeeWaiverLodgedFrom"
                            type="date"
                            class="form-control"
                            placeholder="DD/MM/YYYY"
                            :max="filterFeeWaiverLodgedTo || null"
                        />
                </div>

                <div class="col-md-3">
                        <label for="lodged_to" class="pt-2 pr-2">Lodged To：</label>
                        <input
                            id="lodged_to"
                            v-model="filterFeeWaiverLodgedTo"
                            type="date"
                            class="form-control"
                            placeholder="DD/MM/YYYY"
                            :min="filterFeeWaiverLodgedFrom || null"
                        />
                </div>

                <div class="col-md-3">
                        <label class="form-label" for="status-filter">Status</label>
                        <select id="status-filter" class="form-select" v-model="filterFeeWaiverStatus">
                            <option value="All">All</option>
                            <option v-for="(s, index) in feewaiver_status" :key="index" :value="s">{{s}}</option>
                        </select>
                </div>
            </div>

            <div class="row">
                <div class="col-lg-12" style="margin-top:25px;">
                    <datatable ref="feewaiver_datatable" :id="datatable_id" :dtOptions="feewaiver_options" :dtHeaders="feewaiver_headers"/>
                </div>
            </div>
        </FormSection>
        </div>
</template>
<script>

import datatable from '@/utils/vue/datatable.vue'
import { v4 as uuid } from 'uuid'
import FormSection from "@/components/forms/section_toggle.vue"
import {
    api_endpoints,
    helpers
}from '@/utils/hooks'
import axios from 'axios'

export default {
    name: 'FeeWaiverDash',
    props: {
    },
    data() {
        let vm = this;
        return {
            processingActionShortcut: false,
            url: '/api/feewaivers_paginated/feewaiver_internal/?format=datatables',
            pBody: 'pBody' + uuid(),
            datatable_id: 'feewaiver-datatable-' + uuid(),
            show_spinner: false, 
            filterFeeWaiverStatus: 'All',
            filterFeeWaiverLodgedFrom: '',
            filterFeeWaiverLodgedTo: '',
            dashboardTitle: '',
            dashboardDescription: '',
            dateFormat: 'DD/MM/YYYY',
            feewaiver_status:[],
            feewaiver_headers:["Lodgement Number", "Organisation", "Status", "Lodged on", "Document", "Assigned To", "", "", "Action", "Participant", "Comments to applicant"],
            feewaiver_options:{
                language: {
                    processing: "<i class='fa fa-4x fa-spinner fa-spin'></i>"
                },
                responsive: true,
                serverSide: true,
                order: [
                    [0, 'desc']
                    ],
                ajax: {
                    "url": '/api/feewaivers_paginated/feewaiver_internal/?format=datatables',
                    "dataSrc": 'data',
                    // adding extra GET params for Custom filtering
                    "data": function ( d ) {
                        d.date_from = vm.filterFeeWaiverLodgedFrom;
                        d.date_to = vm.filterFeeWaiverLodgedTo;
                        d.processing_status = vm.filterFeeWaiverStatus;
                    }

                },
                // dom: 'lBfrtip',
                "dom":  "<'d-flex'<'me-auto'l>fB>" +
                        "<'row'<'col-sm-12'tr>>" +
                        "<'d-flex'<'me-auto'i>p>",
                buttons:[
                    {
                        extend: 'excel',
                        exportOptions: {
                            columns: ':visible'
                        }
                    },
                    {
                        extend: 'csv',
                        exportOptions: {
                            columns: ':visible'
                        }
                    },
                ],
                columns: [
                    {
                        data: "lodgement_number",
                        visible: true,
                        //searchable: false,
                    },
                    {
                        data: "organisation",
                        visible: true,
                        orderable: false,
                    },
                    {
                        data: "processing_status",
                        mRender:function (data,type,full) {
                            let fullStatus = full.processing_status;
                            return fullStatus
                        },
                        //searchable: false,
                        visible: true,
                    },
                    {
                        data: "lodgement_date",
                        mRender:function (data,type,full) {
                            return data != '' && data != null ? moment(data).format(vm.dateFormat): '';
                        },
                        visible: true,
                    },
                    {
                        data: "latest_feewaiver_document",
                        visible: true,
                        orderable: false,
                        mRender:function(data,type,full){
                            if (data) {
                                return `<a href="${data}" target="_blank"><i style="color:red" class="fa fa-file-pdf-o"></i></a>`;
                            } else {
                                return null;
                            }
                        },

                        //searchable: false,
                    },
                    {
                        data: "assigned_officer",
                        visible: true,
                        //searchable: false,
                    },
                    {
                        data: "proposed_status",
                        visible: false,
                        //searchable: false,
                    },
                    {
                        data: "action_shortcut",
                        visible: false,
                        //searchable: false,
                    },
                    {
                        data: "can_process",
                        mRender:function (data,type,full) {
                            //let links = '';
                            let links = full.action_shortcut;
                            /*
                            if(full.can_process){

                                links +=  `<a href='/internal/fee_waiver/${full.id}'>Process</a><br/>`;
                            } else{
                                links +=  `<a href='/internal/fee_waiver/${full.id}'>View</a><br/>`;
                            }
                            */
                            return links;
                        },
                        name: '',
                        searchable: false,
                        orderable: false
                    },
                    {
                        data: "participants",
                        visible: true,
                        orderable: false,
                    },
                    {
                        data: "comments_to_applicant",
                        visible: true,
                        mRender: function (value) {
                            var ellipsis = '...',
                                truncated = _.truncate(value, {
                                    length: 25,
                                    omission: ellipsis,
                                    separator: ' '
                                }),
                                result = '<span>' + truncated + '</span>',
                                popTemplate = _.template('<a href="#" ' +
                                //popTemplate = _.template('<button ' +
                                    'role="button" ' +
                                    'data-bs-toggle="popover" ' +
                                    'data-trigger="click" ' +
                                    'data-placement="top auto"' +
                                    'data-html="true" ' +
                                    'data-container="body" ' +
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
                        //responsivePriority: 50,
                        //width: "50%",
                        //searchable: false,
                    },
                    {
                        data: "id",
                        visible: false,
                        orderable: false,
                    },


                ],
                processing: true,
                initComplete: function() {
                    vm.$refs.feewaiver_datatable.vmDataTable.columns.adjust().draw();
                },
            }
        }
    },
    components:{
        FormSection,
        datatable,
    },
    watch:{
        filterFeeWaiverStatus: function(){
            this.$refs.feewaiver_datatable.vmDataTable.draw();
        },

        filterFeeWaiverLodgedFrom: function(newVal){
            console.log({newVal})
            // If lodged_to date is set and it's before the new lodged_from date
            if (this.filterFeeWaiverLodgedTo && newVal && this.filterFeeWaiverLodgedTo < newVal) {
                // Update the lodged_to date to be the same as lodged_from
                this.filterFeeWaiverLodgedTo = newVal;
            }
            this.$refs.feewaiver_datatable.vmDataTable.draw();
        },
        
        filterFeeWaiverLodgedTo: function(newVal){
            console.log({newVal})
            // If lodged_from date is set and it's after the new lodged_to date
            if (this.filterFeeWaiverLodgedFrom && newVal && this.filterFeeWaiverLodgedFrom > newVal) {
                // Update the lodged_from date to be the same as lodged_to
                this.filterFeeWaiverLodgedFrom = newVal;
            }
            this.$refs.feewaiver_datatable.vmDataTable.draw();
        }
    },
    computed: {
    },
    methods:{
        fetchFilterLists: function(){
            let vm = this;

            vm.$http.get(api_endpoints.filter_list).then((response) => {
                vm.feewaiver_status = response.data.feewaiver_status_choices;
            },(error) => {
            })
        },
        actionShortcutWrapper: async function(id, approvalType) {
            this.removeActionShortcutEventListeners();
            this.$nextTick(async () => {
                if (!this.processingActionShortcut) {
                    await this.actionShortcut(id, approvalType);
                    this.processingActionShortcut = false;
                }
            });
        },
        actionShortcut: async function(id, approvalType) {
            let vm = this;
            this.processingActionShortcut = true;
            let processingTableStr = `.action-${id}`;
            let processViewStr = `.process-view-${id}`;
            let processingTable = $(processingTableStr);
            let processView = $(processViewStr);
            processingTable.replaceWith("<div><i class='fa fa-2x fa-spinner fa-spin'></i></div>");
            processView.replaceWith("");
            let post_url = '/api/feewaivers/' + id + '/final_approval/'
            let res = await axios.post(post_url, {'approval_type': approvalType});
            if (res.status === 200) {
                // this should also be await?
                await this.refreshFromResponse();
            }
        },
        refreshFromResponse: async function(){
            await this.$refs.feewaiver_datatable.vmDataTable.ajax.reload();
            this.addActionShortcutEventListeners();
        },
        addEventListeners: async function(){
            let vm = this;
            // const picker = new TempusDominus(document.getElementById('datetimepicker1'), {
            //     localization: {
            //         format: 'dd/MM/yyyy',
            //         close: 'Close'
            //     },
            //     display: {
            //         components: {
            //             clock: false
            //         },
            //         buttons: {
            //             close: true
            //         }
            //     }
            // });
            // Initialise Proposal Date Filters
            // $(vm.$refs.feewaiverDateToPicker).datetimepicker(vm.datepickerOptions);
            // $(vm.$refs.feewaiverDateToPicker).on('dp.change', function(e){
            //     if ($(vm.$refs.feewaiverDateToPicker).data('DateTimePicker').date()) {
            //         vm.filterFeeWaiverLodgedTo =  e.date.format('DD/MM/YYYY');
            //     }
            //     else if ($(vm.$refs.feewaiverDateToPicker).data('date') === "") {
            //         vm.filterFeeWaiverLodgedTo = "";
            //     }
            //  });
            // $(vm.$refs.feewaiverDateFromPicker).datetimepicker(vm.datepickerOptions);
            // $(vm.$refs.feewaiverDateFromPicker).on('dp.change',function (e) {
            //     if ($(vm.$refs.feewaiverDateFromPicker).data('DateTimePicker').date()) {
            //         vm.filterFeeWaiverLodgedFrom = e.date.format('DD/MM/YYYY');
            //         $(vm.$refs.feewaiverDateToPicker).data("DateTimePicker").minDate(e.date);
            //     }
            //     else if ($(vm.$refs.feewaiverDateFromPicker).data('date') === "") {
            //         vm.filterFeeWaiverLodgedFrom = "";
            //     }
            // });
            // let table = vm.$refs.feewaiver_datatable.vmDataTable
            // table.on('responsive-display.dt', function () {
            //     var tablePopover = $(this).find('[data-bs-toggle="popover"]');
            //     if (tablePopover.length > 0) {
            //         tablePopover.popover();
            //         // the next line prevents from scrolling up to the top after clicking on the popover.
            //         $(tablePopover).on('click', function (e) {
            //             e.preventDefault();
            //             return true;   
            //         });
            //     }
            // }).on('draw.dt', function () {
            //     var tablePopover = $(this).find('[data-bs-toggle="popover"]');
            //     if (tablePopover.length > 0) {
            //         tablePopover.popover();
            //         // the next line prevents from scrolling up to the top after clicking on the popover.
            //         $(tablePopover).on('click', function (e) {
            //             e.preventDefault();
            //             return true;
            //         });
            //     }
            // });

            vm.addActionShortcutEventListeners();
        },
        addActionShortcutEventListeners: function() {
            let vm = this;
            //Internal Action shortcut listeners
            let table = vm.$refs.feewaiver_datatable.vmDataTable
            table.on('click', 'a[data-issue]', async function(e) {
                e.preventDefault();
                var id = $(this).attr('data-issue');
                await vm.actionShortcutWrapper(id, 'issue');
            }).on('click', 'a[data-concession]', async function(e) {
                e.preventDefault();
                var id = $(this).attr('data-concession');
                await vm.actionShortcutWrapper(id, 'issue_concession');
            }).on('click', 'a[data-decline]', async function(e) {
                e.preventDefault();
                var id = $(this).attr('data-decline');
                await vm.actionShortcutWrapper(id, 'decline');
            });
        },
        removeActionShortcutEventListeners: function() {
            let vm = this;
            //Internal Action shortcut listeners
            let table = vm.$refs.feewaiver_datatable.vmDataTable
            table.off('click', 'a[data-issue]', async function(e) {
                /*
                e.preventDefault();
                var id = $(this).attr('data-issue');
                await vm.actionShortcutWrapper(id, 'issue');
                */
            }).off('click', 'a[data-concession]', async function(e) {
                /*
                e.preventDefault();

                var id = $(this).attr('data-concession');
                await vm.actionShortcutWrapper(id, 'issue_concession');
                */
            }).off('click', 'a[data-decline]', async function(e) {
                /*
                e.preventDefault();
                var id = $(this).attr('data-decline');
                await vm.actionShortcutWrapper(id, 'decline');
                */
            });
        },
    },
    mounted: function(){
        this.$nextTick(() => {
            this.fetchFilterLists();
            let vm = this;
            $( 'a[data-bs-toggle="collapse"]' ).on( 'click', function () {
                var chev = $( this ).children()[ 0 ];
                window.setTimeout( function () {
                    $( chev ).toggleClass( "glyphicon-chevron-down glyphicon-chevron-up" );
                }, 100 );
            });
            this.addEventListeners();
        });
    },
    created: function() {

    },
}
</script>

<style scoped>
</style>
