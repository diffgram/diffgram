<template>

  <div id="">

    <trainer_job_preview_info
          @job_info="job = $event"
          :job_id="job_id">

    </trainer_job_preview_info>



    <v-card>

      <!-- TO DO  Sample file?  Permissions issues... -->
      <!-- TO DO  Show guides? -->

      <br />

      
      <!-- TODO review in conept of Internal, ie "Accept" vs Apply-->

        <!-- TODO condition on user_to_job.status properly -->

        <v-btn v-if="!job.user_to_job"
               @click="job_apply()"
               :loading="loading"
               color="primary"
               large
               >
          Apply
        </v-btn>

        <v-btn v-if="job.user_to_job"
               @click="job_annotate()"
               :loading="loading"
               color="primary"
               large
               >
          Launch
        </v-btn>

        <v_error_multiple :error="error">
        </v_error_multiple>

     
    </v-card>

    <v_credential_list :job_id="job_id"
                       :mode_options="'job_detail'"
                       :mode_view="'list'">
      <!-- TODO change to grid-->
    </v_credential_list>

    <!--
    Hide stats for trainers for now, not really clear
    what the value was there or what we were trying to show them.
      Maybe something to do with how much work to do /
        enticing them to be interested in it?
      But perhaps we should just show how many tasks are left as a number?
        Either way it needs some work.
    -->

    <!--
    <v_stats_task :job_id="job_id">
    </v_stats_task>
    -->

  </div>

</template>

<script lang="ts">

import axios from 'axios';
import trainer_job_preview_info from './trainer_job_preview_info';


import Vue from "vue"; export default Vue.extend( {
  name: 'job_detail_trainer',

  components: {
    trainer_job_preview_info : trainer_job_preview_info
  },
  props: ['job_id'],

  data () {
    return {

      success_launch: false,

      share_type: 'Diffgram market (External)',
      permission: 'All secure users',
      field: 'Self Driving',
      category: 'visual',
      type: 'Normal',
      review_by_human_freqeuncy: 'Every 3rd pass (default)',

      error: {

      },

      loading: false,

      description: "",

      job: {

      }


    }
  },
  created() {
    this.success_launch = (this.$route.query["success_launch"] == 'true')
  },
  computed: {
  },
  methods: {

    // TODO get job detail based on hash

    // TODO move to it's own component and then share with builder and trainer

    job_apply: function () {

      this.loading = true

      axios.post('/api/v1/job/apply',
        {
          'job_id' : this.job_id
        })
        .then(response => {
          if (response.data.log.success == true) {

            // careful, job id may change if repeatable like exam

            this.$router.push('/job/' + response.data.log.job_id + '/start')

          }
            this.loading = false

        })
        .catch(error => {

          this.error = error.response.data.log.error
          this.loading = false
        });
    },
    job_annotate: function () {

      // TODO check if used authorized for job first so they don't get booted back
      // TODO only enable button if user authorized

      this.$router.push('/job/' + this.job_id + '/annotate')

    }
  }
}
) </script>
