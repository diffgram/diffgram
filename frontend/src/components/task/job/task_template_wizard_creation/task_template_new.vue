<template>
  <div class="task-template-new-container">
    <main_menu> </main_menu>
    <v-toolbar
      class="mt-4 d-flex justify-space-between"
      dense
      elevation="0"
      fixed
      style="width: 100%"
      height="30px"
    >
      <bread_crumbs :item_list="bread_crumb_list"> </bread_crumbs>
      <button_with_confirm
        @confirm_click="cancel_job_api('archive')"
        color="error"
        icon="archive"
        :icon_style="true"
        tooltip_message="Archive"
        confirm_message="Archive"
        :disabled="job.id == undefined || loading"
        :loading="loading"
      >
      </button_with_confirm>
    </v-toolbar>
    <v-container fluid class="d-flex justify-center">
      <task_template_wizard
        v-if="!loading"
        :project_string_id="project_string_id"
        :mode="mode"
        :job="job"
      >
      </task_template_wizard>
      <v-progress-circular v-else indeterminate> </v-progress-circular>
    </v-container>
  </div>
</template>

<script lang="ts">
import axios from "../../../../services/customInstance";

import task_template_wizard from "./task_template_wizard";
import {archive_task_template} from "./../../../../services/taskTemplateService";
import {create_empty_job} from '../empty_job.js';
import Vue from "vue";

export default Vue.extend({
  name: "task_template_new",
  props: ["project_string_id_route", "job_id_route", "loading_steps"],

  components: {
    task_template_wizard: task_template_wizard,
  },
  mounted: async function () {
    this.mode = "new";
    if (this.job_id_route) {
      this.job_id = this.job_id_route;
      this.mode = "update";
    }
    if (this.job_id) {
      await this.fetch_job_api();
    }
    this.job.share_object.text =
      this.$store.state.project.current.project_string_id + " (Project)";
    //this.$store.commit('set_project_string_id', this.project_string_id)


    this.loading = false;
  },
  data() {
    return {
      loading: false,
      mode: null,
      job: create_empty_job(),
      job_id: null,
    };
  },
  computed: {
    bread_crumb_list: function () {
      return [
        {
          text: "Tasks",
          disabled: false,
          to: "/job/list",
        },
        {
          text: "New Task Template",
          disabled: true,
        },
      ];
    },
    project_string_id: function(){
      let project_string_id = this.project_string_id_route;

      if (!project_string_id) {
        project_string_id = this.job.project_string_id;
      }
      return project_string_id
    }
  },
  methods: {
    cancel_job_api: async function (mode) {
      this.loading = true;
      this.error = {};
      this.success = false;
      this.mode = mode;
      this.job_id = null;
      if (this.job) {
        this.job_id = this.job.id;
      }
      let [result, error] = await archive_task_template(this.job_id, this.job_list, this.mode)
      if(error){
        if (error.response && error.response.status == 403) {
          this.$store.commit("error_permission");

        }
        this.error = this.$route_api_errors(error);

      }
      if(result){
        this.success = true;
        this.$emit("cancel_job_success");
        this.$router.push(`/job/list/`);
      }
      this.loading = false;
    },
    fetch_job_api: async function () {
      this.loading = true;
      try {
        const response = await axios.post(
          `/api/v1/job/${this.job_id}/builder/info`,
          {
            mode_data: "job_edit",
          }
        );
        if (response.data.log.success == true) {
          this.job = response.data.job;
          if(this.job.label_file_list){
            this.job.label_file_list = this.job.label_file_list.map((elm) => ({
              id: elm,
            }));
          }

          this.job.original_attached_directories_dict = {
            ...this.job.attached_directories_dict,
          };
          this.job.share_object = {
            type: "project",
          };
          this.$emit("job_info", this.job);
          this.$store.commit("set_job", this.job);
        }
      } catch (e) {
        console.error(e);
        if (e.response && e.response.status == 403) {
          this.$store.commit("error_permission");
        }
      } finally {
        this.loading = false;
      }
    },
  },
});
</script>

<style>
.task-template-new-container{
  height: 100%;
}
</style>
