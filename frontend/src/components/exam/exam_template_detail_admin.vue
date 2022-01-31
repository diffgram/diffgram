<template>
  <div class="exam-detail-container">
    <v-snackbar top height="200px" dismissible v-model="show_snackbar" color="success">
      <h3>{{snackbar_message}}</h3>
    </v-snackbar>
    <v_error_multiple :error="error">
    </v_error_multiple>
    <exam_detail_header
      :loading="loading"
      :exam="exam"
      @apply_clicked="exam_apply"
      @name_updated="api_update_job"
      :allow_edit="true"
    >
    </exam_detail_header>

    <v-tabs v-model="tab" color="primary" style="height: 100%">
      <v-tab v-for="item in items" :key="item.text">
        <v-icon left>{{ item.icon }}</v-icon>
        {{ item.text }}
      </v-tab>
      <v-tabs-items v-model="tab">
        <v-tab-item class="pt-2">
          <exam_child_list :exam_id="exam_id"></exam_child_list>
        </v-tab-item>

        <v-tab-item>
          <task_template_discussions
            :project_string_id="$store.state.project.current.project_string_id"
            :task_template_id="exam_id"
          ></task_template_discussions>
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
          <!-- Settings -->
          <v_info_multiple :info="info"> </v_info_multiple>

          <v-layout>
            <v-spacer> </v-spacer>
          </v-layout>

          <v_credential_list
            :job_id="exam_id"
            :mode_options="'job_detail'"
            :mode_view="'list'"
          >
          </v_credential_list>

          <job_cancel_actions_button_container
            :job="exam"
          >
          </job_cancel_actions_button_container>
        </v-tab-item>
      </v-tabs-items>
    </v-tabs>
  </div>
</template>

<script lang="ts">
import job_details_label_schema_section from "../task/job/job_detail_labels_schema_section";
import job_cancel_actions_button_container from "../task/job/job_cancel_actions_button_container";
import task_template_discussions from "../discussions/task_template_discussions";
import exam_child_list from "../exam/exam_child_list";
import exam_detail_header from "../exam/exam_detail_header";
import axios from "axios";
import stats_panel from "../stats/stats_panel.vue";
import {exam_start_apply} from '../../services/examsService'
import {get_task_template_details} from '../../services/taskTemplateService'
import { nextTask } from "../../services/tasksServices";

import Vue from "vue";
import Exam_results from "../task/job/exam_results.vue";
import Exam_child_list from "./exam_child_list.vue";
export default Vue.extend({
  name: "exam_template_detail",
  props: ["exam_id"],
  components: {
    Exam_child_list,
    Exam_results,
    job_details_label_schema_section,
    job_cancel_actions_button_container,
    task_template_discussions,
    exam_detail_header,
    exam_child_list,
    stats_panel,
  },

  data() {
    return {
      tab: null,
      items: [
        { text: "Exam Results", icon: "mdi-view-dashboard" },
        { text: "Discussions", icon: "mdi-comment-multiple" },
        { text: "Schema", icon: "mdi-format-paint" },
        { text: "Settings", icon: "mdi-cog" },
      ],
      update_label_file_list: null,
      has_changes: false,

      edit_name: false,
      show_snackbar: false,
      snackbar_message: '',

      exam_name: undefined,
      exam: {},

      info: {},
      error: {},
      label_select_view_only_mode: true,
      request_refresh_labels: null,

      loading: false,
    };
  },
  async created() {
    if (this.$route.path.endsWith("discussions")) {
      this.tab = 1;
    }
    await this.get_exam_details();
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
  methods: {
    get_exam_details: async function () {
      this.loading = true;
      this.exam = await get_task_template_details(this.exam_id);
      this.$emit("job_info", this.exam);
      this.$store.commit("set_job", this.exam);
      this.loading = false;
    },
    reset_local_info() {
      this.exam_name = this.$store.state.job.current.name;
      this.set_document_title();
    },
    set_document_title() {
      document.title = this.exam_name;
    },
    show_success_snackbar(text){
      this.show_snackbar = true
      this.snackbar_message = text
    },
    sleep: function (ms) {
      return new Promise((resolve) => setTimeout(resolve, ms));
    },
    exam_apply: async function () {

      this.loading = true
      const [apply_result, error] = await exam_start_apply(this.exam_id);
      if(apply_result && apply_result.log && apply_result.log.success){
        this.loading = false;
        this.show_success_snackbar("You've sucessfully applied to this exam! Going to exam now...");
        await this.sleep(4000);
        this.$router.push(`/${this.$store.state.project.current.project_string_id}/examination/${apply_result.log.job_id}`);
      }
      if(error){
        this.error = this.$route_api_errors(error)
        this.loading = false;
      }


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
            name: this.exam.name,
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
