<template>
<div v-cloak>

<v-card>
  <v-container>
    <v-layout>
      <!-- Hide while WIP -->
      <!--
      <v-text-field v-model="search"
                    append-icon="search"
                    label="Search"
                    single-line
                    hide-details></v-text-field>

      -->

      <h2> Events </h2>


      <v-spacer> </v-spacer>
      <v-btn @click="refresh_event_list"
              :loading="loading"
              :disabled="loading"
              color="primary"
              icon
              text
              >
      <v-icon> refresh </v-icon>
      </v-btn>

    </v-layout>



    <v-data-table :headers="header_list"
                  :options.sync="options"
                  :items="event_list"
                  :search="search"
                  v-model="selected"
                  class="elevation-1"
                  item-key="id"
                  >

      <!-- TODO status and other stuff here? -->

      <!-- appears to have to be item for vuetify syntax-->
      <template slot="item" slot-scope="props">
        <tr>
          <td>                 

            <div v-if="props.item.file">
            {{ props.item.file.image.original_filename }}
            </div>
          </td>

          <td>

            <!--
            <div v-if="props.item.file">
            {{ props.item.file.created_time }}
            </div>
            -->

          {{props.item.time_created}}

          </td>

          <td>

            {{ props.item.status }}

            <!-- Disable while WIP Oct 6 2020
               Changed from image / next thing based to being more general -->
            <v-btn @click="route_action_event(props.item)"
                    :loading="loading"
                    :disabled="true"
                    color="primary">
              View
            </v-btn>

          </td>
      </tr>

      </template>

      <v-alert slot="no-results"  color="error" icon="warning">
        Your search for "{{ search }}" found no results.
      </v-alert>

    </v-data-table>

 </v-container>
</v-card>

</div>
</template>

<script lang="ts">

import axios from 'axios';

  import Vue from "vue"; export default Vue.extend( {
    name: 'event_list_data_table',

    props: {
      'project_string_id': {},
      'flow_id': {} 
      },
  watch: {

    flow_id() {
      this.refresh_event_list()
    }

  },

  mounted() {

    this.refresh_event_list()

    // ie triggered by  this.$store.commit('action_event_list_refresh')
    // defined in store.js action 
    var self = this
    this.refresh_watcher = this.$store.watch((state) => {
      return this.$store.state.action.refresh_event_list
    },
      (new_val, old_val) => {     
        self.refresh_event_list()      
      },
    )
  },
  destroyed() {
    this.refresh_watcher() // destroy
  },
  data() {
    return {


      search: null,
      loading: false,

      event_list : [],

      selected : [],  // would prefer selected_list but vuetify seems to need 'selected'

      options : {
        'sortBy': ['column2'],
        'sortDesc': [true],
        'itemsPerPage': -1
      },

      header_list: [
        {
          text: "Name",
          align: 'left',
          sortable: false,
          value: ''
        },
        {
          text: "Time",
          align: 'left',      
          sortable: true,
          value: 'id'
        },
        {
          text: "Action",
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
          + '/action/flow/event/list'

      axios.post(url, {

        flow_id : Number(this.flow_id)

      })
      .then(response => {

        this.event_list = response.data.event_list
        this.loading = false

      })
      .catch(error => {
        console.log(error);
      });

    },

    route_action_event: function(flow_event) {

      let url = '/project/'
          + this.project_string_id
          + '/flow/'
          + this.flow_id
          + '/event/'
          + flow_event.id

      this.$router.push(url)

    }

  }
}

) </script>
