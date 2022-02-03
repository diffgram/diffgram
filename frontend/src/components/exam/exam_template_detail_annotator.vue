<template>
  <div class="exam-detail-container">
    <v-snackbar top height="200px" dismissible v-model="show_snackbar" color="success">
      <h3>{{snackbar_message}}</h3>
    </v-snackbar>
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
            <div class="d-flex flex-wrap justify-center mt-4 mb-4 pa-4" style="border: 1px solid #e0e0e0">
              <credential_badge
                v-if="awarded_credentials_list.length > 0"
                v-for="credential in awarded_credentials_list"
                :credential="credential">
              </credential_badge>
              <h2 v-else>No credentials awarded by this exam.</h2>


            </div>
            <h2>When you approve this exam.</h2>
            <v-card-actions>
              <v-btn x-large color="success" @click="exam_apply"><v-icon>mdi-shield-star</v-icon>Apply To Exam</v-btn>
            </v-card-actions>

          </v-card>
        </v-tab-item>
        <v-tab-item>
            <task_template_discussions
              :project_string_id="$store.state.project.current.project_string_id"
              :task_template_id="exam_id"
            ></task_template_discussions>

        </v-tab-item>
        <v-tab-item>
          <guide_display :guide="exam.guide"></guide_display>

        </v-tab-item>
      </v-tabs-items>
    </v-tabs>
  </div>
</template>

<script lang="ts">
import credential_badge from '../task/credential/credential_badge'
import guide_display from '../task/guide/guide_display'
import task_template_discussions from '../discussions/task_template_discussions'
import exam_detail_header from './exam_detail_header'
import axios from "axios";
import {exam_start_apply} from '../../services/examsService'
import {get_task_template_details, get_task_template_credentials} from '../../services/taskTemplateService'
import Vue from "vue";

export default Vue.extend({
  name: "exam_template_detail_annotator",
  props: ["exam_id", "exam"],
  components: {
    exam_detail_header,
    guide_display,
    task_template_discussions,
    credential_badge
  },
  data() {
    return {
      tab: null,
      items: [
        { text: "Apply", icon: "mdi-view-dashboard" },
        { text: "Discussions", icon: "mdi-comment-multiple" },
        { text: "Instructions / Guide", icon: "mdi-book" },
      ],
      update_label_file_list: null,
      credentials_list: [],
      snackbar_message: '',
      show_snackbar: false,
      has_changes: false,

      edit_name: false,
      loading: false,

      exam_name: undefined,
      job_current_watcher: undefined,

      info: {},
      error: {},

    };
  },
  async created() {
    if (this.$route.path.endsWith("discussions")) {
      this.tab = 1;
    }
    await this.get_exam_details();
    await this.get_exam_credentials();
    this.reset_local_info();
  },
  computed: {
    awarded_credentials_list: function(){
      return this.credentials_list.filter(elm => elm.kind === 'awards')
    }
  },
  methods: {
    get_exam_credentials: async function(){
      this.loading = true;
      this.credentials_list = await get_task_template_credentials({
        job_id: this.exam_id,
        project_string_id: this.$store.state.project.current.project_string_id,
        builder_or_trainer: {
          mode: this.$store.state.builder_or_trainer.mode
        }
      });
      this.loading = false;
    },
    reset_local_info() {
      this.exam_name = this.$store.state.job.current.name;
      this.set_document_title();
    },
    get_exam_details: async function () {
      this.loading = true;
      this.$emit("job_info", this.$props.exam);
      this.$store.commit("set_job", this.$props.exam);
      this.loading = false;
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
