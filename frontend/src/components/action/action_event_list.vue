<template>
<div v-cloak>

<!--
<v-spacer></v-spacer>
<v-text-field v-model="search"
              append-icon="search"
              label="Search"
              single-line
              hide-details></v-text-field>
<v-spacer></v-spacer>
-->
  
<v-layout column>

  <v_error_multiple :error="error">
  </v_error_multiple>

    <v-container container--fluid grid-list-md>

      <div v-for="item in event_list"
           v-bind:key="item.id"
                >

          <action_event_existing_single
              :project_string_id="project_string_id"
              :action_event="item"
              >
          </action_event_existing_single>

      </div>

    </v-container>


</v-layout>


</div>
</template>

<script lang="ts">

import axios from '../../services/customInstance';
import action_event_existing_single from './action_event_existing_single.vue'


import Vue from "vue"; export default Vue.extend( {
    name: 'event_list_data_table',

    props: {
      'project_string_id': {},
      'flow_event_id': {} 
      },
  components: {
    action_event_existing_single : action_event_existing_single
  },
  mounted() {
   
   this.refresh_event_list()

  },
  data() {
    return {

      search: null,
      loading: false,
      error: {},

      event_list : [],

      selected : [],  // would prefer selected_list but vuetify seems to need 'selected'
      
      header_list: [
        {
          text: "Something",
          align: 'left',
          sortable: false,
          value: ''
        },
        {
          text: "Name",
          align: 'left',
          value: ""
        }
      ]

    }
  },

  methods: {

    refresh_event_list: function () {

      if (this.project_string_id == null) {
        return
      }

      var url = null
      this.loading = true

      url = '/api/v1/project/'
          + this.project_string_id
          + '/action/event/list'

      axios.post(url, {

        flow_event_id : Number(this.flow_event_id)

      })
      .then(response => {

        this.event_list = response.data.event_list
        this.loading = false

      })
      .catch(error => {
        console.log(error);
      });

    }

  }
}

) </script>
