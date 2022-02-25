<template>
  <div id="export">

    <v-card>
      <v-container>

        <v-card-title>
          <h2> Export </h2>
        </v-card-title>

        <v-flex>

          <v-layout>

            <diffgram_select
              :item_list="source_list"
              v-model="source"
              label="Source"
              :disabled="loading"
            >
            </diffgram_select>


            <v_directory_list
              v-if="source == 'directory' "
              :project_string_id="project_string_id"
              :show_new="false"
              :show_update="false"
              @change_directory="">
            </v_directory_list>


            <div class="pl-2 pr-2">
              <job_select
                v-if="source == 'job' "
                v-model="job"
                label="Job"
                :loading="loading"
              >
              </job_select>
            </div>

            <!-- TASK -->
            <v-text-field
              v-if="source == 'task'"
              v-model="task_id"
              label="Task ID">
            </v-text-field>


            <v-select :items="kind_list"
                      v-model="kind"
                      label="Kind"
                      item-value="text">
            </v-select>

            <div class="pl-4 pr-4">
              <v-checkbox v-model="ann_is_complete"
                          data-cy="complete-files-only-checkbox"
                          label="Complete Files Only">
              </v-checkbox>
            </div>


            <!-- Only show for beta
                  This is not quite the right setup but at least it simplifies it for
                  now.

                Hide for now, this is really not fully supported anymore
                and even for admins it just clutters up the display
                -->
            <!--
            <v-select v-if="$store.state.user.current.api.api_actions
                      && kind=='Annotations'"
                      :items="file_comparison_mode_list"
                      v-model="file_comparison_mode"
                      label="File comparison"
                      item-value="text">
            </v-select>
            -->

            <v-switch v-if="kind=='TF Records'"
                      v-model="masks"
                      label="Masks"
                      item-value="text">
            </v-switch>


            <!-- Jan 20 , 2020 , Disabled on not job.id
            because we load the job list and it
            will be empty to start and may remain empty-->

            <!-- Moved this to right hand side so it's move obvious the info
              is selected-->

            <div class="pa-2">
              <v-btn @click="generate_annotations_function"
                     :loading="loading"
                     data-cy="generate-export"
                     @click.native="loader = 'loading'"
                     :disabled="loading || (source == 'job' && !job.id)"
                     color="primary"
              >

                Generate
                <v-icon right> build</v-icon>

              </v-btn>
            </div>


            <v-btn color="blue darken-1" text
                   href="https://diffgram.readme.io/docs/export"
                   target="_blank"
                   icon>
              <v-icon>help</v-icon>
            </v-btn>

          </v-layout>

          <v-alert type="info"
                   v-if="over_free_plan_limit">

            <v-chip color="red"
                    text-color="white"
            >{{active_instances}}
            </v-chip>
            active instances.

            Free Plan has limit of
            <v-chip color="white">100</v-chip>
            .

            <v-btn color="white"
                   @click="$router.push('/pricing')">
              Upgrade to paid plan now
            </v-btn>

          </v-alert>

          <v-alert type="info"
                   v-if="task_id && !generate_annotations_success && !generate_annotations_pending"
                   dismissible
          >
            Click Generate to build task export.
          </v-alert>


          <!-- Context that the generate / download is a 2 step
            process and may not be clear to someone new -->

          <v-alert type="info"
                   v-if="export_list && export_list.length == 0">
            Click Generate to build your first export or call SDK/API.
          </v-alert>

          <v-alert type="info"
                   v-if="generate_annotations_pending && !generate_annotations_success">
            Generating export.
          </v-alert>

          <v-alert type="success"
                   v-if="generate_annotations_success">
            Done generating
          </v-alert>


          <v_error_multiple :error="error">
          </v_error_multiple>

          <!--
           Context that some browsers block download requests from programs

           jan 23, 2020 export_list.length != 0 context:
           not relevant if nothing to download and clutters
           new click to generate message

          -->

          <v-alert v-if="export_list && export_list.length != 0
                    && !task_id"
                   type="info"
                   dismissible>
            Must allow popups for download action.
          </v-alert>


          <v-container>

            <v-spacer></v-spacer>

            <v-btn @click="get_export_list"
                   :loading="loading"
                   :disabled="loading"
                   icon
            >
              <v-icon> refresh</v-icon>

            </v-btn>

            <v-skeleton-loader
              :loading="loading"
              type="table"
            >

              <v-data-table v-bind:headers="header"
                            :loading="loading"
                            :options.sync="options"
                            :items="export_list"
                            data-cy="export-table"
                            item-key="id">

                <!-- appears to have to be item for vuetify syntax-->
                <template slot="item" slot-scope="props">

                  <tr data-cy="export-row">
                    <td>
                      {{ props.item.created_time | moment("dddd, MMMM Do H:mm:ss a") }}

                    </td>

                    <td>

                      <!-- TODO init is probably not the right status here
                        but not a fan of it relying on the percent complete == 100 only -->

                      <v-tooltip v-if="props.item.status == 'init'
                               && props.item.percent_complete != 100"
                                 bottom>
                        <template v-slot:activator="{ on }">
                          <v-progress-linear :value="props.item.percent_complete"
                                             v-on="on"
                          >
                          </v-progress-linear>
                        </template>
                        {{Math.round(props.item.percent_complete)}} %
                      </v-tooltip>

                      <div v-if="props.item.status == 'complete'">
                        <v-icon color="success"
                        >check
                        </v-icon>
                      </div>

                      <tooltip_icon
                        v-if="props.item.status == 'failed'"
                        :tooltip_message="props.item.status_text"
                        icon="error"
                        color="error">
                      </tooltip_icon>


                    </td>

                    <td>

                      <v-layout>

                        <export_source_icons
                          :source="props.item.source"
                          :disabled="loading">
                        </export_source_icons>

                        <!-- TODO at click go to directory or task or something ?

                          Curious about putting icon inside of chip
                          -->

                        <div class="pl-2">
                          <regular_chip
                            v-if="props.item.directory && props.item.source == 'directory'"
                            :message=props.item.directory.nickname
                            tooltip_message="Name"
                            color="primary"
                            tooltip_direction="bottom"
                            :small="true"
                          >
                          </regular_chip>

                          <regular_chip
                            v-if="props.item.job && props.item.source == 'job'"
                            :message=props.item.job.name
                            tooltip_message="Go to Job"
                            color="green"
                            tooltip_direction="bottom"
                            :small="true"
                            :is_clickable="true"
                            @click="$router.push('/job/' + props.item.job.id)"
                          >
                          </regular_chip>

                          <regular_chip
                            v-if="props.item.task && props.item.source == 'task'"
                            :message=props.item.task.id
                            tooltip_message="Go to Task"
                            color="purple"
                            tooltip_direction="bottom"
                            :small="true"
                            :is_clickable="true"
                            @click="$router.push('/task/' + props.item.task.id)">

                          </regular_chip>
                        </div>

                      </v-layout>

                    </td>

                    <!-- Hidden while
                         that mode is pushed back to beta-->
                    <!--
                    <td>
                      {{ props.item.file_comparison_mode }}
                    </td>
                    -->
                    <td>
                      {{ props.item.file_list_length }}
                    </td>

                    <td>
                      <v-icon v-if="props.item.ann_is_complete == true"
                              color="primary">check
                      </v-icon>
                    </td>

                    <td>
                      <v-icon v-if="props.item.masks == true"
                              color="success"
                      >check
                      </v-icon>
                    </td>

                    <td>
                      {{ props.item.kind }}
                    </td>

                    <td data-cy="export-column">

                      <v-layout>

                        <v-flex class="flex-row">

                          <tooltip_button
                            tooltip_message="Download"
                            data-cy="download_export"
                            @click="post_export_link(props.item)"
                            icon="file_download"
                            :text_style="true"
                            :disabled="props.item.status != 'complete'"
                            color="primary">
                          </tooltip_button>
                          <tooltip_button
                            tooltip_message="Export To 3rd Party Integration"
                            @click="open_connection_export_dialog(props.item)"
                            icon="mdi-database-export"
                            :text_style="true"
                            data-cy="export-third-party"
                            :disabled="props.item.status != 'complete'"
                            color="primary">
                          </tooltip_button>

                        </v-flex>


                        <v-flex>
                          <v-select
                            v-if="props.item.kind=='Annotations' || !props.item.kind"
                            :items="format_options"
                            v-model="format"
                            label="Download format"
                            item-value="text">
                          </v-select>

                          <v-text-field v-else
                                        label="Download format"
                                        value="TF Records"
                                        :disabled="true"
                          >
                          </v-text-field>
                        </v-flex>

                        <button_with_confirm
                          @confirm_click="update_export(props.item, 'ARCHIVE')"
                          color="primary"
                          icon="archive"
                          :icon_style="true"
                          tooltip_message="Archive"
                          :loading="loading">
                        </button_with_confirm>
                      </v-layout>
                    </td>
                  </tr>

                </template>

                <div v-if="!loading">

                  <v-alert slot="no-data" color="error" icon="warning">
                    No results found.
                  </v-alert>
                </div>

              </v-data-table>

            </v-skeleton-loader>

          </v-container>


        </v-flex>
        <export_connection_dialog
          :project_string_id="project_string_id"
          :export_obj="selected_item"
          :format="format"
          ref="export_connection_dialog"
        ></export_connection_dialog>

      </v-container>
    </v-card>

    <free_tier_limit_dialog
      :message="message_free_tier_limit"
      :details="details_free_tier_limit"
      ref="free_tier_limit_dialog">

    </free_tier_limit_dialog>
  </div>
