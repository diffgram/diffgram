<template>
  <div v-cloak>
    <v-card elevation="0">
      <!-- credential new button -->
      <div v-if="['job_edit', 'direct_route'].includes(mode_options)">
        <v-layout class="d-flex justify-lg-space-between">
            <button_with_menu
              datacy="open-create-credential"
              tooltip_message="Add"
              button_text="Create Credential"
              icon_color="white"
              :icon_style="false"
              icon="add"
              background="secondary"
              v-if="$store.state.builder_or_trainer.mode == 'builder'"
              color="white"
              @menu_open="$refs.create_credential.reset()"
            >

              <template slot="content">

                <v_credential_type_new_or_edit
                  ref="create_credential"
                  :project_string_id="project_string_id"
                  @refresh_list="credential_list_api"
                  :mode="'new'">
                </v_credential_type_new_or_edit>

              </template>

            </button_with_menu>

          <div>
            <v-btn @click="credential_list_api"
                   :loading="loading"
                   data-cy="refresh-credentials"
                   class="pr-6"
                   color="primary"
                   outlined
            >
              <v-icon>mdi-refresh</v-icon>
              Refresh
            </v-btn>
          </div>

        </v-layout>

      </div>
      <!-- credential new button -->

      <!-- being list view -->
      <div v-if="mode_view=='list'">

        <v-container fluid>

          <v-layout class="d-flex">
            <!-- Attach credentials -->

            <div v-if="['job_edit'].includes(mode_options)" class="d-flex mr-auto">

              <v-btn @click="attach_selected('awards', 'add')"
                     dark

                     data-cy="grants-button"
                     v-if="allow_awards"
                     class="mr-4"
                     :disabled="loading || this.selected.length === 0"
                     color="secondary">
                Grants
                <v-icon right> mdi-trophy</v-icon>
              </v-btn>

              <v-btn @click="attach_selected('requires', 'add')"
                     dark
                     data-cy="requires-button"
                     class="mr-4"
                     :disabled="loading || this.selected.length === 0"
                     color="warning">
                Requires
                <v-icon right> mdi-seal</v-icon>
              </v-btn>

              <v-btn @click="attach_selected('remove', 'remove')"
                     dark

                     data-cy="clear-button"
                     :disabled="loading || this.selected.length === 0"
                     color="error">
                Clear
                <v-icon right> mdi-close-circle</v-icon>
              </v-btn>


            </div>

          </v-layout>
        </v-container>


        <v_error_multiple :error="error_attach">
        </v_error_multiple>




        <!-- Icons for Trainers (on their individual crednetial page)

             In context of their homepage / credential page
             TODO prefer to have parent component set mode options
              then it try to "know" about what mode. I think knowning about
              mode is one abstraction higher then this component
            -->

        <v-container
          v-if="$store.state.builder_or_trainer.mode == 'trainer'
                   && mode_options != 'job_detail'
                   && credential_list.length > 0 "
          container--fluid
          grid-list-md
        >
          <v-btn @click="credential_list_api"
                 :loading="loading"
                 color="primary"
                 text
                 icon
          >
            <v-icon>mdi-refresh</v-icon>
            Refresh
          </v-btn>
          <v-layout>

            <v-flex xs4 md1 v-for="(item, index) in credential_list" :key="index">


              <div v-if="item.status == 'active'" >

                <v-badge color="primary">
                  <v-icon dark slot="badge">check</v-icon>
                </v-badge>

              </div>

              <div>

                <v-img v-if="item.credential_type.image"
                       :src="item.credential_type.image.url_signed_thumb"
                       width="100%"
                       height="100%"/>

                {{ item.credential_type.name }}

                <thumbnail
                  v-if="item.image"
                  class="pa-4"
                  :item="item"
                >
                </thumbnail>

              </div>

            </v-flex>
          </v-layout>
        </v-container>

        <v-container fluid style="border: 1px solid #ababab" v-if="credential_list.length === 0"
                     class="d-flex flex-column align-center justify-center ma-0">
          <h1>No Credentials to Display</h1>
          <v-icon size="250">mdi-shield-star-outline</v-icon>
        </v-container>

        <!-- End icons for trainers -->


        <!--  Job Detail
             Maybe should be a seperate component?
            -->
        <v-layout v-if="mode_options == 'job_detail' && credential_list.length > 0">


          <v-flex>

            <v-card class="ma-4">

              <v-container>
                <h2>
                  <v-icon color="orange">mdi-seal</v-icon>
                  Requires
                </h2>

                <credential_list_view_only :credential_list="credential_list"
                                           :kind="'requires'"
                >
                </credential_list_view_only>

              </v-container>
            </v-card>

          </v-flex>

          <v-flex>

            <v-card class="ma-4">

              <v-container>
                <h2>
                  <v-icon color="green"
                  >mdi-trophy
                  </v-icon>
                  Grants
                </h2>

                <credential_list_view_only :credential_list="credential_list"
                                           :kind="'awards'"
                >
                </credential_list_view_only>

              </v-container>
            </v-card>

          </v-flex>
        </v-layout>

        <!-- End job detail -->


        <!-- TODO don't show data table if Trainer,
            because we want to show the credential instances
            and the table is for templates.
            And to put more of a point on it, they serve a different puproses
            so we want to visually display the information differently.
            -->

        <!--  Default view, ie on credential/list

            Wondering if this should use the mode_options more
            and let parent know about trainer / builder mode -->

        <v-data-table v-if="$store.state.builder_or_trainer.mode == 'builder' && mode_options != 'job_detail'"
                      v-bind:headers="header_view"
                      :items="credential_list"
                      class="elevation-1"
                      item-key="id"
                      v-model="selected"
                      :options.sync="options"
                      footer-props.prev-icon="mdi-menu-left"
                      footer-props.next-icon="mdi-menu-right"
        >

          <!-- review rows-per-page-items setting-->
          <!-- appears to have to be item for vuetify syntax-->
          <template slot="item"
                    slot-scope="props">
            <tr>

              <td v-if="['job_edit'].includes(mode_options)">
                <v-checkbox v-model="props.isSelected"
                            :data-cy="`credential-checkbox-${props.index}`"
                            @change="props.select($event)"
                            primary>
                </v-checkbox>
              </td>

              <td v-if="['job_edit'].includes(mode_options)">
                <div v-if="props.item.kind == 'awards'">
                  <v-icon color="green">
                    mdi-trophy
                  </v-icon>
                  Grants
                </div>

                <div v-if="props.item.kind == 'requires'">
                  <v-icon color="orange">
                    mdi-seal
                  </v-icon>
                  Requires
                </div>

              </td>

              <!-- This isn't built yet credential_detail(props.item) -->

              <td @click="">
                {{ props.item.name }}
              </td>

              <td>
                <img v-if="props.item.image"
                     :src="props.item.image.url_signed_thumb"
                     alt="props.item.image.original_filename">
              </td>

              <td>

                <!-- start Edit -->
                <v-dialog :close-on-content-click="false">

                  <template v-slot:activator="{ on }">
                    <v-btn v-on="on"
                           color="primary"
                           icon
                           text>
                      <v-icon> edit</v-icon>
                    </v-btn>
                  </template>

                  <v_credential_type_new_or_edit
                    :project_string_id="project_string_id"
                    :mode="'edit'"
                    :credential_type_prop="props.item"
                    @edit_success="credential_list_api()">
                  </v_credential_type_new_or_edit>

                </v-dialog>
                <!-- end NEW -->
              </td>
            </tr>
          </template>
          <div v-if="!loading">
            <v-alert slot="no-data" color="error" icon="warning">
              No results found.
            </v-alert>
          </div>


        </v-data-table>
      </div>
      <!-- end list view -->


    </v-card>


  </div>
