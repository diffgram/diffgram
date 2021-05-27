<template>
  <div v-if="!upload_source" class="d-flex justify-center flex-column">
    <h1 class="text-center">
      <v-icon x-large color="primary">mdi-upload</v-icon>
      Where do you want to upload your files from?
    </h1>
    <br>
    <br>
    <div class="d-flex justify-space-around">
      <v-btn
        x-large
        color="primary lighten-2"
        data-cy="from_connections_button"
        @click="set_upload_source('connections')"
      >
        <v-icon class="mr-4">mdi-cloud</v-icon>
        Cloud Providers
      </v-btn>
      <v-btn
        color="primary"
        x-large
        data-cy="from_local_button"
        @click="set_upload_source('local')"
      >
        <v-icon class="mr-4">mdi-laptop</v-icon>
        My Computer
      </v-btn>
    </div>
  </div>
  <div v-else-if="with_prelabeled == undefined && upload_mode === 'new'" class="d-flex justify-center flex-column">
    <h1 class="text-center">
      <v-icon x-large color="primary">mdi-upload</v-icon>
      Do you want to add Pre-Labeled data? (Json/Csv format)
    </h1>
    <br>
    <br>
    <div class="d-flex justify-space-around">
      <v-btn
        x-large
        data-cy="with_no_pre_labels_button"
        color="primary lighten-2"
        @click="set_with_pre_labeled(false)"
      >
        No
      </v-btn>
      <v-btn
        color="primary"
        x-large
        data-cy="with_pre_labels_button"
        @click="set_with_pre_labeled(true)"
      >
        Yes
      </v-btn>
    </div>
  </div>
  <v-card v-else elevation="0" style="height: 100%" class="ma-0 d-flex flex-column">
    <v-card-title v-if="upload_mode === 'update'">Update Files</v-card-title>
    <v-card-title v-if="upload_mode === 'new'">Upload New Files</v-card-title>
    <div class="d-flex justify-end align-center">

      <div class="pa-0">
        <button_with_menu
          tooltip_message="Import Settings"
          icon="settings"
          color="primary"
          :close_by_button="true"
        >
          <template slot="content">
            <v-layout column class="pa-0">

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
    <v-card-text v-if="upload_mode === 'new' || 'update'">

      <v-container style="height: 100%" fluid class="pa-0 pl-4" column>


        <v-row
          style="height: 100%;"
          v-if="$store.state.project.current_directory && Object.keys($store.state.project.current_directory).length > 0">
          <v-col cols="8"

                 class="pa-4">
            <v-layout column>
              <v-row v-if="upload_source === 'connections'">
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
              <v-row v-if="upload_source === 'connections'">
                <v-col cols="12" class="pa-0">

                  <connector_import_renderer
                    :project_string_id="project_string_id"
                    :connection="incoming_connection"
                    :video_split_duration="video_split_duration"
                    @update_bucket_name="update_bucket_name"
                    @update_file_list="update_file_list_from_connection"
                    ref="connection_import_renderer"
                  >
                  </connector_import_renderer>
                </v-col>
              </v-row>
              <v-row v-if="upload_source === 'local'">
                <vue-dropzone class="mb-12 d-flex align-center justify-center" ref="myVueDropzone" id="dropzone"
                              data-cy="vue-dropzone"
                              style="min-height: 350px"
                              :useCustomSlot=true
                              :options="dropzoneOptions"
                              @vdropzone-upload-progress="update_progress"
                              @vdropzone-file-added="file_added"
                              v-on:vdropzone-thumbnail="thumbnail"
                              @vdropzone-sending="drop_zone_sending_event"
                              @vdropzone-complete="drop_zone_complete">
                  <div class="dropzone-custom-content">
                    <v-icon class="upload-icon" size="84">mdi-cloud-upload</v-icon>
                    <h3 class="dropzone-custom-title">Desktop Drag and Drop</h3>
                  </div>

                </vue-dropzone>

              </v-row>
            </v-layout>
          </v-col>
          <v-col cols="4" class="pa-0  ma-0 pt-10" style="max-height: 600px; overflow-y: auto">
            <h2>Data to Upload: </h2>
            <v-data-table hide-default-footer :headers="file_table_headers" :items="file_list_to_upload">
              <template v-slot:body="{ items }">
                <tbody>
                <tr v-for="file in file_list_to_upload.filter(f => f.data_type === 'Annotations')">
                  <td>
                    <p class="secondary--text ma-0"><strong>{{ file.name }}</strong></p>
                  </td>
                  <td>
                    <p class="secondary--text  ma-0"><strong>
                      <v-icon color="secondary">mdi-brush</v-icon>
                      {{file.data_type}}</strong></p>
                  </td>
                  <td>
                    <v-btn color="error" icon @click="remove_file(file)">
                      <v-icon>mdi-delete</v-icon>
                    </v-btn>
                  </td>

                </tr>
                <tr v-for="file in file_list_to_upload.filter(f => f.data_type !== 'Annotations')">
                  <td>
                    <p class="ma-0"><strong>{{ file.name }}</strong></p>
                  </td>
                  <td>
                    <p class="ma-0"><strong>
                      <v-icon>mdi-file</v-icon>
                      {{file.data_type}}</strong></p>
                  </td>
                  <td>
                    <v-btn color="error" icon @click="remove_file(file)">
                      <v-icon>mdi-delete</v-icon>
                    </v-btn>
                  </td>

                </tr>
                </tbody>
              </template>
            </v-data-table>
          </v-col>

        </v-row>
        <v-alert class="pa-4 ma-8" v-else type="warning"> Please select a dataset/directory to upload files.

        </v-alert>
        <v-row>
          <v_error_multiple :error="error_file_uploads"></v_error_multiple>
        </v-row>
        <v-row>

        </v-row>
      </v-container>


    </v-card-text>
    <v-card-actions class="d-flex justify-end flex-grow-1" style="align-items: center">
      <div>
        <v_error_multiple :error="error">
        </v_error_multiple>
        <v-btn @click="move_to_next_step"
               x-large
               data-cy="continue_upload_step"
               :loading="loading_annotations"
               color="primary"
               :disabled="should_disable_continue">
          Continue
        </v-btn>
      </div>
    </v-card-actions>
  </v-card>
