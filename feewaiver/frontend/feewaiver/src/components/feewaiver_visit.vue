<template lang="html">
    <FormSection :formCollapse="false" :label="label" :Index="'index_' + visit.index" :noChevron="!isInternal" :customClass="'mb-3'">
        <div class="row">
            <button v-if="visit.index > 0 && !isInternal" class="btn btn-primary float-end" style="margin-top:5px;" @click.prevent="removeVisit()">Remove Visit</button>
        </div>

        <div class="row mb-2">
            <label for="visit_description" class="col-sm-4 col-form-label" >Provide the details and purpose of your visit</label>
            <div class="col-sm-8">
                <textarea 
                    :disabled="readonly" 
                    required 
                    class="form-control" 
                    name="visit_description" 
                    v-model="visit.description"
                    :id="'visit_description_' + visit.index"
                />
            </div>
        </div>

        <div class="row mb-2">
            <label for="parks" class="col-sm-4 col-form-label">Park/s with entry fees you intend to visit</label>
            <div :id="'parks_parent_' + visit.index" class="col-sm-6 parkclass">
                <select :disabled="readonly" :id="'parks_' + visit.index" class="form-select" multiple="multiple">
                    <option v-for="park in paidParks" :key="park.id" :value="park.id">{{park.name}}</option>
                </select>
            </div>
        </div>

        <div class="row mb-2">
            <label class="col-sm-4 col-form-label">Are you intending to camp during your visit?</label>
            <div class="col-sm-8 d-flex align-items-center">
                <div class="form-check form-check-inline mb-0">
                    <input 
                        :disabled="readonly" 
                        class="form-check-input" 
                        :id="'yes_' + visit.index" 
                        type="radio" 
                        v-model="visit.camping_requested" 
                        :value="true"
                    >
                    <label class="form-check-label" :for="'yes_' + visit.index">Yes</label>
                </div>
                <div class="form-check form-check-inline mb-0">
                    <input 
                        :disabled="readonly" 
                        class="form-check-input" 
                        :id="'no_' + visit.index" 
                        type="radio" 
                        v-model="visit.camping_requested" 
                        :value="false"
                    >
                    <label class="form-check-label" :for="'no_' + visit.index">No</label>
                </div>
            </div>
        </div>

        <div v-if="visit.camping_requested" class="col-sm-10">
            <div v-if="isInternal" :key="feeWaiverId" class="form-group mb-3">
                <div class="row">
                    <label for="camping_assessment" class="col-sm-4 col-form-label">Applicable camping waiver</label>
                        <div class="col-sm-8">
                            <select :disabled="!canProcess" class="form-select" id="camping_assessment" v-model="visit.camping_assessment">
                                <option v-for="choice in campingChoices" :key="Object.keys(choice)[0]" :value="Object.keys(choice)[0]">{{Object.values(choice)[0]}}</option>
                            </select>
                        </div>
                </div>
            </div>
            <div class="form-group mb-3">
                <div class="row">
                    <label for="free_parks" class="col-sm-4 col-form-label">Are there other parks not listed above you intend to camp at?</label>
                    <div class="col-sm-6 campgroundclass">
                        <select :disabled="readonly" :id="'free_parks_' + visit.index" class="form-select" multiple="multiple">
                        </select>
                    </div>
                </div>
            </div>
        </div>
        <div class="row mb-2">
            <label class="col-sm-4 col-form-label">Date from</label>
            <div class="col-sm-3">
                <div class="input-group date" >
                    <input 
                        :disabled="readonly" 
                        required 
                        type="date" 
                        class="form-control" 
                        placeholder="DD/MM/YYYY" 
                        v-model="visit.date_from" 
                        :id="'dateFromPicker_' + visit.index"
                        :max="visit.date_to"
                    />
                </div>
            </div>
        </div>

        <div class="row mb-2">
            <label class="col-sm-4 col-form-label">Date to</label>
            <div class="col-sm-3">
                <div class="input-group date" >
                    <input 
                        :disabled="readonly" 
                        required 
                        type="date" 
                        class="form-control" 
                        placeholder="DD/MM/YYYY" 
                        v-model="visit.date_to" 
                        :id="'dateToPicker_' + visit.index"
                        :min="visit.date_from"
                    />
                </div>
            </div>
        </div>

        <div class="row mb-2">
            <label for="number_of_vehicles" class="col-sm-4 col-form-label">Number of vehicles used for visit</label>
            <div class="col-sm-1">
                <input :disabled="readonly" required type="number" class="form-control" name="number_of_vehicles" min="0" step="1" v-model="visit.number_of_vehicles">
            </div>
        </div>

        <div class="row mb-2">
            <label for="number_of_participants" class="col-sm-4 col-form-label">Number of participants</label>
            <div class="col-sm-1">
                <input :disabled="readonly" required type="number" class="form-control" name="number_of_participants" min="0" step="1" v-model="visit.number_of_participants">
            </div>
        </div>

        <div class="row">
            <label class="col-sm-4 col-form-label">Age of participants</label>
            <div class="col-sm-8">
                <div class="d-flex flex-wrap justify-content-between">
                    <div class="form-check">
                        <input 
                            :ref="'age_of_participants_' + visit.index" 
                            :disabled="readonly" 
                            class="form-check-input" 
                            type="checkbox" 
                            :id="'15_' + visit.index" 
                            value="15" 
                            v-model="visit.age_of_participants_array"
                        >
                        <label class="form-check-label" :for="'15_' + visit.index">Under 15 yrs</label>
                    </div>
                    <div class="form-check">
                        <input 
                            :disabled="readonly" 
                            class="form-check-input" 
                            type="checkbox" 
                            :id="'24_' + visit.index" 
                            value="24" 
                            v-model="visit.age_of_participants_array"
                        >
                        <label class="form-check-label" :for="'24_' + visit.index">15-24 yrs</label>
                    </div>
                    <div class="form-check">
                        <input 
                            :disabled="readonly" 
                            class="form-check-input" 
                            type="checkbox" 
                            :id="'25_' + visit.index" 
                            value="25" 
                            v-model="visit.age_of_participants_array"
                        >
                        <label class="form-check-label" :for="'25_' + visit.index">25-39 yrs</label>
                    </div>
                    <div class="form-check">
                        <input 
                            :disabled="readonly" 
                            class="form-check-input" 
                            type="checkbox" 
                            :id="'40_' + visit.index" 
                            value="40" 
                            v-model="visit.age_of_participants_array"
                        >
                        <label class="form-check-label" :for="'40_' + visit.index">40-59 yrs</label>
                    </div>
                    <div class="form-check">
                        <input 
                            :disabled="readonly" 
                            class="form-check-input" 
                            type="checkbox" 
                            :id="'60_' + visit.index" 
                            value="60" 
                            v-model="visit.age_of_participants_array"
                        >
                        <label class="form-check-label" :for="'60_' + visit.index">60 yrs and over</label>
                    </div>
                </div>
                <div v-if="ageOfParticipantsErrorText" class="text-danger mt-2">
                    <span aria-live="polite">{{ ageOfParticipantsErrorText }}</span>
                </div>
            </div>
        </div>

        <div v-if="isInternal" class="float-end">
            <label>Issue?</label>
            <input :disabled="readonly" type="checkbox" :id="'visit_issue_' + visit.index" :value="true" v-model="visit.issued" @change.prevent="recalcVisits">
        </div>
    </FormSection>
