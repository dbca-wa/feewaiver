<template lang="html">
  <div :class="['card', customClass]">
    <div v-if="!hideHeader" class="card-header">
      <h3 class="card-title">
        {{ label }}
        <a
          :id="custom_id"
          :href="'#' + section_id"
          :aria-controls="section_id"
          class="panelClicker"
          data-bs-toggle="collapse"
          expanded="true"
        >
          <span
            v-if="!noChevron"
            :class="panel_chevron_class"
            style="color: #333;"
          />
        </a>
      </h3>
    </div>
    <div :id="section_id" :class="panel_collapse_class">
      <div class="card-body">
        <slot />
      </div>
    </div>
  </div>
</template>

<script>
import {v4 as uuidv4} from 'uuid';

export default {
  name: "FormSection",
  props: {
    label: {
      type: String,
      default: '',
    },
    Index: {
      type: [String, Number],
      default: 0,
    },
    formCollapse: {
      type: Boolean,
      default: false,
    },
    hideHeader: {
      type: Boolean,
      default: false,
    },
    treeHeight: {
      type: Boolean,
      default: false,
    },
    noChevron: {
      type: Boolean,
      default: false,
    },
    customClass: {
      type: [String, Object, Array],
      default: '',
    },
  },
  data: function () {
    return {
      title: "Section title",
      custom_id: uuidv4(),
      clickHandler: null,
    };
  },
  computed: {
    section_id: function () {
      return "section_" + this.Index;
    },
    panel_chevron_class: function () {
      return this.formCollapse
        ? "bi bi-chevron-down float-end"
        : "bi bi-chevron-up float-end";
    },
    panel_collapse_class: function () {
      if (this.formCollapse) {
        return "card-body collapse";
      } else if (this.treeHeight) {
        return "card-body collapse show flex-container";
      } else {
        return "card-body collapse show";
      }
    },
  },
    mounted: function() {
        let vm = this
        this.clickHandler = function() {
            const chev = this.querySelector('span');
            setTimeout(function() {
                chev.classList.toggle('bi-chevron-up');
                chev.classList.toggle('bi-chevron-down');
                console.log('vm.section_id')
                console.log(vm.section_id)
                if (chev.classList.contains('bi-chevron-up')) {
                    $('#' + vm.section_id).find('.card-body').slideDown()
                } else if (chev.classList.contains('bi-chevron-down')) {
                    $('#' + vm.section_id).find('.card-body').slideUp()
                }
            }, 0);
        };
        
        document.getElementById(this.custom_id).addEventListener('click', this.clickHandler);
    },
    beforeUnmount: function() {
        // Remove event listener to prevent memory leaks
        const element = document.getElementById(this.custom_id);
        if (element && this.clickHandler) {
            element.removeEventListener('click', this.clickHandler);
        }
    }
}
</script>

<style lang="css">
    h3.card-title{
        font-weight: bold;
        font-size: 25px;
        padding:20px;
    }
    .flex-container {
        display: flex;
        flex-direction: column;
        min-height: 325px;
    }
</style>