</template>

<script lang="ts">

  import {route_errors} from '../regular/regular_error_handling'
  import export_source_icons from '../regular_concrete/export_source_icons'
  import free_tier_limit_dialog from '../free_tier_limits/free_tier_limit_dialog'

  import axios from '../../services/customInstance';
  import Vue from "vue";
  import Export_connection_dialog from "./export_connection_dialog.vue";
  import {create_event} from "../event/create_event";


  export default Vue.extend({
      name: 'export',

      components: {
        Export_connection_dialog,
        free_tier_limit_dialog,
        export_source_icons
      },
      props: {
        'project_string_id': {
          default: null
        },
        'version_id': {
          default: 0
        },
        'export_menu': {
          default: null
        }
      },
      data() {
        return {

          task_id: null,

          ann_is_complete: true,

          job: {},

          message_free_tier_limit: '',
          details_free_tier_limit: '',

          single_export_loading: false,

          // Should match export_source_icons.vue
          source_list: [
            {
              'name': 'directory',
              'display_name': 'Dataset',
              'icon': 'mdi-folder',
              'color': 'primary'
            },
            {
              'name': 'job',
              'display_name': 'Job',
              'icon': 'mdi-inbox',
              'color': 'green'
            },
            {
              'name': 'task',
              'display_name': 'Task',
              'icon': 'mdi-flash-circle',
              'color': 'purple'
            }
          ],

          source: "directory",

          masks: false,

          generate_annotations_pending: false,
          generate_annotations_success: false,

          annotation_example: false,

          format: 'JSON',
          format_options: ['JSON'], // ['JSON', 'YAML'],  // aug 12, 2020 pending weak ref resolution on yaml thing

          error: {},

          over_free_plan_limit: false,
          active_instances: 0,

          url: null,

          file_comparison_mode: "latest",
          file_comparison_mode_list: ["latest", "vs_original"],

          kind: "Annotations",
          kind_list: ["Annotations"],

          export_list: [],

          current_export: {},

          loading: false,

          options: {
            'sortBy': ['column1'],
            'sortDesc': [true],
            'itemsPerPage': -1
          },
          dialog: false,

          header: [
            {
              text: "Date",
              align: 'left',
              sortable: true,
              value: 'id'
            },
            {
              text: "Status",
              align: 'left',
              sortable: false,
              value: 'status'
            },
            {
              text: "Source",
              align: 'left',
              sortable: false,
            },
            /*
            {
              text: "Comparison Mode",
              align: 'left',
              sortable: false,
            },
            */
            {
              text: "File Count",
              align: 'left',
              value: 'file_list_length',
              sortable: true,
            },
            {
              text: "Complete Only",
              align: 'left',
              value: 'ann_is_complete',
              sortable: true,
            },
            {
              text: "Masks",
              align: 'left',
              sortable: false,
            },
            {
              text: "Kind",
              align: 'left',
              sortable: false,
            },
            {
              text: "Actions",
              align: 'left',
              sortable: false,
            }
          ],
          selected_item: {}
        }
      },
      computed: {},
      watch: {
        export_menu(state) {
          if (state == true) {
            this.get_export_list()
          }
        }
      },
      created() {
        this.task_id = this.$route.query["task_id"]
        if (this.task_id) {
          this.source = "task"

          /*
            we don't want this to be too aggressive / duplicate
            so if we we have already loaded the list then skip doing it

            we do want to generate this right away when clicked though so it's smoother
            from the UI.

            tried checking export list but not right approach

            Pushing the route to just the path has the effect that at
            least if we go click something else
            the most recent history is without this
           *
           */

          // this.generate_annotations_function()

        }
      },

      mounted() {
        this.get_export_list();
        this.add_visit_history_event();
      },

      methods: {
        add_visit_history_event: async function () {
          const event_data = await create_event(this.$props.project_string_id, {
            page_name: 'export_dashboard',
            object_type: 'page',
            user_visit: 'user_visit',
          })
        },
        open_connection_export_dialog(item) {
          this.selected_item = item;
          this.$refs.export_connection_dialog.open_export_dialog();
        },
        generate_annotations_function() {

          this.loading = true
          this.generate_annotations_success = false
          this.free_plan_limit = false
          this.error = {}

          // For now we assume that ann_is_complete being False includes
          // "All" so we reset it to None
          if (this.ann_is_complete == false) {
            this.ann_is_complete = null
          }

          axios.post('/api/walrus/project/' + String(this.project_string_id)
            + '/export/to_file',
            {
              kind: this.kind,
              source: this.source,
              masks: this.masks,
              file_comparison_mode: this.file_comparison_mode,
              version_id: this.version_id,
              directory_id: this.$store.state.project.current_directory.directory_id,
              job_id: this.job.id,
              task_id: this.task_id,
              ann_is_complete: this.ann_is_complete

            })
            .then(response => {
              if (response.data.success = true) {

                this.current_export = response.data.export
                this.export_list.unshift(this.current_export)
                this.generate_annotations_pending = true

                var self = this
                this.generate_annotations_status_interval = setInterval(function () {
                  self.generate_annotations_status()
                }, 10000)

                this.loading = false
              }

            }).catch(e => {

            console.log(e)
            if (e.response.data.log &&
              e.response.data.log.error.free_tier_limit) {
              this.message_free_tier_limit = 'The invite failed because you reached your one of the in the free tier of Diffgram.'
              this.details_free_tier_limit = e.response.data.log.error.free_tier_limit;
              this.$refs.free_tier_limit_dialog.open();
            }
            this.error = route_errors(e)

            this.loading = false
          })
        },

        get_export_list() {

          this.loading = true
          this.error = {}

          axios.get('/api/walrus/project/' + String(this.project_string_id)
            + '/export/working_dir/list')
            .then(response => {
              /* In new context a 200 is a success so we don't need to check it
               * (400 should be pushed to catch / error handling)
               */

              this.export_list = response.data.export_list
              this.loading = false

            }).catch(e => {
            console.log(e)
            this.error = route_errors(e)
            this.loading = false
          })
        },

        post_export_link(export_) {

          this.loading = true
          axios.post('/api/walrus/project/' + String(this.project_string_id)
            + '/export/link', {
            'format': this.format,
            'id': export_.id,
            'return_mode': "url"
          })
            .then(response => {

              this.url = response.data
              this.loading = false

              window.open(this.url);

            }).catch(e => {
            console.log(e)
            this.loading = false
          })
        },


        generate_annotations_status() {

          this.single_export_loading = true

          axios.get('/api/walrus/project/' + String(this.project_string_id)
            + '/export/' + this.current_export.id
            + '/status')
            .then(response => {
              if (response.data.success = true) {

                if (response.data.export.status == "complete") {

                  this.generate_annotations_success = true
                  clearInterval(this.generate_annotations_status_interval)
                }

                // general updates to status
                for (let i in this.export_list) {
                  if (this.export_list[i].id == response.data.export.id) {
                    this.export_list.splice(i, 1, response.data.export)
                  }
                }

              }
              /* Careful to set loading to false,
               * since loading refers to the HTTP reqest NOT the specific export.
               * It's confusing if everything else shows "loading",
               * and it blocks the user being able to refresh it manually.
               * We already block download if individuala items aren't ready
               * so this isn't needed.
               *
               */
              this.single_export_loading = false

            }).catch(e => {
            console.log(e)
            this.single_export_loading = false
          })
        },


        update_export(export_, mode) {

          this.loading = true
          axios.post('/api/walrus/project/' + String(this.project_string_id)
            + '/export/update', {
            id: parseInt(export_.id),
            mode: mode
          })
            .then(response => {


              this.loading = false
              // refresh
              this.get_export_list()


            }).catch(e => {
            console.log(e)
            this.loading = false
          })
        }
      }
    }
  ) </script>

