<template lang="html">
    <modal transition="modal fade" @ok="ok()" @cancel="cancel()" title="Communications log" xlarge>
        <div class="container-fluid">
            <table :id="table_id" class="hover table table-striped table-bordered border dt-responsive " cellspacing="0" width="100%">
            </table>
        </div>
        <template v-slot:footer>
            <span></span>
        </template>
    </modal>
</template>

<script>
//import $ from 'jquery'
import modal from '@vue-utils/bootstrap-modal.vue'
import {v4 as uuidv4} from 'uuid';
import alert from '@vue-utils/alert.vue'

export default {
    name:'Communications-Log',
    components:{
        modal,
        alert
    },
    props:{
        comms_url:{
            type: String,
            required: true
        },
    },
    data:function () {
        let vm = this;
        return {
            isModalOpen:false,
            table_id: uuidv4(),
            dateFormat: 'DD/MM/YYYY HH:mm:ss',
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
                            $(cell).popover();
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
        }
    },
    computed: {

    },
    methods:{
        ok:function () {
            console.log('ok clicked');
        },
        cancel:function () {
            this.close()
        },
        close:function () {
            let vm = this;
            vm.isModalOpen = false;
        },
   },
   mounted:function () {
        let vm =this;
        $('#' + vm.table_id).DataTable(vm.commsDtOptions);
   }
}
</script>

<style lang="css">
.btn-file {
    position: relative;
    overflow: hidden;
}
.btn-file input[type=file] {
    position: absolute;
    top: 0;
    right: 0;
    min-width: 100%;
    min-height: 100%;
    font-size: 100px;
    text-align: right;
    filter: alpha(opacity=0);
    opacity: 0;
    outline: none;
    background: white;
    cursor: inherit;
    display: block;
}
.top-buffer{margin-top: 5px;}
.top-buffer-2x{margin-top: 10px;}
</style>
