<template>
  <div v-cloak class="job-launches-container">
    <v-card class="pr-10 pl-10" elevation="0">
      <main_menu>
      </main_menu>
      <h1 class="pl-4 pt-4">
        <v-icon color="primary" size="48">mdi-format-list-bulleted-type</v-icon>
        Job Launches Log:
      </h1>
      <v-layout class="d-flex justify-start pl-8 pb-4 pr-8 align-center" style="width: 100%;">
        <v-row>
          <v-col cols="1" class="d-flex align-center">
            <v-btn color="primary" @click="refresh_list" :loading="loading">
              <v-icon>mdi-sync</v-icon>
              Refresh
            </v-btn>
          </v-col>
          <v-col cols="2" class="pt-5">
            <diffgram_select
              :item_list="status_list"
              v-model="status"
              label="Status"
              item-value="value"
              :return_object="true"
              :disabled="loading"
              :clearable="true"
            >

            </diffgram_select>
          </v-col>
          <v-col cols="3" class="pt-5">
            <date_picker
              @date="date = $event"
              :with_spacer="false"
              :initialize_empty="true"
            >
            </date_picker>
          </v-col>
        </v-row>
      </v-layout>

      <regular_table
        :item_list="job_launches_list"
        :column_list="headers_selected"
        :header_list="headers"

        v-model="selected">

        <template slot="time_created" slot-scope="props">
          <p> {{props.item.time_created}} </p>
        </template>

        <template slot="job_name" slot-scope="props">
          <p> {{props.item.job_name}} </p>
        </template>

        <template slot="status" slot-scope="props">
          <job_launch_status_icons :status="props.item.status"></job_launch_status_icons>
        </template>

        <template slot="job_launch_info" slot-scope="props">
          <p>
            {{props.item.job_launch_info}}
          </p>
        </template>

        <template slot="time_completed" slot-scope="props">
          <p> {{props.item.time_completed}} </p>

        </template>

      </regular_table>


    </v-card>

  </div>
</template>

<script lang="ts">

  import axios from '../../../services/customInstance';
  import job_type from './job_type';
  import job_launch_status_icons from '../../regular_concrete/job_launch_status_icons'


  import Vue from "vue";

  export default Vue.extend({
      name: 'job_launches_list',

      components: {
        job_type,
        job_launch_status_icons
      },

      props: {

        // TODO clarify why we have this prop here
        // since using Vuex store for job_list below
        'project_string_id': {
          default: null
        }

      },
      watch: {
        '$route': 'mount'
      },
      data() {
        return {

          success_launch: null,

          selected: [],

          options: {
            'sortBy': ['column5'],
            'sortDesc': [true],
            'itemsPerPage': 25
          },

          job_launches_list: [],

          org_list: ["None"],
          org: "None",    // Continue theme / notes on back end this must be string
          // "None" and not null for current back end setup

          loading: false,
          inference_selected_loading: false,

          my_jobs_only: false,

          share_type: "project",

          status_list:[
            {'name': 'Completed', 'value': 'completed', 'icon': 'mdi-check'},
            {'name': 'Started', 'value': 'started', 'icon': 'mdi-sync'},
            {'name': 'Failed', 'value': 'failed', 'icon': 'mdi-cancel'},
          ],
          status: 'All',

          instance_type_list: ['All', 'polygon', 'box', 'tag'],
          instance_type: 'All',

          metadata_limit_options: [10, 25, 100, 250],
          metadata_limit: 10,

          request_next_page_flag: false,
          request_next_page_available: true,

          instance_changes: [],
          date:{},
          headers: [
            {
              text: "Date Launched",
              align: 'left',
              sortable: true,
              value: 'time_created'
            },
            {
              text: "Job Name",
              align: 'left',
              sortable: false,
              value: 'job_name'
            },
            // TBD idea of "last used" or something like that
            {
              text: "Status",
              align: 'left',
              sortable: false,
              value: 'status'
            },
            {
              text: "Job Launch Information",
              align: 'left',
              sortable: false,
              value: 'job_launch_info'
            },
            {
              text: "Time Completed",
              align: 'left',
              sortable: false,
              value: 'time_completed'
            }
          ],
          headers_selected: [
            "time_created",
            "job_name",
            "status",
            "job_launch_info",
            "time_completed"
          ],
        }
      },
      computed: {

        bread_crumb_list: function () {
          return [
            {
              text: 'Tasks',
              disabled: true
            }
          ]
        },
        metadata: function () {
          return {
            project_string_id: this.$store.state.project.current.project_string_id,
            date_from: this.date.from,
            date_to: this.date.to,
            status: this.status ? this.status.value : 'All',
            builder_or_trainer: {
              mode: 'builder'
            },
          }
        }
      },

      created() {
      },

      mounted() {

        this.job_launch_list_api()

      },
      methods: {

        item_changed() {
          this.request_next_page_available = false
        },
        refresh_list() {
          this.job_launch_list_api();
        },
        async job_launch_list_api() {

          this.loading = true
          try {
            const response = await axios.post('/api/v1/job-launch/list', {
              'metadata': this.metadata
            })

            if (response.data['job_launch_list'] != null) {

              this.job_launches_list = response.data['job_launch_list']
              this.metadata_previous = response.data['metadata']
            }
          } catch (error) {

            console.error(error);
          } finally {
            this.loading = false;
          }
        },
      }
    }
  ) </script>

<style scoped>
  .job-launches-container {
    padding: 2rem 2rem;
  }
</style>
