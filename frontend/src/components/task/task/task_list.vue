<template>
  <div v-cloak>
    <v-card data-cy="task_list_container">
      <v-layout>
        <!-- Temporary button -->

        <v-layout
          v-if="
            external_interface === 'labelbox' &&
            !pending_initial_dir_sync &&
            task_list.length > 0
          "
        >
          <v-row>
            <v-col cols="12" class="d-flex align-center justify-center">
              <h3 class="mr-4">Start labeling with</h3>
              <img
                width="100px"
                height="80px"
                src="https://labelbox.com/static/images/logo-v3.svg"
                alt=""
              />
              <a
                :href="`https://editor.labelbox.com/?project=${labelbox_project_id}`"
                target="_blank"
              >
                <v-btn type="primary" color="primary" class="ml-4">
                  <v-icon>mdi-play</v-icon>
                  Start Labeling
                </v-btn>
              </a>
            </v-col>
          </v-row>
        </v-layout>
        <v-layout
          v-else-if="
            external_interface === 'datasaur' &&
            !pending_initial_dir_sync &&
            task_list.length > 0
          "
        >
          <v-row>
            <v-col cols="12" class="d-flex align-center justify-center">
              <h3 class="mr-4">Start labeling with</h3>
              <img
                width="150px"
                height="100px"
                src="https://venturebeat.com/wp-content/uploads/2020/02/datasaur.png?w=1200&strip=all"
                alt=""
              />
              <a
                :href="`https://datasaur.ai/projects/${datasaur_project_id}/`"
                target="_blank"
              >
                <v-btn type="primary" color="primary" class="ml-4">
                  <v-icon>mdi-play</v-icon>
                  Start Labeling
                </v-btn>
              </a>
            </v-col>
          </v-row>
        </v-layout>

        <v-container>
          <v-layout>
            <!-- Filters -->
            <button_with_menu
              tooltip_message="Filters"
              icon="mdi-filter"
              :close_by_button="true"
              offset="x"
              color="primary"
              datacy="task_list_filters"
              datacyclose="task_list_close_filters"
            >
              <template slot="content">
                <task_status_select
                  :clearable="true"
                  v-model="task_status"
                  label="Status"
                  @change="page_number = 0"
                  :disabled="loading"
                >
                </task_status_select>

                <v-select
                  v-model="issues_filter"
                  @change="page_number = 0"
                  :items="issue_filter_options"
                  :clearable="true"
                  label="Filer by Issues"
                  item-text="name"
                  item-value="value"
                ></v-select>

                <date_picker
                  @date="(date = $event), (page_number = 0)"
                  :with_spacer="false"
                  :initialize_empty="true"
                >
                </date_picker>

                <v-select
                  data-cy="task_list_per_page_limit_selector"
                  :items="per_page_limit_options"
                  v-model="per_page_limit"
                  label="Per Page"
                  item-value="text"
                  :disabled="loading"
                  @change="page_number = 0"
                ></v-select>

                <global_dataset_selector
                  class="ml-4 mr-8"
                  label="Incoming Dataset"
                  :clearable="true"
                  :update_from_state="false"
                  :set_current_dir_on_change="false"
                  :initial_dir_from_state="false"
                  @change_directory="on_change_dir, (page_number = 0)"
                />

                <v-btn
                  @click="refresh_task_list"
                  :loading="loading"
                  color="primary"
                  data-cy="task_list_refresh_task_list"
                >
                  Refresh
                </v-btn>
              </template>
            </button_with_menu>

            <v-spacer></v-spacer>

            <v-row
              class="pt-3"
              v-if="$store.state.job.current.file_count_statistic"
            >
              <div
                v-if="
                  !loading &&
                  page_end_index >
                    $store.state.job.current.file_count_statistic &&
                  $store.state.job.current.file_count_statistic > per_page_limit
                "
              >
                <v-chip color="white" text-color="primary"
                >No more pages.
                </v-chip
                >
              </div>
              <div>
                <v-chip color="white" text-color="primary">
                  {{ page_start_index }} to
                  {{ page_end_index }}
                </v-chip>

                <v-chip class="pl-2 pr-2" color="white" text-color="primary"
                >of {{ $store.state.job.current.file_count_statistic }}
                </v-chip>
              </div>

              <standard_button
                v-show="page_number != 0"
                datacy="task_list_previous_page"
                tooltip_message="Previous Page"
                @click="previous_page()"
                :disabled="loading"
                :icon_style="true"
                icon="mdi-chevron-left-box"
                color="primary"
              >
              </standard_button>

              <standard_button
                v-show="
                  page_end_index <
                    $store.state.job.current.file_count_statistic &&
                  $store.state.job.current.file_count_statistic > per_page_limit
                "
                tooltip_message="Next Page"
                datacy="task_list_next_page"
                @click="next_page()"
                :disabled="
                  loading ||
                  page_end_index > $store.state.job.current.file_count_statistic
                "
                :icon_style="true"
                icon="mdi-chevron-right-box"
                color="primary"
              >
              </standard_button>
            </v-row>

            <button_with_menu
              tooltip_message="Show/Hide Columns"
              icon="mdi-format-columns"
              :close_by_button="true"
              v-if="!view_only"
              offset="x"
              color="primary"
              datacy="show-hide-columns"
            >
              <template slot="content">
                <v-select
                  :items="column_list_all"
                  v-model="column_list"
                  multiple
                  label="Columns"
                  :disabled="loading"
                  data-cy="select-column"
                >
                </v-select>

                <standard_button
                  tooltip_message="Reset"
                  @click="column_list = column_list_backup"
                  v-if="column_list != column_list_backup"
                  icon="mdi-autorenew"
                  :icon_style="true"
                  color="primary"
                >
                </standard_button>
              </template>
            </button_with_menu>

            <v-select
              v-if="selected_tasks.length !== 0"
              :clearable="true"
              :items="actions_list"
              v-model="selected_action"
              item-value="value"
              item-text="name"
              label="Actions"
              class="mr-4"
              data-cy="select-task-list-action"
            >
            </v-select>
            <v-btn
              @click="show_confirm_archive_model"
              v-if="selected_action === 'archive' && selected_tasks.length > 0"
              :loading="loading"
              :disabled="selected_tasks.length === 0"
              color="error"
            >
              <v-icon>mdi-archive</v-icon>
              Archive
            </v-btn>
            <v-btn
              @click="() => on_batch_assign_dialog_open('assignee', false)"
              v-if="selected_action === 'assign' && selected_tasks.length > 0"
              :loading="loading"
              :disabled="selected_tasks.length === 0"
              color="primary"
              data-cy="add-batch-annotators-open"
            >
              <v-icon>mdi-account-plus-outline</v-icon>
              Add annotators
            </v-btn>
            <v-btn
              @click="() => on_batch_assign_dialog_open('assignee', true)"
              v-if="selected_action === 'remove' && selected_tasks.length > 0"
              :loading="loading"
              :disabled="selected_tasks.length === 0"
              color="error"
              data-cy="remove-batch-annotators-open"
            >
              <v-icon>mdi-account-minus-outline</v-icon>
              Remove annotators
            </v-btn>
            <v-btn
              @click="() => on_batch_assign_dialog_open('reviewer', false)"
              v-if="selected_action === 'assignReviewers' && selected_tasks.length > 0"
              :loading="loading"
              :disabled="selected_tasks.length === 0"
              color="primary"
            >
              <v-icon>mdi-account-plus-outline</v-icon>
              Add reviewers
            </v-btn>
            <v-btn
              @click="() => on_batch_assign_dialog_open('reviewer', true)"
              v-if="selected_action === 'removeReviewers' && selected_tasks.length > 0"
              :loading="loading"
              :disabled="selected_tasks.length === 0"
              color="error"
            >
              <v-icon>mdi-account-minus-outline</v-icon>
              Remove reviewers
            </v-btn>
          </v-layout>
        </v-container>
      </v-layout>

      <v_error_multiple :error="error_attach"></v_error_multiple>

      <v_error_multiple :error="get_annotations_error"></v_error_multiple>

      <v-alert type="success" v-if="show_success_attach"></v-alert>

      <v_error_multiple :error="error_send_task"></v_error_multiple>

      <v-skeleton-loader
        :loading="loading"
        type="table"
        data-cy="skeletonloader"
      >
        <task_list_table
          :project_string_id="project_string_id"
          :task_list="task_list"
          :allow_reviews="allow_reviews"
          :column_list="column_list"
          @assign_dialog_open="on_assign_dialog_open"
        >

        </task_list_table>


      </v-skeleton-loader>

      <v-container
        v-if="!loading && task_list.length === 0 && has_filters_applied"
      >
        <v-row>
          <v-col
            cols="12"
            class="d-flex flex-column align-center justify-center"
          >
            <h2>No tasks available for current criteria.</h2>
            <v-icon size="160" color="primary">mdi-archive</v-icon>
            <h4>
              If you already added files to the attached datasets, tasks should
              start appearing soon!
            </h4>
            <h4>Press the refresh button to check for new tasks.</h4>
          </v-col>
        </v-row>
      </v-container>
      <v-container
        v-if="task_list.length === 0 && !has_filters_applied && !loading"
      >
        <v-row>
          <v-col
            cols="12"
            class="d-flex flex-column align-center justify-center"
          >
            <h2>We are syncing tasks from the attached Datasets...</h2>
            <v-icon size="160" color="primary">mdi-sync</v-icon>
            <h4>
              Please change the search criteria and press the refresh button to
              check for new tasks.
            </h4>
          </v-col>
        </v-row>
      </v-container>
      <!-- end list view -->
    </v-card>

    <v-dialog v-model="dialog_confirm_archive" max-width="450px">
      <v-card>
        <v-card-title class="headline"> Confirm Task Archive</v-card-title>
        <v-card-text>
          Are you sure you want to archive this tasks?
        </v-card-text>
        <v_error_multiple :error="error_archive_task"></v_error_multiple>
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
    <add_assignee
      :job="job"
      :members_list_prop="members_list"
      :reviewers_list_prop="reviewers_list"
      :dialog_type="task_assign_dialog_type"
      :dialog="task_assign_dialog_open"
      :assignees="task_to_assign ? task_list.find(task => task.id === task_to_assign)[this.task_assign_dialog_type === 'assignee' ? 'task_assignees' : 'task_reviewers'] : []"
      :loading="task_assign_dialog_loading"
      :plural="task_assign_batch"
      :remove_mode="remove_mode"
      @close="on_assign_dialog_close"
      @assign="assign_user_to_task"
    />
    <v-snackbar v-model="snackbar_success" :timeout="3000" color="primary">
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
import axios from "axios";
import _ from 'lodash'
import {route_errors} from "../../regular/regular_error_handling";
import task_status_icons from "../../regular_concrete/task_status_icons.vue";
import task_list_table from "./task_list_table.vue";
import task_status_select from "../../regular_concrete/task_status_select.vue";
import task_input_list_dialog from "../../input/task_input_list_dialog.vue";
import add_assignee from "../../dialogs/add_assignee.vue"
import {
  assignUserToTask,
  batchAssignUserToTask,
  batchRemoveUserFromTask,
  getTaskListFromJob
} from "../../../services/tasksServices"
import {get_task_template_members} from "../../../services/taskTemplateService"
import global_dataset_selector from "../../attached/global_dataset_selector.vue"

