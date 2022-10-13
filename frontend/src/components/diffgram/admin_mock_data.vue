<template>
  <div>

    <h1> Mock Data </h1>

    <tooltip_button
      tooltip_message="Generate random instances within current project"
      @click="mockAnnotations($store.state.project.current.project_string_id)"
      button_message="Mock Annotations"
      color="primary">
    </tooltip_button>


  </div>
</template>

<script lang="ts">


import { mockAnnotations } from "../../services/mockServices";

import Vue from "vue"; export default Vue.extend( {

  name: 'admin_mock_data',
  components: {
  },
  props: [''],
  data() {
    return {
      
    }
  },
  created() {

  },
  methods: {
    mockAnnotations,

  }
}

) </script>
