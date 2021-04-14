<template>
  <div v-cloak>

      <tooltip_icon
          tooltip_message="Normal"
          v-if="type == 'Normal'"
          icon="mdi-flash-circle"
          color="green"
          icon_size="size"
                    >
      </tooltip_icon>

      <tooltip_icon
          tooltip_message="Exam"
          v-if="type == 'Exam'"
          icon="mdi-test-tube"
          color="purple"
          icon_size="size"
                    >
      </tooltip_icon>

  </div>
</template>

<script lang="ts">

import Vue from "vue";

export default Vue.extend( {
  name: 'job_type',
  props: {
    'type': {
      default: null
    },
    // Tried using the name sized first, but didn't seem to work as
    // expected so just use this for now...
    // type is integer ie 30, default of null works too
    'size': { 
      default: null
    }

  },
  data() {
    return {
    }
  },
  computed: {

  },

  created() {

  },
  methods: {

  }
}

) </script>
