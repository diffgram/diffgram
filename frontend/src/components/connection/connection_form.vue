<template>

  <v-container fluid class="d-flex align-center pa-0">
    <v-skeleton-loader :loading="loading" :width="form_width" :height="form_height" type="paragraph@4"
                       class="d-flex flex-column flex-grow-1">
      <v-container class="ma-0 d-flex flex-column justify-start">
        <v-toolbar
          no-gutters
          elevation="0"
          fixed
        >
          <v-toolbar-items class="d-flex pa-0 justify-start align-center">

            <!--
            https://vuetifyjs.com/en/components/text-fields

            flat : Removes elevation (shadow) added to element when using the solo or solo-inverted props
            solo, makes it look box like (no line under it)
            -->
            <div v-if="connection_id !== 'new'" class="pa-0 d-flex justify-center align-center">
              <h2 class="mr-2">ID</h2>
              <regular_chip
                :message=connection.id
                tooltip_message="ID"
                v-if="connection_id !== 'new'"
                color="grey"
                tooltip_direction="bottom"
                :small="true"
              >
              </regular_chip>
            </div>

            <!-- TBD , maybe save and test -->


            <tooltip_button tooltip_message="Save"
                            @click="save_connection"
                            icon="save"
                            :text_style="true"
                            :left="true"
                            :large="buttons_size_large"
                            :disabled="!has_changes"
                            color="primary">
            </tooltip_button>

            <tooltip_button tooltip_message="Test"
                            class="ma-0"
                            @click="test_connection(connection_id)"
                            icon="mdi-test-tube"
                            :disabled="loading_test"
                            :text_style="true"
                            :left="true"
                            :large="buttons_size_large"
                            color="primary">
            </tooltip_button>

            <tooltip_button
              tooltip_message="Back to List"
              @click="$router.push('/connection/list')"
              icon="list"
              v-if="show_return_button"
              :icon_style="true"
              :large="true"
              color="primary">
            </tooltip_button>

            <div class="pa-2">
              <div v-if="has_changes">
                Changes detected.
              </div>
              <div v-else>
                No changes.
              </div>
            </div>

            <!-- TODO 'test connection' status... -->

            <div>
              <v-checkbox v-model="connection.archived"
                          label="Archived"
                          class="no-gutters"
                          dense
                          hide-details="auto"
                          @change="has_changes = true"
                          :disabled="loading"
              >
              </v-checkbox>
            </div>


          </v-toolbar-items>
        </v-toolbar>
        <v-skeleton-loader :loading="loading_save || loading_test" :width="form_width" :height="form_height"
                           type="list-item">

          <v-container v-if="may_edit" class="pa-0">
            <v-alert type="success"
                     v-model="success_saved"
                     dismissible>
              Saved
            </v-alert>

            <v-alert type="success"
                     v-model="success_run"
                     dismissible>
              Connection Test Successful!
            </v-alert>

            <connection_docs_suggest :error="error"
                                     :integration_name="connection.integration_name"></connection_docs_suggest>

          </v-container>
        </v-skeleton-loader>

        <v_error_multiple :error="error">
        </v_error_multiple>

        <v-container fluid>
          <!-- base_class -->
          <v-row justify="center" no-gutters>
            <v-col>
              <diffgram_select
                :item_list="$store.state.connection.integration_spec_list"
                v-model="connection.integration_name"
                label="Integration"
                :disabled="loading"
                @change="on_integration_change"
              >
              </diffgram_select>
            </v-col>
          </v-row>
          <v-row v-if="connection.integration_name && connection_form_specs[connection.integration_name].name"
                 no-gutters>
            <v-col>
              <v-text-field
                style="font-size: 18pt"
                v-model="connection.name"
                @input="has_changes = true"
                label="Connection Name"
                :disabled="loading"
                placeholder="My Connection"
              >
              </v-text-field>
            </v-col>
          </v-row>
          <v-row v-if="connection.integration_name && connection_form_specs[connection.integration_name].private_host"
                 no-gutters>
            <v-col>
              <v-text-field
                label="Private Host"
                v-model="connection.private_host"
                @input="has_changes = true"
                flat
              >
              </v-text-field>
            </v-col>
          </v-row>
          <v-row v-if="connection.integration_name && connection_form_specs[connection.integration_name].private_id"
                 no-gutters>
            <v-col>
              <v-text-field
                label="Private ID"
                v-model="connection.private_id"
                @input="has_changes = true"
                flat
              >
              </v-text-field>
            </v-col>
          </v-row>
          <v-row v-if="connection.integration_name && connection_form_specs[connection.integration_name].private_secret"
                 no-gutters>
            <v-col>
              <v-text-field
                :label="connection_form_specs[connection.integration_name].private_secret_label ? connection_form_specs[connection.integration_name].private_secret_label : 'Private Secret'"
                v-model="connection.private_secret"
                @input="has_changes = true"
                flat
              >
              </v-text-field>
            </v-col>
          </v-row>
          <v-row v-if="connection.integration_name && connection_form_specs[connection.integration_name].account_email"
                 no-gutters>
            <v-col>
              <v-text-field
                label="Account Email"
                v-model="connection.account_email"
                @input="has_changes = true"
                flat
              >
              </v-text-field>
            </v-col>
          </v-row>
          <v-row
            v-if="connection.integration_name && connection_form_specs[connection.integration_name].project_id_external"
            no-gutters>
            <v-col>
              <v-text-field
                label="Google Project Id"
                v-model="connection.project_id_external"
                @input="has_changes = true"
                flat
              >
              </v-text-field>
            </v-col>
          </v-row>
          <v-row
            v-if="connection.integration_name && connection_form_specs[connection.integration_name].disabled_ssl_verify"
            no-gutters>
            <v-col>
              <v-checkbox v-model="connection.disabled_ssl_verify"
                          label="Disabled SSL Verify"
                          color="orange"
                          @change="has_changes = true"
                          hide-details
              ></v-checkbox>
            </v-col>
          </v-row>
          <v-row>
            <v-col cols="12" class="d-flex align-center">
              <p>
                <strong>
                  <v-icon color="primary">mdi-file-document</v-icon>
                  Learn more about connections
                  <a class="primary--text"
                     target="_blank"
                     href="https://diffgram.readme.io/docs/new-source">Here</a>
                </strong>
              </p>
            </v-col>
          </v-row>
        </v-container>


        <v-container v-if="may_edit == false"
                     elevation="0">
          <v-container>

            <!-- Not Implemneted -->

          </v-container>
        </v-container>
      </v-container>


    </v-skeleton-loader>
  </v-container>

