<template>
  <div class="exam-detail-container">


    <v-tabs v-model="tab" color="primary" style="height: 100%">
      <v-tab v-for="item in items" :key="item.text">
        <v-icon left>{{ item.icon }}</v-icon>
        {{ item.text }}
      </v-tab>
      <v-tabs-items v-model="tab">
        <v-tab-item class="pt-2">
          <v-card style="min-height: 500px" class="d-flex flex-column">
            <h2>You Will Get The Following Awards: </h2>
            <div class="d-flex flex-wrap">
              <v-icon>mdi-badge</v-icon>
              <v-icon>mdi-badge</v-icon>
              <v-icon>mdi-badge</v-icon>
              <v-icon>mdi-badge</v-icon>
            </div>
            <h2>When you approve this exam.</h2>
            <v-card-actions>
              <v-btn x-large @click="exam_apply">Apply</v-btn>
            </v-card-actions>

          </v-card>
        </v-tab-item>
      </v-tabs-items>
    </v-tabs>
  </div>
</template>

<script lang="ts">

import axios from "axios";
import {exam_start_apply} from '../../services/examsService'
import Vue from "vue";

export default Vue.extend({
  name: "exam_template_detail",
  props: ["exam_id"],
  components: {
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
  methods: {
    reset_local_info() {
      this.job_name = this.$store.state.job.current.name;
      this.set_document_title();
    },
    set_document_title() {
      document.title = this.job_name;
    },
    exam_apply: async function () {

      this.loading = true
      const apply_result = await exam_start_apply(this.exam_id);
      this.loading = false;

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