</template>

<script>
    import FormSection from "@/components/forms/section_toggle.vue"
    import 'bootstrap/dist/css/bootstrap.css'
    import "select2/dist/css/select2.min.css"
    // import "select2-bootstrap-theme/dist/select2-bootstrap.min.css"
    import '@popperjs/core/dist/umd/popper.min.js'
    // import '@eonasdan/tempus-dominus/dist/js/tempus-dominus.min.js'
    // import '@eonasdan/tempus-dominus/dist/css/tempus-dominus.min.css'

    export default {
        name: 'FeeWaiverVisit',
        props:{
            isInternal: {
                type: Boolean,
                default: false,
            },
            readonly: {
                type: Boolean,
                default: true,
            },
            visit:{
                type: Object,
                required:true
            },
            participantGroupList: {
                type: Array,
                required:true,
            },
            parksList: {
                type: Array,
                required:true,
            },
            /*
            campGroundsList: {
                type: Array,
                required:true,
            },
            */
            campingChoices: {
                type: Array,
                required:true,
            },
            feeWaiverId:{
                type: String,
                //required: true,
            },
            canProcess:{
                type: Boolean,
                default: false,
            },
            Index: String,
            label: String,
        },
        data:function () {
            let vm = this;
            return {
                //selectableCampGrounds: [],
                datepickerOptions:{
                    format: 'DD/MM/YYYY',
                    showClear:true,
                    useCurrent:false,
                    keepInvalid:true,
                    allowInputToggle:true
                },

            }
        },
        components: {
            FormSection,
        },
        computed: {
            ageOfParticipantsErrorText: function() {
                let errorText = "Please select at least one participant age group";
                if (this.visit && this.visit.age_of_participants_array && this.visit.age_of_participants_array.length > 0) {
                    errorText = '';
                }
                return errorText;
            },
            campingRequested: function() {
                return this.visit.camping_requested;
            },
            selectedParks: function() {
                return this.visit.selected_park_ids;
            },
            paidParks: function() {
                let paid = []
                for (let park of this.parksList) {
                    if (park.entrance_fee) {
                        paid.push(park);
                    }
                }
                return paid;
            },
            freeParks: function() {
                let free = []
                for (let park of this.parksList) {
                    if (!park.entrance_fee) {
                        free.push(park);
                    }
                }
                return free;
            },

        },
        watch: {
            campingRequested: {
                handler: async function(newVal, oldVal) {
                    if (newVal) {
                        //await this.triggerCampGroundSelector();
                        await this.triggerFreeParksSelector();
                    }
                },
                //deep: true
            },
            /*
            selectedParks: {
                handler: async function(newParks, oldParks) {
                    await this.triggerCampGroundSelector();
                },
                //deep: true
            },
            */

        },

        methods:{
            /*
            triggerCampGroundSelector: async function(internal) {
                await this.$nextTick();
                //this.updateCampGrounds(this.visit.selected_park_ids);
                this.addCampGroundEventListener();
                //this.updateSelectableCampGrounds(newParks, internal);
                this.updateSelectableCampGrounds(this.visit.selected_park_ids, internal);
            },
            */
            removeVisit: function() {
                this.$parent.removeVisit(this.visit.index);
            },
            triggerFreeParksSelector: async function(internal) {
                await this.$nextTick();
                this.addFreeParksEventListener(internal);
                //this.updateSelectableCampGrounds(this.visit.selected_park_ids, internal);
            },


            recalcVisits: async function() {
                await this.$nextTick();
                this.$emit('recalc-visits-flag');
                let url = `/api/feewaivers/${this.feeWaiverId}/log_visit_action/`;
                await this.$http.post(url,this.visit);
            },
            /*
            updateSelectableCampGrounds: function(newParks, internal) {
                let vm = this;
                //this.removeCampGroundEventListener();
                let selectableCampGrounds = [];
                for (let campGround of this.campGroundsList) {
                    let parkId = campGround.park_id ? campGround.park_id.toString() : null;
                    if (!parkId || (newParks && newParks.includes(parkId))) {
                        selectableCampGrounds.push(campGround);
                    }
                }
                let el_campgrounds = $('#campgrounds_'+vm.visit.index);
                let dataArr = []
                for (let campGround of selectableCampGrounds) {
                    let selected = false;
                    // check for previously selected campgrounds
                    for (let option of el_campgrounds.find("option")) {
                        if (campGround.id == option.value && option.selected) {
                            selected = true;
                        }
                    }
                    // with internal flag, load from db
                    if (internal) {
                        //for (let park of newParks) {
                        for (let camp of this.visit.selected_campground_ids) {
                            if (campGround.id == camp) {
                                selected = true;
                            }
                        }
                    }
                    dataArr.push({id: campGround.id, text: campGround.name, defaultSelected: false, selected: selected});
                }
                el_campgrounds.html('').select2({data: dataArr});
                el_campgrounds.trigger('change');
            },
            */

            updateJqueryData: function() {
                // required when loading data from backend
                let vm = this;

                // parks
                let el_parks = $('#parks_'+vm.visit.index)
                el_parks.val(vm.visit.selected_park_ids);
                el_parks.trigger('change');
                // campgrounds
                let el_fr_date = $('#dateFromPicker_' + vm.visit.index);
                el_fr_date.val(vm.visit.date_from);
                el_fr_date.trigger('change');
                let el_to_date = $('#dateToPicker_' + vm.visit.index);
                el_to_date.val(vm.visit.date_to);
                el_to_date.trigger('change');
            },
            addEventListeners: function() {
                let vm = this;
                // Parks multi select
                let el_fr_date = $('#dateFromPicker_' + vm.visit.index);
                let el_to_date = $('#dateToPicker_' + vm.visit.index);

                // // "From" field
                // el_fr_date.datetimepicker({
                //   format: "DD/MM/YYYY",
                //   minDate: "now",
                //   showClear: true,
                // });
                // el_fr_date.on("dp.change", function(e) {
                //   if (el_fr_date.data("DateTimePicker") && el_fr_date.data("DateTimePicker").date()) {
                //     vm.visit.date_from = e.date.format("DD/MM/YYYY");
                //     el_to_date.data("DateTimePicker").minDate(e.date);
                //   } else if (el_fr_date.data("date") === "") {
                //     vm.visit.date_from = "";
                //   }
                // });

                // // "To" field
                // el_to_date.datetimepicker({
                //   format: "DD/MM/YYYY",
                //   showClear: true,
                // });
                // el_to_date.on("dp.change", function(e) {
                //   if (el_to_date.data("DateTimePicker") && el_to_date.data("DateTimePicker").date()) {
                //     vm.visit.date_to = e.date.format("DD/MM/YYYY");
                //   } else if (el_to_date.data("date") === "") {
                //     vm.visit.date_to = "";
                //   }
                // });
                
                $('.input-group').css('z-index', 20);
                
                // Parks
                let parkLabel = 'parks_' + vm.visit.index;
                let parkParentLabel = 'parks_parent_' + vm.visit.index;
                let el_parks = $('#' + parkLabel);
                  el_parks.select2({
                      //placeholder: "parks",
                  });
                el_parks.on('select2:select', function(e) {
                    let val = e.params.data;
                    if (!vm.visit.selected_park_ids.includes(val.id)) {
                        vm.visit.selected_park_ids.push(val.id);
                    }
                }).
                on("select2:unselect",function (e) {
                    let val = e.params.data;
                    if (vm.visit.selected_park_ids.includes(val.id)) {
                        let index = vm.visit.selected_park_ids.indexOf(val.id);
                        vm.visit.selected_park_ids.splice(index, 1);
                    }
                });
                $('.parkclass').css('z-index', 10);
            },
            addFreeParksEventListener: function(internal) {
                let vm = this;
                // Free Parks
                let freeParkLabel = 'free_parks_' + vm.visit.index;
                let el_free_parks = $('#' + freeParkLabel);
                  el_free_parks.select2({
                      //placeholder: "parks",
                  });
                el_free_parks.on('select2:select', function(e) {
                    let val = e.params.data;
                    if (!vm.visit.selected_free_park_ids.includes(val.id)) {
                        vm.visit.selected_free_park_ids.push(val.id);
                    }
                }).
                on("select2:unselect",function (e) {
                    let val = e.params.data;
                    if (vm.visit.selected_free_park_ids.includes(val.id)) {
                        let index = vm.visit.selected_free_park_ids.indexOf(val.id);
                        vm.visit.selected_free_park_ids.splice(index, 1);
                    }
                });
                let dataArr = []
                for (let park of vm.freeParks) {
                    let selected = false;
                    for (let option of el_free_parks.find("option")) {
                        if (park.id == option.value && option.selected) {
                            selected = true;
                        }
                    }
                    // with internal flag, load from db
                    if (internal) {
                        //for (let park of newParks) {
                        for (let db_park of this.visit.selected_free_park_ids) {
                            if (park.id == db_park) {
                                selected = true;
                            }
                        }
                    }
                    dataArr.push({id: park.id, text: park.name, defaultSelected: false, selected: selected});
                }
                el_free_parks.html('').select2({data: dataArr});
                el_free_parks.trigger('change');
                $('.campgroundclass').css('z-index', 5);
            },
            /*
            addCampGroundEventListener: function() {
              //await this.$nextTick();
              let vm = this;
              // CampGrounds
              let campGroundLabel = 'campgrounds_' + vm.visit.index;
              //let campGroundParentLabel = 'campgrounds_parent_' + vm.visit.index;
              let el_campgrounds = $('#' + campGroundLabel);
              el_campgrounds.select2({
                  //placeholder: "campgrounds",
              });
              el_campgrounds.on('select2:select', function(e) {
                  let val = e.params.data;
                  if (!vm.visit.selected_campground_ids.includes(val.id)) {
                      vm.visit.selected_campground_ids.push(val.id);
                  }
              }).
              on("select2:unselect",function (e) {
                  let val = e.params.data;
                  if (vm.visit.selected_campground_ids.includes(val.id)) {
                      let index = vm.visit.selected_campground_ids.indexOf(val.id);
                      vm.visit.selected_campground_ids.splice(index, 1);
                  }
              });
              $('.campgroundclass').css('z-index', 5);
            },
            */

        },

        mounted: function() {
        },
        created: async function() {
            await this.$nextTick();
            this.addEventListeners();
            this.updateJqueryData();
            if (this.isInternal) {
                await this.triggerFreeParksSelector(true);
            }

            /*
            if (this.isInternal) {
                await this.triggerCampGroundSelector(true);
            }
            */
        },
    }
</script>

<style lang="css" scoped>
    .headerbox {
        padding: 50px;
    }
    .section{
        text-transform: capitalize;
    }
    .list-group{
        margin-bottom: 0;
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
</style>

