<template>
  <div v-cloak>
    <v-card>

      <v-card-title>
        Guides
      </v-card-title>

      <v-alert type="info"
            dismissible>

      Guides instruct trainers on how to complete annotations.
      Optional: Choose a different guide for reviewers.

    </v-alert>

      <!-- start NEW -->
      <v-dialog v-model="new_guide_menu"
              :close-on-content-click="false"
              :nudge-width="200"
              offset-x>

        <template v-slot:activator="{ on }">

          <v-btn v-on="on"
                 outlined
                 :disabled="false">
            <v-icon> add </v-icon>
            Create
          </v-btn>
        </template>

        <v_guide_new_or_edit
                    :project_string_id="project_string_id"
                    :mode="'new'"
                     @guide_new_success="guide_list_api()">
        </v_guide_new_or_edit>

      </v-dialog>
      <!-- end NEW -->

      <v-container grid-list-sm>
        <v-layout md-3>

          <!-- Templates (or perhaps "Examples" is better)
               aren't fully supported yet
              https://docs.google.com/document/d/1HRQpEBlr50BNu-uii--OuPgxDgZ7WhneqOZ84WdBXIU/edit#heading=h.gcxu7enxtu7k
              -->
          <!--
          <v-select :items="type_list"
                    v-model="type"
                    label="Type"
                    item-value="text"
                    :disabled="loading"
                    @change="">
          </v-select>
          -->

          <v-checkbox v-model="my_stuff_only"
                      label="Only Show Created By Me">
          </v-checkbox>


          <v-btn @click="guide_list_api"
                 :loading="loading"
                 color="primary"
                 icon
                 text
                 >
            <v-icon>refresh</v-icon>
          </v-btn>

          <!-- TODO use built in next page?-->
          <!--
  <v-btn @click="next_page"
         :loading="loading"
         :disabled="!request_next_page_available">
    Next page
  </v-btn>
  -->
          <!-- Attach guides -->




        </v-layout>
      </v-container>


      <v_error_multiple :error="error_attach">
      </v_error_multiple>

      <v-alert type="success"

               v-if="show_success_attach">
        Updated.
      </v-alert>

      <v-data-table v-bind:headers="header_view"
                    :items="guide_list"
                    class="elevation-1"
                    item-key="id"
                    :options.sync="options">

        <!-- review rows-per-page-items setting-->
        <!-- appears to have to be item for vuetify syntax-->
        <template slot="item"
                  slot-scope="props">

          <tr>

            <td v-if="mode == 'attach' ">
              <div v-if="props.item.kind == 'default'">
                <v-icon>
                  mdi-book-open
                </v-icon>
                Default
              </div>

              <div v-if="props.item.kind == 'review'">
                <v-icon>
                  mdi-briefcase-check
                </v-icon>
                Review
              </div>

            </td>

            <td>
              {{props.item.name}}
            </td>

            <td>
              <!-- Not sure about having this as a menu
                  or a dialog... but for now dialog seems better maybe
                  then should edit be a dialog too?-->
              <v-dialog :close-on-content-click="false"
                      :nudge-width="-200"
                      offset-x
                      :disabled="false">

              <!-- Caution, must be inside activator thing to
                   render in this (dialog / menu ) scope!!!-->
              <template v-slot:activator="{ on }">
                <div v-on="on">

                  <VueMarkDown
                               :source="props.item.description_markdown.slice(0, 30)">
                  </VueMarkDown>

                  <div v-if="props.item.description_markdown.length >= 30">
                    <v-btn outlined> More </v-btn>
                  </div>

                </div>
              </template>

              <v-card>
                <VueMarkDown :source="props.item.description_markdown">
                </VueMarkDown>
              </v-card>

              </v-dialog>
            </td>


            <td v-if="mode=='attach'">
              <!-- QUESTION, show "swap" button if already has
      other guide ie :
      v-if="['review', undefined].includes(props.item.kind)" -->
                <v-btn v-if="[undefined].includes(props.item.kind) &&
                       !metadata_previous.guide_info.guide_default_id"
                       @click="attach_selected(props.item.id, 'Default', 'update')"
                       dark
                       :disabled="loading"
                       color="green">
                  Default
                  <v-icon right> mdi-book-open </v-icon>
                </v-btn>

                <v-btn v-if="[undefined].includes(props.item.kind) &&
                       !metadata_previous.guide_info.guide_review_id"
                       @click="attach_selected(props.item.id, 'Review', 'update')"
                       dark
                       :disabled="loading"
                       color="purple">
                  Review
                  <v-icon right> mdi-briefcase-check </v-icon>
                </v-btn>


                <div v-if="['default', 'review'].includes(props.item.kind)">
                  <v-btn @click="attach_selected(props.item.id, props.item.kind, 'remove')"
                         dark
                         :disabled="loading"
                         color="warning">
                    Remove
                    <v-icon right> mdi-minus </v-icon>
                  </v-btn>
                </div>
            </td>


            <td>
              <!-- start Edit -->
              <v-dialog :close-on-content-click="false">

                <template v-slot:activator="{ on }">
                  <v-btn v-on="on"
                         color="primary"
                         icon
                         text>
                    <v-icon> edit </v-icon>
                  </v-btn>
                </template>

                <v_guide_new_or_edit
                            :project_string_id="project_string_id"
                            :mode="'edit'"
                            :guide="props.item"
                             @edit_guide_success="guide_list_api()">
                </v_guide_new_or_edit>

              </v-dialog>
              <!-- end NEW -->

            </td>

          </tr>
        </template>
        <div v-if="!loading">
          <v-alert slot="no-data"  color="error" icon="warning">
            No results found.
          </v-alert>
        </div>


      </v-data-table>


    </v-card>

  </div>
