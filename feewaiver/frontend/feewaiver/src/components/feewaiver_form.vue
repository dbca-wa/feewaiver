<template lang="html">
    <div v-if="showFormSpinner">
        <i class='fa fa-5x fa-spinner fa-spin'></i>
    </div>
    <div v-else :class="containingClass">
        <form id="feewaiver-form" @submit.prevent="submit">
            <div v-if="!isInternal" class="card border headerbox mb-3">
                <strong>
                    <p>Welcome to the entry fee waiver request form. Entry fee waivers may be provided to certain groups undertaking organised outings in <a href='https://parks.dpaw.wa.gov.au/know/park-entry-fees' target='_blank'>parks with entry fees</a> managed by the Department of Biodiversity Conservation and Attractions (DBCA).</p>
                    <p>Please fill out the details in the form below and submit to the Department. You will be notified of the outcome of your request by email. You may also apply for a camping fee waiver by selecting yes to camping during your visit. If the park you are camping at does not have park entry fees, it can be selected once you have selected yes to camping. Any applicable camping fee reduction or waiver will be applied by the department when processing your request.</p>
                    <p>You can add multiple visits to the same fee waiver request by clicking add another visit prior to submitting.</p>
                </strong>
            </div>
            <FormSection :formCollapse="false" label="Contact Details" Index="contact_details" :noChevron="!isInternal" :customClass="'mb-3'">
                <div class="row mb-2">
                    <label for="organisation" class="col-sm-2 col-form-label">Organisation</label>
                    <div class="col-sm-4">
                        <input :disabled="readonly" required type="text" class="form-control" id="organisation" name="organisation" placeholder="" v-model="contactDetails.organisation">
                    </div>
                    <label for="contact_name" class="col-sm-2 col-form-label">Contact Name</label>
                    <div class="col-sm-4">
                        <input :disabled="readonly" required type="text" class="form-control" id="contact_name" name="contact_name" placeholder="" v-model="contactDetails.contact_name">
                    </div>
                </div>

                <div class="row mb-2">
                    <label for="postal_address" class="col-sm-2 col-form-label">Postal Address</label>
                    <div class="col-sm-4">
                        <input :disabled="readonly" required type="text" class="form-control" id="postal_address" name="postal_address" placeholder="" v-model="contactDetails.postal_address">
                    </div>
                </div>

                <div class="row mb-2">
                    <label for="suburb" class="col-sm-2 col-form-label">Suburb</label>
                    <div class="col-sm-4">
                        <input :disabled="readonly" required type="text" class="form-control" id="suburb" name="suburb" placeholder="" v-model="contactDetails.suburb">
                    </div>
                    <label for="state" class="col-sm-1 col-form-label">State</label>
                    <div class="col-sm-2">
                        <input :disabled="readonly" required type="text" class="form-control" id="state" name="state" placeholder="" v-model="contactDetails.state">
                    </div>
                    <label for="postcode" class="col-sm-1 col-form-label">Postcode</label>
                    <div class="col-sm-2">
                        <input :disabled="readonly" required type="text" class="form-control" id="postcode" name="postcode" placeholder="" v-model="contactDetails.postcode">
                    </div>
                </div>

                <div class="row mb-2">
                    <label for="phone" class="col-sm-2 col-form-label">Phone</label>
                    <div class="col-sm-4">
                        <input :disabled="readonly" required type="text" class="form-control" id="phone" name="phone" placeholder="" v-model="contactDetails.phone">
                    </div>
                </div>

                <div class="row mb-2">
                    <label for="contact_details_email" class="col-sm-2 col-form-label">Email</label>
                    <div class="col-sm-4">
                        <input :disabled="readonly" required type="email" class="form-control" name="email" placeholder="" v-model="contactDetails.email" id="contact_details_email">
                        <span class="error" aria-live="polite"></span>
                    </div>
                    <label for="email_confirmation" class="col-sm-2 col-form-label">Confirm Email</label>
                    <div class="col-sm-4">
                        <input :disabled="readonly" required type="email" class="form-control" name="email_confirmation" placeholder="" v-model="contactDetails.email_confirmation" id="email_confirmation">
                    </div>
                </div>

                <div class="row mb-2">
                    <label for="contact_details_cc_email" class="col-sm-2 col-form-label">CC Email (if applicable)</label>
                    <div class="col-sm-4">
                        <input :disabled="readonly" type="email" class="form-control" name="email" placeholder="" v-model="contactDetails.cc_email" id="contact_details_cc_email">
                        <span class="error" aria-live="polite"></span>
                    </div>
                </div>

                <div class="row mb-2">
                    <label for="participants" class="col-sm-4 col-form-label">Participants</label>
                    <div class="col-sm-6">
                        <select :disabled="readonly" required id="participants" ref="participants" class="form-select" v-model="contactDetails.participants_id">
                            <option value=""></option>
                            <option v-for="group in participantGroupList" :key="group.id" :value="group.id">{{group.name}}</option>
                        </select>
                    </div>
                </div>

                <div class="row mb-2">
                    <label class="col-sm-4 col-form-label">Provide a brief explanation of your organisation</label>
                    <div class="col-sm-8">
                        <textarea :disabled="readonly" required class="form-control" v-model="contactDetails.organisation_description"/>
                    </div>
                </div>

                <div class="row">
                    <label class="col-sm-4 col-form-label">Attach any other documentation you want to provide</label>
                    <div class="col-sm-8">
                        <FileField
                            class="input_file_wrapper"
                            ref="contact_details_documents"
                            name="contact-details-documents"
                            :isRepeatable="true"
                            :documentActionUrl="documentActionUrl"
                            :replace_button_by_text="true"
                            @update-temp-doc-coll-id="updateTempDocCollId"
                            :key="documentActionUrl"
                            :readonly="readonly"
                        />
                    </div>
                </div>
            </FormSection>

            <div v-for="visit in visits" >
                <VisitSection 
                    :key="'visit' + visit.index + '_' + uuid"
                    :formCollapse="false" 
                    :label="'Visit ' + (visit.index + 1)"
                    :Index="'index_' + visit.index"
                    :ref="'visit_' + visit.index"
                    :id="'visit_' + visit.index"
                    :visit="visit"
                    :participantGroupList="participantGroupList"
                    :parksList="parksList"
                    :campingChoices="campingChoices"
                    :feeWaiverId="feeWaiverId"
                    :canProcess="canProcess"
                    :isInternal="isInternal"
                    :readonly="readonly"
                    @recalc-visits-flag="recalcVisitsFlag"
                />
            </div>

            <div v-if="isInternal">
                <FormSection :formCollapse="false" label="Comments to applicant" :Index="'comments_to_applicant' + feeWaiverId">
                    <div class="form-group">
                        <div class="row">
                        <label class="col-sm-4 col-form-label">Comments</label>
                        <div class="col-sm-8">
                            <textarea :disabled="readonly" class="form-control" v-model="feeWaiver.comments_to_applicant"/>
                        </div>
                        </div>
                    </div>
                </FormSection>
            </div>

            <div>
                <input type="hidden" name="csrfmiddlewaretoken" :value="csrf_token"/>
                <div class="row mb-5">
                    <div v-if="feeWaiverId && canProcess" class="fixed-bottom bg-light py-2">
                            <div class="container">
                            <p class="d-flex justify-content-end">
                                <button class="btn btn-primary float-end" style="margin-top:5px;" @click.prevent="save()">Save Changes</button>
                            </p>
                            </div>
                    </div>
                    <div v-else-if="!feeWaiverId" class="fixed-bottom bg-light py-2">
                        <div class="container">
                            <p class="d-flex justify-content-end gap-2">
                                <input type="button" @click.prevent="addVisit" class="btn btn-primary" value="Add another visit"/>
                                <button :title="submitDisabledText" :disabled="submitDisabled" class="btn btn-primary" type="submit">Submit</button>
                            </p>
                        </div>
                    </div>
                </div>

            </div>
        </form>
    </div>
