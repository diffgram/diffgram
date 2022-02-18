<template>

  <div id="">


    <main_menu height="130">
      <template slot="second_row">

        <v-toolbar
          dense
          elevation="0"
          fixed
          style="width: 100%;"
          height="30px"
                   >

          <bread_crumbs
            :item_list=bread_crumb_list>
          </bread_crumbs>

        </v-toolbar>
      </template>

      <template slot="third_row" >
        <v-toolbar fixed
                   height="50px"
                   elevation="0">
          <v-container>
            <v-layout>
              <div v-if="loading == false">
                <h2>
                  {{job.name}}
                </h2>
              </div>

              <div class="pl-2 pr-2">
                <regular_chip
                  v-if="$store.state.job.current.file_count_statistic != undefined"
                  :message=$store.state.job.current.file_count_statistic
                  tooltip_message="File Count"
                  color="primary"
                  tooltip_direction="bottom">
                </regular_chip>
              </div>

              <v-spacer></v-spacer>

              <v_job_info_builder v-if="job_id"
                                  :job_id="job_id"
                                  @job_info="update_job_info($event)"
                                  :mode_view="'job_edit'"
                                  :mode_data="'job_edit'">
              </v_job_info_builder>

              <v_job_cancel :job="job"
                            @cancel_job_success="$router.push('/job/list')"
              >
              </v_job_cancel>

              <div class="pr-2">
                <v-btn :disabled="loading"
                        @click="create_job_and_redirect"
                        :loading="loading"
                        class="primary--text"
                        color="white">
                  Save Draft
                </v-btn>
              </div>

              <div class="pl-2">
                <v-btn :disabled="!job_id || loading"
                        @click="job_launch"
                        :loading="loading"
                        color="primary">
                  Launch
                </v-btn>
              </div>
              </v-layout>
          </v-container>


        </v-toolbar>
      </template>
    </main_menu>

  <v-container width='90%'>
   <v-card :elevation="0">

        <v-alert type="success"
                 dismissible
                 v-if="save_draft_staus === 'success'"
        >

          Draft Saved.

        </v-alert>
        <v-alert type="success"
                 dismissible
                 v-if="save_draft_staus === 'error'"
        >

          Problems saving draft, please check the fields with errors.

        </v-alert>
        <v-alert type="info"
                 dismissible
                 v-if="$store.state.job.current.file_count_statistic == 0"
        >

          Manage your Annotation Workflow

        </v-alert>

        <div v-if="job.launch_attempt_log">
          <div v-if="Object.keys(job.launch_attempt_log).length > 0">

            <h3> Launch Attempt Log </h3>

            <div v-for="key in Object.keys(job.launch_attempt_log)">

              <h4> {{key}} </h4>
              <v_error_multiple :error="job.launch_attempt_log[key]['error']">
              </v_error_multiple>

            </div>

            <h3> Next launch attempt: {{job.launch_datetime_deferred}} </h3>

          </div>
        </div>

        <v_error_multiple :error="error_launch">
        </v_error_multiple>

        <v-stepper v-model="stepper" vertical>

          <v-stepper-step step="1" :complete="stepper > 1" editable>
            Setup & Schema
          </v-stepper-step>
          <v-stepper-content step="1">
            <v-skeleton-loader :loading="loading_job_fetch" height="600px" width="600px" type="article, actions">
              <job_new_form
                v-model="job"
                :job_id=job_id
                :quick_create="true"
                :project_string_id="project_string_id"
                ref="job_new_form"
                @job-created="on_job_created"
                @job-updated="on_job_updated"
              >

              </job_new_form>

            </v-skeleton-loader>

          </v-stepper-content>


          <v-stepper-step step="2"
                          :complete="stepper > 2"
                          editable>
            Data
          </v-stepper-step>
          <v-stepper-content step="2">


            <div v-if="project_string_id && job_id">
              <v-container fluid>
                <v-row class="d-flex justify-space-between">
                  <v-col cols="6">
                    <job_file_routing
                      :job="job"
                      :latest_dataset="latest_dataset"
                      :project_string_id="project_string_id"
                      ref="job_file_routing"
                      @directories_updated="on_attached_dirs_updated"
                      @output_dir_actions_update="on_output_dirs_updated"
                    ></job_file_routing>

                  </v-col>
                  <v-col cols="6">
                    <job_pipeline_mxgraph :job_object="job"></job_pipeline_mxgraph>
                  </v-col>
                </v-row>
              </v-container>
            </div>

            <v-btn color="primary"
                   large
                   @click="create_job_and_redirect(), stepper = 3">
            Next
            </v-btn>


          </v-stepper-content>


          <v-stepper-step step="3" :complete="stepper > 3">
            Guides & Awards
          </v-stepper-step>
          <v-stepper-content step="3">

            <v-alert v-if="$store.state.job.current.file_count_statistic == 0"
                     type="warning">
              No files attached. Consider going back to Files, selecting desired files and clicking "Attach."
              <br>
              Or confirm SDK / API is attaching files as desired.
            </v-alert>

            <div v-if="job_id">

              <v_guide_list :job_id="job_id"
                            :project_string_id="project_string_id"
                            :mode=" 'attach' "
              >
              </v_guide_list>


              <v-btn @click="show_credentials=!show_credentials"
                     color="primary"
                     outlined
                     class="pa-2"
              >
                Optional: Awards
              </v-btn>

              <v_credential_type_attach_to_job
                v-if="show_credentials==true"
                :job_id="job_id">
              </v_credential_type_attach_to_job>

              <v_task_bid_new v-if="
                            job.type == 'Normal' &&
                            job.share_type == 'market'
                            "
                              :job="job">
              </v_task_bid_new>
            </div>


          </v-stepper-content>
        </v-stepper>

      </v-card>
  </v-container>

  </div>

