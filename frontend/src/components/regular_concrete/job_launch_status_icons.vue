<template>
<div>

  <tooltip_icon
      v-if="status === 'completed'"
      tooltip_message="Complete"
      icon="mdi-check"
      color="green"
      :large="large"
                >
  </tooltip_icon>

  <tooltip_icon
      v-if="status === 'started'"
      tooltip_message="Started"
      icon="mdi-sync"
      color="primary"
      :large="large"
                >
  </tooltip_icon>

  <tooltip_icon
    v-if="status === 'failed'"
    tooltip_message="Failed"
    icon="mdi-alert"
    color="error"
    :large="large"
  >
  </tooltip_icon>


</div>
</template>

<script lang="ts">

import Vue from "vue";

export default Vue.extend( {

  name: 'job_launch_status_icons',

  props: {
    // built in vue js
    'status': {
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
    return {}
  },
  created(){

  }
}

) </script>
