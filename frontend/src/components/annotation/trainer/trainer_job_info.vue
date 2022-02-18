<template>
  <div v-cloak>
    <v-layout>

      <!-- TODO clarify difference between this and trainer_job_preview -->


      <!--
       Feb 2020 We no longer show info here
        because it conflicts too much with how job renders

        But for now this component still "gets"
        the job info... so need it

       IF we want it to act as example info control need to import it somewhere else.

      More generally this component is a little bit confused

        -->

      <div v-if="job.td_api_trainer_basic_training == true">
        <h2> <v-icon>mdi-heart</v-icon> Basic Training </h2>
      </div>

    </v-layout>
  </div>
</template>

<script lang="ts">

import axios from '../../../services/customInstance';

import Vue from "vue"; export default Vue.extend( {
  name: 'annotation_trainer_job_info',
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

  watch: {

  },

  created() {

      this.job_trainer_info()

  },
  methods: {
    job_trainer_info: function () {

      this.loading = true

      axios.get(
        '/api/v1/job/' + this.job_id +
        '/trainer/info'
      ).then(response => {

          if (response.data.log.success == true) {

            this.job = response.data.job

            this.$emit('job_info', this.job)
            this.$store.commit('set_job', this.job)

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
