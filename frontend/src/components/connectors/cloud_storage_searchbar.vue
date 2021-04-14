<template>
  <v-container fluid class="text-center pa-0">
    <v-row class="flex ma-0" >
      <v-col cols="12" class="pa-0">
        <v-skeleton-loader :loading="isFetchingBuckets" height="82px" type="list-item"
                           class="full-width skeleton-loader-autocomplete">
          <diffgram_select
            v-if="Object.keys(error_connection).length === 0"
            :item_list="bucket_list"
            v-model="bucket"
            label="Select your bucket"
            :disabled="!connection"
            data-cy="bucket-selector"
            @change="change_bucket"
          >
          </diffgram_select>
          <v_error_multiple :error="error_connection">
          </v_error_multiple>
          <connection_docs_suggest :error="error_connection" :integration_name="connection.integration_name"></connection_docs_suggest>
        </v-skeleton-loader>
      </v-col>
    </v-row>
    <v-row>
      <v-col cols="12">
          <v-skeleton-loader v-if="Object.keys(error_connection).length === 0" :loading="isFetchingBuckets || loading" height="200px" type="card"
                             class="full-width skeleton-loader-autocomplete">
            <v-card elevation="1"
                    style="max-height: 600px"
                    class="overflow-y-auto">

              <v-container class="d-flex justify-start ma-0"
                           v-if="!bucket_empty">

                <v-treeview v-model="selection"
                            selectionType="leaf"
                            selectable
                            selected-color="blue"
                            :load-children="fetch_folder"
                            return-object
                            :items="items">
                  <template v-slot:prepend="{ item, open }">
                    <v-icon v-if="item.name.endsWith('/')" :data-cy="`import-select-node-${item.name}`">
                      mdi-folder
                    </v-icon>
                    <v-icon v-else :data-cy="`import-select-node-${item.name}`">
                      mdi-file
                    </v-icon>
                  </template>
                </v-treeview>

              </v-container>

              <v-container v-else>

                <v-row class="d-flex flex-column justify-center align-center">
                  <v-card-title class="d-flex justify-center">
                    <h3 class="text-center">This bucket is empty, please use a non-empty bucket.</h3>
                  </v-card-title>
                  <v-card-text>
                    <v-icon size="180">
                      mdi-file-cloud
                    </v-icon>
                  </v-card-text>
                </v-row>

              </v-container>
            </v-card>
          </v-skeleton-loader>
      </v-col>
    </v-row>
    <v-row v-if="Object.keys(error_connection).length === 0">
      <v-col cols="12">
        <v-btn
               :disabled="(loading && status_test_connection !== 200) || (bucket === '' || bucket_empty) || this.selection.length === 0"
               large
               id="google-import-button"
               color="success"
               data-cy="show-import-dialog"
               @click="show_confirm_dialog">
          Import to Diffgram
        </v-btn>
      </v-col>
    </v-row>
    <v-row class="flex ma-0" justify="space-between">
      <v-col padding="0" cols="12" class="pa-0 d-flex flex-row align-center ma-0">
        <v-dialog
          v-model="dialog"
          id="import-dialog"
          max-width="290"
        >
          <v-card>
            <v-card-title class="headline">Import from 3rd Party Cloud Storage Service?</v-card-title>

            <v-card-text>
              <div v-if="importStatus == 'pending'">
                <p>
                  Are you sure you want to start importing the selected files?
                </p>
                <p><strong>You are about to import {{selection.length}} items.</strong></p>
              </div>

              <p v-else-if="importStatus === 'loading'">
                Starting folder import...
                <v-progress-circular
                  indeterminate
                  color="primary">

                </v-progress-circular>
              </p>
              <div v-else-if="importStatus === 'success'">
                <p>Folder import started successfully! Files are now being imported to Diffgram.</p>
                <br>
                <p class="align-center text-center">
                  <v-icon right color="success" size="x-large" dark dense class="display-3" data-cy="success-check">
                    mdi-check
                  </v-icon>
                </p>
              </div>
              <div v-else-if="importStatus === 'error'">
                <p>There was an error starting the import. Please check your connection.</p>
                <br>
                <p class="align-center text-center">
                  <v-icon right color="error" size="x-large" dark dense class="display-3"> mdi-alert-decagram</v-icon>
                </p>
                <v_error_multiple :error="import_error">
                </v_error_multiple>
                <connection_docs_suggest :error="error" :integration_name="connection.integration_name"></connection_docs_suggest>
              </div>
            </v-card-text>

            <v-card-actions v-if="importStatus != 'success'">
              <v-spacer></v-spacer>

              <v-btn
                color="gray darken-1"
                text
                @click="dialog = false"
              >
                Cancel
              </v-btn>

              <v-btn
                color="green darken-1"
                text
                data-cy="start-importing"
                @click="start_folder_fetch"
              >
                Start Importing
              </v-btn>
            </v-card-actions>

            <v-card-actions v-else class="d-flex justify-center">
              <v-btn
                color="gray darken-1"
                text
                data-cy="close-import-dialog"
                @click="close_success_dialog"
              >
                Close
              </v-btn>
            </v-card-actions>
          </v-card>
        </v-dialog>
      </v-col>

    </v-row>

  </v-container>
