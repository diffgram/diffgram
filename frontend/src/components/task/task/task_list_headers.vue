<template>
  <div class="d-flex">
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
          v-model="filters.status"
          label="Status"
          @change="reset_page"
          :disabled="loading"
        >
        </task_status_select>

        <v-select
          v-model="filters.issues_filter"
          @change="reset_page"
          :items="issue_filter_options"
          :clearable="true"
          label="Filer by Issues"
          item-text="name"
          item-value="value"
        ></v-select>

        <date_picker
          @date="update_date"
          :with_spacer="false"
          :initialize_empty="true"
        >
        </date_picker>

        <v-select
          data-cy="task_list_per_page_limit_selector"
          :items="per_page_limit_options"
          v-model="filters.limit_count"
          label="Per Page"
          item-value="text"
          :disabled="loading"
          @change="reset_page"
        ></v-select>

        <global_dataset_selector
          class="ml-4 mr-8"
          label="Incoming Dataset"
          :clearable="true"
          :update_from_state="false"
          :set_current_dir_on_change="false"
          :initial_dir_from_state="false"
          @change_directory="on_change_dir"
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
      v-if="total_task_count"
    >
      <standard_button
        v-show="filters.page_number > 0"
        datacy="task_list_previous_page"
        tooltip_message="Previous Page"
        @click="previous_page()"
        :disabled="loading"
        :icon_style="true"
        icon="mdi-chevron-left-box"
        color="primary"
      >
      </standard_button>
      <div v-if="!loading && page_end_index > total_task_count && total_task_count > filters.limit_count">
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
        >of {{ total_task_count }}
        </v-chip>
      </div>



      <standard_button
        v-show="page_end_index < total_task_count && total_task_count > filters.limit_count"
        tooltip_message="Next Page"
        datacy="task_list_next_page"
        @click="next_page()"
        :disabled="loading || !total_task_count"
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
          @change="update_column_list"
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
import task_input_list_dialog from "../../input/task_input_list_dialog.vue";
import add_assignee from "../../dialogs/add_assignee.vue"
import global_dataset_selector from "../../attached/global_dataset_selector.vue"
import Vue from "vue";
import task_status_select from "../../regular_concrete/task_status_select.vue";
import {TaskFilters} from '../../../types/TaskFilters'
export default Vue.extend({
  name: "task_list_headers",
  components: {
    task_status_select,
    task_input_list_dialog,
    add_assignee,
    global_dataset_selector
  },
  props: {
    project_string_id: {type: String, required: true},
    filters: {type: Object as () => TaskFilters, required: true},
    job_id: {type: Number, required: false},
    total_task_count: {type: Number, required: true},
    loading: {type: Boolean, required: false},
  },
  watch: {},
  data() {
    return {
      view_only: false,
      per_page_limit_options: [5, 10, 25, 100, 250],
      issues_filter: undefined,
      issue_filter_options: [
        {name: "Filter By Tasks With Open Issue", value: "open_issues"},
        {name: "Filter By Tasks With Closed Issues", value: "closed_issues"},
        {name: "Filter By Tasks Any Issues", value: "issues"},
      ],
      date: undefined,

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
    };
  },

  created() {

  },
  methods: {
    reset_page: function(){
      this.filters.page_number = 0
    },
    update_date: function(date){
      this.filters.page_number = 0;
      this.filters.date_from = date.from
      this.filters.date_to = date.to
    },
    refresh_task_list: function () {
      this.$emit('refresh_task_list', this.filters)
    },
    on_change_dir(dir) {
      this.reset_page()
      this.incoming_directory = dir;
    },
    update_column_list(col_list){
      this.$emit('update_column_list', col_list)
    },
    async next_page() {
      this.filters.page_number += 1;
      this.$emit('refresh_task_list', this.filters)
    },
    async previous_page() {
      this.filters.page_number -= 1;
      this.$emit('refresh_task_list', this.filters)
    },
  },
  computed: {

    page_start_index: function () {
      return this.filters.page_number * this.filters.limit_count + 1;
    },
    page_end_index: function () {
      let count = this.filters.page_number * this.filters.limit_count + this.filters.limit_count;
      if (count > this.total_task_count) {
        count = this.total_task_count;
      }
      return count;
    },
  }
});
</script>

<style scoped>
tr:hover {
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
