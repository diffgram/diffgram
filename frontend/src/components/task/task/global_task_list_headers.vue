<template>
  <div>
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
  </div>
</template>

<script lang="ts">
import axios from "axios";
import _ from 'lodash'
import {route_errors} from "../../regular/regular_error_handling";
import task_status_icons from "../../regular_concrete/task_status_icons.vue";
import task_input_list_dialog from "../../input/task_input_list_dialog.vue";
import add_assignee from "../../dialogs/add_assignee.vue"
import {assignUserToTask, batchAssignUserToTask, batchRemoveUserFromTask} from "../../../services/tasksServices"
import {get_task_template_members} from "../../../services/taskTemplateService"
import global_dataset_selector from "../../attached/global_dataset_selector.vue"

import pLimit from "p-limit";

import Vue from "vue";
import task_status_select from "../../regular_concrete/task_status_select.vue";

export default Vue.extend({
  name: "task_list",
  components: {
    task_status_select,
    task_status_icons,
    task_input_list_dialog,
    add_assignee,
    global_dataset_selector
  },
  props: {
    project_string_id: {type: String, required: true},
    task_list: {type: Array, required: true},
    header_list: {type: Array},
    allow_reviews: {type: Boolean},
    column_list: {type: Array, required: true},
  },
  watch: {},
  data() {
    return {
      loading: true,
      selected: [],
      header_list_default: [
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
      selected_task_id: undefined,
      view_only: false,
      remove_mode: false,
      next_task_loading: false,
    };
  },

  computed: {
    header_list_computed: function () {
      if (!this.header_list) {
        return this.header_list_default
      }
      return this.header_list
    },
    selected_tasks: function () {
      return this.task_list.filter((t) => t.is_selected);
    },
  },
  created() {

  },
  methods: {
    rowclick(task) {
      if (!this.column_list.includes("Select")) {
        this.route_task(task.id);
      }
    },
    route_task(task_id) {
      let url = `/task/${task_id}`;
      this.$router.push(
        {
          path: url,
          query: {
            view_only: this.open_read_only_mode,
          },
        });
    },
    on_assign_dialog_open: function(task_id, type) {
      this.$emit('assign_dialog_open', task_id, type)
    },

    route_task_diff(task_id) {
      this.$router.push(
        "/task/" + task_id + "/diff/" + "compare_review_to_draw"
      );
    },
    on_change_dir(dir) {
      this.incoming_directory = dir;
    },
    open_input_log_dialog(task_id) {
      this.selected_task_id = task_id;
      this.$refs.task_input_list_dialog.open();
    },

  },
});
</script>

<style scoped>
tr:hover{
  cursor: pointer !important;
}
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
