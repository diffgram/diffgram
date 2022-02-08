<template>
  <v-container fluid>
    <v-layout>
      <v-row>
        <v-col cols="4">
          <annotator_performance :job_id="job_id"
                                 :project_string_id="project_string_id">

          </annotator_performance>
        </v-col>
        <v-col cols="8">
          <v-card class="pa-6">
            <v-card-title>Tasks Count</v-card-title>
            <v-alert type="error" :value="errors">
              {{ errors }}
            </v-alert>

            <date_picker @date="date = $event">
            </date_picker>

            <v-select :items="status_list"
                      v-model="status"
                      label="Status"
                      item-value="text"
                      :disabled="loading"
                      @change="">
            </v-select>

            <v-btn @click="stats_task_api"
                   color="primary">
              Refresh
            </v-btn>

            Total: {{ count_task }}

            <line_chart :chart-data="datacollection"
                        :options="options">
            </line_chart>
          </v-card>
        </v-col>
      </v-row>
    </v-layout>


  </v-container>
</template>

<script lang="ts">


import axios from 'axios';
import Vue from "vue";
import annotator_performance from "./annotator_performance.vue";

export default Vue.extend({
    name: 'stats_task',
    components: {
      annotator_performance
    },
    props: {
      'job_id':
        {default: null},
      'mode':
        {default: "by_job"},
      'project_string_id':{
        default: null
      }
    },
    data() {
      return {
        datacollection: {},

        labels: [],
        values: [],

        date: {},

        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            xAxes: [{
              type: 'time',
              distribution: 'series',
              time: {
                unit: 'day',
                unitStepSize: 1,
                displayFormats: {
                  'day': 'MMM DD'
                }
              },
            }],

            yAxes: [{
              ticks: {
                beginAtZero: true,
                fixedStepSize: 1
              }
            }]
          }
        },

        // TODO add more
        status_list: ['all', 'created', 'available', 'in_review', 'complete'],
        status: 'all',


        count_task: null,

        loading: false,
        errors: null,
        result: null,

        auth: {},
        show_auth: false,

        permission_level_list: ['Editor', 'Viewer'],
        permission_level: 'Editor',

      }
    },
    mounted() {

      this.stats_task_api()

    },
    methods: {
      fillData() {
        this.datacollection = {
          labels: this.labels,
          datasets: [
            {
              label: this.status,
              data: this.values,
              backgroundColor: '#1e1e1e'
            },

          ]
        }
      },

      stats_task_api: function () {

        this.loading = true
        this.errors = null
        this.result = null

        axios.post('/api/v1/diffgram/stats/task',
          {
            'date_from': this.date.from,
            'date_to': this.date.to,
            'status': this.status,
            'job_id': this.job_id,
            'mode': this.mode

          }).then(response => {
          let log = response.data.log
          if (log.success == true) {
            this.labels = response.data.stats.labels
            this.values = response.data.stats.values
            this.fillData()

            this.count_task = response.data.stats.count_task

          }
          this.loading = false

        })
          .catch(error => {
            this.loading = false
          });
      }
    }
  }
) </script>
