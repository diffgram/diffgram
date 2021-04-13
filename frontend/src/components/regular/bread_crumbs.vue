<template>

  <v-breadcrumbs
      :items="bread_crumb_list_internal">
  </v-breadcrumbs>

</template>

<script lang="ts">

/*
 *
 *https://vuetifyjs.com/en/components/breadcrumbs
 *
 * Note use the "to" for router (single page)
 * href for external?
 *
 * Project home is supplied by default
 *
 * Example items
 * bread_crumb_list: function () {
      return [
        {
          text: 'Tasks',
          disabled: false,         
          to: '/job/list'
        },
        {
          text: 'New',
          disabled: true
        }
      ]
    }
 * 
 */

import Vue from "vue";

export default Vue.extend( {
  name: 'bread_crumbs',
  props: {
    'item_list': {
      default: null
    },
    'loading': {
      default: false
     },
    'disabled': {
      default: false
     },
    'show_project': {
      default: true,
      type: Boolean
     }
  },
  data() {
    return {

    }
  },
  created(){

  },
  computed: {
    bread_crumb_list_internal: function () {
      /* 
       * Trying to think about "Default" / shared concepts here
       *  
       */

      let internal = []

      if (this.show_project == true) {
        internal = [ {
          text: this.$store.state.project.current.name,
          disabled: false,
          to: '/home/dashboard',
        }]
      }

      return [... internal,  ... this.item_list]
    }
  },
}

) </script>
