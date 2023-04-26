<template>
  <div>
    <regular_table
      :item_list="task_list"
      :header_list="header_list_computed"
      :column_list="column_list"
      v-model="selected"
      :hidedefaultfooter="true"
      @rowclick="rowclick($event)"
    >
      <template slot="Select" slot-scope="props">
        <v-checkbox data-cy="select-task-list-item" v-model="props.item.is_selected"></v-checkbox>
      </template>

      <template slot="Status" slot-scope="props">
        <task_status_icons :status="props.item.status"></task_status_icons>
      </template>

      <template slot="Preview" slot-scope="props">
        <file_preview_with_hover_expansion
          :show_preview_details="false"
          :file="props.item.file"
          :project_string_id="project_string_id"
          tooltip_direction="right"
          @view_file_detail="route_task(props.item.id)"
          :file_preview_width="100"
          :file_preview_height="100"
        >
        </file_preview_with_hover_expansion>
      </template>

      <template slot="ID" slot-scope="props">
        {{ props.item.id }}
      </template>

      <template slot="AnnotationCount" slot-scope="props">
        <div v-if="props.item.file && props.item.file.instance_list">
          {{ props.item.file.instance_list.length }}
        </div>
      </template>

      <template slot="DataUpdateLog" slot-scope="props">
        <v-btn
          @click.stop.prevent="open_input_log_dialog(props.item.id)"
          type="primary"
          small
          color="primary"
          outlined
        >
          <v-icon color="primary">mdi-format-list-bulleted</v-icon>
        </v-btn>
      </template>

      <template slot="IncomingDataset" slot-scope="props">
        <v-icon color="primary">mdi-folder</v-icon>
        {{ props.item.incoming_directory.nickname }}
      </template>

      <template slot="Job" slot-scope="props">
        <v-btn small text outlined color="secondary" @click="$router.push(`/job/${props.item.job.id}`)">
          <v-icon size="26">mdi-file-link</v-icon>
          {{props.item.job.name}}
        </v-btn>
      </template>

      <template slot="AssignedUser" slot-scope="props">
        <div class="display-assigned-users">
          <standard_button
            tooltip_message="Manage assignees"
            class="hidden-sm-and-down"
            color="primary"
            @click.stop.prevent="() => on_assign_dialog_open(props.item.id, 'assignee')"
            icon="mdi-account-plus-outline"
            datacy="open-add-assignee-dialog"
            large
            :icon_style="true"
            :bottom="true"
          >
          </standard_button>
          <v_user_icon
            style="z-index: 1"
            v-if="props.item.task_assignees && props.item.task_assignees.length > 0"
            :user_id="props.item.task_assignees[0].user_id"
          />
          <v-tooltip v-if="props.item.task_assignees && props.item.task_assignees.length > 1" bottom>
            <template v-slot:activator="{ on, attrs }">
              <v-avatar v-bind="attrs" v-on="on" class="show-number-of-users">
                + {{ props.item.task_assignees.length - 1 }}
              </v-avatar>
            </template>
            <span>{{ props.item.task_assignees.length }} users assigned to complete this task</span>
          </v-tooltip>
        </div>
      </template>

      <template v-if="allow_reviews" slot="AssignedReviewer" slot-scope="props">
        <div class="display-assigned-users">
          <standard_button
            tooltip_message="Manage reviewers"
            class="hidden-sm-and-down"
            color="primary"
            @click.stop.prevent="() => on_assign_dialog_open(props.item.id, 'reviewer')"
            icon="mdi-account-plus-outline"
            large
            :icon_style="true"
            :bottom="true"
          >
          </standard_button>
          <v_user_icon
            style="z-index: 1"
            v-if="props.item.task_reviewers.length > 0" :user_id="props.item.task_reviewers[0].user_id"
          />
          <v-tooltip v-if="props.item.task_reviewers.length > 1" bottom>
            <template v-slot:activator="{ on, attrs }">
              <v-avatar v-bind="attrs" v-on="on" class="show-number-of-users">
                + {{ props.item.task_reviewers.length - 1 }}
              </v-avatar>
            </template>
            <span>{{ props.item.task_reviewers.length }} users assigned to complete this task</span>
          </v-tooltip>
        </div>
      </template>

      <template slot="LastUpdated" slot-scope="props">
        <div v-if="props.item.time_updated">
          {{
            props.item.time_updated | moment("subtract", "7 hours", "from")
          }}
        </div>
      </template>

      <template slot="Created" slot-scope="props">
        <div v-if="props.item.time_created">
          {{ props.item.time_created | moment("ddd, MMM Do H:mm:ss a") }}
        </div>
      </template>

      <template slot="Action" slot-scope="props">
        <standard_button
          tooltip_message="Go to Task"
          @click.stop.prevent="route_task(props.item.id)"
          icon="mdi-file-find"
          icon_style="success"
          :icon_style="true"
          :disabled="loading"
          :large="true"
          button_color="secondary"
          color="secondary"
        >
        </standard_button>

      </template>

      <template slot="Rating" slot-scope="props">
        <v-rating v-model="props.item.review_star_rating_average" readonly>
        </v-rating>
      </template>

      <template slot="GoldStandardMissing" slot-scope="props">
        {{ props.item.gold_standard_missing }}
      </template>
    </regular_table>

    <task_input_list_dialog
      :task_id="selected_task_id"
      :project_string_id="project_string_id"
      ref="task_input_list_dialog"
    ></task_input_list_dialog>

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

export default Vue.extend({
  name: "task_list",
  components: {
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
          text: "Job",
          header_string_id: "Job",
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