</template>

<script>
    import { api_endpoints, helpers }from '@/utils/hooks'
    import FormSection from "@/components/forms/section_toggle.vue"
    import 'bootstrap/dist/css/bootstrap.css';
    import 'bootstrap/dist/js/bootstrap.bundle.min.js';
    import 'eonasdan-bootstrap-datetimepicker';
    import VisitSection from "./feewaiver_visit.vue"
    import FileField from '@/components/forms/filefield_immediate.vue'
    import Swal from 'sweetalert2';
    import axios from 'axios';

    export default {
        name: 'FeeWaiverForm',
        props:{
            feeWaiverId:{
                type: String,
                //required: true,
            },
            isFinalised:{
                type: Boolean,
                //required: true,
            },
            isInternal: {
                type: Boolean,
                default: false,
            },
            canProcess:{
                type: Boolean,
                default: false,
            },
        },
        data:function () {
            let vm = this;
            return {
                submitDisabled: true,
                submitDisabledText: '',
                feeWaiver: {},
                uuid: 0,
                showFormSpinner: false,
                payload: {},
                contactDetails: {},
                participantGroupList: [],
                temporary_document_collection_id: null,
                parksList: [],
                //campGroundsList: [],
                campingChoices: [],
                //visitIdx: 0,
                visits: [
                    {
                        index: 0,
                        selected_park_ids: [],
                        selected_free_park_ids: [],
                        //selected_campground_ids: [],
                        age_of_participants_array: [],
                        camping_requested: false,
                    },
                ],
            }
        },
        components: {
            FormSection,
            VisitSection,
            FileField,
        },
        watch: {
            visits: {
                handler: async function() {
                    await this.checkValidVisit();
                },
                deep: true
            },
        },
        computed: {
            readonly: function() {
                if (this.isFinalised) {
                    return true
                } else if (this.isInternal) {
                    return !this.canProcess;
                } else {
                    return false;
                }
            },
            csrf_token: function() {
              return helpers.getCookie('csrftoken')
            },
            containingClass: function() {
                let cclass = 'container';
                if (this.feeWaiverId) {
                    //cclass = 'col-sm-12';
                    cclass = '';
                }
                return cclass;
            },
            documentActionUrl: function() {
                let url = '';
                if (this.contactDetails && this.contactDetails.id) {
                    url = helpers.add_endpoint_join(
                        '/api/feewaivers/',
                        //this.contactDetails.id + '/process_contact_details_document/'
                        this.feeWaiver.id + '/process_contact_details_document/'
                    )
                } else if (!this.feeWaiverId) {
                    // internal view
                    url = 'temporary_document';
                }
                return url;
            },

        },
        methods:{
            checkValidVisit: async function() {
                await this.$nextTick();
                this.submitDisabled = false;
                this.submitDisabledText = '';
                for (let visit of this.visits) {
                    if (!visit.selected_park_ids.length && !visit.selected_free_park_ids.length) {
                        this.submitDisabled = true;
                        this.submitDisabledText = 'You must select at least one park per visit';
                    }
                }
            },
            recalcVisitsFlag: async function() {
                let allVisitsUnchecked = true;
                await this.$nextTick();
                this.allVisitsUnchecked = true;
                for (let visit of this.visits) {
                    if (visit.issued) {
                        allVisitsUnchecked = false;
                    }
                }
                this.$emit('all-visits-unchecked', allVisitsUnchecked);
            },
            updateTempDocCollId: function(id) {
                this.temporary_document_collection_id = id.temp_doc_id;
            },
            addVisit: async function () {
                await this.$nextTick();
                let lastVisitPosition = this.visits.length;
                let visit = {
                    //index: ++this.visitIdx,
                    index: lastVisitPosition,
                    selected_park_ids: [],
                    selected_free_park_ids: [],
                    //selected_campground_ids: [],
                    age_of_participants_array: [],
                    camping_requested: false,
                }

                this.visits.push(visit);
                // focus on new Visit section
                await this.$nextTick();
                let visitRefDescriptionLabel = 'visit_description_' + visit.index;
                let visitDescriptionRef = document.getElementById(visitRefDescriptionLabel);
                visitDescriptionRef.focus();
            },

            addEventListeners: function() {
                let vm = this;
                const contactDetailsEmail = document.getElementById('contact_details_email');
                const emailConfirmation = document.getElementById('email_confirmation');
                const emailError = document.querySelector('#contact_details_email + span.error');
                contactDetailsEmail.addEventListener('input', function(evt) {
                    if (contactDetailsEmail.validity.valid) {
                        emailError.textContent = '';
                        emailError.className = 'error';
                    } else {
                        showEmailError();
                    }
                });
                contactDetailsEmail.onpaste = e => {
                    e.preventDefault();
                    return false;
                };
                emailConfirmation.onpaste = e => {
                    e.preventDefault();
                    return false;
                };
                contactDetailsEmail.onblur = e => {
                    showEmailError();
                };
                emailConfirmation.onblur = e => {
                    showEmailError();
                };
                const form = document.getElementsByTagName('form')[0]
                form.addEventListener('submit', function(evt) {
                    if (!contactDetailsEmail.validity.valid) {
                        showEmailError();
                        evt.preventDefault();
                    }
                });
                function showEmailError() {
                    emailError.className = 'error';
                    emailError.textContent = '';
                    let errorFound = false;
                    if (contactDetailsEmail.validity.valueMissing || !vm.contactDetails.email) {
                        emailError.textContent = 'You need to enter an email address';
                        errorFound = true;
                    } else if (contactDetailsEmail.validity.typeMismatch) {
                        emailError.textContent = 'Entered value needs to be an email address';
                        errorFound = true;
                    } else if (vm.contactDetails.email && vm.contactDetails.email_confirmation && vm.contactDetails.email !== vm.contactDetails.email_confirmation) {
                        emailError.textContent = 'Email addresses are not identical';
                        errorFound = true;
                    }

                    if (errorFound) {
                        emailError.className = 'error active';
                    }
                }

            },
            submit: async function(){
                let visitRef = null;
                let ageOfParticipants = null;
                for (let visit of this.visits) {
                    if (visit && visit.age_of_participants_array && visit.age_of_participants_array.length < 1) {
                        const visitIdxRef = 'visit_' + visit.index;
                        const ageOfParticipantsIdx = 'age_of_participants_' + visit.index
                        visitRef = this.$refs[visitIdxRef];
                        ageOfParticipants = visitRef[0].$refs[ageOfParticipantsIdx];
                    }
                }
                const contactDetailsEmail = document.getElementById('contact_details_email');
                if (!contactDetailsEmail.validity.valid || this.contactDetails.email !== this.contactDetails.email_confirmation) {
                    contactDetailsEmail.focus();
                } else if (ageOfParticipants) {
                    ageOfParticipants.focus();
                } else {
                    let swalTitle = "Submit Request";
                    let swalText = "Are you sure you want to submit this request?";
                    await this.updatePayload();
                    await Swal.fire({
                        title: swalTitle,
                        text: swalText,
                        icon: "question",
                        showCancelButton: true,
                        confirmButtonText: 'Submit'
                    });
                    try {
                        const returnedFeeWaiver = await this.$http.post(api_endpoints.feewaivers,this.payload);
                        
                        this.$router.push({
                            name: 'submit_feewaiver',
                            // params: { fee_waiver: returnedFeeWaiver.data}
                            state: { fee_waiver: returnedFeeWaiver.data }
                        });
                    } catch (error) {
                        let swalTitle = "Error";
                        let swalText = error.data[0];
                        if (error.data[0].slice(0,1) === '"{') {
                            // remove the {} from the data string with slice
                            swalText = error.data[0].slice(1,-1);
                        }
                        await Swal.fire({
                            title: swalTitle,
                            text: swalText,
                            icon: "error",
                            //showCancelButton: true,
                            confirmButtonText: 'Ok'
                        });
                    }

                }
            },
            removeVisit: function(visitIdx) {
                // remove visit
                let i = 0;
                for (let visit of this.visits) {
                    if (visit.index === visitIdx) {
                        this.visits.splice(i, 1);
                    }
                    i++
                }
                // reindex
                let ii = 0;
                for (let visit of this.visits) {
                    visit.index = ii;
                    ii++
                }
                // force load of visit child components
                ++this.uuid;
            },
            updatePayload: async function() {
                await this.$nextTick();
                this.payload = {};
                this.payload = {
                    'contact_details': Object.assign({}, this.contactDetails),
                    'fee_waiver': Object.assign({}, this.feeWaiver),
                    'visits': [],
                    'temporary_document_collection_id': this.temporary_document_collection_id,
                }
                for (let visitData of this.visits) {
                    let visit = Object.assign({}, visitData);
                    // convert date strings
                    if (visit.date_from) {
                        visit.date_from = moment(visit.date_from, 'DD/MM/YYYY').format('YYYY-MM-DD');
                    }
                    if (visit.date_to) {
                        visit.date_to = moment(visit.date_to, 'DD/MM/YYYY').format('YYYY-MM-DD');
                    }
                    // add to payload
                    this.payload.visits.push(visit)
                }
                //});
            },
            save: async function(confirmSave=true) {
                await this.updatePayload()
                let url = `/api/feewaivers/${this.feeWaiverId}/assessor_save/`;
                const feeWaiverRes = await axios.post(url, this.payload);

                console.log({confirmSave})
                console.log({feeWaiverRes})

                if (confirmSave) {
                    Swal.fire(
                        'Saved',
                        'Fee Waiver has been saved',
                        'success'
                    );
                }
                return feeWaiverRes
            },
            fetchAdminData: async function() {
                this.participantGroupList = [];
                const response = await this.$http.get(api_endpoints.admin_data);

                for (let group of response.data.participants_list) {
                    this.participantGroupList.push(group)
                }
                for (let group of response.data.parks_list) {
                    this.parksList.push(group)
                }
                for (let choice of response.data.camping_choices) {
                    this.campingChoices.push(choice)
                }
            },
            loadFeeWaiverData: async function() {
                const url = api_endpoints.feewaivers + this.feeWaiverId + '/feewaiver_contactdetails_pack/';

                const returnVal = await this.$http.get(url);
                this.feeWaiver.id = returnVal.data.fee_waiver.id;
                this.feeWaiver.lodgement_number = returnVal.data.fee_waiver.lodgement_number;
                this.feeWaiver.fee_waiver_purpose = returnVal.data.fee_waiver.fee_waiver_purpose;
                this.feeWaiver.comments_to_applicant = returnVal.data.fee_waiver.comments_to_applicant;
                this.feeWaiver.assigned_officer = returnVal.data.fee_waiver.assigned_officer;
                this.feeWaiver.assigned_officer_id = returnVal.data.fee_waiver.assigned_officer_id;
                this.feeWaiver.can_process = returnVal.data.fee_waiver.can_process;
                // visits should be empty if reading from backend
                this.visits = []
                //this.visitIdx = -1;
                for (let retrievedVisit of returnVal.data.fee_waiver.visits) {
                    let visit = Object.assign({}, retrievedVisit);
                    // we are now saving the index to db
                    visit.date_to = moment(visit.date_to, 'YYYY-MM-DD').format('DD/MM/YYYY');
                    visit.date_from = moment(visit.date_from, 'YYYY-MM-DD').format('DD/MM/YYYY');
                    visit.number_of_vehicles = visit.number_of_vehicles.toString()
                    this.visits.push(visit);
                }
                // sort array
                this.visits.sort(function(a, b) {
                    return a.index - b.index
                });
                this.contactDetails = Object.assign({}, returnVal.data.contact_details);
                // TODO: try to improve this
                if (this.contactDetails.participants_code) {
                    this.contactDetails.participants_id = this.contactDetails.participants_code;
                }
            },

        },
        mounted: function() {
        },
        created: async function() {
            if (this.isInternal) {
                this.showFormSpinner = true;
                await this.loadFeeWaiverData();
                await this.recalcVisitsFlag();
                this.showFormSpinner = false;
            }
            await this.fetchAdminData();
            await this.$nextTick();
            await this.checkValidVisit();
            this.addEventListeners();
            ++this.uuid;
        },
    }
</script>

<style lang="css">
    .input_file_wrapper {
        margin: 1.5em 0 0 0;
    }
    .headerbox {
        padding: 50px;
    }
    .section{
        text-transform: capitalize;
    }
    .list-group{
        margin-bottom: 0;
    }
    .fixed-top{
        position: fixed;
        top:56px;
    }
    .insurance-items {
        padding-inline-start: 1em;
    }
    .my-container {
        display: flex;
        flex-direction: row;
        align-items: center;
    }
    .grow1 {
        flex-grow: 1;
    }
    .grow2 {
        flex-grow: 2;
    }
    .input-file-wrapper {
        margin: 1.5em 0 0 0;
    }
    .error {
        color: red;
    }
</style>

