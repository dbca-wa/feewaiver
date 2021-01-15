<template lang="html">
    <div v-if="feeWaiver" class="container" id="internalAssessment">
      <div class="row">
        <!--h3>Entry Fee Waiver Request: {{ feeWaiver.lodgement_number }}</h3-->
        <h3>{{ assessmentTitle }}</h3>
        <div class="col-md-3">
            <CommsLogs :comms_url="comms_url" :logs_url="logs_url" :comms_add_url="comms_add_url" :disable_add_entry="false"/>

            <div class="row">
                <div class="panel panel-default">
                    <div class="panel-heading">
                        Workflow
                    </div>
                    <div class="panel-body panel-collapse">
                        <div class="row">
                            <div class="col-sm-12">
                                <strong>Status</strong><br/>
                                {{ feeWaiver.processing_status }}
                            </div>
                            <div class="col-sm-12">
                                <div class="separator"></div>
                            </div>

                            <div class="col-sm-12 top-buffer-s">
                                <strong>Currently assigned to</strong><br/>
                                <div class="form-group">
                                    <template>
                                        <select ref="assigned_officer" :disabled="!canAssign" class="form-control" v-model="feeWaiver.assigned_officer_id">
                                            <option :value="null"></option>
                                            <option v-for="member in feeWaiver.action_group" :value="member.id">{{member.first_name}} {{member.last_name}}</option>
                                        </select>
                                        <a v-if="canAssign && feeWaiver.assigned_officer != feeWaiver.current_officer.id" @click.prevent="assignRequestUser()" class="actionBtn pull-right">Assign to me</a>
                                    </template>
                                </div>
                            </div>

                            <div class="col-sm-12 top-buffer-s" v-if="!isFinalised && canProcess">
                                <div v-if="show_spinner"><i class='fa fa-5x fa-spinner fa-spin'></i></div>
                                <div v-else>
                                <template v-if="canProcessAssessor">
                                    <div class="row">
                                        <div class="col-sm-12">
                                            <strong>Action</strong><br/>
                                        </div>
                                    </div>
                                    <div class="row">
                                        <div class="col-sm-12">
                                            <button style="width:80%;" class="btn btn-primary" :disabled="allVisitsUnchecked" @click.prevent="workflowAction('propose_issue')">Propose Issue Fee Waiver</button><br/>
                                        </div>
                                    </div>
                                    <div class="row">
                                        <div class="col-sm-12">
                                            <button style="width:80%;" class="btn btn-primary top-buffer-s" :disabled="allVisitsUnchecked" @click.prevent="workflowAction('propose_concession')">Propose Issue Concession</button><br/>
                                        </div>
                                    </div>
                                    <div class="row">
                                        <div class="col-sm-12">
                                            <button style="width:80%;" class="btn btn-primary top-buffer-s" :disabled="false" @click.prevent="workflowAction('propose_decline')">Propose Decline</button><br/>
                                        </div>
                                    </div>
                                </template>
                                <template v-if="canProcessApprover">
                                    <div class="row">
                                        <div class="col-sm-12">
                                            <button style="width:80%;" class="btn btn-primary top-buffer-s" :disabled="false" @click.prevent="workflowAction('return_to_assessor')">Return to Assessor</button><br/>
                                        </div>
                                    </div>
                                    <div class="row">
                                        <div class="col-sm-12">
                                            <button style="width:80%;" class="btn btn-primary top-buffer-s" :disabled="allVisitsUnchecked" @click.prevent="finalApproval('issue')">Issue Fee Waiver</button><br/>
                                        </div>
                                    </div>
                                    <div class="row">
                                        <div class="col-sm-12">
                                            <button style="width:80%;" class="btn btn-primary top-buffer-s" :disabled="allVisitsUnchecked" @click.prevent="finalApproval('issue_concession')">Issue Concession</button><br/>
                                        </div>
                                    </div>
                                    <div class="row">
                                        <div class="col-sm-12">
                                            <button style="width:80%;" class="btn btn-primary top-buffer-s" :disabled="false" @click.prevent="finalApproval('decline')">Decline</button><br/>
                                        </div>
                                    </div>
                                </template>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <div class="col-md-1"></div>
        <div class="col-md-8">
            <div v-if="feeWaiverId" class="row">
                <FeeWaiverForm 
                :feeWaiverId="feeWaiverId"
                 ref="fee_waiver_form"
                :key="feeWaiverId"
                 :isInternal="true"
                 :canProcess="canProcess"
                 :isFinalised="isFinalised"
                 @all-visits-unchecked="updateVisits"
                />
            </div>
        </div>
        </div>
        <div v-if="workflowActionType">
            <AssessmentWorkflow ref="assessment_workflow" :feeWaiver="feeWaiver" :workflow_type="workflowActionType" :key="'workflow_action_' + workflowActionType"/>
        </div>
    </div>
