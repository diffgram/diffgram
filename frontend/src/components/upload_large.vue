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

                      <v-row class="pa-0">
                        <v-col class="pa-0">
                          <h2>To: </h2>
                        </v-col>
                      </v-row>

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

                    <v-row class="d-flex align-center">

                      <v_directory_list v-if="!mode"
                                        :set_from_id="initial_dataset ? initial_dataset.directory_id : undefined"
                                        :show_text_buttons="true"
                                        :project_string_id="project_string_id"
                                        @change_directory="on_change_directory"
                                        :show_new="true"
                                        :show_update="true"
                      >
                      </v_directory_list>

                      <tooltip_button
                          tooltip_message="Generate Sample Data"
                          @click="open_confirm_dialog_sample_data"
                          icon="mdi-apps-box"
                          :bottom="true"
                          :icon_style="true"
                          color="primary">
                      </tooltip_button>


                      <div class="pa-4">
                        <button_with_menu
                          tooltip_message="Import Settings"
                          icon="settings"
                          color="primary"
                          :close_by_button="true"
                        >
                          <template slot="content">
                            <v-layout column class="pa-6">

                              <v-alert type="info">
                                Select desired setting before uploading. <br>
                                Lower duration results in faster import.
                              </v-alert>

                              <v-slider
                                label="Video Split Duration"
                                min=0
                                max=240
                                step=10
                                thumb-label="always"
                                ticks
                                hint="In Seconds. Set to 0 to disable."
                                persistent-hint
                                v-model="video_split_duration">
                              </v-slider>

                              <!-- TODO put FPS settings here too? -->

                            </v-layout>
                          </template>

                        </button_with_menu>
                      </div>
                    </v-row>

                    <v-row >
                      <v-alert v-if="sync_job_list
                            && sync_job_list.length != 0"
                          dismissible type="info">

                        <p class="ma-0" style="font-size: 12px"> When importing to directory
                          "{{this.$store.state.project.current_directory.nickname}}",
                          tasks will be created for the following jobs: </p>

                        <ul v-if="!loading_sync_jobs">

                          <li v-for="job in sync_job_list" class="ma-0"
                              style="list-style-type: none; font-size: 12px">
                            <v-icon style="font-size: 16px">mdi-sync</v-icon>
                            {{job.name}}
                          </li>
                        </ul>
                        <v-progress-circular v-else indeterminate></v-progress-circular>
                      </v-alert>
                    </v-row>

                      <!--                     <v-col cols="4" class="ml-6">-->
                      <!--                       -->
                      <!--                       <job_select-->
                      <!--                         label="Job (Optional)"-->
                      <!--                         :view_only_mode="false"-->
                      <!--                         v-model="job"-->
                      <!--                         :status="['draft', 'active', 'in_review', 'reported', 'save_for_later']"-->
                      <!--                       >-->

                      <!--                       </job_select>-->
                      <!--                        -->
                      <!--                     </v-col>-->




                  </v-layout>
                </v-col>
              </v-row>
            </v-layout>
          </v-card-text>
        </v-card>
        <v-card elevation="0" class="mb-5">
          <v-card-text class="pa-0">


            <v-layout class="pa-8" column>
              <v-row class="pa-0">
                <v-col class="pa-0">
                  <h2>From: </h2>
                </v-col>
              </v-row>
              <v-row
                v-if="$store.state.project.current_directory && Object.keys($store.state.project.current_directory).length > 0">
                <v-col :cols="cloud_col_count" class="pa-4">
                  <v-layout column>
                    <v-row>
                      <v-col cols="12" class="pa-0">
                        <connection_select
                          :project_string_id="project_string_id"
                          v-model="incoming_connection"
                          :show_new="true"
                          :features_filters="{files_import: true, files_export:true}"
                          data-cy="connection-select"
                        >
                        </connection_select>
                      </v-col>
                    </v-row>
                    <v-row>
                      <v-col cols="12" class="pa-0">

                        <connector_import_renderer
                          :project_string_id="project_string_id"
                          :connection="incoming_connection"
                          :video_split_duration="video_split_duration"
                          :job_id="job.id"
                          @update_bucket_name="update_bucket_name"
                          ref="connection_import_renderer"
                        >
                        </connector_import_renderer>
                      </v-col>
                    </v-row>
                  </v-layout>
                </v-col>
                <v-col v-if="!bucket_name || bucket_name == ''" cols="6" class="pa-4">
                  <vue-dropzone class="mb-12 d-flex align-center justify-center" ref="myVueDropzone" id="dropzone"
                                data-cy="vue-dropzone"
                                style="min-height: 120px"
                                :useCustomSlot=true
                                :options="dropzoneOptions"
                                @vdropzone-sending="drop_zone_sending_event"
                                @vdropzone-complete="drop_zone_complete">
                    <div class="dropzone-custom-content">
                      <v-icon class="upload-icon" size="84">mdi-cloud-upload</v-icon>
                      <h3 class="dropzone-custom-title">Desktop Drag and Drop</h3>
                    </div>
                  </vue-dropzone>

                </v-col>
              </v-row>
              <v-row  v-if="!bucket_name || bucket_name == ''">
                <v-col cols="12" class="d-flex justify-center">
                  <v-btn
                    :disabled="file_list_to_upload.length === 0"
                    @click="open_upload_wizard_dialog"
                    color="success"
                    x-large>
                    Start Uploading {{file_list_to_upload.length}} files.
                  </v-btn>
                </v-col>
              </v-row>
              <v-alert class="pa-4 ma-8" v-else type="warning"> Please select a dataset/directory to upload files.

              </v-alert>
              <v-row class="d-flex justify-end">
                <v-col cols="2">
                  <v-btn v-if="!mode && show_labels_button"
                         color="blue"
                         outlined
                         @click="$router.push('/project/' +
                        $store.state.project.current.project_string_id
                        + '/labels')">
                    Continue to Labels
                  </v-btn>
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
                          @start_upload="upload_to_diffgram"
                          :file_list="file_list_to_upload"
                          ref="upload_wizard_dialog"></upload_wizard_dialog>
  </div>


