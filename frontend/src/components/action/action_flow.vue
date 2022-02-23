<template>
  <div id="">

    <v-card>
      <v-container>

        <!-- Flow level info -- >

       <!-- email to send to (defaults to user email) -->

        <v-layout class="d-flex flex-column">
          <v-row class="d-flex justify-end align-center">
            <v-col cols="1" v-if="flow_id">
              <!-- Archive button -->
              <div class="pa-4">
                <button_with_confirm
                  @confirm_click="api_flow_update('ARCHIVE')"
                  color="red"
                  icon="archive"
                  :icon_style="true"
                  tooltip_message="Archive Flow"
                  confirm_message="Archive Flow"
                  :loading="loading">
                </button_with_confirm>
              </div>
              <!-- Archive button -->

            </v-col>
            <v-col cols="2">
              <v-btn color="primary"
                     dark
                     small
                     class="justify-end"
                     href="https://diffgram.readme.io/docs/setting-up-email-notifications"
                     target="_blank"
              >
                Actions Help
                <v-icon right>mdi-lifebuoy</v-icon>

              </v-btn>
            </v-col>

          </v-row>
          <v-row>
            <v-col cols="12">
              <v-text-field label="Name"
                            v-model="flow.name"
              >
              </v-text-field>
            </v-col>
          </v-row>
          <v-row>
            <v-col cols="12">
              <v-select :items="trigger_types"
                        item-text="name"
                        v-model="flow.trigger_type"
                        item-value="value"
                        label="Trigger When: "
                        @change="change_trigger_type()"
              >

              </v-select>

            </v-col>
          </v-row>
          <v-row>
            <v-col cols="12">
              <v-select :items="time_windows"
                        item-text="name"
                        v-model="flow.time_window"
                        item-value="value"
                        label="Trigger Every: "
                        @change="change_trigger_type()"
              >

              </v-select>

            </v-col>
          </v-row>
          <v-row>
            <v-col cols="12">
              <v-btn v-if="flow_id" :loading="loading" color="primary" @click="update_or_new">
                Update
              </v-btn>
              <v-btn v-else :loading="loading" color="primary" @click="update_or_new">
                Create
              </v-btn>
            </v-col>
          </v-row>

          <!-- Hide while WIP -->
          <!--
          <v-switch label="Active"
                    v-model="flow.active">
          </v-switch>
          -->

          <!--
          <v-btn @click="api_flow_update('UPDATE')"
                  :loading="loading"
                  :disabled="loading"
                  color="primary">
            Update
          </v-btn>
          -->
          <v-alert type="success"
                   :value="success"
                   dismissible>
            Updated.
          </v-alert>

        </v-layout>

        <v-layout>

          <v_error_multiple :error="error">
          </v_error_multiple>

        </v-layout>

        <v-layout>


          <action_existing_list
            v-if="flow_id"
            :project_string_id="project_string_id"
            :flow_id="flow_id"
          >
          </action_existing_list>

        </v-layout>


        <!-- Hide, not relevant in new context -->

        <!--
        <v-alert type="info">
          Upload below or email to:
          {{flow.string_id}}@action.diffgram.com
        </v-alert>

        <v-alert type="info"
                 dismissible
        >
          If the action has not been run in a while it will take about a minute
          for it to warm up.
          After that it will run quickly.
        </v-alert>
        -->

        <flow_event_list
          v-if="flow_id"
          :project_string_id="project_string_id"
          :flow_id="flow_id"
        >
        </flow_event_list>



      </v-container>

    </v-card>

  </div>
</template>

<script lang="ts">

  import axios from '../../services/customInstance';
  import action_existing_list from './action_existing_list.vue';
  import upload from '../upload_large.vue';
  import flow_event_list from './action_flow_event_list.vue';


  import Vue from "vue";

  export default Vue.extend({

      name: 'flow',

      components: {
        action_existing_list: action_existing_list,
        upload: upload,
        flow_event_list: flow_event_list
      },
      props: {
        'project_string_id': {
          default: null
        },
        'flow_id': {
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
          flow: {
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
            '/action/flow/new',
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
            '/action/flow/update',
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
