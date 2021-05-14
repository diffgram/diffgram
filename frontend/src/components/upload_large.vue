<template>
  <div class="upload-container" id="upload">
    <v-layout>
      <v-flex class="flex-column">
        <h1 class="pt-10 pb-6">Import</h1>
        <v-card elevation="0" class="mb-5">
          <v-card-text>
            <v-layout class="pa-8">
              <v-row>
                <v-col cols="12" class="pa-0">
                  <v-layout column>
                    <v-row class="d-flex justify-space-between">
                      <v-col cols="2" class="d-flex justify-self-end">
                        <v-btn color="blue darken-1"
                               text
                               small
                               outlined
                               type="primary"
                               href="https://diffgram.readme.io/docs/importing-your-data"
                               target="_blank"
                        >
                          <v-icon left>mdi-book</v-icon>
                          Help
                        </v-btn>

                      </v-col>

                    </v-row>
                    <v-row  v-if="!bucket_name || bucket_name == ''">
                      <v-col cols="12" class="d-flex justify-center">
                        <v-btn
                          @click="open_upload_wizard_dialog"
                          :disabled="!current_directory"
                          color="success"
                          x-large>
                          <v-icon>mdi-upload</v-icon>
                          Start New Data Upload
                        </v-btn>
                      </v-col>
                    </v-row>


                  </v-layout>
                </v-col>
              </v-row>
            </v-layout>
          </v-card-text>
        </v-card>

      </v-flex>

    </v-layout>

    <!-- Proactive warning in the context
       of users navigating away from page while uploading still.
      -->
    <v-alert v-if="is_actively_sending == true"
             type="info"
    >
      Keep window open. Upload in progress.
    </v-alert>


    <v_input_view v-if="!mode"
                  :project_string_id="project_string_id"
                  :request_refresh="request_refresh">
    </v_input_view>


    <v-layout v-if="!mode">
      <v-flex>
        <!--
        <v-card-title>
          <h3>Need other input methods or support for different files?</h3>
        </v-card-title>

        <v-card-actions>

          <v-btn href="https://docs.google.com/forms/d/e/1FAIpQLSdPYN2jtgZnoCa6QiViliGoKcEd9gVM-MREiqsu1sRqtLtaHA/viewform"
                  target="_blank"
                  color="primary">
            Request
            <v-icon right>mdi-message-alert</v-icon>
          </v-btn>
        </v-card-actions>
        -->
      </v-flex>
    </v-layout>

    <v-layout v-if="!mode">
      <v-flex>
        <v-card>
          <v-divider></v-divider>
          <v-card-subtitle>
            <h3>Someone else handles data input?</h3>
          </v-card-subtitle>

          <v-card-actions>
            <v-dialog v-model="v_collaborate_new"
                      width="800">

              <template v-slot:activator="{ on }">
                <v-btn v-on="on"
                       color="primary">
                  Add team members
                  <v-icon right>mdi-account-multiple-plus</v-icon>
                </v-btn>
              </template>

              <v_collaborate_new :project_string_id="project_string_id">
              </v_collaborate_new>

            </v-dialog>

          </v-card-actions>

        </v-card>
      </v-flex>
    </v-layout>
    <v-dialog v-model="dialog_confirm_sample_data" max-width="450px">
      <v-card >
        <v-card-title class="headline">
          Create sample data
        </v-card-title>
        <v-card-text>
          Do you want to create sample data?
          This will add 3 sample images to the directory: {{current_directory.nickname}}
        </v-card-text>
        <v_error_multiple :error="error_sample_data">
        </v_error_multiple>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn
            color="primary darken-1"
            text
            @click="dialog_confirm_sample_data = false"
          >
            Cancel
          </v-btn>
          <v-btn
            color="success darken-1"
            text
            :loading="loading_create_sample_data"
            @click="create_sample_dataset"
          >
           Create Sample Data
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
    <v-snackbar
      v-model="snackbar_success"
      :timeout="3000"
      color="primary"
    >
      Sample data created successfully.
      Look below at the input table to view
      the data.

      <template v-slot:action="{ attrs }">
        <v-btn
          color="white"
          text
          v-bind="attrs"
          @click="snackbar_success = false"
        >
          Close
        </v-btn>
      </template>
    </v-snackbar>
    <upload_wizard_dialog
      :project_string_id="project_string_id"
      :initial_dataset="undefined"
      ref="upload_wizard_dialog">

    </upload_wizard_dialog>
  </div>


</template>

