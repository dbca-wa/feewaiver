<template lang="html">
            <FormSection :formCollapse="false" :label="label" :Index="'index_' + visit.index" :noChevron="!isInternal" >
                <div class="col-sm-12">
                    <div class="form-group">
                        <div class="row">
                            <button v-if="visit.index > 0 && !isInternal" class="btn btn-primary pull-right" style="margin-top:5px;" @click.prevent="removeVisit()">Remove Visit</button>
                        </div>
                    </div>
                </div>
                <div class="col-sm-10">
                    <div class="form-group">
                        <div class="row">
                            <label for="visit_description" class="col-sm-4 control-label" >Provide the details and purpose of your visit</label>
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
                    </div>
                </div>
                <div class="col-sm-10">
                    <div class="form-group">
                        <div class="row">
                            <label class="col-sm-4 control-label">Park/s you intend to visit</label>
                            <div :id="'parks_parent_' + visit.index" class="col-sm-6 parkclass">
                                <select :disabled="readonly" :id="'parks_' + visit.index" class="form-control" multiple="multiple">
                                    <option v-for="park in paidParks" :value="park.id">{{park.name}}</option>
                                </select>
                            </div>
                        </div>
                    </div>

                    <div class="form-group">
                        <div class="row">
                              <label class="col-sm-4">Are you intending to camp on CALM land during your visit?</label>
                                <input :disabled="readonly" class="col-sm-1" :id="'yes_' + visit.index" type="radio" v-model="visit.camping_requested" v-bind:value="true">
                                <label class="col-sm-1" for="yes">Yes</label>
                                <input :disabled="readonly" class="col-sm-1" :id="'no_' + visit.index" type="radio" v-model="visit.camping_requested" v-bind:value="false">
                                <label class="col-sm-1" for="no">No</label>
                        </div>
                    </div>
                </div>
                <div v-if="visit.camping_requested" class="col-sm-10">
                    <div v-if="isInternal" :key="feeWaiverId" class="form-group">
                        <div class="row">
                            <label class="col-sm-4">Applicable camping waiver</label>
                                <div class="col-sm-8">
                                    <select :disabled="!canProcess" class="form-control" v-model="visit.camping_assessment">
                                        <option v-for="choice in campingChoices" :value="Object.keys(choice)[0]">{{Object.values(choice)[0]}}</option>
                                    </select>
                                </div>
                        </div>
                    </div>
                    <div class="form-group">
                        <div class="row">
                            <label class="col-sm-4 control-label">Are there other parks not listed above you intend to camp at?</label>
                            <div class="col-sm-6 campgroundclass">
                                <select :disabled="readonly" :id="'free_parks_' + visit.index" class="form-control" multiple="multiple">
                                </select>
                            </div>
                        </div>
                    </div>
                    <!--div class="form-group">
                        <div class="row">
                            <label class="col-sm-4 control-label">Campground/s</label>
                            <div :id="'campgrounds_parent_' + visit.index" class="col-sm-6 campgroundclass">
                                <select :disabled="readonly" required :id="'campgrounds_' + visit.index" class="form-control" multiple="multiple">
                                </select>
                            </div>
                        </div>
                    </div-->
                </div>
                <div class="col-sm-10">
                    <div class="form-group">
                        <div class="row">
                            <label class="col-sm-4 control-label">Date from</label>
                            <div class="col-sm-4">
                                <div class="input-group date" >
                                        <input 
                                            :disabled="readonly" 
                                            required 
                                            type="text" 
                                            class="form-control" 
                                            placeholder="DD/MM/YYYY" 
                                            v-model="visit.date_from" 
                                            :id="'dateFromPicker_' + visit.index"
                                        />
                                        <span class="input-group-addon">
                                            <span class="glyphicon glyphicon-calendar"></span>
                                        </span>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="form-group">
                        <div class="row">
                            <label class="col-sm-4 control-label">Date to</label>
                            <div class="col-sm-4">
                                <div class="input-group date" >
                                        <input 
                                            :disabled="readonly" 
                                            required 
                                            type="text" 
                                            class="form-control" 
                                            placeholder="DD/MM/YYYY" 
                                            v-model="visit.date_to" 
                                            :id="'dateToPicker_' + visit.index"
                                            />
                                        <span class="input-group-addon">
                                            <span class="glyphicon glyphicon-calendar"></span>
                                        </span>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="form-group">
                        <div class="row">
                            <label for="number_of_vehicles" class="col-sm-4 control-label">Number of vehicles used for visit</label>
                            <div class="col-sm-4">
                                <input :disabled="readonly" required type="number" class="form-control" name="number_of_vehicles" min="0" step="1" v-model="visit.number_of_vehicles">
                            </div>
                        </div>
                    </div>
                    <div class="form-group">
                        <div class="row">
                            <label for="number_of_participants" class="col-sm-4 control-label">Number of participants</label>
                            <div class="col-sm-4">
                                <input :disabled="readonly" required type="number" class="form-control" name="number_of_participants" min="0" step="1" v-model="visit.number_of_participants">
                            </div>
                        </div>
                    </div>
                    <div class="form-group">
                        <div class="row" >
                            <label class="col-sm-4 control-label">Age of participants</label>
                            <div class="col-sm-8">
                            <p>
                                <input :ref="'age_of_participants_' + visit.index" :disabled="readonly" type="checkbox" :id="'15_' + visit.index" value="15" v-model="visit.age_of_participants_array">
                                <label>Under 15 yrs</label>
                                <input :disabled="readonly" type="checkbox" :id="'24_' + visit.index" value="24" v-model="visit.age_of_participants_array">
                                <label>15-24 yrs</label>
                                <input :disabled="readonly" type="checkbox" :id="'25_' + visit.index" value="25" v-model="visit.age_of_participants_array">
                                <label>25-39 yrs</label>
                                <input :disabled="readonly" type="checkbox" :id="'40_' + visit.index" value="40" v-model="visit.age_of_participants_array">
                                <label>40-59 yrs</label>
                                <input :disabled="readonly" type="checkbox" :id="'60_' + visit.index" value="60" v-model="visit.age_of_participants_array">
                                <label>60 yrs and over</label>
                            </p>
                            <p>
                                <span class="error" aria-live="polite">{{ ageOfParticipantsErrorText }}</span>
                            </p>
                            </div>
                        </div>
                    </div>
                    <div v-if="isInternal" class="pull-right">
                        <label>Issue?</label>
                        <input :disabled="readonly" type="checkbox" :id="'visit_issue_' + visit.index" :value="true" v-model="visit.issued" @change.prevent="recalcVisits">
                    </div>
                </div>
            </FormSection>

