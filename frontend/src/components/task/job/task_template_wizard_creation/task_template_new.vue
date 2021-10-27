<template>

  <div id="">
    <main_menu>

    </main_menu>
    <v-toolbar
      class="mt-4"
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
    <v-container fluid class="d-flex justify-center">
      <task_template_wizard
        :project_string_id="project_string_id"
        :job="job">

      </task_template_wizard>
    </v-container>

  </div>

</template>

<script lang="ts">

  import axios from 'axios';
  import sillyname from 'sillyname';
  import task_template_wizard from './task_template_wizard'


  import Vue from "vue";

  export default Vue.extend({
      name: 'task_template_new',
      props: [
        'project_string_id_route',
        'job_id_route'],

      components: {
        task_template_wizard: task_template_wizard,
      },
      mounted: async function(){
        if (this.job_id_route) {
          this.job_id = this.job_id_route;
        }
        if(this.job_id){
          await this.fetch_job_api();
        }
        this.job.share_object.text = this.$store.state.project.current.project_string_id + ' (Project)'
        //this.$store.commit('set_project_string_id', this.project_string_id)


        this.project_string_id = this.project_string_id_route
        console.log('AAAAAAA', this.project_string_id)
        if(!this.project_string_id){
          this.project_string_id = this.job.project_string_id;
        }
        this.loading = false
      },
      data() {
        return {
          project_string_id: null,
          job: {
            name: sillyname().split(" ")[0],
            label_mode: 'closed_all_available',

            loading: false,
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
            member_list_ids: ["all"]
          },
          job_id: null,

        }
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
              text: 'New Task Template',
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
        fetch_job_api: async function() {

          this.loading = true
          try{
            const response = await axios.post(
              `/api/v1/job/${this.job_id}/builder/info`,
              {
                'mode_data': 'job_edit'
              }
            );
            if (response.data.log.success == true) {

              this.job = response.data.job
              this.job.label_file_list = this.job.label_file_list.map(elm => ({id: elm}) );
              this.original_attached_directories_dict = {
                ...this.attached_directories_dict
              };
              console.log('AAAA', this.job.label_file_list);
              this.job.share_object = {
                'type': 'project'
              };
              this.$emit('job_info', this.job)
              this.$store.commit('set_job', this.job)
            }

          }
          catch(e){
            console.error(e);
            if (e.response && e.response.status == 403) {
              this.$store.commit('error_permission')
            }


          }
          finally{
            this.loading = false
          }

        },


      }
    }
  ) </script>