</template>

<script lang="ts">
  // @ts-nocheck
  // because of beforeRouteLeave

  import Vue from "vue";
  import Connector_import_renderer from "./connectors/connector_import_renderer.vue";
  import upload_wizard_dialog from "./input/upload_wizard_dialog.vue";
  import axios from "axios";
  import {create_event} from "./event/create_event";

  export default Vue.extend({
      name: 'upload_large',
      components: {
        Connector_import_renderer,
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
          file_list_to_upload: [],
          dialog_confirm_sample_data: false,
          loading_create_sample_data: false,

          incoming_connection: null,
          snackbar_success: false,

          showSuccess: "Success",

          request_refresh: null,

          accepted_files: ".jpg, .jpeg, .png, .mp4, .m4v, .mov, .avi, .csv, .txt",

          upload_header_message: "Upload images or videos",

          refresh_interval: null,
          error_sample_data: {},

          sync_job_list: [],

          loading_sync_jobs: false,

          video_split_duration: 60,

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
        incoming_connection: function(newval, oldval){
          if(!this.newval){
            this.bucket_name = undefined;
          }
        }
      },
      computed: {
        cloud_col_count: function(){
          if(!this.incoming_connection){
            return 6
          }
          if(this.bucket_name !== ''){
            return 12
          }
        },
        current_directory: function(){
          return this.$store.state.project.current_directory;
        },
        dropzoneOptions: function () {

          // CAUTION despite being a computed property any values that CHANGE
          // after component is created don't seem to get actually reflected sometimes...
          // The drop zone options things doesn't update well from vuex, depsite being a computed prop
          // I think the actual vue js dropzone thing may be updating properly though
          // (Context of moving to using drop_zone_sending_event() for thing from vuex)
          const $vm = this;
          return {
            init: function(){
              this.on("addedfile", function(file) {
                $vm.file_list_to_upload.push(file);
              });
              this.on('removedfile', function(file){
                $vm.file_list_to_upload.splice($vm.file_list_to_upload.indexOf(file), 1);
              });
            },
            url: '/api/walrus/project/' + this.project_string_id + '/upload/large',
            chunking: true,
            addRemoveLinks: true,
            forceChunking: true,
            autoProcessQueue: false,
            chunkSize: 1024 * 1024 * 5,
            height: 120,
            // number of concurrent uploads at a time, each upload still goes at same speed
            parallelUploads: 1,

            thumbnailWidth: 150,
            thumbnailHeight: 150,
            maxFilesize: 5000,
            headers: {
              "project_string_id": this.project_string_id,
              "mode": this.mode,
              "flow_id": this.flow_id
            },
            acceptedFiles: this.accepted_files
          }

        }
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
        update_bucket_name: function(name){
          this.bucket_name = name
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
        drop_zone_sending_event(file, xhr, formData) {

          // Doing this here since options doesn't update properly

          formData.append('directory_id',
            this.$store.state.project.current_directory.directory_id);

          formData.append('video_split_duration',
            this.video_split_duration);
          if (this.job && this.job.id) {
            formData.append('job_id',
              this.job.id);
          }


          this.is_actively_sending = true
        },

        // drop zone complete
        async on_change_directory(directory) {
          this.loading_sync_jobs = true;
          this.sync_job_list = await this.update_sync_jobs_list(directory)
          this.loading_sync_jobs = false
        },
        async update_sync_jobs_list(dir) {
          try {
            if (!dir || !dir.jobs_to_sync || !dir.jobs_to_sync.job_ids || !dir.jobs_to_sync.job_ids.length > 0) {
              return []
            }
            const response = await axios.post('/api/v1/job/list', {
              metadata: {
                mode_data: 'job_detail',
                builder_or_trainer: {
                  mode: 'builder'
                },
                project_string_id: this.$store.state.project.current.project_string_id,
                status: 'active',
                job_ids: dir.jobs_to_sync.job_ids
              }


            })

            if (response.data.Job_list) {
              return response.data.Job_list
            }
          } catch (error) {
            console.error(error);
          }
        },
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

