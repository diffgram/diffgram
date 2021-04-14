<template>
<div>

  <tooltip_icon      
      v-if="source == 'directory'"
      tooltip_message="Dataset"
      icon="mdi-folder"
      color="primary"              
      :large="large"
                >
  </tooltip_icon>

  <tooltip_icon      
      v-if="source == 'job'"
      tooltip_message="Job"
      icon="mdi-inbox"
      color="green"                            
      :large="large"
                >
  </tooltip_icon>

  <tooltip_icon      
      v-if="source == 'task'"
      tooltip_message = "Task"
      icon="mdi-flash-circle"
      color="purple"
      :large="large"
                >
  </tooltip_icon>

  <!-- TODO other sources? -->


</div>
</template>

<script lang="ts">

/*
 *  ie example usage:
 
 1) import, ie
 
 import export_source_icons from '../regular_concrete/export_source_icons'

AND register it ie
  components: {
    export_source_icons
   },


2) Define in component
 
<export_source_icons
    :source="source"
    :disabled="loading">
</export_source_icons>

 *  
 */

import Vue from "vue";

export default Vue.extend( {

  name: 'export_source_icons',

  props: {
    // built in vue js
    'source': {
      default: null,
      type: String
    },
    'disabled' : {
      default: false,
      type: Boolean
    },
    'large' : {
      default: false,
      type: Boolean
    }
  },
  data() {
    return {
    }
  },
  created(){
  }
}

) </script>
