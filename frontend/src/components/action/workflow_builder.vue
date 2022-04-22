<template>
  <v-container fluid id="" style="height: 100%;">

    <v-card style=" min-height: 800px">
      <v-card-title>Workflow Builder</v-card-title>
      <div class="d-flex">
        <v-card class="ml-2" width="30%" style=" min-height: 700px">
          <v-card-title>Steps: </v-card-title>
          <v-card-text>

          </v-card-text>


        </v-card>
      </div>

    </v-card>

  </v-container>
</template>

<script lang="ts">

  import axios from '../../services/customInstance';
  import action_existing_list from './action_existing_list.vue';
  import upload from '../upload_large.vue';
  import workflow_run_list from './workflow_run_list.vue';


  import Vue from "vue";

  export default Vue.extend({

      name: 'workflow_builder',

      components: {
        action_existing_list: action_existing_list,
        upload: upload,
        workflow_run_list: workflow_run_list
      },
      props: {
        'project_string_id': {
          default: null
        },
        'workflow_id': {
          default: null
        }
      },

      data() {
        return {
          trigger_types: [
            {name: 'Task is completed.', value: 'task_completed'},
            {name: 'Task is created.', value: 'task_created'},
            {name: 'Task Template is completed.', value: 'task_template_completed'},
            {name: 'Files are uploaded.', value: 'input_file_uploaded'},
            // {name: 'Instances are uploaded.', value: 'input_instance_uploaded'},
          ],
          time_windows: [
            {name: 'No Aggregation time.', value: '1_minute'},
            {name: '5 Minutes.', value: '5_minutes'},
            {name: '10 Minutes.', value: '10_minutes'},
            {name: '30 Minutes.', value: '30_minutes'},
            {name: '1 hour.', value: '1_hours'},
            {name: '4 hours.', value: '4_hours'},
            {name: '12 hours.', value: '12_hours'},
            {name: '1 Day', value: '1_days'},
          ],
          loading: false,
          error: {},
          success: false,
          workflow: {
            name: null,
            active: null,
            is_new: null,
            time_window: undefined,
            kind: null
          }
        }
      },

      watch: {

        // for "updates in place" to page.
        // this is really stupid but vue js / router doesn't seem
        // to have better way to do this
        // have to do this on all components ...
        // and can't call this.created() for some reason

        flow_id() {
          this.api_get_flow()
        }

      },

      created() {
        if(this.$route.params.flow_id){
          this.flow_id = this.$route.params.flow_id
          this.api_get_flow()
        }
      },
      computed: {},
      methods: {
        update_or_new: function(){
          if(this.flow_id){
            this.api_flow_update("UPDATE");
          }
          else{
            this.api_flow_new();
          }
        },
        api_flow_new: function () {

          this.loading = true
          this.error = {}
          this.success = false

          axios.post(
            '/api/v1/project/' + this.project_string_id +
            '/actions/workflow/new',
            {
              name: this.flow.name,
              trigger_type: this.flow.trigger_type,
              time_window: this.flow.time_window

            }).then(response => {

            this.flow = response.data.flow;
            this.flow_id = this.flow.id;
            this.success = true
            this.loading = false

          }).catch(error => {

            if (error.response.status == 400) {
              this.error = error.response.data.log.error
            }
            this.loading = false
            console.log(error)
          });

        },
        change_trigger_type: function () {

        },
        api_get_flow: function () {

          if (!this.flow_id) { return }

          this.loading = true
          this.error = {}
          this.success = false

          axios.post(
            '/api/v1/project/' + this.project_string_id +
            '/flow/single',
            {
              flow_id: Number(this.flow_id),
              time_window: this.flow.time_window,
              name: this.flow.name,
              trigger_type: this.flow.trigger_type

            }).then(response => {

            this.flow = response.data.flow
            this.loading = false

          }).catch(error => {

            if (error.response.status == 400) {
              this.error = error.response.data.log.error
            }
            this.loading = false
            console.log(error)
          });

        },


        api_flow_update: function (mode) {

          this.loading = true
          this.error = {}
          this.success = false

          axios.post(
            '/api/v1/project/' + this.project_string_id +
            '/actions/workflow/update',
            {
              flow_id: this.flow_id ? Number(this.flow_id) : undefined,
              name: this.flow.name,
              trigger_type: this.flow.trigger_type,
              time_window: this.flow.time_window,
              active: this.flow.active,
              mode: mode

            }).then(response => {

            this.flow = response.data.flow

            this.success = true
            this.loading = false


            // careful mode is local, not this.mode
            if (mode == 'ARCHIVE') {

              let url = '/project/' + this.project_string_id +
                '/flow/list'

              this.$router.push(url)

            }

          }).catch(error => {

            if (error.response.status == 400) {
              this.error = error.response.data.log.error
            }
            this.loading = false
            console.log(error)
          });

        }

      }
    }
  ) </script>
