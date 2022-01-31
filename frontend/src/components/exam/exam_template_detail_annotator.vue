<template>
  <div class="exam-detail-container">
    <exam_detail_header
      :loading="loading"
      :exam="exam"
      @apply_clicked="exam_apply"
      :allow_edit="false"
    >
    </exam_detail_header>

    <v-tabs v-model="tab" color="primary" style="height: 100%">
      <v-tab v-for="item in items" :key="item.text">
        <v-icon left>{{ item.icon }}</v-icon>
        {{ item.text }}
      </v-tab>
      <v-tabs-items v-model="tab">
        <v-tab-item class="pt-2">
          <v-card style="min-height: 500px" class="d-flex flex-column justify-center align-center">
            <h1>You Will Get The Following Awards: </h1>
            <div class="d-flex flex-wrap mt-4 mb-4 pa-4" style="border: 1px solid #e0e0e0">
              <v-icon size="96">mdi-shield-star</v-icon>
              <v-icon size="96">mdi-shield-star</v-icon>
              <v-icon size="96">mdi-shield-star</v-icon>
              <v-icon size="96">mdi-shield-star</v-icon>
            </div>
            <h2>When you approve this exam.</h2>
            <v-card-actions>
              <v-btn x-large color="success" @click="exam_apply"><v-icon>mdi-shield-star</v-icon>Apply To Exam</v-btn>
            </v-card-actions>

          </v-card>
        </v-tab-item>
        <v-tab-item>
          <v-tab-item>
            <task_template_discussions
              :project_string_id="$store.state.project.current.project_string_id"
              :task_template_id="exam_id"
            ></task_template_discussions>
          </v-tab-item>

        </v-tab-item>
      </v-tabs-items>
    </v-tabs>
  </div>
</template>

<script lang="ts">

import exam_detail_header from './exam_detail_header'
import axios from "axios";
import {exam_start_apply} from '../../services/examsService'
import {get_task_template_details} from '../../services/taskTemplateService'
import Vue from "vue";

export default Vue.extend({
  name: "exam_template_detail",
  props: ["exam_id"],
  components: {
    exam_detail_header
  },
  data() {
    return {
      tab: null,
      items: [
        { text: "Apply", icon: "mdi-view-dashboard" },
        { text: "Discussions", icon: "mdi-comment-multiple" },
        { text: "Guide", icon: "mdi-book" },
      ],
      update_label_file_list: null,
      has_changes: false,

      edit_name: false,
      loading: false,

      exam_name: undefined,
      job_current_watcher: undefined,

      info: {},
      exam: {},
      error: {},

    };
  },
  async created() {
    if (this.$route.path.endsWith("discussions")) {
      this.tab = 1;
    }
    await this.get_exam_details();
    this.reset_local_info();
  },
  computed: {},
  methods: {
    reset_local_info() {
      this.exam_name = this.$store.state.job.current.name;
      this.set_document_title();
    },
    get_exam_details: async function () {
      this.loading = true;
      this.exam = await get_task_template_details(this.exam_id);
      this.$emit("job_info", this.exam);
      this.$store.commit("set_job", this.exam);
      this.loading = false;
    },
    set_document_title() {
      document.title = this.exam_name;
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
            name: this.exam_name,
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
