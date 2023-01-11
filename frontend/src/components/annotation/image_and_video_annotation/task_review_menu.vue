<template>

  <div id="">

    <!-- WIP WIP WIP-->

    <v-btn>
      Can't review?
    </v-btn>

    <v-btn>
      Report
    </v-btn>


  </div>

</template>

<script lang="ts">

import Vue from "vue"; export default Vue.extend( {
  name: 'task_review_menu',
  props: ['job_id'],

  data () {
    return {

      rating: 3


    }
  },
  created() {

  },
  computed: {
  },
  methods: {

  }
}
) </script>
