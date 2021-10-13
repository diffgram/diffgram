<template>
  <div v-cloak>
    <div v-if="['job_edit'].includes(mode_view)">
      {{ job.status }}
    </div>

    <div v-if="['job_detail'].includes(mode_view)">

      <!-- For now treating the
        general "job only" attributes
        as *different* from something that updates tasks
        too like the labels thing. -->

      <v-layout>

        <v-spacer> </v-spacer>   

        <!-- output_dir_action -->
        <icon_from_regular_list
            :item_list="output_dir_action_icon_list"
            :value="job.output_dir_action">
        </icon_from_regular_list>

        <icon_from_regular_list
            :item_list="share_icon_list"
            :value="job.share_type">
        </icon_from_regular_list>

        <job_type :type="job.type"
                  :size="40">
        </job_type>

      </v-layout>

      <!-- TODO job status component -->
      <div>
        {{ job.status }}  Tasks Remaining: {{ job.tasks_remaining }}
      </div>

      <div class="pa-2">
      <v-progress-linear v-model="job.percent_completed">
      </v-progress-linear>
      </div>


    </div>

    <div v-if="job.td_api_trainer_basic_training == true">
      <h2> <v-icon>mdi-heart</v-icon> Basic Training </h2>
    </div>
  </div>
</template>


<script lang="ts">

import axios from 'axios';
import job_type from './job_type';
import { route_errors } from '../../regular/regular_error_handling'

import Vue from "vue";

export default Vue.extend( {
  name: 'job_overview_and_task_list',
  components: {
    job_type
  },
  props: {
    'job_id': {
      default: null
    },
    'mode_data': {
      default: null     // job_edit, job_detail
    },
    // not clear on difference between use for view and data in this context yet
    'mode_view': {
      default: null     // job_edit, job_detail
    }
  },
  data() {
    return {
      loading: false,

      share_icon_list : [
        {
          'display_name': 'Shared with Project',
          'name': 'project',
          'icon': 'mdi-lightbulb',
          'color': 'blue'
        },
        {
          'display_name': 'Shared with Org',
          'name': 'org',
          'icon': 'mdi-domain',
          'color': 'green'
         }
      ],

      output_dir_action_icon_list : [
        {
          'display_name': 'Output Dataset Action: Copy',
          'name': 'copy',
          'icon': 'mdi-content-copy',
          'color': 'blue'
        },
        {
          'display_name': 'Output Dataset Action: Move',
          'name': 'move',
          'icon': 'mdi-file-move',
          'color': 'green'
         },
         {
          'display_name': 'Output Dataset Action: None',
          'name': 'nothing',
          'icon': 'mdi-circle-off-outline',
          'color': 'gray'
         }
      ],


      info: {},
      error: {},

      job: {
        percent_completed: 0,
        label_dict: null
      },

    }
  },
  computed: {

  },

  watch: {

  },

  created() {

    this.job_builder_info()

  },
  methods: {
    job_builder_info: function () {

      this.loading = true

      axios.post(
        '/api/v1/job/' + this.job_id +
        '/builder/info', {
          'mode_data': this.mode_data
        }
      ).then(response => {

        if (response.data.log.success == true) {

          this.job = response.data.job
          this.$emit('job_info', this.job)
          this.$store.commit('set_job', this.job)
        }

        this.loading = false

      })
        .catch(error => {

          if (error.response.status == 403) {
            this.$store.commit('error_permission')
          }

          console.error(error);
          this.loading = false

        });
    },

  }
}

) </script>
