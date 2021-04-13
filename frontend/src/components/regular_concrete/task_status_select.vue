<template>


    <diffgram_select
      :item_list="icon_list"
      v-model="item_internal"
      :label="label"    
      :disabled="disabled"
      @input="$emit('input', $event)"
      @change="$emit('change', $event)"
            >
  </diffgram_select>
  

</template>

<script lang="ts">

/*
 *  For now this is a select, but could look at making it a
 *  multiple select in future
 *
 *  1) Define in component
 
<task_status_select
    v-model="share_type"
    label="Share type"
    :disabled="loading">
</task_status_select>


    2) Set Default data ie
    share_type = "project"  // note lower case
 *  
 */

import Vue from "vue";

export default Vue.extend( {

  name: 'task_status_select',

  props: {
    // built in vue js
    'value': {
      default: null,
      type: String
    },
    'label': {
      default: null,
      type: String
    },
    'disabled' : {
      default: false,
      type: Boolean
    }
  },
  data() {
    return {
      item_internal: null,

      icon_list : [
        {
          'display_name': 'All',
          'name': 'all',
          'icon': 'mdi-select-all',
          'color': 'blue'
        },
        {
          'display_name': 'Complete',
          'name': 'complete',
          'icon': 'mdi-check',
          'color': 'green'
        },
        {
          'display_name': 'Available',
          'name': 'available',
          'icon': 'mdi-inbox',
          'color': 'primary'
        },
        {
          'display_name': 'Deferred',
          'name': 'deferred',
          'icon': 'mdi-debug-step-over',
          'color': 'gray'
         },
         {
          'display_name': 'In Review',
          'name': 'in_review',
          'icon': 'mdi-magnify',
          'color': 'pink'
         }
      ]

    }
  },
  created(){
    this.item_internal = this.value
  },
  watch: {
    /* 
     * If we just edit this directly
     * (ie at created), then it won't change nicely when
     * updated from server
     *
     * If we set it directly then it does the "prop doesn't mutate"
     * thing
     *
     * BUT we still do need to set it at created otherwise the
     * very first load isn't handled...
     *
     */
    value: function (item) {
      this.item_internal = item
    }
  }
}

) </script>
