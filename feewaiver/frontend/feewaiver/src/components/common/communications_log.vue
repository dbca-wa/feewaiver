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
import 'bootstrap/dist/js/bootstrap.bundle.min.js'

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
                    {
                        title: 'To',
                        data: 'to',
                        'render': function(value) {
                            return vm.processString(value);
                        }
                    },
                    {
                        title: 'CC',
                        data: 'cc',
                          'render': function (value) {
                            return vm.processString(value);
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
                            return vm.processString(value);
                        }
                    },
                    {
                        title: 'Text',
                        data: 'text',
                        'render': function (value) {
                            return vm.processString(value);
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
        processString: function (context_str) {
            let truncated = this.truncateString(context_str, 25);
            let popover_id = uuidv4();
            let result_html = ''
            let body = `<p>${context_str}</p>`;

            if (truncated.length < context_str.length) {
                result_html = truncated + `<button popovertarget="${popover_id}" class="link-button">more...</button><div id="${popover_id}" popover class="popover-content">${body}</div>`
            } else {
                result_html = body
            }
            return result_html;
        },
        truncateString: function(str, maxLength) {
            if (str.length > maxLength) {
                return str.slice(0, maxLength - 3) + '...';
            }
            return str;
        },
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

/* Start: Popover */
.link-button {
    background: none;
    border: none;
    color: #03a9f4;
    text-decoration: underline;
    cursor: pointer;
    padding: 0;
    font: inherit;
}
.link-button:focus {
    outline: none;
}
.popover-content {
    max-width: 300px;
    width: auto;
    word-wrap: break-word;
    padding: 10px;
    border: 1px solid #ccc;
    background-color: white;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}
/* END: Popover */
</style>

