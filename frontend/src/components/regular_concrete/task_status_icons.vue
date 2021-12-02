<template>
<div data-cy="task_status_icons">

  <tooltip_icon
      v-if="status == 'complete'"
      tooltip_message="Complete"
      icon="mdi-check"
      color="green"
      :large="large"
                >
  </tooltip_icon>

  <tooltip_icon
      v-if="status == 'available'"
      tooltip_message="Available"
      icon="mdi-inbox"
      color="primary"
      :large="large"
                >
  </tooltip_icon>

  <tooltip_icon
    v-if="status == 'in_progress'"
    tooltip_message="In Progress"
    icon="mdi-account-clock-outline"
    color="primary"
    :large="large"
  >
  </tooltip_icon>

  <tooltip_icon
    v-if="status == 'review_requested'"
    tooltip_message="In review"
    icon="mdi-archive-eye-outline"
    color="primary"
    :large="large"
  >
  </tooltip_icon>

  <tooltip_icon
    v-if="status == 'requires_changes'"
    tooltip_message="Requires changes"
    icon="mdi-clipboard-alert-outline"
    color="red"
    :large="large"
  >
  </tooltip_icon>

  <tooltip_icon
      v-if="status == 'deferred'"
      tooltip_message = "Deferred"
      icon="mdi-debug-step-over"
      color="gray"
      :large="large"
                >
  </tooltip_icon>

  <tooltip_icon
      v-if="status == 'in_review'"
      tooltip_message = "In Review"
      icon="mdi-magnify"
      color="pink"
      :large="large"
                >
  </tooltip_icon>

  <!-- TODO other statues? -->


</div>
</template>

<script lang="ts">

/*
 * Note: This should mirior task_status_select so they look similar
 * same concepts but in different formats
 *
 *  ie example usage:
 *
 *1) import, ie

 import task_status_icons from '../regular_concrete/task_status_icons'

 *
 *  2) Define in component

<task_status_icons
    :status="status"
    :disabled="loading">
</task_status_icons>

 *
 */

import Vue from "vue";

export default Vue.extend( {

  name: 'task_status_icons',

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
    return {
    }
  },
  created(){
  }
}

) </script>
