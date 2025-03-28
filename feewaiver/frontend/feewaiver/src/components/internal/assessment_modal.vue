<template lang="html">
    <div id="AssessmentWorkflow">
        <modal transition="modal fade" @ok="ok()" @cancel="cancel()" :title="modalTitle" large force>
          <div class="container-fluid">
            <div class="row">
                <div class="col-sm-12">
                        <div class="form-group">
                          <div class="row">
                              <div class="col-sm-3">
                                  <label class="form-label pull-left" for="details">Details</label>
                              </div>
            			      <div class="col-sm-6">
                                  <textarea class="form-control" placeholder="add details" id="details" v-model="workflowDetails"/>
                              </div>
                          </div>
                        </div>
                        <div class="form-group">
                            <div class="row">
                                <div class="col-sm-3">
                                    <label class="form-label pull-left"  for="Name">Attachments</label>
                                </div>
            			        <div class="col-sm-9">
                                    <FileField ref="comms_log_file" name="comms-log-file" :isRepeatable="true" :documentActionUrl="documentActionUrl"  />
                                </div>
                            </div>
                        </div>

                </div>
              
            </div>
          </div>
            <div slot="footer">
                <div v-if="errorResponse" class="form-group">
                    <div class="row">
                        <div class="col-sm-12">
                            <strong>
                                <span style="white-space: pre;">{{ errorResponse }}</span>
                            </strong>
                        </div>
                    </div>
                </div>
                <div v-if="processingWorkflow">
                    <button type="button" disabled class="btn btn-default" @click="ok"><i class="fa fa-spinner fa-spin"></i> Processing</button>
                </div>
                <div v-else>
                    <button type="button" class="btn btn-default" @click="ok" >Ok</button>
                    <button type="button" class="btn btn-default" @click="cancel">Cancel</button>
                </div>
            </div>
        </modal>
    </div>
</template>
<script>
import Vue from "vue";
import modal from '@vue-utils/bootstrap-modal.vue';
import { api_endpoints, helpers, cache_helper } from "@/utils/hooks";
require("select2/dist/css/select2.min.css");
require("select2-bootstrap-theme/dist/select2-bootstrap.min.css");
import FileField from '@/components/forms/filefield_immediate.vue'

export default {
    name: "AssessmentWorkflow",
    data: function() {
      return {
            isModalOpen: false,
            workflowDetails: "",
            errorResponse: "",
            modalTitle: "",
            processingWorkflow: false,
      }
    },
    components: {
      modal,
      FileField,
    },
    props:{
          workflow_type: {
              type: String,
              default: '',
          },
          feeWaiver: {
              type: Object,
              required: true,
          },
      },
    computed: {
        documentActionUrl: function() {
            return `/api/feewaivers/${this.feeWaiver.id}/process_comms_log_document/`;
        },
    },
    filters: {
      formatDate: function(data) {
          return data ? moment(data).format("DD/MM/YYYY HH:mm:ss") : "";
      }
    },
    methods: {
      setModalTitle: function() {
          if (this.workflow_type === 'propose_issue') {
              this.modalTitle = 'Propose Issue';
          } else if (this.workflow_type === 'propose_concession') {
              this.modalTitle = 'Propose Concession';
          } else if (this.workflow_type === 'propose_decline') {
              this.modalTitle = 'Propose Decline';
          } else if (this.workflow_type === 'issue') {
              this.modalTitle = 'Issue';
          } else if (this.workflow_type === 'issue_concession') {
              this.modalTitle = 'Issue Concession';
          } else if (this.workflow_type === 'decline') {
              this.modalTitle = 'Decline';
          } else if (this.workflow_type === 'return_to_assessor') {
              this.modalTitle = 'Return to Assessor';
          }
      },
      cancel: async function() {
          await this.$refs.comms_log_file.cancel();
          this.close();
      },
      close: function () {
          this.$parent.workflowActionType = '';
          this.isModalOpen = false;
      },
      ok: async function(){        
          this.processingWorkflow = true;
          let post_url = '/api/feewaivers/' + this.feeWaiver.id + '/workflow_action/'
          let payload = new FormData(this.form);
          
          this.workflowDetails ? payload.append('comments', this.workflowDetails) : null;
          this.$refs.comms_log_file.commsLogId ? payload.append('comms_log_id', this.$refs.comms_log_file.commsLogId) : null;
          this.workflow_type ? payload.append('workflow_type', this.workflow_type) : null;
          this.modalTitle ? payload.append('email_subject', this.modalTitle) : null;
          let feeWaiverRes = await this.$parent.parentSave(false)
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
          this.processingWorkflow = false;
      },
    },
    created: async function() {
    },
    mounted: function() {
        this.$nextTick(() => {
            this.setModalTitle();
        });
    }
};
</script>

<style lang="css">
.top-buffer{margin-top: 5px;}
.top-buffer-2x{margin-top: 10px;}
</style>