</template>

<script>
  import {debounce} from "debounce";
  import axios from 'axios';
  import {mapState} from 'vuex'
  import diffgram_select from '../regular/diffgram_select'
  import connection_docs_suggest from '../connection/connection_docs_suggest'

  export default {
    props: ['connection', 'project_string_id', 'label', 'video_split_duration', 'job_id'],
    name: "cloud_storage_searchbar",
    components: {
      'diffgram_select': diffgram_select,
      'connection_docs_suggest': connection_docs_suggest
    },
    data() {
      return {
        items: [],
        selection: [],
        dialog: false,
        loading: true,
        bucket_empty: false,
        isFetchingBuckets: false,
        bucket_list: [],
        bucket: '',
        error_connection: {},
        import_error: {},
        importStatus: 'pending',
        status_test_connection: -1,


      }
    },
    created() {
      this.list_buckets();
    },
    methods: {
      fetch_folder: function (item) {
        const connector_id = this.connection.id;
        return axios.post(`/api/walrus/v1/connectors/${connector_id}/fetch-data`,
          {
            opts: {
              action_type: 'get_folder_contents',
              path: item.name,
              bucket_name: this.bucket
            },
            project_string_id: this.$props.project_string_id
          })
          .then(res => {
            const new_folders = res.data.result;
            const new_structure = this.create_folder_structure(new_folders)
            item.children = new_structure;
          })

          .catch(error => {
            this.error_connection = this.$route_api_errors(error);
          })
      },
      init_tree_data: async function () {
        if (this.bucket === '') return
        try {
          this.loading = true;
          const connector_id = this.connection.id;
          const data = await axios.post(`/api/walrus/v1/connectors/${connector_id}/fetch-data`, {
            opts: {
              action_type: 'get_folder_contents',
              path: '',
              bucket_name: this.bucket
            },
            project_string_id: this.$props.project_string_id
          });
          this.folder_contents = data.data.result;
          const num_files = data.data.result.filter(elm => !elm.endsWith('/')).length;
          const num_folders = data.data.result.filter(elm => elm.endsWith('/')).length;
          this.bucket_empty = num_files === 0 && num_folders === 0;
          this.status_test_connection = data.status;
          this.items = this.create_folder_structure(data.data.result)


        } catch (error) {
          // Discuss if there already exists a good abstraction for error handling.
          console.log(error)
          this.error_connection = this.$route_api_errors(error);
          if (error.response) {
            /*
             * The request was made and the server responded with a
             * status code that falls out of the range of 2xx
             */
          } else if (error.request) {
            /*
             * The request was made but no response was received, `error.request`
             * is an instance of XMLHttpRequest in the browser and an instance
             * of http.ClientRequest in Node.js
             */
          } else {
            // Something happened in setting up the request and triggered an Error
          }
        } finally {
          this.isLoadingAutocomplete = false;
          this.loading = false;
        }
      },
      change_bucket: function () {
        this.error_connection = {};
        this.items = [];
        this.init_tree_data()
        this.$emit('update_bucket_name', this.bucket)
      },
      close_success_dialog: function () {
        this.$store.commit('request_input_list_refresh');
        this.dialog = false;
      },
      start_folder_fetch: async function () {
        this.importStatus = 'loading';
        const connector_id = this.connection.id;
        const directory_id = this.$store.state.project.current_directory.directory_id;
        try {
          const data = await axios.post(`/api/walrus/v1/connectors/${connector_id}/fetch-data`, {
            opts: {
              action_type: 'fetch_folder',
              path: this.selection.map(item => item.id),
              directory_id: directory_id,
              bucket_name: this.bucket,
              video_split_duration: this.$props.video_split_duration,
              job_id: this.$props.job_id
            },
            project_string_id: this.$props.project_string_id
          });

          if (data.status === 200 && !data.data.error) {
            this.importStatus = 'success';
          } else {
            this.syncStatus = 'error'
          }
          return data;
        } catch (error) {
          // Discuss if there already exists a good abstraction for error handling.
          this.import_error = this.$route_api_errors(error);
          if (error.response) {
            /*
             * The request was made and the server responded with a
             * status code that falls out of the range of 2xx
             */
            this.importStatus = 'error';
          } else if (error.request) {
            /*
             * The request was made but no response was received, `error.request`
             * is an instance of XMLHttpRequest in the browser and an instance
             * of http.ClientRequest in Node.js
             */
            this.importStatus = 'error';
          } else {
            // Something happened in setting up the request and triggered an Error
            this.importStatus = 'error';
          }
          return error;
        }

      },
      show_confirm_dialog: function () {
        this.importStatus = 'pending';
        this.dialog = true;
      },
      create_folder_structure(folders) {
        const result = folders.map(folder => {
          if (folder.endsWith('/')) {
            return {'id': folder, 'name': folder, 'children': []}
          } else {
            return {'id': folder, 'name': folder}
          }

        });
        return result
      },
      list_buckets: async function () {
        try {
          const connector_id = this.connection.id;
          this.isFetchingBuckets = true;
          this.bucket_list = [];
          this.loading = true;
          this.error_connection = {}
          this.items = [];
          this.selection = [];
          const data = await axios.post(`/api/walrus/v1/connectors/${connector_id}/fetch-data`, {
            opts: {
              action_type: 'list_buckets',
            },
            project_string_id: this.$props.project_string_id
          });


          this.status_test_connection = data.status;

          this.bucket_list = data.data.result.map(r => {
            return {
              name: r,
              diplay_name: r,
              id: r,
              icon: 'mdi-database',
              color: 'primary'
            }
          });
          if (this.bucket_list.length > 0) {
            this.bucket = this.bucket_list[0].name;
            this.change_bucket();
          }

        } catch (error) {          // Discuss if there already exists a good abstraction for error handling.
          this.error_connection = this.$route_api_errors(error);
          if (error.response) {
            this.status_test_connection = error.response.status;
          }
          if (error.request) {
            /*
             * The request was made but no response was received, `error.request`
             * is an instance of XMLHttpRequest in the browser and an instance
             * of http.ClientRequest in Node.js
             */
            this.status_test_connection = -1;
          } else {
            // Something happened in setting up the request and triggered an Error
            this.status_test_connection = -1;
          }
        } finally {
          this.loading = false;
          this.isFetchingBuckets = false;
        }
      },
    },
    watch: {
      'connection': function(){
        this.list_buckets();
        this.$emit('update_bucket_name', this.bucket)

      },
    }
  }
</script>

<style scoped>
  .full-width {
    width: 100%;
  }

  .full-height {
    height: 100%;
  }
</style>
