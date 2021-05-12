<template>
  <v-card elevation="0" class="mb-5">
    <div class="d-flex justify-end align-center">
      <v-btn-toggle v-model="upload_mode_toggle" color="secondary">
        <v-btn @click="upload_mode = 'new'">Upload New Data</v-btn>
        <v-btn @click="upload_mode = 'update'">Update Existing</v-btn>
      </v-btn-toggle>
      <div class="pa-4">
        <v_error_multiple :error="error">
        </v_error_multiple>
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
    </div>
    <v-card-text class="pa-0" v-if="upload_mode === 'new'">

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

        <v-alert class="pa-4 ma-8" v-else type="warning"> Please select a dataset/directory to upload files.

        </v-alert>
      </v-layout>
      <h2>Uploaded Data: </h2>
      <v-data-table hide-default-footer :headers="file_table_headers" :items="file_list_to_upload">
        <template v-slot:body="{ items }">
          <tbody>
          <tr v-for="file in file_list_to_upload.filter(f => f.data_type === 'Annotations')">
            <td>
              <p class="secondary--text"><strong>{{ file.name }}</strong></p>
            </td>
            <td>
              <p class="secondary--text"><strong><v-icon color="secondary">mdi-brush</v-icon>{{file.data_type}}</strong></p>
            </td>
            <td><v-btn color="error" icon @click="remove_file(file)"> <v-icon>mdi-delete</v-icon></v-btn></td>

          </tr>
          <tr v-for="file in file_list_to_upload.filter(f => f.data_type !== 'Annotations')">
            <td>
              <p><strong>{{ file.name }}</strong></p>
            </td>
            <td>
              <p><strong><v-icon>mdi-file</v-icon>{{file.data_type}}</strong></p>
            </td>
            <td><v-btn color="error" icon @click="remove_file(file)"> <v-icon>mdi-delete</v-icon></v-btn></td>

          </tr>
          </tbody>
        </template>
      </v-data-table>
      <div class="d-flex justify-end pa-4">
        <v-btn @click="move_to_next_step"
               x-large
               color="primary"
               :disabled="file_list_to_upload.length === 0 || file_list_to_upload.filter(f => f.data_type === 'Raw Media').length === 0">
          Continue
        </v-btn>
      </div>
    </v-card-text>
  </v-card>
</template>

<script lang="ts">
  import axios from 'axios';
  import Vue from "vue";
  import connector_import_renderer from "../connectors/connector_import_renderer";

  export default Vue.extend({
      name: 'new_or_update_upload_screen',
      components: {
        connector_import_renderer,
      },
      props: {
        'project_string_id': {
          default: null
        }
      },

      data() {

        return {
          file_list_to_upload: [],
          error: {},
          accepted_files: ".jpg, .jpeg, .png, .mp4, .m4v, .mov, .avi, .csv, .txt, .json",
          file_table_headers: [
            {
              text: 'File Name',
              align: 'start',
              sortable: false,
              value: 'diffgram_value',
            },
            {
              text: 'Data Type',
              value: 'type',
              align: 'start',
              sortable: false,
            },
            {
              text: 'Actions',
              value: 'file_value',
              align: 'start',
              sortable: false,
            },
          ],
          upload_mode: 'new',
          bucket_name: undefined,
          incoming_connection: null,
          upload_mode_toggle: 0,
          video_split_duration: 60,
        }


      },
      computed: {
        cloud_col_count: function () {
          if (!this.incoming_connection) {
            return 6
          }
          if (this.bucket_name !== '') {
            return 12
          }
        },
        dropzoneOptions: function () {

          // CAUTION despite being a computed property any values that CHANGE
          // after component is created don't seem to get actually reflected sometimes...
          // The drop zone options things doesn't update well from vuex, depsite being a computed prop
          // I think the actual vue js dropzone thing may be updating properly though
          // (Context of moving to using drop_zone_sending_event() for thing from vuex)
          const $vm = this;
          return {
            init: function () {
              this.on("addedfile", function (file) {
                console.log('added file', file)
                if (file.type === 'application/json' || file.type === 'text/csv') {
                  file.data_type = 'Annotations';
                } else {
                  file.data_type = 'Raw Media';
                }
                $vm.file_list_to_upload.push(file);
                $vm.$emit('file_list_updated', $vm.file_list_to_upload)
              });
              this.on('removedfile', function (file) {
                $vm.file_list_to_upload.splice($vm.file_list_to_upload.indexOf(file), 1);
                $vm.$emit('file_list_updated', $vm.file_list_to_upload)
              });
            },
            url: '/api/walrus/project/' + this.project_string_id + '/upload/large',
            chunking: true,
            // addRemoveLinks: true,
            forceChunking: true,
            autoProcessQueue: false,
            chunkSize: 1024 * 1024 * 5,
            height: 200,
            // number of concurrent uploads at a time, each upload still goes at same speed
            parallelUploads: 1,

            thumbnailWidth: 75,
            thumbnailHeight: 75,
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
      watch: {
        incoming_connection: function (newval, oldval) {
          if (!this.newval) {
            this.bucket_name = undefined;
          }
        }
      },
      mounted() {
      },

      beforeDestroy() {

      },

      methods: {
        upload_raw_media: async function(file_list){
          this.$refs.myVueDropzone.dropzone.removeAllFiles()
          for(const file of file_list){
            this.$refs.myVueDropzone.manuallyAddFile(file, file.dataURL)
            this.file_list_to_upload.push(file);
          }
          this.$refs.myVueDropzone.processQueue();
          alert('upload started!')
        },
        move_to_next_step: function(){
          const annotationFile = this.file_list_to_upload.filter(f => f.data_type === 'Annotations');
          const raw_media = this.file_list_to_upload.filter(f => f.data_type === 'Raw Media');
          if(raw_media.length === 0){
            this.error.media_files = 'Please upload at least one media file to continue.'
            return
          }
          if (annotationFile.length === 0){
            // No Annotations Case, jump to last step
            this.$emit('change_step_no_annotations')
          }
          else{
            // No Annotations Case, jump to last step
            this.$emit('change_step_annotations')
          }
        },
        remove_file: function(file){
          console.log('this.$refs.myVueDropzone.', this.$refs.myVueDropzone)
          this.$refs.myVueDropzone.removeFile(file)
        },
        update_bucket_name: function (name) {
          this.bucket_name = name
        },
        drop_zone_sending_event(file, xhr, formData) {

          // Doing this here since options doesn't update properly
          console.log('AAAADDD PARAPMS', file);
          formData.append('directory_id',
            this.$store.state.project.current_directory.directory_id);

          formData.append('video_split_duration',
            this.video_split_duration);
          formData.append('uuid', file.uuid);
          formData.append('input_batch_id', file.input_batch_id);
          if (this.job && this.job.id) {
            formData.append('job_id',
              this.job.id);
          }


          this.is_actively_sending = true
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
  .vue-dropzone{
    max-height: 200px;
    display: flex;
    flex-wrap: wrap;
    overflow-y: scroll;
  }
</style>
