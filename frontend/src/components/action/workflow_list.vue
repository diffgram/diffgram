<template>
  <div v-cloak class="action_flow_container">
    <h1>Workflows</h1>

    <new_flow
      color="success"
      :project_string_id="$store.state.project.current.project_string_id">

    </new_flow>

    <v-data-table :headers="header_list"
                  :items="flow_list"
                  :search="search"
                  v-model="selected"
                  class="elevation-1"
                  item-key="id"
    >

      <template slot="item" slot-scope="props">
        <tr>
          <td  @click="route_flow(props.item)"><h3 class="workflow-title"> {{ props.item.name }}</h3></td>

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

import axios from '../../services/customInstance';
import new_flow from '../action/action_new_flow.vue'
import Vue from "vue";

export default Vue.extend({
    name: 'action_flow_list',

    props: {
      'project_string_id': {}
    },
    watch: {},

    components: {
      new_flow: new_flow
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
          + '/workflow/' + flow.id

        this.$router.push(url)

      }

    }
  }
) </script>
<style scoped>
.workflow-title:hover {
  color: #1565c0;
  cursor: pointer;
}

.action_flow_container {
  padding: 2rem 2rem;
}
</style>
