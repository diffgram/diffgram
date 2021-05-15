<template>

  <div id="">

    <v-alert id="success_launch"
             type="success"
             v-if="success_launch">
      Launched.
    </v-alert>


    <v_job_info_builder :job_id="job_id"
                        :mode_data="'job_detail'"
                        :mode_view="'job_detail'"
                        @job_info="job = $event"
                        ref="job_builder_info"
    >
    </v_job_info_builder>


     <v_error_multiple :error="error">
    </v_error_multiple>

    <!--
    <v-btn v-if="!job.user_to_job"
            @click="job_apply()"
            :loading="loading"
            color="primary"
            large
    >
      Start Annotating
    </v-btn>

    <v-btn v-if="job.user_to_job"
            @click="job_annotate()"
            :loading="loading"
            color="primary"
            large
    >
      Continue Annotating
    </v-btn>
    -->

    <v-btn v-if="job.type == 'Exam'"
            @click="route_exam_result()"
            :loading="loading"
            color="primary">
      Exam Results
    </v-btn>


    <!-- What about a preview of guide?
         ie so don't have to click into a task
        -->

    <v_task_list :job_id="job_id"
                 :job="job"
                 :project_string_id="project_string_id"
                 :external_interface="external_interface"
                 :show_detail_button="true"
                 :open_read_only_mode="has_external_integration"
                 :mode_options="'job_detail'"
                 :mode_view="'list'"
                 @task_count_changed="update_job"
    >
    </v_task_list>

   
    <v_stats_task :job_id="job_id">
    </v_stats_task>

    <v_credential_list :job_id="job_id"
                       :mode_options="'job_detail'"
                       :mode_view="'list'">
    </v_credential_list>

    <v-card>
      <v-container>
        <h2> Actions </h2>
        <v_job_cancel :job="job"></v_job_cancel>
      </v-container>
    </v-card>

  </div>

</template>

<script lang="ts">

  import axios from 'axios';
  import vue_scroll_to from 'vue-scrollto'

  import Vue from "vue";

  export default Vue.extend({
      name: 'job_detail_builder',
      props: ['job_id'],
      components: {
      },
      data() {
        return {

          success_launch: false,

          share_type: 'Diffgram market (External)',
          permission: 'All secure users',
          field: 'Self Driving',
          category: 'visual',
          type: 'Normal',
          review_by_human_freqeuncy: 'Every 3rd pass (default)',

          error: {},

          loading: false,

          description: "",

          job: {}


        }
      },
      created() {
        this.success_launch = (this.$route.query["success_launch"] == 'true')

      },
      mounted() {

        if (this.success_launch == true) {
          // careful to include the '#' pound sign
          let options = {
            offset: -80   // otherwise to buttom of element
          }
          vue_scroll_to.scrollTo('#success_launch', options)
        }
      },
      computed: {
        has_external_integration: function(){
          const external_interfaces_providers = ['labelbox']
          return this.job.interface_connection
                  &&  external_interfaces_providers.includes(this.job.interface_connection.integration_name)
        },
        external_interface: function(){
          if(this.job.interface_connection){
            return this.job.interface_connection.integration_name
          }
          return undefined
        },
        project_string_id: function(){
          return this.$store.state.project.current.project_string_id;
        }
      },
      methods: {
        update_job: function(){
          this.$refs['job_builder_info'].job_builder_info();
        },
        job_apply: function () {

          this.loading = true

          axios.post('/api/v1/job/apply',
            {
              'job_id': this.job_id
            })
            .then(response => {
              if (response.data.log.success == true) {

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

        },

        route_exam_result: function () {
          this.$router.push('/job/' + this.job_id + '/exam/results')

        }
      }
    }
  ) </script>