</template>

<script lang="ts">
  import axios from 'axios';
  import Vue from "vue";
  import connector_import_renderer from "../connectors/connector_import_renderer";
  import mime from 'mime-types';

  export default Vue.extend({
      name: 'new_or_update_upload_screen',
      components: {
        connector_import_renderer,
      },
      props: {
        'project_string_id': {
          default: null
        },
        'initial_dataset': {
          default: undefined
        },
        'error_file_uploads': {
          default: null
        },
        'batch': {
          default: null
        },
        'upload_mode': {
          default: null
        }

      },

      data() {

        return {
          file_list_to_upload: [],
          error: {},
          sync_job_list: [],
          current_directory: undefined,
          with_prelabeled: undefined,
          connection_upload_error: undefined,
          file_update_error: undefined,
          loading_annotations: false,
          upload_source: null,
          accepted_annotation_file_types: ['json', 'csv'],
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
          bucket_name: undefined,
          incoming_connection: null,
          upload_mode_toggle: 0,
          video_split_duration: 60,
        }


      },
      computed: {
        should_disable_continue: function () {
          if (this.$props.upload_mode === 'new') {
            if (this.file_list_to_upload.length === 0 ||
              this.file_list_to_upload.filter(f => f.data_type === 'Raw Media').length === 0) {
              return true
            }
          }
          if (this.$props.upload_mode === 'update') {
            if (this.file_list_to_upload.length === 0) {
              return true
            }
          }
          return false;
        },
        cloud_col_count: function () {
          if (!this.incoming_connection || !this.incoming_connection.id) {
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
                if (file.type === 'application/json' || file.type === 'text/csv') {
                  file.data_type = 'Annotations';
                } else {
                  file.data_type = 'Raw Media';
                }
                file.source = 'local';
                $vm.file_list_to_upload.push(file);
                console.log('FILEEEE', file)

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
            height: 450,
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
            acceptedFiles: this.accepted_files,
            previewTemplate: this.template()
          }

        }
      },
      watch: {
        upload_mode: function (new_val) {
          this.$emit('upload_mode_change', new_val)
        },
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
        template: function () {
          return `<div class="dz-preview dz-file-preview" style="width: 150px; height: 150px;">
              <div class="dz-image" style="width: 150px; height: 150px;">
                  <div style="width: 150px; height: 150px;" data-dz-thumbnail-bg></div>
              </div>
              <div class="dz-details">
                  <div class="dz-size"><span data-dz-size></span></div>
                  <div class="dz-filename"><span data-dz-name></span></div>
              </div>
              <div class="dz-success"><i class="fa fa-check"></i></div>
              <div class="dz-error-message"><span data-dz-errormessage></span></div>
              <div class="dz-success-mark"><i class="fa fa-check"></i></div>
              <div class="dz-error-mark"><i class="fa fa-close"></i></div>
          </div>`;
        },
        thumbnail: function(file, dataUrl) {
          var j, len, ref, thumbnailElement;
          if (file.previewElement) {
            file.previewElement.classList.remove("dz-file-preview");
            ref = file.previewElement.querySelectorAll("[data-dz-thumbnail-bg]");
            for (j = 0, len = ref.length; j < len; j++) {
              thumbnailElement = ref[j];
              thumbnailElement.alt = file.name;
              thumbnailElement.style.backgroundImage = 'url("' + dataUrl + '")';
            }
            return setTimeout(((function (_this) {
              return function () {
                return file.previewElement.classList.add("dz-image-preview");
              };
            })(this)), 1);
          }
        },
        set_with_pre_labeled: function (val) {
          console.log('aaaaa', val)
          this.with_prelabeled = val;
          this.$emit('complete_question', 4);
        },
        set_upload_source: function (val) {
          this.upload_source = val;
          this.$emit('complete_question', 3);
        },
        update_file_list_from_connection: function (file_list) {
          const to_add = [];
          for (const item of file_list) {
            let data_type = 'Raw Media';
            const extension = item.name.split('.').pop();
            console.log('es', extension)
            if (extension && this.accepted_annotation_file_types.includes(extension)) {
              data_type = 'Annotations'
            }
            to_add.push({
              ...item,
              source: 'connection',
              data_type: data_type,
              type: mime.lookup(extension)
            })
          }
          this.file_list_to_upload = this.file_list_to_upload.filter(item => item.source !== 'connection');
          this.file_list_to_upload = [...this.file_list_to_upload, ...to_add]
          this.$emit('file_list_updated', this.file_list_to_upload)
        },
        reset_total_files_size: function (file) {
          this.$emit('reset_total_files_size')
        },
        file_added: function (file) {
          this.$emit('file_added', file)
        },
        update_progress: function (file, totalBytes, totalBytesSent) {
          this.$emit('progress_updated', file, totalBytes, totalBytesSent)
        },
        upload_local_raw_media: async function (local_file_list) {
          if (!local_file_list || local_file_list.length === 0) {
            return
          }
          // We want to remove them because we'll re-add them with the batch data and uuid data.
          for (const file of this.$refs.myVueDropzone.dropzone.files) {
            const new_file_data = local_file_list.find(elm => elm.upload.uuid === file.upload.uuid)
            if (!new_file_data) {
              // If there's no match its because we are handling the prelabeled data json or csv, so we discard it here.
              this.$refs.myVueDropzone.removeFile(file);
              continue
            }

            file.uuid = new_file_data.uuid;
            file.input_batch_id = new_file_data.input_batch_id;
          }
          this.$refs.myVueDropzone.processQueue();
        },
        update_progress_percentage: function (percent) {
          this.$emit('update_progress_percentage', percent)
        },
        upload_connection_raw_media: async function (connection_file_list) {
          if (!connection_file_list || connection_file_list.length === 0) {
            return
          }
          const connector_id = this.incoming_connection.id;
          const directory_id = this.$store.state.project.current_directory.directory_id;
          try {
            let processed_files = 0;
            await Promise.all(connection_file_list.map(async (file) => {
              const data = await axios.post(`/api/walrus/v1/connectors/${connector_id}/fetch-data`, {
                opts: {
                  action_type: 'fetch_folder',
                  path: [file.id],
                  directory_id: directory_id,
                  bucket_name: this.bucket_name,
                  video_split_duration: this.$props.video_split_duration,
                  job_id: this.$props.job_id,
                  batch_id: this.$props.batch.id,
                  file_uuid: file.uuid,
                },
                project_string_id: this.$props.project_string_id
              });

              if (data.status === 200 && !data.data.error) {
                processed_files += 1;
                this.update_progress_percentage((processed_files * 1.0 / connection_file_list.length) * 100);
                return data;

              }
            }));

          } catch (error) {
            // Discuss if there already exists a good abstraction for error handling.
            this.connection_upload_error = this.$route_api_errors(error);
            this.$emit('error_update_files', this.connection_upload_error)
            console.error(error);
          }
        },
        update_files: async function (file_data) {
          try {
            let processed_files = 0;
            await Promise.all(Object.keys(file_data).map(async (file_key) => {
              const file = file_data[file_key]
              const data = await axios.post(`/api/walrus/v1/project/${this.$props.project_string_id}/input/packet`, {
                file_id: file.file_id,
                instance_list: file.instance_list,
                frame_packet_map: file.frame_packet_map,
                mode: 'update',
                batch_id: this.$props.batch.id,
                project_string_id: this.$props.project_string_id,
                extract_labels_from_batch: true
              });
              if (data.status === 200 && !data.data.error) {
                this.$emit('error_update_files', undefined);
                processed_files += 1;
                this.update_progress_percentage((processed_files * 1.0 / Object.keys(file_data).length) * 100);
                return data;

              }
            }));

          } catch (error) {
            this.file_update_error = this.$route_api_errors(error);
            this.$emit('file_update_error', this.file_update_error)
            console.error(error);
          }

        },
        upload_raw_media: async function (file_list) {
          this.$emit('upload_in_progress')
          if (this.$props.upload_mode === 'update') {
            await this.update_files(file_list)
          } else if (this.$props.upload_mode === 'new') {
            const local_file_list = file_list.filter(f => f.source === 'local');
            await this.upload_local_raw_media(local_file_list);
            const connection_file_list = file_list.filter(f => f.source === 'connection');
            await this.upload_connection_raw_media(connection_file_list);
          } else {
            throw new Error('Invalid upload mode.')
          }

        },
        move_to_next_step: function () {
          const annotationFile = this.file_list_to_upload.filter(f => f.data_type === 'Annotations');
          const raw_media = this.file_list_to_upload.filter(f => f.data_type === 'Raw Media');
          if(this.with_prelabeled && annotationFile.length === 0){
            this.error = {}
            this.error.pre_labeled_data = 'Please upload your pre labeled data on a JSON or CSV file to continue.'
            return
          }
          if (this.$props.upload_mode === 'update') {
            if (raw_media.length > 0) {
              this.error = {}
              this.error.media_files = 'Media file not allowed in update mode. Please upload a CSV or a JSON file.'
              return
            }
            if (annotationFile.length != 1) {
              this.error = {}
              this.error.annotations_file = 'Please upload just 1 annotation file.'
              return
            }

          } else if (this.$props.upload_mode === 'new') {
            if (raw_media.length === 0) {
              this.error = {}
              this.error.media_files = 'Please upload at least one media file to continue.'
              return
            }
          }
          if (annotationFile.length === 0) {
            // No Annotations Case, jump to last step
            this.$emit('change_step_no_annotations')
            this.$emit('complete_question', 17)

          } else {
            // No Annotations Case, jump to last step
            this.$emit('change_step_annotations')
            this.$emit('complete_question', 5)
          }

        },
        remove_file: function (file) {
          this.error = undefined;
          if (file.source === 'local') {
            this.$refs.myVueDropzone.removeFile(file)
          } else if (file.source === 'connection') {
            this.$refs.connection_import_renderer.remove_selection(file)
          }
        },
        update_bucket_name: function (name) {
          this.bucket_name = name
        },
        drop_zone_sending_event(file, xhr, formData) {
          // Doing this here since options doesn't update properly
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


        },

      }
    }
  ) </script>

<style scoped>
  .vue-dropzone {
    max-height: 350px;
    width: 83%;
    display: flex;
    flex-wrap: wrap;
    overflow-y: auto;
  }
</style>
