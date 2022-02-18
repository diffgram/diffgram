<template>
  <v-container fluid class="text-center">
    <v-row>
      <v-col cols="12">
        <v_error_multiple :error="error_connection">
        </v_error_multiple>

      </v-col>
    </v-row>
    <v-row>
      <v-col cols="12">
        <v-skeleton-loader :loading="isFetchingBuckets" width="100%" height="46px" type="list-item"
                           class="full-width skeleton-loader-autocomplete">
          <diffgram_select

            :item_list="bucket_list"
            v-model="bucket"
            label="Select your bucket"
            :disabled="!connection"
            @change="change_bucket"
          >

          </diffgram_select>
        </v-skeleton-loader>
      </v-col>
    </v-row>

    <v-row>
      <v-col cols="12">
        <v-skeleton-loader :loading="isFetchingBuckets || loading" height="350px" type="card" class="full-width skeleton-loader-autocomplete">
          <v-card elevation="1" height="350px" class="overflow-y-auto">
            <v-container v-if="!bucket_empty">
              <v-treeview
                v-model="selection"
                selectionType="independent"
                selectable
                selected-color="blue"
                :load-children="fetch_folder"
                return-object
                :items="items"
                @input="on_select_item"
              >
                <template v-slot:prepend="{ item, open }">
                  <v-icon v-if="item.name.endsWith('/')">
                    mdi-folder
                  </v-icon>
                  <v-icon v-if="item.is_root">
                    mdi-database
                  </v-icon>
                  <v-icon v-else>
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
  </v-container>
</template>

<script>
  import axios from '../../services/customAxiosInstance';
  import diffgram_select from '../regular/diffgram_select'

  export default {
    props: ['connection', 'project_string_id', 'label', 'export_obj', 'format'],
    name: "export_storage_searchbar",
    components: {diffgram_select},
    data() {
      return {
        items: [],
        selection: [],
        exportStatus: 'pending',
        loading: true,
        bucket_empty: false,
        isFetchingBuckets: false,
        bucket_list: [],
        bucket: '',
        error_connection: {},
        export_error: {},
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
              just_folders: true,
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
      on_select_item: function (payload){
        // Allow just selection of one at a time.
        if(payload.length > 1){
          const last = payload[payload.length - 1]
          this.selection = [last]
        }
        this.$emit('folder-selected', this.selection);
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
              just_folders: true,
              bucket_name: this.bucket
            },
            project_string_id: this.$props.project_string_id
          });
          this.folder_contents = data.data.result;
          this.status_test_connection = data.status;
          this.items = this.create_folder_structure(data.data.result)
          this.items.unshift({'id': '', 'name': 'Root Directory of the Bucket.', is_root: true})
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
      start_export: async function () {
        this.exportStatus = 'loading';
        this.status_test_connection = -1;
        this.loading = true;
        const connector_id = this.connection.id;
        const directory_id = this.$store.state.project.current_directory.directory_id;
        try {
          const data = await axios.post(`/api/walrus/v1/connectors/${connector_id}/put-data`, {
            opts: {
              action_type: 'send_export',
              path: this.selection[0].id,
              directory_id: directory_id,
              bucket_name: this.bucket,
              export_id: this.$props.export_obj.id.toString(),
              format: this.$props.format
            },
            project_string_id: this.$props.project_string_id
          });

          if (data.status === 200 && !data.data.error) {
            this.exportStatus = 'success';
            this.status_test_connection = data.status;
            this.$emit('export-success')
            this.selection = [];
            this.on_select_item([]);
            this.error_connection = {};
          } else {
            this.exportStatus = 'error'
          }
          return data;
        } catch (error) {
          // Discuss if there already exists a good abstraction for error handling.
          this.selection = [];
          this.on_select_item([]);
          this.error_connection = this.$route_api_errors(error);
          this.exportStatus = 'error';

          if (error.response) {
            /*
             * The request was made and the server responded with a
             * status code that falls out of the range of 2xx
             */
            this.status_test_connection = error.response.status;
            // this.$emit('onExportStart', error)
          } else if (error.request) {
            /*
             * The request was made but no response was received, `error.request`
             * is an instance of XMLHttpRequest in the browser and an instance
             * of http.ClientRequest in Node.js
             */
            this.exportStatus = 'error';
          } else {
            // Something happened in setting up the request and triggered an Error
            this.exportStatus = 'error';
            return error
          }
          return error;
        } finally {
          this.loading = false;
        }


      },
      list_buckets: async function () {

        try {
          const connector_id = this.connection.id;
          this.isFetchingBuckets = true;
          this.bucket_list = []
          this.loading = true;
          const data = await axios.post(`/api/walrus/v1/connectors/${connector_id}/fetch-data`, {
            opts: {
              action_type: 'list_buckets',
            },
            project_string_id: this.$props.project_string_id
          });

          this.status_test_connection = data.status;
          if (data.data.result) {
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
              this.bucket = this.bucket_list[0].name
              this.change_bucket();
            }
          }


        } catch (error) {
          // Discuss if there already exists a good abstraction for error handling.
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
      'connection': 'list_buckets'
    }
  }
</script>

<style scoped>
  .v-list-item--link::before {
    background-color: red;
  }
</style>