</template>

<script lang="ts">

  import axios from 'axios';

  import Vue from "vue";
  import {create_event} from "../../event/create_event"; export default Vue.extend( {
    name: 'guide_list',
    props: {
      'project_string_id': {
        default: null
      },
      'job_id': {
        default: null
      },
      'mode': {
        default: null
      }
    },

    data() {
      return {

        selected: [],

        options: {
          'sortBy': ['column2'],
          'sortDesc': [true],
          'itemsPerPage': 10
        },

        error_attach: {},
        show_success_attach: false,

        new_guide_menu: false,

        attach_kind_list: ['Default', 'Review'],
        attach_kind: 'Default',

        type_list: ['guides', 'Templates'],
        type: "",

        update_or_remove_list: ['Update', 'Remove'],
        update_or_remove: 'Update',

        loading: false,

        my_stuff_only: false,

        guide_list: [],

        metadata_limit_options: [10, 25, 100, 250],
        metadata_limit: 10,

        request_next_page_flag: false,
        request_next_page_available: true,

        metadata_previous: {
          guide_info: {}
        },

        // For attaching to job
        attach_to_job_header: [
          {
            text: "Kind", // ie default, review etc.
            align: 'left',
            sortable: true,
            value: 'kind'
          },
          {
            text: "Name",
            align: 'left',
            sortable: false,
            value: 'name'
          },
          {
            text: "Description Preview",
            align: 'left',
            sortable: false,
            value: 'description_markdown'
          },
          {
            text: "Actions",
            align: 'left',
            sortable: false
          }
        ],

        guide_list_page_header: [
          {
            text: "Name",
            align: 'left',
            sortable: false,
            value: 'name'
          },
          {
            text: "Description Preview",
            align: 'left',
            sortable: false,
            value: 'description_markdown'
          },
          {
            text: "Actions",
            align: 'left',
            sortable: false
          }
        ]

      }
    },
    computed: {
      header_view: function () {
        if (!this.mode) {
          return this.guide_list_page_header

        } else if (this.mode == 'attach') {
          return this.attach_to_job_header
        }
      },

      metadata: function () {

        return {
          'my_stuff_only': this.my_stuff_only,
          'limit': this.metadata_limit,
          'request_next_page': this.request_next_page_flag,
          'file_view_mode': this.file_view_mode,
          'previous': this.metadata_previous,
          'job_id': parseInt(this.job_id),
          'mode': this.mode
        }

      }

    },
    mounted() {
      this.add_visit_history_event();
      // why at mounted and not created?
      this.guide_list_api()

    },
    methods: {

      add_visit_history_event: async function(){
        const event_data = await create_event(this.project_string_id, {
          page_name: 'guide_list',
          object_type: 'page',
          user_visit: 'user_visit',
        })
      },
      guide_list_api() {

        // there were some issues with how the
        // project string gets setup from the url (because the url doesn't contain the id),
        // so just use this from Store for now

        axios.post(
          '/api/v1/project/' + this.$store.state.project.current.project_string_id +
          '/guide/list', {

          'metadata': this.metadata

        }).then(response => {

          if (response.data.log.success == true) {

            this.guide_list = response.data.guide_list
            this.metadata_previous = response.data.metadata
          }

        })
          .catch(error => {
            console.error(error);
            this.loading = false

          });
      },

      attach_selected(guide_id, attach_kind, update_or_remove) {

        this.attach_kind = attach_kind
        this.update_or_remove = update_or_remove

        this.loading = true
        this.show_success_attach = false
        this.error_attach = {}

        axios.post('/api/v1/guide/attach/job',
          {
            'update_or_remove': this.update_or_remove,
            'kind': this.attach_kind,
            'job_id': parseInt( this.job_id ),
            'guide_id': guide_id

          })
          .then(response => {
            if (response.data.log.success = true) {

              this.selected = []
              this.show_success_attach = true
              this.guide_list_api()

            }

            this.loading = false

          }).catch(e => {

            this.error_attach = e.response.data.log.error
            console.error(e)
            this.loading = false

          })

      },


    }
  }

) </script>
