<template>
  <div class="exam-detail-container">
    <div class="d-flex justify-space-between align-center mb-6">
      <h1 class="pa-2">
        <v-layout>
          <div
            class="font-weight-light clickable"
            @click="$router.push('/job/list')"
          >
            {{ $store.state.project.current.name }} /
            <span class="secondary--text">
              <strong>
              <v-icon color="secondary">mdi-test-tube</v-icon>
              <span v-if="$store.state.job.parent_id">Exams</span>
              <span v-else>Exams Templates</span>
              </strong>
            </span>
            /
          </div>

          <div
            v-if="edit_name != true"
            class="font-weight-normal pl-2 d-flex align-center"
            @dblclick="edit_name = true"
          >
            {{ job_name }}
            <tooltip_button
              v-if="edit_name == false"
              tooltip_message="Edit Name"
              tooltip_direction="bottom"
              @click="edit_name = true"
              icon="edit"
              :icon_style="true"
              color="primary"
            >
            </tooltip_button>
          </div>

          <v-text-field
            v-if="edit_name == true"
            v-model="job_name"
            @input="has_changes = true"
            @keyup.enter="(edit_name = false), api_update_job()"
            solo
            flat
            style="font-size: 22pt; border: 1px solid grey; height: 55px"
            color="blue"
          >
          </v-text-field>

          <div>
            <button_with_confirm
              v-if="edit_name == true"
              @confirm_click="api_update_job()"
              color="primary"
              icon="save"
              :icon_style="true"
              tooltip_message="Save Name Updates"
              confirm_message="Confirm"
              :loading="loading"
              :disabled="loading"
            >
            </button_with_confirm>
          </div>

          <tooltip_button
            v-if="edit_name == true"
            tooltip_message="Cancel Name Edit"
            datacy="cancel_edit_name"
            @click="edit_name = false"
            icon="mdi-cancel"
            :icon_style="true"
            color="primary"
            :disabled="loading"
          >
          </tooltip_button>
        </v-layout>
      </h1>
    </div>

    <v-tabs v-model="tab" color="primary" style="height: 100%">
      <v-tab v-for="item in items" :key="item.text">
        <v-icon left>{{ item.icon }}</v-icon>
        {{ item.text }}
      </v-tab>
      <v-tabs-items v-model="tab">
        <v-tab-item class="pt-2">
          <exam_results :exam_id="exam_id"></exam_results>
        </v-tab-item>

        <v-tab-item>
          <task_template_discussions
            :project_string_id="$store.state.project.current.project_string_id"
            :task_template_id="exam_id"
          ></task_template_discussions>
        </v-tab-item>

        <v-tab-item>
          <!-- TODO update to use new reporting pattern-->
          <v_stats_task :job_id="exam_id"> </v_stats_task>
        </v-tab-item>

        <v-tab-item>
          <job_details_label_schema_section
            :label_select_view_only_mode="label_select_view_only_mode"
            :request_refresh_labels="request_refresh_labels"
            :loading="loading"
            :error="error"
            :info="info"
            @update_label_file_list="update_label_file_list = $event"

          ></job_details_label_schema_section>
        </v-tab-item>

        <v-tab-item>
          <job_pipeline_mxgraph
            :job_id="exam_id"
            :show_output_jobs="true"
            class="mt-4 mb-4 pb-8 pt-8"
          >
          </job_pipeline_mxgraph>
        </v-tab-item>

        <v-tab-item>
          <!-- Settings -->
          <v_info_multiple :info="info"> </v_info_multiple>



          <v-layout>
            <v-spacer> </v-spacer>

            <!-- output_dir_action -->
            <icon_from_regular_list
              :item_list="output_dir_action_icon_list"
              :value="$store.state.job.current.output_dir_action"
            >
            </icon_from_regular_list>

            <icon_from_regular_list
              :item_list="share_icon_list"
              :value="$store.state.job.current.share_type"
            >
            </icon_from_regular_list>

            <job_type :type="$store.state.job.current.type" :size="40">
            </job_type>
          </v-layout>

          <v_credential_list
            :job_id="exam_id"
            :mode_options="'job_detail'"
            :mode_view="'list'"
          >
          </v_credential_list>

          <v_job_cancel_actions_button_container
            v-if="$store.state.job.current"
            :job="$store.state.job.current"
          >
          </v_job_cancel_actions_button_container>
        </v-tab-item>
      </v-tabs-items>
    </v-tabs>
  </div>