</template>

<script>

    import { api_endpoints, helpers }from '@/utils/hooks'
    import FormSection from "@/components/forms/section_toggle.vue"
    import 'bootstrap/dist/css/bootstrap.css';
    require("moment");
    require("select2/dist/css/select2.min.css");
    require("select2-bootstrap-theme/dist/select2-bootstrap.min.css");
    import select2 from "select2/dist/js/select2.full.js";
    require('eonasdan-bootstrap-datetimepicker/build/css/bootstrap-datetimepicker.min.css');
    require('eonasdan-bootstrap-datetimepicker/build/js/bootstrap-datetimepicker.min.js');

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

              // "From" field
              el_fr_date.datetimepicker({
                format: "DD/MM/YYYY",
                //format: 'LT',
                //minDate: "now",
                showClear: true,
                //allowInputToggle: true,
              });
              el_fr_date.on("dp.change", function(e) {
                if (el_fr_date.data("DateTimePicker").date()) {
                  vm.visit.date_from = e.date.format("DD/MM/YYYY");
                  el_to_date.data("DateTimePicker").minDate(e.date);
                } else if (el_fr_date.data("date") === "") {
                  vm.visit.date_from = "";
                }
              });

              // "To" field
              el_to_date.datetimepicker({
                format: "DD/MM/YYYY",
                //format: 'LT',
                //minDate: "now",
                //minDate: el_fr_date,
                showClear: true,
                //allowInputToggle: true,
              });
              el_to_date.on("dp.change", function(e) {
                if (el_to_date.data("DateTimePicker").date()) {
                  vm.visit.date_to = e.date.format("DD/MM/YYYY");
                } else if (el_to_date.data("date") === "") {
                  vm.visit.date_to = "";
                }
              });
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
                      // remove associated campgrounds
                      //vm.selectableCampGrounds
                      /*
                      for (let campGround of vm.campGroundsList) {
                          if (campGround.park_id == val.id) {
                              let index = vm.visit.selected_campground_ids.indexOf(campGround.id.toString());
                              vm.visit.selected_campground_ids.splice(index, 1);
                          }
                      }
                      */
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