<script lang="ts">
  // @ts-nocheck
  // because of beforeRouteLeave

  import Vue from "vue";

  import upload_wizard_dialog from "./input/upload_wizard_dialog.vue";
  import axios from "axios";
  import {create_event} from "./event/create_event";

  export default Vue.extend({
      name: 'upload_large',
      components: {
        upload_wizard_dialog
      },
      props: {
        'project_string_id': {
          default: null
        },
        'flow_id': {
          default: null
        },
        'initial_dataset':{
          default: undefined
        },
        'show_labels_button': {
          default: false
        },
        'mode': {
          // TODO declare a proper default mode not just assuming "null"
          default: null
        }
      },
      data: function () {
        return {
          v_collaborate_new: false,
          bucket_name: undefined,
          dialog_confirm_sample_data: false,
          loading_create_sample_data: false,


          snackbar_success: false,

          showSuccess: "Success",

          request_refresh: null,



          upload_header_message: "Upload images or videos",

          refresh_interval: null,
          error_sample_data: {},

          sync_job_list: [],

          loading_sync_jobs: false,

          is_actively_sending: false,

          tabs: 2,

          tab: null,

          job: {}

        }
      },

      beforeRouteLeave(to, from, next) {
        /*
         * Careful need to call next if we want here can't just
         * straight return
         * but do still need return after so other thing doesn't fire
         *
         * https://router.vuejs.org/guide/advanced/navigation-guards.html#in-component-guards
         *
         * Another way to do it is this
         * https://forum.vuejs.org/t/prevent-from-navigating-away/41932
         * but this seems cleaner
         * and could still add a fancy (non system) dialog thing in future...
         */

        if (this.is_actively_sending == false) {
          next()
          return
        }

        const answer = window.confirm(
          'Do you really want to leave? Upload in progress.')
        if (answer) {
          next()
        } else {
          next(false)
        }

      },
      watch: {

      },
      computed: {
        current_directory: function(){
          return this.$store.state.project.current_directory;
        },

      },

      created() {
        if (this.mode == "flow") {
          this.accepted_files = ".jpg, .jpeg, .png"
          this.upload_header_message = "Images uploaded here will be run on this flow."
        }
      },
      mounted(){
        this.add_visit_history_event();
      },
      destroyed() {
        // not actually clear if this is needed.
        clearInterval(this.refresh_interval)
      },
      methods: {
        open_upload_wizard_dialog: function(){
          this.$refs.upload_wizard_dialog.open();
        },
        upload_to_diffgram: function(file, pre_labeled_data){
          this.file_list_to_upload.push(file)
        },
        add_visit_history_event: async function(){
          const event_data = await create_event(this.$props.project_string_id, {
            page_name: 'import_dashboard',
            object_type: 'page',
            user_visit: 'user_visit',
          })
        },

        create_sample_dataset: async function(){
          this.loading_create_sample_data = true;
          try{
            const response = await axios.post('/api/walrus/v1/gen-data', {
              data_type: 'dataset',
              dataset_id: this.current_directory.directory_id,
              project_id: this.$store.state.project.current.id,
            })
            if(response.status === 200){
              this.request_refresh = Date.now();
              this.dialog_confirm_sample_data = false;
              this.snackbar_success = true;
            }
          }
          catch (error) {
            this.error_sample_data = this.$route_api_errors(error);
          }
          finally {
            this.loading_create_sample_data = false;
          }
        },
        open_confirm_dialog_sample_data: function(){
          this.dialog_confirm_sample_data = true;
        },


        // drop zone complete

        drop_zone_complete() {

          this.is_actively_sending = false

          // Not super happy with this but something to think on
          // how deeply we want to integrate this with upload
          // or if we even want to show this here at all

          if (Date.now() < this.request_refresh + 5000) {
            return
          }

          // current default mode
          if (!this.mode) {
            this.request_refresh = Date.now()

            var self = this

            // "fast" one
            setTimeout(function () {
              self.request_refresh = Date.now()
            }, 2500)

            // "ongoing" one, cleared at destroy
            // context of long running video operations may be 10 min+
            // and to user it could look like it's "frozen".
            // so we use perpetual thing till component is destroyed
            // long term I'm sure there's some more graceful way here

            this.refresh_interval = setInterval(function () {
              self.request_refresh = Date.now()
            }, 20000)

          }

          if (this.mode == 'flow') {

            var self = this
            setTimeout(function () {
              self.$store.commit('action_event_list_refresh')
            }, 3500)
            setTimeout(function () {
              self.$store.commit('action_event_list_refresh')
            }, 6000)

          }

        }

      }
    }
  ) </script>

<style scoped>
  .upload-container {
    padding: 0 2rem;
  }

  .upload-icon {
    color: #b8dbfd !important;
  }
</style>

