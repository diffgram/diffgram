<template>
  <div id="input_view">

    <v-card elevation="0">
      <v-container fluid>

        <v-card-title>
          <h3> {{ title }} </h3>

          <v-btn @click="get_input_list"
                 :loading="loading"
                 @click.native="loader = 'loading'"
                 :disabled="loading"
                 color="primary"
                 data-cy="refresh-input-icon"
                 icon
                 text
          >
            <v-icon> refresh</v-icon>
          </v-btn>

        </v-card-title>

        <v-layout v-if="show_filters">
          <diffgram_select
            v-if="show_status_filter"
            :item_list="status_filters_list"
            v-model="status_filter"
            label="Status"
            :disabled="loading"
            @change="get_input_list"
          >
          </diffgram_select>

          <date_picker @date="date = $event"
                       :with_spacer="true"
                       :initialize_empty="true">
          </date_picker>

          <v-select
            :items="metadata_limit_options"
            v-model="metadata_limit"
            label="Limit"
            item-value="text"
            :disabled="loading"></v-select>

          <v-text-field
            type="number"
            clearable
            v-model="batch_id_filter"
            label="Filter by Batch ID">
          </v-text-field>


          <v-text-field
            type="number"
            clearable
            v-model="file_id_filter"
            label="Filter by File ID">
          </v-text-field>


          <!-- Admin only
               as we are still reviewing this feature -->

          <!-- Retry -->
          <tooltip_button
            tooltip_message="Retry Selected Inputs"
            @click="update_import(null, 'RETRY')"
            icon="mdi-redo-variant"
            :loading="loading"
            :disabled="loading || selected.length == 0"
            :text_style="true"
            color="primary">
          </tooltip_button>


          <button_with_confirm
            v-if="$store.state.user.current.is_super_admin == true"
            @confirm_click="update_import(null, 'ARCHIVE')"
            color="pink"
            icon="archive"
            tooltip_message="Archive and remove associated file."
            :icon_style="true"
            :loading="loading"
            :disabled="loading || selected.length == 0">
          </button_with_confirm>


        </v-layout>


        <v_error_multiple :error="error">
        </v_error_multiple>

        <v-alert type="warning"
                 v-if="error_video"
                 dismissible
        >
          {{error_video}}

          <v-btn color="blue darken-1"
                 dark
                 href="https://diffgram.readme.io/docs/video-specifications"
                 target="_blank"
          >
            <v-icon left>mdi-video</v-icon>
            Video docs
          </v-btn>

        </v-alert>


        <v-data-table style="overflow-x: auto;"
                      :headers="headers"
                      :items="input_list"
                      item-key="id"
                      :options.sync="options"
                      v-model="selected"
                      show-select
                      data-cy="input-table"
        >
          <!-- maybe look at
            :show-select="$store.state.user.current.is_super_admin"-->


          <!-- appears to have to be item for vuetify syntax-->
          <template slot="item" slot-scope="props">
            <tr >
              <td>
                <v-checkbox

                  v-model="props.isSelected"
                  @change="props.select($event)"
                  primary>
                </v-checkbox>
              </td>

              <td>
                <span>{{ props.item.created_time | moment("ddd, MMM D h:mm:ss a") }} </span>

              </td>

              <td>

                <!--
                   These are two seperate tooltips even though they repeat the status text
                   in new setup having two activators in one template did not seem to work
                   maybe have to use a different variable name (ie "on" can't be reused??)
                  -->

                <v-layout>
                  <div v-if="props.item.status == 'processing' && props.item.processing_deferred != true">
                    <v-tooltip bottom>
                      <!-- Use negation here as we are adding a bunch of new
                           statuses -->
                      <!-- Don't show if queued since otherwise it doesn't
                            make sense / redundent / different-->

                      <template v-slot:activator="{ on }">
                        <v-progress-circular indeterminate
                                             v-on="on"
                                             color="primary">
                        </v-progress-circular>
                      </template>


                      <span v-if="props.item.status_text">
                      {{props.item.status_text}}
                      </span>
                      <span v-if="props.item.status">
                      {{props.item.status}}
                      </span>

                      <!-- careful 'status' vs 'status_text', status_text may be null
                          which can be confusing for visual display (since it suppresses null values)
                          -->
                    </v-tooltip>
                  </div>



                  <!-- Update log
                       As of Sept 3 2020 this is just errors
                       In future could be other updates too
                    -->
                  <button_with_menu
                    v-if="props.item.mode=='update'
                        && props.item.status=='failed'
                        && props.item.update_log"
                    tooltip_message="Log"
                    icon="error"
                    color="primary"
                    :close_by_button="true"
                  >

                    <template slot="content">
                      <v-layout column>

                        <v-card-title> Log</v-card-title>

                        <v_error_multiple :error="props.item.update_log['error']">
                        </v_error_multiple>

                        <!-- Not showing info messages here yet -->


                      </v-layout>
                    </template>

                  </button_with_menu>


                  <!-- Uploading -->
                  <tooltip_icon
                    v-if="props.item.source == 'from_resumable' &&
                            props.item.status == 'init'"
                    tooltip_message="Uploading - Keep Window Open!"
                    icon="mdi-progress-upload"
                    color="black">
                  </tooltip_icon>

                  <!-- VIDEO processing status -->
                  <tooltip_icon
                    v-if="props.item.status == 'loaded_video'"
                    tooltip_message="Processing - Loading Video"
                    icon="mdi-video-plus"
                    color="primary">
                  </tooltip_icon>

                  <tooltip_icon
                    v-if="props.item.status == 'retrying'"
                    tooltip_message="Retrying..."
                    icon="mdi-progress-wrench"
                    color="primary">
                  </tooltip_icon>

                  <tooltip_icon
                    v-if="props.item.status == 'pushing_frames_into_processing_queue'"
                    tooltip_message="Processing - Pushing Frames"
                    icon="mdi-library-video"
                    color="green">
                  </tooltip_icon>

                  <tooltip_icon
                    v-if="props.item.status == 'processing_frames_in_queue'"
                    tooltip_message="Processing Frames"
                    icon="mdi-tray-full"
                    color="primary">
                  </tooltip_icon>

                  <!-- End VIDEO status -->

                  <!-- Downloaded
                     ie for from API
                    -->
                  <tooltip_icon
                    v-if="props.item.status == 'downloaded'"
                    tooltip_message="Processing"
                    icon="mdi-progress-download"
                    color="primary">
                  </tooltip_icon>

<!--                  <p  v-if="props.item.log && props.item.status == 'failed'" class="error&#45;&#45;text">{{JSON.stringify(props.item.log)}}</p>-->
<!--                  <p  v-if="props.item.status == 'failed'" class="error&#45;&#45;text">{{props.item.status_text}}</p>-->
                  <tooltip_icon
                    v-if="props.item.status == 'failed'"
                    :tooltip_message="props.item.status_text"
                    icon="error"
                    color="error">
                  </tooltip_icon>

                  <tooltip_icon
                    v-if="props.item.status == 'success'"
                    tooltip_message="Success"
                    icon="check"
                    color="green">
                  </tooltip_icon>


                  <tooltip_icon
                    v-if="props.item.processing_deferred == true"
                    tooltip_message="Queued"
                    icon="mdi-timer-sand"
                    color="orange">
                  </tooltip_icon>

                </v-layout>
              </td>

              <td>
                <v-tooltip v-if="props.item.percent_complete != 0
                             && props.item.processing_deferred != true"
                           bottom>
                  <template v-slot:activator="{ on }">
                    <v-progress-linear v-model="props.item.percent_complete"
                                       v-on="on"
                    >
                    </v-progress-linear>
                  </template>
                  {{Math.round(props.item.percent_complete)}} %
                </v-tooltip>
              </td>

              <td style="overflow:auto;">
                <span>
                    {{ props.item.original_filename}}
                </span>

              </td>
              <td>

                <a
                  @click="filter_by_batch(props.item.batch_id)">
                  {{ props.item.batch_id}}
                </a>

              </td>
              <td>

                <a
                  class="file-link"
                  :href="'/file/' + props.item.file_id">
                  {{ props.item.file_id}}
                </a>
                <div v-if='props.item.newly_copied_file_id'>
                Copied to ->
                </div>
                <a v-if='props.item.newly_copied_file_id'
                  :href="'/file/' + props.item.newly_copied_file_id">
                  {{ props.item.newly_copied_file_id}}
                </a>


              </td>
              <td>

                <a
                  v-if="props.item.task_id"
                  :href="`/task/${props.item.task_id}/?view_only=true`">
                  {{ props.item.task_id}}
                </a>
                <p v-else>N/A</p>

              </td>

              <td>
                <!-- In update mode, Dataset doesn't really make sense to list -->
                <regular_chip
                  v-if="props.item.directory &&
                                 props.item.mode !='update' "
                  :message=props.item.directory.nickname
                  tooltip_message="Go to Dataset"
                  color="primary"
                  tooltip_direction="bottom"
                  :small="true"
                  @click="$router.push('/studio/annotate/'
                      + project_string_id + '?dataset=' + props.item.directory.id)"
                >
                </regular_chip>

                <div v-if="props.item.mode == 'update'">
                  N/A
                </div>
              </td>

              <td>

                <tooltip_icon
                  v-if="props.item.media_type == 'image'"
                  tooltip_message="Image"
                  icon="image"
                  color="primary">
                </tooltip_icon>


                <div v-if="props.item.media_type == 'video'">

                  <tooltip_icon
                    tooltip_message="Video"
                    icon="mdi-file-video"
                    color="green">
                  </tooltip_icon>

                  <div v-if="props.item.video_was_split">
                    <v-icon color="green"
                            alt="props.item.media_type">mdi-directions-fork
                    </v-icon>


                    Split Duration:
                    {{props.item.video_split_duration}}
                    seconds.
                  </div>

                  <!-- TODO, get the FPS info here too if applicable?-->

                </div>
                <div v-if="props.item.media_type == 'label'">
                  <v-icon alt="props.item.media_type">label</v-icon>
                </div>

              </td>

              <!-- Source
                ie ["from_resumable", "from_url", "from_video_split"]
                -->

              <td>
                <!-- For now mode is part of this too -->
                <v-layout>
                  <tooltip_icon
                    v-if="props.item.source == 'from_resumable'"
                    tooltip_message="User Interface"
                    icon="mdi-television-guide"
                    color="primary">
                  </tooltip_icon>

                  <tooltip_icon
                    v-else-if="props.item.source == 'from_video_split'"
                    tooltip_message="Video Split"
                    icon="mdi-call-split"
                    color="blue">
                  </tooltip_icon>

                  <tooltip_icon
                    v-else-if="props.item.source == 'from_url'"
                    tooltip_message="SDK / API"
                    icon="mdi-api"
                    color="green">
                  </tooltip_icon>

                  <v-chip v-else small color="primary">
                    <strong> {{props.item.source}}</strong>
                  </v-chip>

                  <tooltip_icon
                    v-if="props.item.mode == 'update'"
                    tooltip_message="Update"
                    icon="mdi-database-plus"
                    color="primary">
                  </tooltip_icon>


                  <tooltip_button
                    v-if="props.item.mode == 'update' || props.item.mode == 'update_with_existing'"
                    tooltip_message="Raw Instance List & Frame Map"
                    icon="mdi-dump-truck"
                    :icon_style="true"
                    @click="open_input_payload_dialog(props.item)"
                    color="primary">
                  </tooltip_button>



                </v-layout>


              </td>

              <td>

                <div v-if="$store.state.user.current.is_super_admin == true">

                  ID: {{ props.item.id }}

                  {{ props.item.total_time }}

                  {{ props.item.raw_data_blob_path }}

                  <div v-if="props.item.retry_log">

                    {{props.item.time_last_attempted}}
                    {{props.item.retry_count}}

                    <div v-for="key in Object.keys(props.item.retry_log)">

                      <h4> {{key}} <span><strong>{{props.item.retry_log[key]['info']}}</strong></span></h4>

                    </div>
                  </div>

                </div>

              </td>

            </tr>
          </template>

          <div v-if="!loading">

            <v-alert slot="no-data" color="error" icon="warning">
              No results found.
            </v-alert>
          </div>

        </v-data-table>


        <div v-if="$store.state.user.current.is_super_admin == true">
          <v-checkbox v-model="show_deferred"
                      label="SA: show_deferred">
          </v-checkbox>
          <v-checkbox v-model="show_archived"
                      label="SA: show_archived">
          </v-checkbox>
        </div>


      </v-container>
    </v-card>
    <input_payload_dialog :selected_input="selected_input"
                          :project_string_id="project_string_id"
                          ref="payload_dialog">

    </input_payload_dialog>

  </div>
