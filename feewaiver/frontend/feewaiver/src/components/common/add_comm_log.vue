<template lang="html">
    <div id="AddComms">
        <modal transition="modal fade" @ok="ok()" @cancel="cancel()" title="Communication log - Add entry" large>
            <div class="container-fluid">
                <form class="form-horizontal" name="commsForm">
                    <alert :show.sync="showError" type="danger"><strong>{{errorString}}</strong></alert>
                    <div class="row mb-2">
                        <div class="col-sm-3">
                            <label class="form-label pull-left"  for="Name">To</label>
                        </div>
                        <div class="col-sm-4">
                            <input type="text" class="form-control" name="to" v-model="comms.to">
                        </div>
                    </div>
                    <div class="row mb-2">
                        <div class="col-sm-3">
                            <label class="form-label pull-left"  for="Name">From</label>
                        </div>
                        <div class="col-sm-4">
                            <input type="text" class="form-control" name="fromm" v-model="comms.fromm">
                        </div>
                    </div>
                    <div class="row mb-2">
                        <div class="col-sm-3">
                            <label class="form-label pull-left"  for="Name">Type</label>
                        </div>
                        <div class="col-sm-4">
                            <select class="form-select" name="type" v-model="comms.type">
                                <option value="">Select Type</option>
                                <option value="email">Email</option>
                                <option value="mail">Mail</option>
                                <option value="phone">Phone</option>
                            </select>
                        </div>
                    </div>
                    <div class="row mb-2">
                        <div class="col-sm-3">
                            <label class="form-label pull-left"  for="Name">Subject/Description</label>
                        </div>
                        <div class="col-sm-9">
                            <input type="text" class="form-control" name="subject" style="width:70%;" v-model="comms.subject">
                        </div>
                    </div>
                    <div class="row mb-2">
                        <div class="col-sm-3">
                            <label class="form-label pull-left"  for="Name">Text</label>
                        </div>
                        <div class="col-sm-9">
                            <textarea name="text" class="form-control" style="width:70%;" v-model="comms.text"></textarea>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-sm-3">
                            <label class="form-label pull-left"  for="Name">Attachments</label>
                        </div>
                        <div class="col-sm-9">
                            <template v-for="(f,i) in files">
                                <div :class="'row top-buffer file-row-'+i">
                                    <div class="col-sm-4">
                                        <span v-if="f.file == null" class="btn btn-info btn-file pull-left">
                                            Attach File <input type="file" :name="'file-upload-'+i" :class="'file-upload-'+i" @change="uploadFile('file-upload-'+i,f)" :ref="'fileInput-' + i"/>
                                        </span>
                                        <span v-else class="btn btn-info btn-file pull-left">
                                            Update File <input type="file" :name="'file-upload-'+i" :class="'file-upload-'+i" @change="uploadFile('file-upload-'+i,f)" :ref="'fileInput-' + i"/>
                                        </span>
                                    </div>
                                    <div class="col-sm-4">
                                        <span>{{f.name}}</span>
                                    </div>
                                    <div class="col-sm-4">
                                        <button @click="removeFile(i)" class="btn btn-danger">Remove</button>
                                    </div>
                                </div>
                            </template>
                            <a href="" @click.prevent="attachAnother"><i class="fa fa-lg fa-plus top-buffer-2x"></i></a>
                        </div>
                    </div>
                </form>
            </div>
            <div slot="footer">
                <button type="button" v-if="addingComms" disabled class="btn btn-default" @click="ok"><i class="fa fa-spinner fa-spin"></i> Adding</button>
                <!-- <button type="button" v-else class="btn btn-default" @click="ok">Add</button> -->
                <!-- <button type="button" class="btn btn-default" @click="cancel">Cancel</button> -->
            </div>
        </modal>
    </div>
</template>

