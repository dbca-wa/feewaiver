<template lang="html">
    <div class="container" >
        <div class="row">
            <div class="col-sm-12">
                <div class="row">
                    <div v-if="feeWaiver && feeWaiver.id" class="col-sm-offset-3 col-sm-6 borderDecoration">
                        <strong>Your Entry Fee Waiver Request form has been successfully submitted.</strong>
                        <br/>
                        <table>
                            <tbody>
                                <tr>
                                    <td><strong>Entry Fee Waiver Request:</strong></td>
                                    <td><strong>{{feeWaiver.lodgement_number}}</strong></td>
                                </tr>
                                <tr>
                                    <td><strong>Date/Time:</strong></td>
                                    <td><strong> {{formatDate(feeWaiver.lodgement_date)}}</strong></td>
                                </tr>
                            </tbody>
                        </table>
                        <router-link :to="{name:'external-feewaiver-form'}" style="margin-top:15px;" class="btn btn-primary">Lodge another request</router-link>
                    </div>
                    <div v-else class="col-sm-offset-3 col-sm-6 borderDecoration">
                        <strong>Sorry, it looks like there is no Fee Waiver currently in your session.</strong>
                        <br /><router-link :to="{name:'external-feewaiver-form'}" style="margin-top:15px;" class="btn btn-primary">Return to form</router-link>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>
<script>

import moment from 'moment';

export default {
  data: function() {
    let vm = this;
    return {
        "feeWaiver": {},
        "dataLoaded": false
    }
  },
  components: {
  },
  computed: {
  },
  methods: {
    formatDate(data) {
        return data ? moment(data).format('DD/MM/YYYY HH:mm:ss') : '';
    }
  },
  mounted: function() {
      this.$nextTick(() => {
          if (this.dataLoaded && !Object.keys(this.feeWaiver).length) {
              this.$router.push({
                  name: 'external-feewaiver-form',
              });
          }
      });
  },
    beforeRouteEnter(to, from, next) {
        next(vm => {
            // Try to get data from history state
            if (history.state && history.state.fee_waiver) {
                vm.feeWaiver = Object.assign({}, history.state.fee_waiver);
            }
            
            // Mark that we attempted to load data
            vm.dataLoaded = true;
            
            // If no data was found and we're not coming from the form page,
            // redirect to the form page
            if (!Object.keys(vm.feeWaiver).length && from.name !== 'external-feewaiver-form') {
                vm.$router.push({
                    name: 'external-feewaiver-form',
                });
            }
        });
    }
}
</script>

<style lang="css" scoped>
.borderDecoration {
    border: 1px solid;
    border-radius: 5px;
    padding: 50px;
    margin-top: 70px;
}
</style>
