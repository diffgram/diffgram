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
 *  Context that we may want same icons and styling
 *  BUT difference labels and contexts for usage (ie scope vs share type vs ...)
 *  
 *  Jury is still out of if this is more or less brittle then
 *  having a global variable for icon_list
 *
 *  Perhaps depends what it is...
 *
 *  One thing with this is that it enforces the "lowercase" return value
 *
 *  ie example usage:
 *
 *  1) Define in component
 
<job_status_select
    v-model="share_type"
    label="Share type"
    :disabled="loading">
</job_status_select>


    2) Set Default data ie
    share_type = "project"  // note lower case
 *  
 */

import Vue from "vue";

export default Vue.extend( {

  name: 'job_status_select',

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
          'name': 'All',
          'icon': 'mdi-select-all',
          'color': 'primary'
        },
        {
          'display_name': 'Draft',
          'name': 'draft',
          'icon': 'mdi-file',
          'color': 'orange'
        },
        {
          'display_name': 'Active',
          'name': 'active',
          'icon': 'mdi-inbox',
          'color': 'green'
         },
         {
          'display_name': 'Complete',
          'name': 'complete',
          'icon': 'mdi-check',
          'color': 'gray'
         },
         {
          'display_name': 'Cancelled',
          'name': 'cancelled',
          'icon': 'mdi-cancel',
          'color': 'red'
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
