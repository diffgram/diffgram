<template>
  <div v-cloak>
    <v-card>

      <v-card-title>
        Task List
      </v-card-title>

      <!-- Temporary button -->
      <v-btn  @click="$router.push('/task/' + task_list[0].id )"
              :loading="loading"
              color="primary"
              large
      >
        Start Annotating
      </v-btn>

      <v-layout v-if="external_interface === 'labelbox' && !pending_initial_dir_sync && task_list.length > 0">
        <v-row>
          <v-col cols="12" class="d-flex align-center justify-center">
            <h3 class="mr-4">Start labeling with</h3>
            <img width="100px" height="80px" src="https://labelbox.com/static/images/logo-v3.svg" alt="">
            <a :href='`https://editor.labelbox.com/?project=${labelbox_project_id}`' target="_blank">
              <v-btn type="primary" color="primary" class="ml-4">
                <v-icon>mdi-play</v-icon>
                Start Labeling
              </v-btn>
            </a>
          </v-col>
        </v-row>
      </v-layout>
      <v-layout v-else-if="external_interface === 'datasaur' && !pending_initial_dir_sync && task_list.length > 0">
        <v-row>
          <v-col cols="12" class="d-flex align-center justify-center">
            <h3 class="mr-4">Start labeling with</h3>
            <img width="150px" height="100px"
                 src="https://venturebeat.com/wp-content/uploads/2020/02/datasaur.png?w=1200&strip=all" alt="">
            <a :href='`https://datasaur.ai/projects/${datasaur_project_id}/`' target="_blank">
              <v-btn type="primary" color="primary" class="ml-4">
                <v-icon>mdi-play</v-icon>
                Start Labeling
              </v-btn>
            </a>
          </v-col>
        </v-row>
      </v-layout>
      <!-- TODO show date picker if null ?-->

      <!--
      <date_picker @date="date = $event">
      </date_picker>
      -->

      <!-- start list view -->
      <div v-if="mode_view=='list'">

        <v-container>
          <v-layout>

            <div v-if="['direct_route', 'exam_results'].includes(mode_data)">

              <!--
              <v-checkbox v-model="my_stuff_only"
                          label="My tasks Only">
              </v-checkbox>
              -->
              <v-layout class="d-flex justify-start align-center">
                <task_status_select
                  :clearable="true"
                  v-model="task_status"
                  label="Status"
                  :disabled="loading">
                </task_status_select>
                <v-select
                  v-model="issues_filter"
                  :items="issue_filter_options"
                  :clearable="true"
                  label="Filer by Issues"
                  item-text="name"
                  item-value="value"
                ></v-select>
                <date_picker @date="date = $event" :with_spacer="false" :initialize_empty="true">
                </date_picker>
                <v_directory_list
                  class="ml-4 mr-8"
                  :project_string_id="project_string_id"
                  :show_new="false"
                  :clearable="true"
                  label="Incoming Dataset"
                  :show_update="false"
                  :update_from_state="false"
                  :set_current_dir_on_change="false"
                  :initial_dir_from_state="false"
                  @change_directory="on_change_dir"
                ></v_directory_list>
                <v-btn @click="refresh_task_list"
                       :loading="loading"
                       color="primary">
                  Refresh
                </v-btn>
                <v-layout class="ml-6 d-flex justify-self-end align-center">
                  <v-select
                    :clearable="true"
                    :items="actions_list"
                    v-model="selected_action"
                    item-value="value"
                    item-text="name"
                    label="Actions"
                    class="mr-4"
                    :disabled="selected_tasks.length === 0">
                  </v-select>
                  <v-btn @click="show_confirm_archive_model"
                         v-if="selected_action === 'archive' && selected_tasks.length > 0"
                         :loading="loading"

                         :disabled="selected_tasks.length === 0"
                         color="error">
                    <v-icon>mdi-archive</v-icon>
                    Archive
                  </v-btn>
                </v-layout>
              </v-layout>

            </div>

          </v-layout>
        </v-container>


        <v_error_multiple :error="error_attach">
        </v_error_multiple>

        <v-alert type="success"

                 v-if="show_success_attach">

        </v-alert>

        <v_error_multiple :error="error_send_task">
        </v_error_multiple>
        <v-data-table v-bind:headers="header_view"
                      v-if="task_list.length > 0"
                      :items="task_list"
                      item-key="id"
                      :loading="loading"
                      :options.sync="options"
                      footer-props.prev-icon="mdi-menu-left"
                      footer-props.next-icon="mdi-menu-right">

          <!-- review rows-per-page-items setting-->
          <!-- appears to have to be item for vuetify syntax-->
          <template slot="item"
                    slot-scope="props">

            <tr>
              <td>
                <v-checkbox v-model="props.item.is_selected">
                </v-checkbox>

              </td>
              <td>
                {{props.item.id}}

              </td>
              <td>
                <v-btn @click="open_input_log_dialog(props.item.id)" type="primary" small color="primary" outlined>
                  <v-icon color="primary">mdi-format-list-bulleted</v-icon>
                </v-btn>

              </td>
              <td>
                <v-icon color="primary">mdi-folder</v-icon>
                {{props.item.incoming_directory.nickname}}

              </td>
              <td>
                <task_status_icons
                  :status="props.item.status"
                >
                </task_status_icons>
              </td>
              <td v-if="mode_data!='exam_results'">
                {{props.item.task_type}}
              </td>
              <td>
                <div v-if="props.item.time_updated">
                  {{props.item.time_updated | moment("ddd, MMM Do H:mm:ss a")}}
                </div>
              </td>
              <td>
                <div v-if="props.item.time_created">
                  {{props.item.time_created | moment("ddd, MMM Do H:mm:ss a")}}
                </div>
              </td>

              <td v-if="mode_data!='exam_results' && show_detail_button">

                  <v-btn @click="route_task(props.item.id)"
                         :loading="loading"
                         color="primary"
                         v-if="!integration_name"
                       >
                    View
                  </v-btn>

                <v-container v-if="!props.item.loading && props.item.status === 'available'"
                             class="d-flex justify-center align-center">

                  <v-btn v-if="integration_name === 'scale_ai'"
                         @click="send_to_external(props.item)"
                         :loading="loading"
                         class="d-flex align-center mr-4"
                         :outlined=true
                         color="primary">
                    <span>Send To:</span>
                    <v-img style="margin-bottom: 5px" width="80px" height="45px"
                           src="https://uploads-ssl.webflow.com/5f07389521600425ba513006/5f1750e39c67ad3dd7c69015_logo_scale.png">

                    </v-img>

                  </v-btn>

                </v-container>

                <v-container class="d-flex justify-center align-center"
                             v-if="integration_name&&
                                  !props.item.loading
                                  && props.item.status === 'in_progress'">
                  <p class="primary--text font-weight-bold">
                    <v-icon color="primary">mdi-refresh</v-icon>
                    Task is being processed by external provider.
                  </p>
                </v-container>
                <v-container class="d-flex justify-center align-center"
                             v-else-if="!props.item.loading && props.item.status === 'complete'">

                  <a
                    v-if="integration_name === 'labelbox' && props.item.external_id"
                    :href='`https://editor.labelbox.com/?project=${labelbox_project_id}&label=${props.item.external_id}`'
                    target="_blank">

                    <v-btn
                      @click="send_to_external(props.item)"
                      :loading="loading"
                      class="d-flex align-center mr-4 justify-center"
                      :outlined=true
                      color="primary">
                      <v-img style="margin-bottom: 0px" width="32px" height="32px"
                             src="https://cdn.theorg.com/e1e775ca-6ad1-4c9e-847e-44856cfc75a4_thumb.jpg">

                      </v-img>
                      <span>View On Labelbox:</span>

                    </v-btn>
                  </a>
                </v-container>
     
                <v-container class="d-flex justify-center align-center"
                             v-if="integration_name && !props.item.loading">
                  <v-btn @click="route_task(props.item.id)"
                         :loading="loading"
                         color="primary">
                    View
                  </v-btn>
                </v-container>

                <v-progress-linear v-if="loading"
                                     color="primary"
                                     :indeterminate="true"></v-progress-linear>

                <!-- TODO review this function -->

                <!--
                <v-btn v-if="props.item.task_type == 'review' &&
                       props.item.status == 'complete' &&
                       props.item.job_type != 'Exam'
                       "
                       @click="route_task_diff(props.item.id)"
                       :loading="loading"
                       color="green">
                  Review
                </v-btn>
                    -->
              </td>

              <td>
                  <v_user_icon :user_id="props.item.assignee_user_id">
                  </v_user_icon>
              </td>

              <td v-if="mode_data=='exam_results'">
                <v-rating v-model="props.item.review_star_rating_average"
                          readonly
                >
                </v-rating>
              </td>
              <td v-if="mode_data=='exam_results'">
                {{props.item.gold_standard_missing}}
              </td>

            </tr>
          </template>

          <div v-if="!loading">
            <v-alert slot="no-data" color="error" icon="warning">
              No results found.
            </v-alert>
          </div>

        </v-data-table>
        <v-container v-else-if="task_list.length === 0 && has_filters_applied">
          <v-row>
            <v-col cols="12" class="d-flex flex-column align-center justify-center">
              <h2>No tasks available for current criteria.</h2>
              <v-icon size="160" color="primary">mdi-archive</v-icon>
              <h4>If you already added files to the attached datasets, tasks should start appearing soon!</h4>
              <h4>Press the refresh button to check for new tasks.</h4>
            </v-col>
          </v-row>
        </v-container>
        <v-container v-else-if="task_list.length === 0 && !has_filters_applied">
          <v-row>
            <v-col cols="12" class="d-flex flex-column align-center justify-center">
              <h2>We are syncing tasks from the attached Datasets...</h2>
              <v-icon size="160" color="primary">mdi-sync</v-icon>
              <h4>Please change the search criteria and press the refresh button to check for new tasks.</h4>
            </v-col>
          </v-row>
        </v-container>
      </div>
      <!-- end list view -->

    </v-card>

  <task_input_list_dialog
    :task_id="selected_task_id"
    :project_string_id="project_string_id"
    ref="task_input_list_dialog"
  ></task_input_list_dialog>
    <v-dialog v-model="dialog_confirm_archive" max-width="450px">
      <v-card >
        <v-card-title class="headline">
          Confirm Task Archive
        </v-card-title>
        <v-card-text>
          Are you sure you want to archive this tasks?
        </v-card-text>
        <v_error_multiple :error="error_archive_task">
        </v_error_multiple>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn
            color="primary darken-1"
            text
            @click="dialog_confirm_archive = false"
          >
            Cancel
          </v-btn>
          <v-btn
            color="error darken-1"
            text
            :loading="loading_archive"
            @click="perform_task_list_action"
          >
            Archive Tasks
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
    <v-snackbar
      v-model="snackbar_success"
      :timeout="3000"
      color="primary"
    >
      Tasks archived successfully.

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
  </div>
