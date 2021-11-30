<template>
  <div v-cloak class="action_flow_container">
    <h1>Action Flows</h1>
    <!-- Hide while WIP -->
    <!--
  <v-spacer></v-spacer>
  <v-text-field v-model="search"
                append-icon="search"
                label="Search"
                single-line
                hide-details></v-text-field>
  <v-spacer></v-spacer>
    -->

    <new_flow
      :project_string_id="$store.state.project.current.project_string_id">

    </new_flow>

    <v-data-table :headers="header_list"
                  :items="flow_list"
                  :search="search"
                  v-model="selected"
                  class="elevation-1"
                  item-key="id"
    >

      <!-- appears to have to be item for vuetify syntax-->
      <template slot="item" slot-scope="props">
        <tr>
          <td>{{ props.item.name }}</td>
          <td>{{ props.item.trigger_type }}</td>
          <td>
            <span v-if="props.item.time_window === '1_minute'">No Time Window</span>
            <span v-else>{{props.item.time_window}}</span>

          </td>

          <!--
        <td>

          {{ props.item.active }}

        </td>
            -->

          <td>

            <v-btn @click="route_flow(props.item)"
                   :loading="loading"
                   :disabled="loading"
                   color="primary">
              View
            </v-btn>

          </td>
        </tr>

      </template>

      <v-alert slot="no-results" color="error" icon="warning">
        Your search for "{{ search }}" found no results.
      </v-alert>

    </v-data-table>


  </div>
</template>

<script lang="ts">

  import axios from 'axios';
  import new_flow from '../action/action_new_flow.vue'
  import Vue from "vue";

  export default Vue.extend({
      name: 'action_flow_list',

      props: {
        'project_string_id': {}
      },
      watch: {},

      components: {
        new_flow : new_flow
      },

      mounted() {

        this.refresh_list()

      },
      data() {
        return {

          search: null,
          loading: false,

          flow_list: [],

          selected: [],  // would prefer selected_list but vuetify seems to need 'selected'

          header_list: [
            {
              text: "Name",
              align: 'left',
              sortable: true,
              value: 'name'
            },
            {
              text: "Trigger Event",
              align: 'left',
              value: "trigger_type",

              sortable: false,
            },
            {
              text: "Time Window",
              align: 'left',
              value: "time_window",

              sortable: false,
            },
            {
              text: "Action",
              align: 'left',
              value: "active",

              sortable: false,
            }
          ]

        }
      },

      methods: {

        refresh_list: function () {

          if (this.project_string_id == null) {
            return
          }

          var url = null
          this.loading = true

          url = '/api/v1/project/'
            + this.project_string_id
            + '/action/flow/list'

          axios.post(url, {})
            .then(response => {

              this.flow_list = response.data.flow_list
              this.loading = false

            })
            .catch(error => {
              console.log(error);
            });

        },

        route_flow: function (flow) {

          let url = '/project/' + this.project_string_id
            + '/flow/' + flow.id

          this.$router.push(url)

        }

      }
    }
  ) </script>
<style scoped>
  .action_flow_container {
    padding: 2rem 2rem;
  }
</style>
