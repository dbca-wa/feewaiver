<template lang="html">
    <div class="card" >
      <div v-if="!hideHeader" class="card-header">
        <h3 class="card-title">{{label}} 
            <a :href="'#'+section_id" class="panelClicker" :id="custom_id" data-bs-toggle="collapse" expanded="true" :aria-controls="section_id">
                <span v-if="!noChevron" :class="panel_chevron_class"></span>
            </a>
        </h3>
      </div>
      <div :class="panel_collapse_class" :id="section_id">
        <div class="card-body">
          <slot></slot>
        </div>
      </div>
    </div>
</template>

<script>
import {v4 as uuidv4} from 'uuid';

export default {
    name:"FormSection",
    props: {
        label: {}, 
        Index: {}, 
        formCollapse: {}, 
        hideHeader: {},
        treeHeight: {},
        noChevron: {
            default: false,
        },
    },
    data:function () {
        return {
            title:"Section title",
            panel_chevron_class: null,
            custom_id: uuidv4(),
            clickHandler: null
        }
    },
    computed:{
        section_id: function () {
            return "section_"+this.Index
        },
        panel_collapse_class: function() {
            if (this.formCollapse) {
                this.panel_chevron_class = "bi bi-chevron-down float-end";
                return "card-body collapse";
            } else {
                if (this.treeHeight) {
                    this.panel_chevron_class = "bi bi-chevron-up float-end";
                    return "card-body collapse show flex-container";
                } else {
                    this.panel_chevron_class = "bi bi-chevron-up float-end";
                    return "card-body collapse show";
                }
            }
        },
    },
    mounted: function() {
        // $('#' + this.custom_id).on('click',function () {
        //     var chev = $(this).children()[0];
        //     window.setTimeout(function () {
        //         $(chev).toggleClass("glyphicon-chevron-up glyphicon-chevron-down");
        //     }, 100);
        // });
        this.clickHandler = function() {
            const chev = this.querySelector('span');
            setTimeout(function() {
                chev.classList.toggle('bi-chevron-up');
                chev.classList.toggle('bi-chevron-down');
            }, 100);
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
    h3.panel-title{
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
