<template>
  <div v-cloak>
    <credential_list :project_string_id_prop="project_string_id_prop"></credential_list>

  </div>
</template>

<script lang="ts">

import axios from 'axios';
import credential_list from './credential_list';

import Vue from "vue";
import {create_event} from "../../event/create_event"; export default Vue.extend( {
  name: 'credential_list_page',
  components: {
    credential_list
  },
  props: {
    'project_string_id_prop': {
      default: null
    },
   },
  watch: {

  },
  data() {
    return {

    }
  },
  mounted() {
    this.add_visit_history_event();
  },
  methods: {
    add_visit_history_event: async function(){
      const event_data = await create_event(this.$store.state.project.current.project_string_id, {
        page_name: 'credential_list',
        object_type: 'page',
        user_visit: 'user_visit',
      })
    },
  }
}

) </script>