</template>

<script lang="ts">

  import axios from 'axios';
  import {route_errors} from '../../regular/regular_error_handling'
  import task_status_icons from '../../regular_concrete/task_status_icons'
  import task_status_select from '../../regular_concrete/task_status_select'
  import task_input_list_dialog from '../../input/task_input_list_dialog'


  import Vue from "vue";

  export default Vue.extend({
      name: 'task_list',
      components: {
        task_status_icons,
        task_status_select,
        task_input_list_dialog
      },
      props: {
        'project_string_id': {
          default: null
        },
        'open_read_only_mode': {
          default: null
        },
        'show_detail_button': {
          default: true
        },
        'external_interface': {
          default: undefined
        },
        'job_id': {
          default: null
        },
        'job': {
          default: undefined
        },
        'mode_data': {
          default: "direct_route"   // job_edit, job_detail, user_profile, general/account?
        },
        'mode_view': {
          default: "list"  // list or grid?
        },
      },
      watch: {},
      data() {
        return {
          actions_list: [
            {name: 'Archive', value: 'archive'}
          ],
          selected: [],
          dialog_confirm_archive: false,
          issues_filter: undefined,
          issue_filter_options: [
            {name: 'Filter By Tasks With Open Issue', value: 'open_issues'},
            {name: 'Filter By Tasks With Closed Issues', value: 'closed_issues'},
            {name: 'Filter By Tasks Any Issues', value: 'issues'},
          ],
          loading_archive: false,
          snackbar_success: false,
          selected_action: undefined,
          api_limit_count: 1000,

          date: undefined,   // TODO use date as a prop to sync with stats?

          task_list: [],

          task_status: 'all',
          task_id: undefined,
          selected_task_id: undefined,

          loading: false,
          incoming_directory: undefined,
          options: {
            'sortBy': ['column2'],
            'sortDesc': [true],
            'itemsPerPage': 20
          },

          error_attach: {},
          error_send_task: {},
          error_archive_task: {},
          show_success_attach: false,
          pending_initial_dir_sync: true,


          request_next_page_flag: false,
          request_next_page_available: true,

          header: [
            {
              text: "Select",
              align: 'left',
              sortable: false,
              value: 'is_selected'
            },
            {
              text: "ID",
              align: 'left',
              sortable: true,
              value: 'id'
            },
            {
              text: "Data Update Log",
              align: 'left',
              sortable: true,
              value: 'id'
            },
            {
              text: "Incoming Dataset",
              align: 'left',
              sortable: true,
              value: 'incoming_directory.nickname'
            },
            {
              text: "Status",
              align: 'left',
              sortable: true,
              value: 'status'
            },
            {
              text: "Type",
              align: 'left',
              sortable: true,
              value: 'task_type'
            },
            {
              text: "Last updated",
              align: 'left',
              sortable: true,
              value: 'time_updated'
            },
            {
              text: "Created",
              align: 'left',
              sortable: true,
              value: 'time_created'
            },
            {
              text: "Action",
              align: 'center',
              sortable: false,
              value: ''
            },
            {
              text: "Assigned User",
              align: 'center',
              sortable: false,
              value: ''
            }
          ],

          header_exam_results: [
            {
              text: "ID",
              align: 'left',
              sortable: true,
              value: 'id'
            },
            {
              text: "Status",
              align: 'left',
              sortable: true,
              value: 'status'
            },
            {
              text: "Last updated",
              align: 'left',
              sortable: true,
              value: 'time_updated'
            },
            {
              text: "Average Star Rating",
              align: 'left',
              sortable: true,
              value: ''
            },
            {
              text: "Missed instances",
              align: 'left',
              sortable: true,
              value: ''
            }
          ]

        }
      },

      computed: {
        header_view: function () {
          if (this.mode_data == "exam_results") {
            return this.header_exam_results
          }

          return this.header
        },
        has_filters_applied: function () {
          if (this.date) {
            return this.date.from || this.date.to
          }
          if (this.incoming_directory && this.incoming_directory.directory_id) {
            return true;
          }
          return false
        },
        selected_tasks: function(){
          return this.task_list.filter(t => t.is_selected);
        },
        labelbox_project_id: function () {
          if (this.job.interface_connection &&
            this.job.interface_connection.integration_name === 'labelbox') {
            const labelbox_mapping_task_template = this.job.external_mappings.filter(elm => {
              if (elm.connection_id === this.job.interface_connection_id) {
                return true
              }
            })
            if (labelbox_mapping_task_template.length > 0) {
              return labelbox_mapping_task_template[0].external_id;
            }
          }
          return undefined
        },
        datasaur_project_id: function () {
          if (this.job.interface_connection &&
            this.job.interface_connection.integration_name === 'datasaur') {
            const labelbox_mapping_task_template = this.job.external_mappings.filter(elm => {
              if (elm.connection_id === this.job.interface_connection_id) {
                return true
              }
            })
            if (labelbox_mapping_task_template.length > 0) {
              return labelbox_mapping_task_template[0].external_id;
            }
          }
          return undefined
        },
        integration_name: function () {
          if (this.job.interface_connection) {
            return this.job.interface_connection.integration_name;
          }
          return undefined;
        }

      },
      mounted() {
        if (this.job) {
          this.pending_initial_dir_sync = this.job.pending_initial_dir_sync
        }
        this.task_list_api()

      },
      methods: {
        async send_to_external(task) {
          task.loading = true;
          this.error_send_task = {};
          const connection = this.job.interface_connection;
          if (!connection) {
            return false;
          }
          const integration_name = connection.integration_name;
          try {
            let url;
            if (integration_name === 'scale_ai') {
              url = '/api/walrus/v1/connections/send-task-to-scale-ai';
            }
            if (!url) {
              return false;
            }
            const response = await axios.post(url, {
              task_id: task.id
            });
            if (response.status === 200) {
              task.status = 'in_progress'
            }

          } catch (error) {
            this.error_send_task = route_errors(error)
          } finally {
            task.loading = false;
          }

        },
        route_task(task_id) {
          let url = `/task/${task_id}`;

          this.$router.push({
            path: url,
            query: {
              view_only: this.open_read_only_mode
            }
          })
        },
        route_task_diff(task_id) {
          this.$router.push("/task/" + task_id + "/diff/" + "compare_review_to_draw")

        },
        on_change_dir(dir) {
          this.incoming_directory = dir;
        },
        open_input_log_dialog(task_id){
          this.selected_task_id = task_id;
          this.$refs.task_input_list_dialog.open()
        },
        async trigger_connection_interface_refresh() {
          const connection = this.job.interface_connection;
          if (!connection) {
            return;
          }
          if (connection.integration_name !== 'datasaur') {
            return
          }

          try {
            const response = await axios.post(`/api/walrus/v1/connectors/${connection.id}/fetch-data`, {
              opts: {
                'task_template_id': this.job_id,
                'action_type': 'sync_data_from_task_template'
              },
              project_string_id: this.project_string_id

            })

            if (response.data.log.success == true) {

              this.task_list = response.data.task_list
              this.pending_initial_dir_sync = response.data.pending_initial_dir_sync;

            }
            return response
          } catch (error) {
            console.error(error);
            return false;
          }
        },
        async task_list_api() {

          this.loading = true
          try {
            const response = await axios.post(`/api/v1/job/${this.job_id}/task/list`, {
              'date_from': this.date ? this.date.from : undefined,
              'date_to': this.date ? this.date.to : undefined,
              'job_id': this.job_id,
              'mode_data': this.mode_data,
              'incoming_directory_id': this.incoming_directory ? this.incoming_directory.directory_id : undefined,
              'status': this.task_status,
              'issues_filter': this.issues_filter,
              'limit_count': this.api_limit_count
            })

            if (response.data.log.success == true) {

              this.task_list = response.data.task_list
              this.pending_initial_dir_sync = response.data.pending_initial_dir_sync;

            }
            return response
          } catch (error) {
            console.error(error);
            return false;
          } finally {
            this.loading = false
          }

        },
        async refresh_task_list() {
          this.loading = true
          const result = await this.trigger_connection_interface_refresh()
          await this.task_list_api();

          this.loading = false;
        },
        async perform_task_list_action(){
          this.error_archive_task = {};
          this.loading_archive = true;
          try{
            if(this.selected_action === 'archive'){
              const response = await axios.post('/api/v1/task/update', {
                'task_ids': this.selected_tasks.map(x => x.id),
                'status': 'archived'
              })
              if(response.status === 200){
                await this.refresh_task_list();
                this.dialog_confirm_archive = false;
                this.snackbar_success = true;
                this.$emit('task_count_changed')
              }


            }

          }
          catch (error) {
            if(this.selected_action === 'archive'){
              this.error_archive_task = route_errors(error)
            }
          }
          finally {
            this.loading_archive = false;
          }
        },
        show_confirm_archive_model(){
          this.dialog_confirm_archive = true;
        }


      }
    }
  ) </script>