</template>

<script lang="ts">
import v_job_detail_builder from "../task/job/job_detail_builder";
import v_job_cancel_actions_button_container from "../task/job/job_cancel_actions_button_container";
import job_details_label_schema_section from "../task/job/job_detail_labels_schema_section";
import v_job_detail_trainer from "../task/job/job_detail_trainer";
import task_template_discussions from "../discussions/task_template_discussions";
import job_pipeline_mxgraph from "../task/job/job_pipeline_mxgraph";
import axios from "axios";
import job_type from "../task/job/job_type";
import stats_panel from "../stats/stats_panel.vue";
import * as examsServices from "../../services/examsService"
import { nextTask } from "../../services/tasksServices";

import Vue from "vue";
import Exam_results from "../task/job/exam_results.vue";
export default Vue.extend({
  name: "exam_detail",
  props: ["exam_id"],
  components: {
    Exam_results,
    v_job_detail_builder,
    v_job_cancel_actions_button_container,
    job_details_label_schema_section,
    task_template_discussions,
    v_job_detail_trainer,
    job_pipeline_mxgraph,
    job_type,
    stats_panel,
  },

  data() {
    return {
      tab: null,
      items: [
        { text: "Exam Results", icon: "mdi-view-dashboard" },
        { text: "Discussions", icon: "mdi-comment-multiple" },
        { text: "Insights", icon: "mdi-chart-areaspline" },
        { text: "Schema", icon: "mdi-format-paint" },
        { text: "Settings", icon: "mdi-cog" },
      ],
      update_label_file_list: null,
      has_changes: false,

      edit_name: false,

      job_name: undefined,

      info: {},
      error: {},
      label_select_view_only_mode: true,
      request_refresh_labels: null,

      loading: false,
      next_task_loading: false,

      share_icon_list: [
        {
          display_name: "Shared with Project",
          name: "project",
          icon: "mdi-lightbulb",
          color: "blue",
        },
        {
          display_name: "Shared with Org",
          name: "org",
          icon: "mdi-domain",
          color: "green",
        },
      ],

      output_dir_action_icon_list: [
        {
          display_name: "Output Dataset Action: Copy",
          name: "copy",
          icon: "mdi-content-copy",
          color: "blue",
        },
        {
          display_name: "Output Dataset Action: Move",
          name: "move",
          icon: "mdi-file-move",
          color: "green",
        },
        {
          display_name: "Output Dataset Action: None",
          name: "nothing",
          icon: "mdi-circle-off-outline",
          color: "gray",
        },
      ],
    };
  },
  created() {
    if (this.$route.path.endsWith("discussions")) {
      this.tab = 1;
    }
    this.reset_local_info();
    this.job_current_watcher = this.$store.watch(
      (state) => {
        return this.$store.state.job.refresh;
      },
      (new_val, old_val) => {
        this.reset_local_info();
      }
    );
  },
  computed: {},
  beforeDestroy() {
    this.job_current_watcher();
  },
  beforeDestroy() {
    this.job_current_watcher()
  },
  methods: {
    reset_local_info() {
      this.job_name = this.$store.state.job.current.name;
      this.set_document_title();
    },
    set_document_title() {
      document.title = this.job_name;
    },
    get_child_exams_list: function(){
      const child_exams_list = examsServices.get_child_exams_list(metadata)

    },
    api_update_job: function () {
      /*
       * Assumes one job at a time
       *
       * Assumes fields NOT being updated are Null!
       *  So for example update_label_file_list starts off as null
       *  and when update goes to check it, if it's null it won't touch
       *  it.
       */
      this.loading = true;
      this.error = {};
      this.info = {};

      axios
        .post(
          "/api/v1/project/" +
            this.$store.state.project.current.project_string_id +
            "/job/update",
          {
            job_id: parseInt(this.exam_id),
            label_file_list: this.update_label_file_list, // see assumptions on null in note above
            name: this.job_name,
          }
        )
        .then((response) => {
          this.loading = false;
          this.info = response.data.log.info;
          this.edit_name = false;
          this.has_changes = false;
          this.update_label_file_list = null;
          this.$store.commit("set_job", response.data.job);
          this.set_document_title();
        })
        .catch((error) => {
          this.loading = false;
          this.error = this.$route_api_errors(error);
        });
    },
  },
});
</script>

<style>
.exam-detail-container {
  padding: 0 10rem;
  margin-top: 2rem;
  height: 100%;
}
</style>
