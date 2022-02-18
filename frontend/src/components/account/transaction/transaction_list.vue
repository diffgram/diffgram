<template>
  <div v-cloak>
    <v-card>

      <v-card-title>
        Transaction List
      </v-card-title>

      <!-- TODO show date picker if null ?-->
      <!--
      <date_picker @date="date = $event">
      </date_picker>
      -->
      <!-- start list view -->
      <div v-if="mode_view=='list'">

        <v-container>
          <v-layout>

            <div v-if="['direct_route'].includes(mode_data)">

              <!--
              <v-checkbox v-model="my_stuff_only"
                          label="My transactions Only">
              </v-checkbox>
              -->

              <v-btn @click="transaction_list_api"
                     :loading="loading"
                     color="primary">
                Refresh
              </v-btn>

            </div>

          </v-layout>
        </v-container>


        <v_error_multiple :error="error_attach">
        </v_error_multiple>

        <v-alert type="success"

                 v-if="show_success_attach">

        </v-alert>


        <v-data-table v-bind:headers="headers_view"
                      :items="transaction_list"
                      class="elevation-1"
                      item-key="id"
                      :options.sync="options"
                      footer-props.prev-icon="mdi-menu-left"
                      footer-props.next-icon="mdi-menu-right">

          <!-- review rows-per-page-items setting-->
          <!-- appears to have to be item for vuetify syntax-->
          <template slot="item"
                    slot-scope="props">

            <tr>

              <td>
                {{props.item.id}}

              </td>

              <td>
                {{props.item.time_created}}
              </td>

              <td v-if="account.account_type == 'billing'">
                {{format_money(props.item.amount)}}
              </td>
              <td v-else>
                {{props.item.amount}}
              </td>


              <td v-if="props.item.task_id">
                {{format_money(props.item.cost_per_instance)}}
              </td>

              <td v-if="props.item.task_id">
                {{props.item.count_instances_changed}}
              </td>

              <td v-if="props.item.task_id">

                <v-btn @click="route_task(props.item.task_id)"
                       :loading="loading"
                       color="primary">
                  View
                </v-btn>

              </td>
              <td v-if="props.item.task_id">

                <v-btn @click="route_job_detail(props.item.job_id)"
                       :loading="loading"
                       color="primary">
                  View
                </v-btn>

              </td>

            </tr>
          </template>

          <div v-if="!loading">
            <v-alert slot="no-data"  color="error" icon="warning">
              No results found.
            </v-alert>
          </div>

        </v-data-table>
      </div>
      <!-- end list view -->

    </v-card>


  </div>
</template>

<script lang="ts">

import axios from '../../../services/customAxiosInstance';

import Vue from "vue"; export default Vue.extend( {
  name: 'transaction_list',
  props: {
    'account': {
        default: {
          id: null
        }
      },
    'project_string_id': {
      default: null
    },
    'job_id': {
      default: null
    },
    'mode_data': {
      default: "direct_route"   // job_edit, job_detail, user_profile, general/account?
    },
    'mode_view' : {
      default: "list"  // list or grid?
    }
   },
  data() {
    return {

      selected: [],

      date: {},   // TODO use date as a prop to sync with stats?

      transaction_list : [],

      loading: false,

      options: {
        'sortBy': ['column2'],
        'sortDesc': [true],
        'itemsPerPage': 5
      },

      error_attach: {},
      show_success_attach: false,


      request_next_page_flag: false,
      request_next_page_available: true,

      headers: [
        {
          text: "ID",
          align: 'left',
          sortable: true,
          value: 'id'
        },
        {
          text: "Time",
          align: 'left',
          sortable: true,
          value: 'time_created'
        },
        {
          text: "Amount",
          align: 'left',
          sortable: true,
          value: 'amount'
        },
        {
          text: "Per instance",
          align: 'left',
          sortable: true,
          value: 'cost_per_instance'
        },
        {
          text: "Instances changed",
          align: 'left',
          sortable: true,
          value: 'count_instances_changed'
        },
        {
          text: "Task",
          align: 'left',
          sortable: true,
          value: 'task_id'
        },
        {
          text: "Job",
          align: 'left',
          sortable: true,
          value: 'job_id'
        }
      ]

    }
  },

  computed: {
    headers_view: function () {
      if (true) {
        return this.headers
      }
    }

  },
  mounted() {

  },
  watch: {
    account: function () {
      this.transaction_list_api()
    }
  },
  methods: {

    route_job_detail(job_id) {
      this.$router.push("/job/" + job_id)
    },

    route_task(task_id) {
      this.$router.push("/task/" + task_id)
    },

    format_money(value) {
      return '$' + (value / 100).toLocaleString('en-US', {
        maximumFractionDigits: 2,
        minimumFractionDigits: 2
      })
    },

    transaction_list_api() {

      axios.post('/api/v1/transaction/list', {

        //'date_from': this.date.from,
        //'date_to': this.date.to,
        'job_id': this.job_id,
        'account_id' : String(this.account.id),
        'mode_data': this.mode_data

        }).then(response => {

          if (response.data.log.success == true) {

            this.transaction_list = response.data.transaction_list
          }

        })
        .catch(error => {
          console.log(error);
          this.loading = false
        });
    }


  }
}

) </script>