</template>

<script lang="ts">

  import axios from '../../../services/customAxiosInstance';
  import sillyname from 'sillyname';
  import label_select_only from '../../label/label_select_only.vue'
  import job_file_routing from './job_file_routing.vue'
  import job_pipeline_mxgraph from './job_pipeline_mxgraph.vue'
  import job_new_form from './job_new_form.vue'


  import Vue from "vue";

  export default Vue.extend({
      name: 'task_job_new',
      props: [
        'project_string_id_route',
        'job_id_route'],

      components: {
        label_select_only: label_select_only,
        job_pipeline_mxgraph: job_pipeline_mxgraph,
        job_new_form: job_new_form,
        job_file_routing: job_file_routing
      },

      data() {
        return {
          connectors: [
            {
              'display_name': 'Scale AI Account #1',
              'name': 'scale_ai_1',
              'icon': 'mdi-cached',
              'color': 'primary',
              'credentials': {
                'name': 'SCALE AI TEST',
                'secret': '1'
              }
            },
            {
              'display_name': 'Scale AI Account #2',
              'name': 'scale_ai_2',
              'icon': 'mdi-cached',
              'color': 'primary',
              'credentials': {
                'name': 'SCALE AI TEST',
                'secret': '1'
              }
            },
          ],

          show_credentials: false,
          save_draft_staus: false,


          stepper: 1,
          error_launch: {},
          success_launch: false,

          // Caution! We aren't sending job dict back yet
          // so have to still add this on API side too till we turn this
          // into a computed property or something
          job: {
            name: sillyname().split(" ")[0],
            label_mode: 'closed_all_available',
            passes_per_file: 1,
            share_object: {
              // TODO this may fail for org jobs? double check this.
              'text': String,
              'type': 'project'
            },
            share: 'project',
            instance_type: 'box', //"box" or "polygon" or... "text"...
            permission: 'all_secure_users',
            field: 'Other',
            category: 'visual',
            attached_directories_dict: {attached_directories_list: []},
            type: 'Normal',
            connector_data: {},
            // default to no review while improving review system
            review_by_human_freqeuncy: 'No review', //'every_3rd_pass'
            td_api_trainer_basic_training: false,
            file_handling: "use_existing",
            interface_connection: undefined,
            member_list_ids: []
          },
          output_dir: {},
          latest_dataset: undefined,
          // Not super happy with this triplicate setup but more for Org (see org_dict below)
          loading_job_fetch: false,
          category_list: ['visual'],
          share_list: [
            // Training Data by API not yet supported here.
            /*
            {
              'text': 'Training Data by API',
              'type': 'market'
            },
            */],
          checks: {},

          job_id: null,

          loading: true,

          description: "",

          project_string_id: null

        }
      },
      created() {
        //this.$store.commit('set_project_string_id', this.project_string_id)
        if (this.job_id_route) {
          this.loading_job_fetch = true;
          this.job_id = this.job_id_route;
        }

        if (!this.job_id) {
          /* We assume if no job_id is provided then
           * we are creating a new job (not editing an existing one)
           * , which we assume otherwise
           */
          this.$store.commit('clear_job')
        }

        this.project_string_id = this.project_string_id_route

        this.job.share_object.text = this.$store.state.project.current.project_string_id + ' (Project)'

        /* We get the job updated
         * from the job info component at first run
         * can't call update_job_info() directly since
         * it expects to be passed a job
         *
         * We now default to loading in data() but then
         * set it false here in created.
         * this still feels a bit funny, visually it seems to help though...
         *
         * one goal here is so things like the
         * "silly name" don't show if loading an existing
         * job
         */
        this.loading = false

      },

      computed: {
        bread_crumb_list: function () {
          return [
            {
              text: 'Tasks',
              disabled: false,
              to: '/job/list'
            },
            {
              text: 'New Template',
              disabled: true
            }
          ]
        }
      },
      methods: {
        on_job_created(job) {
          this.job_id = job.id
          this.job.id = job.id
          this.stepper = 2;
          const currPath = this.$route.path;
          if (currPath.endsWith('/job/new')) {
            this.$router.push(`/job/new/${this.job_id}`);
          }
        },
        async create_job_and_redirect() {
          this.loading = true;
          this.save_draft_staus = undefined;
          if (!this.job_id) {
            // Create the job

            const res_new_job = await this.$refs.job_new_form.job_new();
            if(!res_new_job || res_new_job.status !== 200){
              this.loading = false;
              this.save_draft_staus = 'error'
              return false;
            }
            // Save any sync directories.
            const res_update_job = await this.$refs.job_new_form.job_update();
            if(!res_new_job || res_new_job.status !== 200){
              this.loading = false;
              this.save_draft_staus = 'error'
              return false;
            }
          } else {
            await this.$refs.job_new_form.job_update();
          }
          this.save_draft_staus = 'success'
          this.loading = false;

        },
        on_attached_dirs_updated(attached_dirs) {
          this.latest_dataset = attached_dirs[attached_dirs.length - 1];
          this.job.attached_directories_dict = {
            attached_directories_list: attached_dirs.map(elm => elm)
          }
        },
        on_output_dirs_updated(output_dir) {
          this.output_dir = output_dir
        },
        on_job_updated() {
          if (this.stepper == 1) {
            this.stepper = 2
          }
        },
        update_job_info(job) {
          this.project_string_id = job.project_string_id
          // Update existing keys, but avoid losing other keys that were already populated like file_handling
          const new_dirs = job.attached_directories_dict.attached_directories_list.map(x => x)
          this.job = {
            ...this.job,
            ...job,
            label_file_list: this.job.label_file_list,
            attached_directories_dict: {
              test: 12312,
              attached_directories_list: new_dirs
            }
          }
          this.job.original_attached_directories_dict = {...job.attached_directories_dict};
          // For now this is for general info only
          // ie file stats and communication with components there
          this.$store.commit('set_job', job)
          if (this.share_list.length > 0) {
            for (let share of this.share_list) {
              if (share.type == job.share_type) {
                this.job.share_object = share
                break
              }
            }
          }
          // If we already have the job created, jump to second step by default?
          this.stepper = 2

          this.loading = false
          this.loading_job_fetch = false;
        },
        async add_dirs_to_job_api() {
          this.loading = true
          this.show_success = false
          this.error_launch = {}
          let dir_list = [];
          if (this.job && this.job.attached_directories_dict && this.job.attached_directories_dict.attached_directories_list) {
            dir_list = this.job.attached_directories_dict.attached_directories_list
          }
          try {
            const response = await axios.post(
              '/api/v1/project/' + this.project_string_id
              + '/job/dir/attach',
              {
                directory_list: dir_list,
                job_id: parseInt(this.job.id),
              })
            return response
          } catch (error) {
            if (error.response) {
              this.error_launch = error.response.data.log.error
            }
            this.loading = false
            return false;
          }
        },
        async add_output_actions_to_job() {
          this.loading = true
          this.show_success = false
          this.error_launch = {}
          if (this.output_dir.action === 'copy' || this.output_dir.action === 'move') {
            if (!this.output_dir.directory) {
              this.error_launch = {
                output_dir: 'Please select a directory for copy/move after tasks are completed.'
              }
              this.loading = false;
              return false
            }
          }
          try {
            const response = await axios.post(
              '/api/v1/project/' + this.project_string_id
              + '/job/set-output-dir',
              {
                output_dir: this.output_dir.directory ? this.output_dir.directory.directory_id.toString() : undefined,
                output_dir_action: this.output_dir.action,
                job_id: parseInt(this.job.id),
              })
            return response
          } catch (error) {
            if (error.response) {
              this.error = error.response.data.log.error
            }
            this.loading = false
          }
        },
        job_launch: async function () {

          this.success_launch = false
          this.error_launch = {}

          this.loading = true

          try {
            const response_output_dirs = await this.add_output_actions_to_job();
            if (!response_output_dirs) {
              return
            }
            const response_dirs_update = await this.add_dirs_to_job_api();
            if (!response_dirs_update) {
              return
            }
            const response = await axios.post(
              '/api/v1/job/launch',
              {
                job_id: parseInt(this.job_id)

              });
            // Push to success / stats page?
            // Show success?

            let launch_flow = response.data.log.info.launch_flow

            if (launch_flow == 'now') {
              this.$router.push('/job/' + this.job_id + '?success_launch=true')
            } else if (launch_flow == 'soon') {
              this.$router.push('/job/list?success_launch=true')

            }


            this.loading = false

          } catch (error) {

            this.loading = false

            this.error_launch = this.$route_api_errors(error)
          }

        },
      }
    }
  ) </script>