import pLimit from "p-limit";

import Vue from "vue";

export default Vue.extend({
  name: "task_list",
  components: {
    task_status_icons,
    task_status_select,
    task_input_list_dialog,
    add_assignee,
    global_dataset_selector,
    task_list_table
  },
  props: {
    project_string_id: {
      default: null,
    },
    open_read_only_mode: {
      default: null,
    },
    show_detail_button: {
      default: true,
    },
    external_interface: {
      default: undefined,
    },
    job_id: {
      default: null,
    },
    job: {
      default: () => ({}),
    },
    mode_data: {
      default: "direct_route", // job_edit, job_detail, user_profile, general/account?
    },
    mode_view: {
      default: "list", // list or grid?
    },
  },
  watch: {},
  data() {
    return {
      actions_list: [
        {name: "Archive", value: "archive"},
        {name: "Assign annotators", value: 'assign'},
        {name: "Remove annotators", value: 'remove'},
      ],

      task_assign_dialog_open: false,
      reviewers_list: [],
      members_list: [],
      task_to_assign: null,
      task_assign_dialog_loading: false,
      task_assign_dialog_type: null,
      task_assign_batch: false,
      job_assignees: false,
      job_reviewers: false,

      allow_reviews: false,

      page_number: 0,
      per_page_limit: 25,
      per_page_limit_options: [5, 10, 25, 100, 250],

      selected: [],
      dialog_confirm_archive: false,
      issues_filter: undefined,
      issue_filter_options: [
        {name: "Filter By Tasks With Open Issue", value: "open_issues"},
        {name: "Filter By Tasks With Closed Issues", value: "closed_issues"},
        {name: "Filter By Tasks Any Issues", value: "issues"},
      ],
      loading_archive: false,
      snackbar_success: false,
      selected_action: undefined,
      date: undefined,
      task_list: [],

      task_status: "all",
      task_id: undefined,

      loading: false,
      incoming_directory: undefined,

      get_annotations_error: {},

      error_attach: {},
      error_send_task: {},
      error_archive_task: {},
      show_success_attach: false,
      pending_initial_dir_sync: true,

      request_next_page_available: true,

      headers_selected_backup: [], // copied from headers_selected during mounted

      column_list: [
        "Status",
        "Preview",
        "AnnotationCount",
        "AssignedUser",
        "LastUpdated",
        "Action",
      ],
      column_list_backup: [],
      column_list_all: [
        "Select",
        "Status",
        "Preview",
        "ID",
        "AnnotationCount",
        "DataUpdateLog",
        "IncomingDataset",
        "AssignedUser",
        "AssignedReviewer",
        "LastUpdated",
        "Action",
      ],

      header_list: [
        {
          text: "Select",
          header_string_id: "Select",
          align: "left",
          sortable: false,
          value: "is_selected",
        },
        {
          text: "Status",
          header_string_id: "Status",
          align: "center",
          sortable: true,
          value: "status",
          width: "25px",
        },
        {
          text: "Preview",
          header_string_id: "Preview",
          align: "center",
          sortable: false,
          width: "100px",
          value: "",
        },
        {
          text: "ID",
          header_string_id: "ID",
          align: "left",
          sortable: true,
          value: "id",
        },
        {
          text: "Annotation Count",
          header_string_id: "AnnotationCount",
          align: "center",
          sortable: true,
          value: "annotation_count",
          width: "25px",
        },
        {
          text: "Data Update Log",
          header_string_id: "DataUpdateLog",
          align: "left",
          sortable: true,
          value: "id",
        },
        {
          text: "Incoming Dataset",
          header_string_id: "IncomingDataset",
          align: "left",
          sortable: true,
          value: "incoming_directory.nickname",
        },
        {
          text: "Assigned User",
          header_string_id: "AssignedUser",
          align: "center",
          sortable: false,
          value: "",
        },
        {
          text: "Assigned Reviewer",
          header_string_id: "AssignedReviewer",
          align: "center",
          sortable: false,
          value: "",
        },
        {
          text: "Type",
          header_string_id: "Type",
          align: "left",
          sortable: true,
          value: "task_type",
        },
        {
          text: "Last Updated",
          header_string_id: "LastUpdated",
          align: "left",
          sortable: true,
          value: "time_updated",
        },
        {
          text: "Created",
          header_string_id: "Created",
          align: "left",
          sortable: true,
          value: "time_created",
        },
        {
          text: "Action",
          header_string_id: "Action",
          align: "left",
          sortable: false,
          value: "",
        },
      ],

      header_exam_results: [
        {
          text: "Average Star Rating",
          align: "left",
          sortable: true,
          value: "",
        },
        {
          text: "Missed instances",
          align: "left",
          sortable: true,
          value: "",
        },
      ],
      view_only: false,
      remove_mode: false,
      next_task_loading: false,
    };
  },

  computed: {
    page_start_index: function () {
      return this.page_number * this.per_page_limit + 1;
    },
    page_end_index: function () {
      let count = this.page_number * this.per_page_limit + this.per_page_limit;
      if (count > this.$store.state.job.current.file_count_statistic) {
        count = this.$store.state.job.current.file_count_statistic;
      }
      return count;
    },
    header_view: function () {
      if (this.mode_data == "exam_results") {
        return this.header_exam_results;
      }

      return this.header;
    },
    has_filters_applied: function () {
      if (this.date) {
        return this.date.from || this.date.to;
      }
      if (this.incoming_directory && this.incoming_directory.directory_id) {
        return true;
      }
      return false;
    },
    selected_tasks: function () {
      return this.task_list.filter((t) => t.is_selected);
    },
    labelbox_project_id: function () {
      if (
        this.job.interface_connection &&
        this.job.interface_connection.integration_name === "labelbox"
      ) {
        const labelbox_mapping_task_template =
          this.job.external_mappings.filter((elm) => {
            if (elm.connection_id === this.job.interface_connection_id) {
              return true;
            }
          });
        if (labelbox_mapping_task_template.length > 0) {
          return labelbox_mapping_task_template[0].external_id;
        }
      }
      return undefined;
    },
    datasaur_project_id: function () {
      if (
        this.job.interface_connection &&
        this.job.interface_connection.integration_name === "datasaur"
      ) {
        const labelbox_mapping_task_template =
          this.job.external_mappings.filter((elm) => {
            if (elm.connection_id === this.job.interface_connection_id) {
              return true;
            }
          });
        if (labelbox_mapping_task_template.length > 0) {
          return labelbox_mapping_task_template[0].external_id;
        }
      }
      return undefined;
    },
    integration_name: function () {
      if (this.job.interface_connection) {
        return this.job.interface_connection.integration_name;
      }
      return undefined;
    },
  },
  created() {
    this.column_list_backup = this.column_list;
  },
  async mounted() {
    if (this.job) {
      this.pending_initial_dir_sync = this.job.pending_initial_dir_sync;
    }
    await this.get_job_members()
    await this.task_list_api();

  },
  methods: {
    async get_job_members() {
      let [members_data, error] = await get_task_template_members(this.job_id);
      if (error) {
        console.error(error)
        return
      }
      if (members_data) {
        this.members_list = members_data.assignees
        this.reviewers_list = members_data.reviewers
      }
    },
    async next_page() {
      this.page_number += 1;
      await this.task_list_api();
    },

    on_assign_dialog_open: function (task_id, type) {
      this.task_assign_dialog_open = true
      this.task_to_assign = task_id
      this.task_assign_dialog_type = type
    },

    on_batch_assign_dialog_open: function (type, remove_mode) {
      this.task_assign_dialog_open = true
      this.task_assign_dialog_type = type
      this.task_assign_batch = true
      this.remove_mode = remove_mode
    },

    on_assign_dialog_close: function () {
      this.task_assign_dialog_open = false
      this.task_to_assign = null
      this.task_assign_dialog_loading = false
      this.task_assign_dialog_type = null
      this.task_assign_batch = false
    },

    assign_user_to_task: async function (user_ids) {
      this.task_assign_dialog_loading = true
      const new_task_assignees = user_ids.map(id => ({user_id: id}))
      if (!this.task_assign_batch) {
        await assignUserToTask(user_ids, this.project_string_id, this.task_to_assign, this.task_assign_dialog_type)
        this.task_list.find(task => task.id === this.task_to_assign)[this.task_assign_dialog_type === "assignee" ? "task_assignees" : "task_reviewers"] = new_task_assignees
      } else {
        if (this.selected_action.includes('assign')) {
          await batchAssignUserToTask(user_ids, this.project_string_id, this.selected_tasks, this.task_assign_dialog_type)
          this.selected_tasks.map(assign_item => {
            const task_assignees = _.merge(_.keyBy(new_task_assignees, 'user_id'), _.keyBy(this.task_list.find(task => task.id === assign_item.id)[this.task_assign_dialog_type === "assignee" ? "task_assignees" : "task_reviewers"], 'user_id'));
            this.task_list.find(task => task.id === assign_item.id)[this.task_assign_dialog_type === "assignee" ? "task_assignees" : "task_reviewers"] = _.values(task_assignees)
          })
        } else {
          await batchRemoveUserFromTask(user_ids, this.project_string_id, this.selected_tasks, this.task_assign_dialog_type)
          this.selected_tasks.map(assign_item => {
            this.task_list.find(task => task.id === assign_item.id)[this.task_assign_dialog_type === "assignee" ? "task_assignees" : "task_reviewers"] = this.task_list.find(task => task.id === assign_item.id)[this.task_assign_dialog_type === "assignee" ? "task_assignees" : "task_reviewers"].filter(user => !user_ids.includes(user.user_id))
          })
        }
        this.task_list.forEach((t) => t.is_selected = false)
      }
      this.on_assign_dialog_close()
    },

    async previous_page() {
      this.page_number -= 1;
      await this.task_list_api();
    },

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
        if (integration_name === "scale_ai") {
          url = "/api/walrus/v1/connections/send-task-to-scale-ai";
        }
        if (!url) {
          return false;
        }
        const response = await axios.post(url, {
          task_id: task.id,
        });
        if (response.status === 200) {
          task.status = "in_progress";
        }
      } catch (error) {
        this.error_send_task = route_errors(error);
      } finally {
        task.loading = false;
      }
    },
    route_task(task_id) {
      let url = `/task/${task_id}`;

      this.$router.push({
        path: url,
        query: {
          view_only: this.open_read_only_mode,
        },
      });
    },
    route_task_diff(task_id) {
      this.$router.push(
        "/task/" + task_id + "/diff/" + "compare_review_to_draw"
      );
    },
    on_change_dir(dir) {
      this.incoming_directory = dir;
    },
    async task_list_api() {
      this.loading = true;
      await this.$nextTick();
      try {
        const filters = {
          page_number: this.page_number,
          date_from: this.date ? this.date.from : undefined,
          date_to: this.date ? this.date.to : undefined,
          job_id: this.job_id,
          mode_data: this.mode_data,
          incoming_directory_id: this.incoming_directory
            ? this.incoming_directory.directory_id
            : undefined,
          status: this.task_status,
          issues_filter: this.issues_filter,
          limit_count: this.per_page_limit,
        }
        const [task_data, err] = await getTaskListFromJob(this.job_id, filters)
        if (err) {
          console.log(err)
          return
        }
        if (task_data.log.success == true) {
          this.task_list = task_data.task_list;
          this.allow_reviews = task_data.allow_reviews
          this.pending_initial_dir_sync =
            task_data.pending_initial_dir_sync;

          if (task_data.allow_reviews) {
            this.column_list = [
              "Status",
              "Preview",
              "AnnotationCount",
              "AssignedUser",
              "AssignedReviewer",
              "LastUpdated",
              "Action",
            ]

            this.actions_list = [
              {name: "Archive", value: "archive"},
              {name: "Assign annotators", value: 'assign'},
              {name: "Remove annotators", value: 'remove'},
              {name: "Assign reviewers", value: 'assignReviewers'},
              {name: "Remove reviewers", value: 'removeReviewers'},
            ]
          } else {
            this.column_list_all = this.column_list_all.filter(col => !["AssignedReviewer"].includes(col))
          }

          this.update_tasks_with_file_annotations(this.task_list);
        }
        return task_data;
      } catch (error) {
        console.error(error);
        return false;
      } finally {
        this.loading = false;
      }
    },

    update_tasks_with_file_annotations: async function (task_list) {
      const limit = pLimit(10); // Max concurrent request.
      try {
        const promises = task_list.map((task) => {
          return limit(() => this.get_file_with_annotations(task));
        });
        const result = await Promise.all(promises);
        return result;
      } catch (error) {
        this.file_update_error = this.$route_api_errors(error);
        console.error(error);
      }
    },

    async get_file_with_annotations(task) {
      if (task.file.type != "image") {
        return;
      }

      let url = "/api/v1/task/" + task.id + "/annotation/list";
      this.get_annotations_error = {};
      this.get_annotations_loading = true;

      try {
        const response = await axios.post(url, {});
        task.file = response.data.file_serialized;
      } catch (error) {
        console.debug(error);
        this.get_annotations_error = this.$route_api_errors(error);
      } finally {
        this.get_annotations_loading = false;
      }
    },

    async refresh_task_list() {
      this.loading = true;
      await this.task_list_api();

      this.loading = false;
    },
    async perform_task_list_action() {
      this.error_archive_task = {};
      this.loading_archive = true;
      try {
        if (this.selected_action === "archive") {
          const response = await axios.post("/api/v1/task/update", {
            task_ids: this.selected_tasks.map((x) => x.id),
            status: "archived",
          });
          if (response.status === 200) {
            await this.refresh_task_list();
            this.dialog_confirm_archive = false;
            this.snackbar_success = true;
            this.$emit("task_count_changed");
          }
        }
      } catch (error) {
        if (this.selected_action === "archive") {
          this.error_archive_task = route_errors(error);
        }
      } finally {
        this.loading_archive = false;
      }
    },
    show_confirm_archive_model() {
      this.dialog_confirm_archive = true;
    },
  },
});
</script>

<style scoped>
.show-number-of-users {
  margin-left: -15px;
  z-index: 0;
  background-color: #d3d3d3
}

.display-assigned-users {
  display: flex;
  flex-direction: row;
  width: 100%;
  align-items: center;
  justify-content: center;
}
</style>