<script>
//import $ from 'jquery'
import modal from '@vue-utils/bootstrap-modal.vue'
import alert from '@vue-utils/alert.vue'
import {helpers,api_endpoints} from "@/utils/hooks.js"
export default {
    name:'Add-Comms',
    components:{
        modal,
        alert
    },
    props:{
        url: {
            type: String,
            required: true
        }
    },
    data:function () {
        let vm = this;
        return {
            isModalOpen:false,
            form:null,
            comms: {},
            state: 'proposed_approval',
            addingComms: false,
            validation_form: null,
            errors: false,
            errorString: '',
            successString: '',
            success:false,
            datepickerOptions:{
                format: 'DD/MM/YYYY',
                showClear:true,
                useCurrent:false,
                keepInvalid:true,
                allowInputToggle:true
            },
            // files: [
            //     {
            //         'file': null,
            //         'name': ''
            //     }
            // ],
            files: [],
            modalKey: Math.random().toString(36).substring(2, 9)
        }
    },
    computed: {
        showError: function() {
            var vm = this;
            return vm.errors;
        },
        title: function(){
            return this.processing_status == 'With Approver' ? 'Issue Comms' : 'Propose to issue approval';
        }
    },
    methods:{
        updateModalKey: function() {
            this.modalKey = Math.random().toString(36).substring(2, 9);
        },
        ok:function () {
            let vm =this;
            if($(vm.form).valid()){
                vm.sendData();
            }
        },
        uploadFile(target, file_obj){
            let vm = this;
            let _file = null;
            var input = $('.'+target)[0];
            if (input.files && input.files[0]) {
                var reader = new FileReader();
                reader.readAsDataURL(input.files[0]); 
                reader.onload = function(e) {
                    _file = e.target.result;
                };
                _file = input.files[0];
            }
            file_obj.file = _file;
            file_obj.name = _file.name;
        },
        removeFile(index){
            this.files.splice(index,1);
        },
        attachAnother(){
            this.files.push({
                'file': null,
                'name': ''
            })
        },
        cancel:function () {
            this.close()
        },
        close:function () {
            let vm = this;
            vm.isModalOpen = false;
            vm.comms = {};
            vm.errors = false;
            $('.has-error').removeClass('has-error');
            vm.validation_form.resetForm();
            let file_length = vm.files.length;

            // Reset all file input fields
            for (let i = 0; i < file_length; i++) {
                if (vm.$refs['fileInput-' + i]) {
                    vm.$refs['fileInput-' + i].value = '';
                }
            }

            for (var i = 0; i < file_length; i++){
                vm.$nextTick(() => {
                    $('.file-row-'+i).remove();
                });
            }

            vm.files = [];

            // Update modalKey to force re-render of modal
            vm.updateModalKey();
            vm.form = document.forms.commsForm;
        },
        sendData:function(){
            let vm = this;
            vm.errors = false;
            let comms = new FormData(vm.form); 

            vm.files.forEach((fileObj, index) => {
                if (fileObj.file) {
                    comms.append('file-' + index, fileObj.file, fileObj.name);
                }
            });
            comms.append('num_files', vm.files.length);

            vm.addingComms = true;
            vm.$http.post(vm.url, comms,{
                }).then((response)=>{
                    vm.addingComms = false;
                    vm.close();
                    //vm.$emit('refreshFromResponse',response);
                },(error)=>{
                    vm.errors = true;
                    vm.addingComms = false;
                    vm.errorString = helpers.apiVueResourceError(error);
                });
        },
        addFormValidations: function() {
            let vm = this;
            vm.validation_form = $(vm.form).validate({
                rules: {
                    to:"required",
                    fromm:"required",
                    type:"required",
                    subject:"required",
                    text:"required",
                },
                messages: {
                },
                showErrors: function(errorMap, errorList) {
                    $.each(this.validElements(), function(index, element) {
                        var $element = $(element);
                        $element.attr("data-original-title", "").parents('.form-group').removeClass('has-error');
                    });
                    // destroy tooltips on valid elements
                    $("." + this.settings.validClass).tooltip("destroy");
                    // add or update tooltips
                    for (var i = 0; i < errorList.length; i++) {
                        var error = errorList[i];
                        $(error.element)
                            .tooltip({
                                trigger: "focus"
                            })
                            .attr("data-original-title", error.message)
                            .parents('.form-group').addClass('has-error');
                    }
                }
            });
       },
   },
   mounted:function () {
        let vm =this;
        vm.form = document.forms.commsForm;
        vm.addFormValidations();
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
