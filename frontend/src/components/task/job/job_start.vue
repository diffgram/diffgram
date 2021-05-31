<template>

  <div id="">

    <v-card>

      <v-card>
        <v-container>
          <h1> {{$store.state.user.current.first_name}}, welcome to {{job.name}} </h1>

          <div v-if="$store.state.user.current.trainer.show_first_time_message == true">

            <!--
            This is your first time on the "job" and there's a lot to take in.
            -->

             <!--
              Getting started video
            -->

            When you need help:
            <v-btn color="blue darken-1" text
                   href="https://diffgram.readme.io/docs/getting-started"
                   target="_blank"
                   icon>
              <v-icon>help</v-icon>
            </v-btn>

          </div>
        </v-container>
      </v-card>

      <v-card>
        <v-container>

          <h3> Guide:</h3>

          <VueMarkDown v-if="job.guide"
                       :source="job.guide.markdown">
          </VueMarkDown>
        </v-container>
      </v-card>




      <!-- Remind about any credentials etc. -->

      <v-card>
        <v-container>

          <v-btn @click="job_annotate()"
                 color="primary">
            Start
          </v-btn>

        </v-container>
      </v-card>

      <!--
  <v-btn>
    Cancel / go back?
  </v-btn>
  -->


    </v-card>



</div>

</template>

<script lang="ts">

import axios from 'axios';


import Vue from "vue"; export default Vue.extend( {
  name: 'job_start',
  props: ['job_id'],

  data () {
    return {

      job: {
        guide: null
      },

      // TODO determine if should show message

      loading: false,


    }
  },
  created() {
      this.job_trainer_info()
  },
  computed: {
  },
  methods: {
    job_annotate: function () {

      // TODO check if used authorized for job first so they don't get booted back
      // TODO only enable button if user authorized

      this.$router.push('/job/' + this.job_id + '/annotate')

    },
    job_trainer_info: function () {

      this.loading = true

      axios.get(
        '/api/v1/job/' + this.job_id +
        '/trainer/info/start'
      ).then(response => {

        if (response.data.log.success == true) {

          this.job = response.data.job

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