</template>

<script lang="ts">

import axios from 'axios';
import credential_list_view_only from './credential_list_view_only';

import Vue from "vue";
import {create_event} from "../../event/create_event";

export default Vue.extend({
    name: 'credential_list',
    components: {
      credential_list_view_only: credential_list_view_only
    },
    props: {
      'project_string_id_prop': {
        default: null
      },
      'job_id': {
        default: null
      },
      'mode_options': {
        default: "direct_route"   // job_edit, job_detail, user_profile, general/account?
      },
      'mode_view': {
        default: "list"  // list or grid?
      },
      'allow_awards':{
        default: false
      }
    },
    watch: {},
    data() {
      return {

        selected: [],


        options: {
          'sortBy': ['column2'],
          'sortDesc': [true],
          'itemsPerPage': 5
        },

        error_attach: {},
        show_success_attach: false,

        attach_kind_list: ['Awards', 'Requires'],
        attach_kind: 'Awards',

        type_list: ['Credentials', 'Templates'],
        type: "",

        add_or_remove_list: ['Add', 'Remove'],
        add_or_remove: 'Add',

        loading: false,

        my_stuff_only: false,

        credential_list: [],

        metadata_limit_options: [10, 25, 100, 250],
        metadata_limit: 10,

        request_next_page_flag: false,
        request_next_page_available: true,

        project_string_id: null,

        header_job_edit: [
          {
            text: "Selected",
            align: 'left',
            sortable: true,
            value: 'selected'
          },
          {
            text: "Kind",
            align: 'left',
            sortable: true,
            value: 'kind'
          },
          {
            text: "Name",
            align: 'left',
            sortable: true,
            value: 'name'
          },
          {
            text: "Icon",
            align: 'left',
            sortable: false,
          },
          {
            text: "Actions",
            align: 'left',
            sortable: false,
          }
        ],
        header: [
          {
            text: "Name",
            align: 'left',
            sortable: true,
            value: 'name'
          },
          {
            text: "Icon",
            align: 'left',
            sortable: false,
          },
          {
            text: "Actions",
            align: 'left',
            sortable: false,
          }
        ]

      }
    },

    computed: {
      header_view: function () {
        if (this.mode_options == "job_edit") {
          return this.header_job_edit
        }

        return this.header

      },

      metadata: function () {

        return {
          'job_id': parseInt(this.job_id),
          'my_stuff_only': this.my_stuff_only,
          'limit': this.metadata_limit,
          'request_next_page': this.request_next_page_flag,
          'file_view_mode': this.file_view_mode,
          'previous': this.metadata_previous,
          'mode_view': this.mode_view,
          'mode_options': this.mode_options,
          'project_string_id': this.project_string_id,
          'builder_or_trainer': this.$store.state.builder_or_trainer
        }

      }

    },
    mounted() {

      // Not sure if I like this
      // But also not a fan of having to have the project in every route
      // especially for something like this that can be relevant without a project

      if (!this.project_string_id_prop) {
        this.project_string_id = this.$store.state.project.current.project_string_id
      } else {
        this.project_string_id = this.project_string_id_prop
      }

      if (this.$store.state.builder_or_trainer.mode == 'trainer') {
        this.my_stuff_only = true
      }
      this.credential_list_api();


    },
    methods: {
      credential_list_api() {

        axios.post('/api/v1/credential/list', {

          'metadata': this.metadata

        }).then(response => {

          if (response.data.log.success == true) {

            this.credential_list = response.data.credential_list
            this.metadata_previous = response.data.metadata
          }

        })
          .catch(error => {
            console.error(error);
            this.loading = false
            //this.logout()
          });
      },

      credential_detail(credential) {

        this.$router.push("/credential/" + credential.id)

      },

      attach_selected(attach_kind, add_or_remove) {

        this.attach_kind = attach_kind
        this.add_or_remove = add_or_remove

        this.loading = true
        this.error_attach = {}
        this.show_success_attach = false

        axios.post('/api/v1/credential/type/attach/job',
          {
            'add_or_remove': this.add_or_remove,
            'kind': this.attach_kind,
            'job_id': parseInt(this.job_id),
            'credential_type_list': this.selected,

          })
          .then(response => {
            if (response.data.log.success = true) {

              this.show_success_attach = true

              this.selected = []
              // refresh list
              this.credential_list_api()

            }

            this.loading = false

          }).catch(e => {
          console.error(e)
          this.error_attach = e.response.data.log.error
          this.loading = false

        })

      },


    }
  }
) </script>
