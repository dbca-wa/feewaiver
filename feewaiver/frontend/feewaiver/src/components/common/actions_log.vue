<template lang="html">
    <modal transition="modal fade" @ok="ok()" @cancel="cancel()" title="Actions log" xlarge>
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
import modal from '@vue-utils/bootstrap-modal.vue'
import {v4 as uuidv4} from 'uuid';
import alert from '@vue-utils/alert.vue'
import 'bootstrap/dist/js/bootstrap.bundle.min.js'

export default {
    name:'Actions-Log',
    components:{
        modal,
        alert
    },
    props:{
        log_url:{
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
            datatableOptions:{
                language: {
                    processing: "<i class='fa fa-4x fa-spinner fa-spin'></i>"
                },
                responsive: true,
                deferRender: true, 
                autowidth: true,
                order: [[3, 'desc']], // order the non-formatted date as a hidden column
                processing:true,
                ajax: {
                    "url": vm.log_url, 
                    "dataSrc": '',
                },
                order: [],
                columns:[
                    {
                        title: 'Who',
                        data:"who",
                        orderable: false
                    },
                    {
                        title: 'What',
                        data:"what",
                        orderable: false
                    },
                    {
                        title: 'When',
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
        $('#' + vm.table_id).DataTable(vm.datatableOptions);
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