</template>
<script>
import CommsLogs from '@common-utils/comms_logs.vue'
import { api_endpoints, helpers } from '@/utils/hooks'
import FeeWaiverForm from '../feewaiver_form.vue'
import Vue from 'vue'
import AssessmentWorkflow from './assessment_modal.vue'


export default {
    name: 'Assessment',
    data: function() {
        let vm = this;
        return {
            allVisitsUnchecked: true,
            feeWaiverId: null,
            feeWaiver: {},
            show_spinner: false,
            workflowActionType: '',
            detailsBody: 'detailsBody'+vm._uid,
            addressBody: 'addressBody'+vm._uid,
            contactsBody: 'contactsBody'+vm._uid,
            siteLocations: 'siteLocations'+vm._uid,
            defaultKey: "aho",
            "feeWaiver": null,
            "original_feeWaiver": null,
            "loading": [],
            selected_referral: '',
            referral_text: '',
            approver_comment: '',
            form: null,
            members: [],
            //department_users : [],
            apiaryReferralGroups: [],
            contacts_table_initialised: false,
            initialisedSelects: false,
            showingProposal:false,
            showingRequirements:false,
            hasAmendmentRequest: false,
            DATE_TIME_FORMAT: 'DD/MM/YYYY HH:mm:ss',
            comms_url: helpers.add_endpoint_json('/api/feewaivers',vm.$route.params.fee_waiver_id+'/comms_log'),
            comms_add_url: helpers.add_endpoint_json('/api/feewaivers',vm.$route.params.fee_waiver_id+'/add_comms_log'),
            logs_url: helpers.add_endpoint_json('/api/feewaivers',vm.$route.params.fee_waiver_id+'/action_log'),
            panelClickersInitialised: false,
        }
    },
    components: {
        CommsLogs,
        FeeWaiverForm,
        AssessmentWorkflow,
    },
    filters: {
        formatDate: function(data){
            return data ? moment(data).format('DD/MM/YYYY HH:mm:ss'): '';
        }
    },
    props: {
    },
    watch: {

    },
    computed: {
        assessmentTitle: function() {
            let title = 'Entry Fee Waiver Request: ' + this.feeWaiver.lodgement_number;
            if (this.feeWaiver && this.feeWaiver.proposed_status && this.feeWaiver.processing_status === "With Approver") {
                switch (this.feeWaiver.proposed_status) {
                    case "Decline":
                        title += ' (Proposed Decision: Decline)';
                        break;
                    case "Fee Waiver":
                        title += ' (Proposed Decision: Issue Fee Waiver)';
                        break;
                    case "Concession":
                        title += ' (Proposed Decision: Issue Concession)';
                        break;
                }
            }
            return title;
        },
        feeWaiver_form_url: function() {
        },
        canProcess: function() {
            let process = false;
            if (this.feeWaiver && this.feeWaiver.can_process) {
                process = true;
            }
            return process;
        },
        canAssign: function() {
            let assign = false;
            if (this.feeWaiver && this.feeWaiver.can_assign) {
                assign = true;
            }
            return assign;
        },
        canProcessAssessor: function() {
            let canProcess = false;
            if (this.feeWaiver.processing_status === 'With Assessor' && this.feeWaiver.can_process) {
                canProcess = true;
            }
            return canProcess;
        },
        canProcessApprover: function() {
            let canProcess = false;
            if (this.feeWaiver.processing_status === 'With Approver' && this.feeWaiver.can_process) {
                canProcess = true;
            }
            return canProcess;
        },
        isFinalised: function(){
            return this.feeWaiver.processing_status == 'Declined' || this.feeWaiver.processing_status == 'Issued';
        },
    },
    methods: {
        updateVisits: function(val) {
            this.allVisitsUnchecked = val;
        },
        commaToNewline(s){
            return s.replace(/[,;]/g, '\n');
        },
        finalApproval: async function(approval_type) {
          this.show_spinner = true;
          let post_url = '/api/feewaivers/' + this.feeWaiver.id + '/final_approval/'
          let payload = {"approval_type": approval_type}
          let feeWaiverRes = await this.parentSave(false)
          if (feeWaiverRes.ok) {
              try {
                  let res = await Vue.http.post(post_url, payload);
                  if (res.ok) {    
                      this.$router.push({
                          name: 'fee-waiver-dash',
                      });
                  }
              } catch(err) {
                  this.errorResponse = 'Error:' + err.statusText;
              } 
          } else {
              this.errorResponse = 'Error:' + feeWaiverRes.statusText;
          }
          this.show_spinner = false;
      },
        updateAssignedOfficerSelect:function(){
            let vm = this;
            $(vm.$refs.assigned_officer).val(vm.feeWaiver.assigned_officer_id);
            $(vm.$refs.assigned_officer).trigger('change');
        },
        /*
        assignRequestUser: function(){
            let vm = this;
            vm.$http.get(helpers.add_endpoint_json('/api/feewaivers',(vm.feeWaiver.id+'/assign_request_user')))
            .then((response) => {
                vm.feeWaiver = response.body;
                //vm.updateAssignedOfficerSelect();
            }, (error) => {
                //vm.updateAssignedOfficerSelect();
                swal(
                    'Proposal Error',
                    helpers.apiVueResourceError(error),
                    'error'
                )
            });
        },
        */
        assignRequestUser: async function(){
            await this.$nextTick();
            const res = await this.$http.get(helpers.add_endpoint_json('/api/feewaivers',(this.feeWaiver.id+'/assign_request_user')))
            this.feeWaiver = res.body;
            await this.$nextTick();
            this.updateAssignedOfficerSelect();
        },
        assignTo: async function() {
            await this.$nextTick();
            const data = {'assigned_officer_id': this.feeWaiver.assigned_officer_id};
            const res = await this.$http.post(helpers.add_endpoint_json('/api/feewaivers',(this.feeWaiver.id+'/assign_to')),data);
            this.feeWaiver = res.body;
            await this.$nextTick();
            this.updateAssignedOfficerSelect();
        },
        unAssign: async function() {
            await this.$nextTick();
            const res = await this.$http.get(helpers.add_endpoint_json('/api/feewaivers',(this.feeWaiver.id+'/unassign')))
            this.feeWaiver = res.body;
            await this.$nextTick();
            this.updateAssignedOfficerSelect();
        },
        /*
        assignTo: function(){
            let vm = this;
            let unassign = true;
            let data = {};
            unassign = vm.feeWaiver.assigned_officer != null ? false: true;
            data = {'assigned_officer_id': vm.feeWaiver.assigned_officer};
            if (!unassign){
                vm.$http.post(helpers.add_endpoint_json('/api/feewaivers',(vm.feeWaiver.id+'/assign_to')),JSON.stringify(data),{
                    emulateJSON:true
                }).then((response) => {
                    vm.feeWaiver = response.body;
                    //vm.updateAssignedOfficerSelect();
                }, (error) => {
                    //vm.updateAssignedOfficerSelect();
                    swal(
                        'Proposal Error',
                        helpers.apiVueResourceError(error),
                        'error'
                    )
                });
            }
            else{
                vm.$http.get(helpers.add_endpoint_json('/api/feewaivers',(vm.feeWaiver.id+'/unassign')))
                .then((response) => {
                    vm.feeWaiver = response.body;
                    //vm.updateAssignedOfficerSelect();
                }, (error) => {
                    //vm.updateAssignedOfficerSelect();
                    swal(
                        'Proposal Error',
                        helpers.apiVueResourceError(error),
                        'error'
                    )
                });
            }
        },
        */
        parentSave: async function() {
            const feeWaiverRes = await this.$refs.fee_waiver_form.save(false);
            return feeWaiverRes;
        },
        workflowAction: function(action) {
            this.workflowActionType = action;
            this.$nextTick(() => {
                this.$refs.assessment_workflow.isModalOpen = true;
            });
        },

        initialiseAssignedOfficerSelect:function(reinit=false){
            let vm = this;
            if (reinit){
                $(vm.$refs.assigned_officer).data('select2') ? $(vm.$refs.assigned_officer).select2('destroy'): '';
            }
            // Assigned officer select
            $(vm.$refs.assigned_officer).select2({
                "theme": "bootstrap",
                allowClear: true,
                placeholder:"Select Officer"
            }).
            on("select2:select", async function (e) {
                var selected = $(e.currentTarget);
                vm.feeWaiver.assigned_officer_id = selected.val();
                //await vm.$nextTick();
                await vm.assignTo();
                /*
            }).on("select2:unselecting", function(e) {
                var self = $(this);
                setTimeout(() => {
                    self.select2('close');
                }, 0);
                */
            }).on("select2:unselect", async function (e) {
                var selected = $(e.currentTarget);
                vm.feeWaiver.assigned_officer_id = null;
                //await vm.$nextTick();
                await vm.unAssign();
            });
            //});
        },


    },
    created: async function() {
        await this.$nextTick();
        const res = await Vue.http.get(`/api/feewaivers/${this.feeWaiverId}.json`)
        this.feeWaiver = res.body;
        await this.$nextTick();
        this.initialiseAssignedOfficerSelect()
    },
    /*
    updated: function(){
        this.$nextTick(() => {
            this.initialiseAssignedOfficerSelect()
        });
    },
    mounted: async function() {
        await this.$nextTick();
        //this.$nextTick(() => {
        //this.initialiseAssignedOfficerSelect()
        //this.updateAssignedOfficerSelect()
        //});
    },
    */
    beforeRouteEnter: function(to, from, next) {
        next(vm => {
            vm.feeWaiverId = to.params.fee_waiver_id;
        })
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
.hidePopover {
    display: none;
}
.separator {
    border: 1px solid;
    margin-top: 15px;
    margin-bottom: 10px;
    width: 100%;
}
</style>