</template>

<script lang="ts">


  /*  Caution, re adding new select controls
   *    expects  @change="has_changes = true"  otherwise won't "save"
   *
   *
   */

  import axios from '../../services/customInstance';

  import Vue from "vue";
  import connection_docs_suggest from './connection_docs_suggest'

  export default Vue.extend({
      name: 'connection_form',
      components: {
        connection_docs_suggest
      },
      props: {
        // Optional, for existing
        'connection_id': {
          default: null
        },
        'may_edit': {
          default: true,
          type: Boolean
        },
        'show_return_button': {
          default: false,
          type: Boolean
        },
        'redirect_on_create': {
          default: true,
          type: Boolean
        },
        'form_width': {
          default: '100%',
          type: String
        },
        'buttons_size_large': {
          default: true,
          type: Boolean
        },
        'form_height': {
          default: '100%',
          type: String
        },
        'reset_on_create': {
          default: false,
          type: Boolean
        }

      },
      data() {
        return {

          success_loading_existing: false,
          success_saved: false,
          success_run: false,

          name: null,

          request_time: null,

          /*
           *
           */
          connection: {
            'name': 'My Connection',
            'archived': false,
            'permission_scope': 'project',
            'id': null,
            'integration_name': null,

            'private_id': null,
            'private_host': null,
            'private_secret': null,
            'disabled_ssl_verify': false,
            'exists_private_secret_hash': null,
            'account_email': null,
            'project_id_external': null

          },

          connection_form_specs: {
            'google_gcp': {
              name: true,
              private_id: true,
              private_secret: true,
              account_email: true,
              project_id_external: true,

            },
            'microsoft_azure': {
              name: true,
              private_secret: true,
              private_secret_label: 'Connection String',
            },
            'amazon_aws': {
              name: true,
              private_id: true,
              private_secret: true,
            },
            'datasaur': {
              name: true,
              private_id: true,
              private_secret: true,
            },
            'labelbox': {
              name: true,
              private_secret: true,
            },
            'scale_ai': {
              name: true,
              private_secret: true,
            },
            'minio': {
              name: true,
              private_host: true,
              private_id: true,
              private_secret: true,
              disabled_ssl_verify: true,
            },
          },
          // WIP
          google_list: [
            {
              'display_name': 'Cloud storage',
              'name': 'instance',
              'icon': 'mdi-google',
              'color': 'green'
            },
            {
              'display_name': 'AutoML',
              'name': 'instance',
              'icon': 'mdi-google',
              'color': 'green'
            },
          ],
          // WIP

          loading: false,
          loading_test: false,
          loading_save: false,
          error: {},
          result: null,

          auth: {},
          show_auth: false,

          has_changes: false,

          permission_level_list: ['Editor', 'Viewer'],
          permission_level: 'Editor',

        }
      },

      computed: {},
      mounted() {


      },

      created() {
        // Defaults
        this.project_string_id = this.$store.state.project.current.project_string_id
        this.org_id = this.$store.state.org.current.id
        if (this.connection_id) {
          this.get_connection(this.connection_id);
        }


      },
      methods: {
        on_integration_change: function (integration) {
          this.connection = {
            'name': this.connection.name,
            'archived': false,
            'permission_scope': 'project',
            'id': null,
            'integration_name': integration,

            'private_id': null,
            'private_secret': null,
            'exists_private_secret_hash': null,
            'account_email': null,
            'project_id_external': null
          }
          this.has_changes = true;

        },
        test_connection: function (connection_id) {

          if (connection_id == 'new') {
            // this will save and test, in case a user clicks test before saving.
            this.save_connection(true)
            return
          }

          this.success_saved = false    // reset because may be used in conjunection with saving then creates confusion
          this.success_run = false
          this.loading_test = true
          this.error = {}

          axios.post('/api/walrus/v1/connection/test', {
            connection_id: parseInt(connection_id),

            project_string_id: this.project_string_id,
            private_id: this.connection.private_id,
            private_host: this.connection.private_host ? this.connection.private_host : undefined,
            disabled_ssl_verify: this.connection.disabled_ssl_verify ? this.connection.disabled_ssl_verify : false,
            private_secret: this.connection.private_secret ? this.connection.private_secret : undefined,
            account_email: this.connection.account_email ? this.connection.account_email : undefined,
            integration_name: this.connection.integration_name ? this.connection.integration_name : undefined,
            project_id_external: this.connection.project_id_external ? this.connection.project_id_external : undefined

          }).then(response => {
            this.success_run = true
            this.loading_test = false
            this.save_connection(false);
          })
            .catch(error => {
              this.loading_test = false
              this.error = this.$route_api_errors(error)

            });


        },

        get_connection: function (connection_id) {

          // NOT fully implemented for Connection context

          if (connection_id == "new") {
            // could also check if it's not a "Number" type or something.
            return
          }

          this.success_loading_existing = false
          this.loading = true
          this.error = {}

          axios.get('/api/v1/connection/info/' + connection_id
          ).then(response => {

            this.connection = response.data.connection
            this.success_loading_existing = true
            this.loading = false

          })
            .catch(error => {
              this.loading = false
              this.error = this.$route_api_errors(error)

            });


        },

        save_connection: function (do_test = true) {
          /*
            * Assumes saving one  at a time.
            * If we don't have a id yet we need to save first
            *
            */

          if (this.has_changes == false &&
            this.connection.id != null) {
            return
          }

          this.connection.project_string_id = this.project_string_id

          this.success_saved = false
          this.loading_save = true
          this.error = {}
          this.request_time = Date.now()
          let updating = false;
          if (this.connection.id) {
            updating = true;
          }
          axios.post('/api/v1/connection/save', {

            connection: this.connection,
            connection_id: this.connection.id

          }).then(response => {

            this.connection = {
              ...this.connection,
              ...response.data.connection
            }

            this.success_saved = true

            // update URL with connection id
            if (this.connection.id && this.redirect_on_create
              && this.$router.currentRoute.path != `/connection/${this.connection.id}`) {
              this.$router.push(`/connection/${this.connection.id}`)
            }
            this.has_changes = false
            this.loading_save = false;
            if (updating) {
              this.$emit('connection-updated', this.connection)
            } else {
              const newConnectionList = this.$store.state.connection.connection_list.map(c => c)
              newConnectionList.push(this.connection);
              this.$store.commit('set_connection_list', newConnectionList)
              this.$emit('connection-created', this.connection)
            }

            if (this.reset_on_create) {
              this.connection = {
                'name': 'My Connection',
                'archived': false,
                'permission_scope': 'project',
                'id': null,
                'integration_name': null,

                'private_id': null,
                'private_host': null,
                'private_secret': null,
                'disabled_ssl_verify': true,
                'exists_private_secret_hash': null,
                'account_email': null,
                'project_id_external': null
              }
            }
            if (do_test && !this.connection.archived) {
              this.test_connection(this.connection.id)
            }


          })
            .catch(error => {
              this.loading_save = false
              this.error = this.$route_api_errors(error)

            });

        }

      },
      watch: {
        connection_id: function (newVal, oldVal) {
          if (newVal) {
            this.get_connection(newVal);
          }
        }
      }
    }
  ) </script>