</template>

<script lang="ts">

  import axios from 'axios';
  import input_payload_dialog from './input_payload_dialog'
  import Vue from "vue";
  import sizeof from 'object-sizeof'

  export default Vue.extend({
      name: 'input_view',
      components:{
        input_payload_dialog
      },
      props: {
        'project_string_id': {
          default: null
        },
        'input_menu': {
          default: null,
          required: false
        },
        'request_refresh': {
          default: null
        },
        'show_status_filter': {
          default: true,
        },
        'task_id': {
          default: null
        },
        'show_filters': {
          default: true
        },
        'initial_status_filter':{
          default: undefined
        },
        'title': {
          default: 'Processing Status & History'
        }
      },

      data() {

        return {

          file_id_filter: null,
          batch_id_filter: null,

          metadata_limit_options: [10, 25, 50, 100, 250, 500],
          metadata_limit: 10,

          date: undefined,
          selected_input: {},

          status_filters_list: [
            {
              'name': 'All',
              'icon': ''
            },
            {
              'name': 'Success',
              'icon': 'check',
              'color': 'green'
            },
            {
              'name': 'Failed',
              'icon': 'error',
              'color': 'red'
            },
            {
              'name': 'Processing',
              'icon': ''
            }
          ],

          status_filter: "All",

          error_video: false,
          show_deferred: true,

          selected: [],

          show_archived: false,

          error: {},

          input_list: [],

          current_input: {},

          options: {
            //sortBy: ['created_time'],
            //sortDesc: [true],
            itemsPerPage: -1
          },

          loading: false,

          headers: [
            {
              text: "Date",
              align: 'left',
              sortable: true,
              value: 'created_time'
            },
            {
              text: "Status",
              align: 'left',
              sortable: true,
              value: 'status'
            },
            {
              text: "Progress",
              align: 'left',
              sortable: true,
              value: 'percent_complete',
              width: "100px",
              fixed: true
            },
            {
              text: "Filename",
              align: 'left',
              sortable: true,
              value: 'original_filename',
              width: "200px",
              fixed: true
            },
            {
              text: "Batch ID",
              align: 'left',
              sortable: true,
              value: 'batch_id'
            },
            {
              text: "File ID",
              align: 'left',
              sortable: true,
              value: 'file_id'
            },
            {
              text: "Task ID",
              align: 'left',
              sortable: true,
              value: 'file_id'
            },
            {
              text: "Dataset (Destination)",
              align: 'left',
              sortable: false
            },
            {
              text: "Type",
              align: 'left',
              sortable: false,
            },
            {
              text: "Source",
              align: 'left',
              sortable: false,
            }
          ]
        }

      },
      computed: {},
      watch: {
        input_menu(state) {
          if (state == true) {
            this.get_input_list()
          }
        },
        request_refresh(state) {
          this.get_input_list()
        },
        task_id: function(old, new_val){
          this.get_input_list();
        }
      },
      mounted() {

        // triggered by  this.$store.commit('request_input_list_refresh')

        var self = this

        this.input_list_refresh_watcher = this.$store.watch((state) => {
            return this.$store.state.input.list_refresh
          },
          (new_val, old_val) => {
            self.get_input_list()
          },
        )
        if(this.$props.initial_status_filter){
          this.status_filter = this.$props.initial_status_filter;
        }
        this.get_input_list()

      },

      beforeDestroy() {
        this.input_list_refresh_watcher() // destroy watcher
      },

      methods: {
        open_input_payload_dialog: function(input){
          this.selected_input = input;
          this.$refs.payload_dialog.open();

        },
        filter_by_batch: function(batch_id){
          this.batch_id_filter = batch_id;
          this.get_input_list()
        },

        async get_input_list() {

          if (this.project_string_id == null) {
            return false
          }

          this.error = {}
          this.error_video = null
          try {
            const response = await axios.post('/api/walrus/v1/project/' + this.project_string_id
              + '/input/view/list', {
              limit: this.metadata_limit,
              show_archived: this.show_archived,
              show_deferred: this.show_deferred,
              status_filter: this.status_filter,
              date_from: this.date ? this.date.from : undefined,
              date_to: this.date ? this.date.to : undefined,
              file_id: parseInt(this.file_id_filter),
              batch_id: parseInt(this.batch_id_filter),
              task_id: this.$props.task_id
            })

            if (response.data.success == true) {

              this.input_list = response.data.input_list

              // Just check most recent one
              // Otherwise when this updates it keeps pulling message

              //for (let input of this.input_list) {}

              if (this.input_list[0]) {

                if (this.input_list[0].status == "failed") {

                  if (this.input_list[0].media_type == "video") {

                    this.error_video = "Uh oh! It looks like one of your videos had an error." +
                      " Hover over / click status icons to see messages."


                  }
                }
              }


            }
          } catch (error) {
            this.error = this.$route_api_errors(error)
            console.error(error)
          } finally {
            this.loading = false
          }

        },


        input_status_single() {

          // TODO review this,
          // was a hold over from export stuff a bit...

          // Would be godo to be able to update singles ones though.

          this.loading = true
          axios.get('/api/project/' + String(this.project_string_id)
            + '/input/' + this.current_input.id
            + '/status')
            .then(response => {
              if (response.data.success = true) {

                if (response.data.input.status == "complete") {

                  this.loading = false
                  this.generate_annotations_success = true
                  for (let i in this.input_list) {
                    if (this.input_list[i].id == response.data.input.id) {
                      this.input_list.splice(i, 1, response.data.input)
                    }
                  }

                  clearInterval(this.generate_annotations_status_interval)
                }

              }
            }).catch(e => {
            console.error(e)
          })
        },

        update_import(id, mode) {

          var id_list = []

          if (id) {
            // import_ is assumed to be an id... this is kinda messsy
            id_list = [parseInt(id)]
          } else {
            for (var input of this.selected) {
              id_list.push(input.id)
            }
          }

          this.loading = true
          axios.post('/api/walrus/v1/project/' + String(this.project_string_id)
            + '/input/update', {
            id_list: id_list,
            mode: mode
          })
            .then(response => {

              this.loading = false
              // refresh
              this.get_input_list()


            }).catch(e => {
            console.error(e)
            this.loading = false
          })
        }
      }
    }
  ) </script>

