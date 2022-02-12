<template>
  <div>


    <!-- task list -->
    <v_task_list :job_id="exam_id"
                 :mode_data="'exam_results'"
                 :mode_view="'list'"
                 >
    </v_task_list>


    <!-- TODO add summary -->

    <!--
    <h2> Summary? </h2>

    overall average star rating
    <br/>
    overall missed / ratio to total instances
    <br/>
    average time per task
   <br/>
        -->

    <!-- options for exam -->
    <h2> Exam actions </h2>

        <v-btn @click="exam_pass_api()"
                :loading="loading"
                color="success">
          Pass
        </v-btn>

        <v-btn @click=""
            :loading="loading"
            color="error">
          Fail
        </v-btn>

    <v_error_multiple :error="error">
    </v_error_multiple>

    <v-alert type="success"
             :value="success">
      Granted credentials
    </v-alert>



  </div>

</template>

<script lang="ts">

import axios from 'axios';


import Vue from "vue"; export default Vue.extend( {
  name: 'exam_results',
  props: ['exam_id'],

  data() {
    return {

      loading: false,
      error: {},
      success: false,

    }
  },
  created() {

  },
  watch: {

  },
  methods: {

    reset: function () {
      this.loading = false,
      this.error = { },
      this.success = false
    },

    exam_pass_api: function() {

      this.reset()

      axios.post('/api/v1/exam/pass',
        {
          'job_id': parseInt(this.exam_id),
        })
        .then(response => {
          if (response.data.log.success == true) {

            this.success = true

          }
          this.loading = false

        })
        .catch(error => {

          if (error.response.status == 403) {
            this.$store.commit('error_permission')
          }

          this.error = error.response.data.log.error
          this.loading = false
        });
    }

  }
}
) </script>
