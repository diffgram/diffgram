<template>
  <div class="exam-detail-container">
    <v-snackbar top height="200px" dismissible v-model="show_snackbar" color="success">
      <h3>{{snackbar_message}}</h3>
    </v-snackbar>
    <v_error_multiple :error="error">
    </v_error_multiple>
    <exam_detail_header
      :loading="loading"
      :exam="examination"
      :object_name="'Examinations'"
      :show_apply_button="false"
      @apply_clicked="exam_apply"
      @name_updated="api_update_job"
    >
    </exam_detail_header>

    <v-tabs v-model="tab" color="primary" style="height: 100%">
      <v-tab v-for="item in items" :key="item.text">
        <v-icon left>{{ item.icon }}</v-icon>
        {{ item.text }}
      </v-tab>
      <v-tabs-items v-model="tab">
        <v-tab-item class="pt-2">
          <v_task_list
            :job_id="examination_id"
            :job="examination"
            :project_string_id="project_string_id"
            :external_interface="null"
            :show_detail_button="true"
            :open_read_only_mode="false"
            :mode_options="'job_detail'"
            :mode_view="'list'"
            @task_count_changed="() => {}"
          >
          </v_task_list>

          <v-container class="mt-4 pa-4" style="border: solid 1px #e0e0e0" v-if="user_can_grade && !(exam_approved)">
            <h2>Actions: </h2>
            <p><strong>Note:</strong> Can only approve once all tasks have been reviewed and completed.</p>
            <div class="d-flex justify-center">
              <v-btn @click="exam_pass_api()"
                     x-large
                     :loading="loading"
                     color="success">
                <v-icon>mdi-test-tube</v-icon>
                Pass
              </v-btn>
            </div>
          </v-container>

          <v-container class="mt-4 pa-4 d-flex flex-column justify-center align-center"
                       style="border: solid 1px #e0e0e0"
                       v-if="exam_approved">
            <v-icon color="success" size="120">mdi-check</v-icon>
            <h3>Exam Approved</h3>
          </v-container>

        </v-tab-item>

        <v-tab-item>
          <task_template_discussions
            :project_string_id="$store.state.project.current.project_string_id"
            :task_template_id="examination_id"
          ></task_template_discussions>
        </v-tab-item>
      </v-tabs-items>
    </v-tabs>


  </div>
</template>

<script lang="ts">
import job_details_label_schema_section from "../task/job/job_detail_labels_schema_section";
import task_template_discussions from "../discussions/task_template_discussions";
import exam_child_list from "../exam/exam_child_list";
import exam_detail_header from "../exam/exam_detail_header";
import v_task_list from "../task/task/task_list";
import axios from "../../services/customInstance";
import stats_panel from "../stats/stats_panel.vue";
import {exam_start_apply} from '../../services/examsService'
import {get_task_template_details} from '../../services/taskTemplateService'
import {exam_pass} from '../../services/examsService'

import Vue from "vue";
import Exam_results from "../task/job/exam_results.vue";
import Exam_child_list from "./exam_child_list.vue";
export default Vue.extend({
  name: "examination_detail",
  props: ["examination_id"],
  components: {
    v_task_list,
    Exam_results,
    job_details_label_schema_section,
    task_template_discussions,
    exam_detail_header,
    exam_child_list,
    stats_panel,
  },

  data() {
    return {
      tab: null,
      items: [
        { text: "Exam Tasks", icon: "mdi-view-dashboard" },
        { text: "Discussions", icon: "mdi-comment-multiple" },
      ],
      has_changes: false,
      credentials_list: false,
      edit_name: false,
      show_snackbar: false,
      snackbar_message: '',

      exam_name: undefined,
      examination: {},

      info: {},
      error: {},
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
  computed: {
    exam_approved: function(){
      return this.examination.exam && this.examination.exam.credentials_awarded;
    },
    project_string_id: function(){
      return this.$store.state.project.current.project_string_id;
    },
    user_can_grade: function(){
      let user_id = this.$store.state.user.current.id
      if(this.$store.state.user.current.is_super_admin){
        return true
      }
      if(this.examination.reviewer_list_ids){
        if(this.examination.reviewer_list_ids.includes(user_id)){
          return true
        }
      }

    }

  },
  beforeDestroy() {
    this.job_current_watcher();
  },
  methods: {
    exam_pass_api: async function(){
      this.loading = true;
      let [result, error] = await exam_pass(this.examination_id);
      if(result){
        this.examination.exam = {
          credentials_awarded: true
        }
        this.show_success_snackbar('Exam Approved! User has been awarded new credentials.')
      }
      if(error){
        this.error = this.$route_api_errors(error)
      }
      this.loading = false;
    },
    get_exam_details: async function () {
      this.loading = true;
      this.examination = await get_task_template_details(this.examination_id);
      this.$emit("job_info", this.examination);
      this.$store.commit("set_job", this.examination);
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
      const [apply_result, error] = await exam_start_apply(this.examination_id);
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
            job_id: parseInt(this.examination_id),
            label_file_list: this.update_label_file_list, // see assumptions on null in note above
            name: this.examination.name,
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
