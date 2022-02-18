<template>
  <div v-cloak>
     <v-card>
      <v-layout>
        <!-- TODO clarify difference between this and trainer_job_info -->


        <job_type :type="job.type"
                  :size="30">
        </job_type>

        <h2>
          {{ job.name }}
        </h2>

        <div v-if="job.td_api_trainer_basic_training == true">
          <h2> <v-icon>mdi-heart</v-icon> Basic Training </h2>
        </div>

      </v-layout>
     </v-card>
  </div>
</template>

<script lang="ts">

import axios from '../../../services/customInstance';
import job_type from './job_type';

/*  Job info ie on job detail page BEFORE we sign up
 *  It makes more sense to use the right component here
 *  then expect back end to magically know which level we are looking for.
 *
 */

import Vue from "vue"; export default Vue.extend( {
  name: 'annotation_trainer_job_preview_info',
  components: {
    job_type : job_type
  },
  props: {
    'job_id': {
      default: null
    }
  },
  data() {
    return {
      loading: false,

      job: {

      }
    }
  },
  computed: {

  },

  created() {

      this.job_trainer_info()

  },
  methods: {
    job_trainer_info: function () {

      this.loading = true

      axios.get(
        '/api/v1/job/' + this.job_id +
        '/trainer/info/start'
      ).then(response => {

          if (response.data.log.success == true) {

            this.job = response.data.job

            this.$emit('job_info', this.job)

          }

        })
        .catch(error => {
          console.error(error);
          this.loading = false

        });
    }
  }
}

) </script>
