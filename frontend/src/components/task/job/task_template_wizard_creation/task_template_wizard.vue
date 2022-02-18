<template>
  <v-container fluid style="width: 100%">
    <v-stepper v-model="step" style="height: 100%" @change="on_change_step">
      <v-stepper-header class="ma-0 pl-8 pr-8">
        <template v-for="(key, index) in Object.keys(steps_configuration)">
          <v-stepper-step

            v-if="!steps_configuration[key].hide"
            :complete="step > steps_configuration[key].number"
            :step="steps_configuration[key].number"
            :editable="job.id != undefined"
          >
            {{steps_configuration[key].header_title}}
          </v-stepper-step>
          <v-divider v-if="index < Object.keys(steps_configuration).length - 1"></v-divider>
        </template>
      </v-stepper-header>

      <v-progress-linear
        color="secondary"
        striped
        v-model="global_progress"
        height="12"
      >
      </v-progress-linear>

      <v-stepper-items style="height: 100%">
        <v_error_multiple :error="error"></v_error_multiple>
        <v-stepper-content
          v-if="!steps_configuration['name'].hide"
          :step="steps_configuration['name'].number"
          style="height: 100%">
          <step_name_task_template
             ref="step_name"
             :title="steps_configuration['name'].title"
             :message="steps_configuration['name'].message"
            :project_string_id="project_string_id"
            :job="job"
            :loading_steps="loading"
            @next_step="go_to_step(steps_configuration['name'].number + 1)"
          ></step_name_task_template>
        </v-stepper-content>
        <v-stepper-content
          v-if="!steps_configuration['labels'].hide"
          :step="steps_configuration['labels'].number"
          style="height: 100%">
          <step_label_selection_task_template
            :project_string_id="project_string_id"
            :job="job"
            :loading_steps="loading"
            @previous_step="go_to_step(steps_configuration['labels'].number - 1)"
            @next_step="go_to_step(steps_configuration['labels'].number + 1)"
          ></step_label_selection_task_template>
        </v-stepper-content>
        <v-stepper-content
          v-if="!steps_configuration['members'].hide"
          :step="steps_configuration['members'].number"
          style="height: 100%">
          <step_users_selection
            :project_string_id="project_string_id"
            :job="job"
            :mode="mode"
            :title="steps_configuration['members'].title"
            :message="steps_configuration['members'].message"
            :loading_steps="loading"
            @previous_step="go_to_step(steps_configuration['members'].number - 1)"
            @next_step="go_to_step(steps_configuration['members'].number + 1)"
          ></step_users_selection>
        </v-stepper-content>
        <v-stepper-content
          v-if="!steps_configuration['reviewers'].hide"
          :step="steps_configuration['reviewers'].number"
          style="height: 100%">
          <step_reviewers_selection
            :project_string_id="project_string_id"
            :job="job"
            :mode="mode"
            :loading_steps="loading"
            @previous_step="go_to_step(steps_configuration['reviewers'].number - 1)"
            @next_step="go_to_step(steps_configuration['reviewers'].number + 1)"
          ></step_reviewers_selection>
        </v-stepper-content>
        <v-stepper-content
          v-if="!steps_configuration['upload'].hide"
          :step="steps_configuration['upload'].number">
          <step_upload_files_task_template
            :project_string_id="project_string_id"
            :job="job"
            :loading_steps="loading"
            @previous_step="go_to_step(steps_configuration['upload'].number - 1)"
            @next_step="go_to_step(steps_configuration['upload'].number + 1)"
          ></step_upload_files_task_template>
        </v-stepper-content>

        <v-stepper-content
          v-if="!steps_configuration['datasets'].hide"
          :step="steps_configuration['datasets'].number">
          <step_attach_directories_task_template
            :project_string_id="project_string_id"
            :job="job"
            :loading_steps="loading"
            @previous_step="go_to_step(steps_configuration['datasets'].number - 1)"
            @next_step="go_to_step(steps_configuration['datasets'].number + 1)"
          ></step_attach_directories_task_template>
        </v-stepper-content>

        <v-stepper-content
          v-if="!steps_configuration['ui_schema'].hide"
          :step="steps_configuration['ui_schema'].number">
          <step_ui_schema_task_template
            :project_string_id="project_string_id"
            :job="job"
            :loading_steps="loading"
            @previous_step="go_to_step(steps_configuration['ui_schema'].number - 1)"
            @next_step="go_to_step(steps_configuration['ui_schema'].number + 1)"
          ></step_ui_schema_task_template>
        </v-stepper-content>

        <v-stepper-content
          v-if="!steps_configuration['guides'].hide"
          :step="steps_configuration['guides'].number">
          <step_guides_task_template
            :project_string_id="project_string_id"
            :job="job"
            :loading_steps="loading"
            @previous_step="go_to_step(steps_configuration['guides'].number - 1)"
            @next_step="go_to_step(steps_configuration['guides'].number + 1)"
          ></step_guides_task_template>
        </v-stepper-content>

        <v-stepper-content
          v-if="!steps_configuration['advanced'].hide"
          :step="steps_configuration['advanced'].number">
          <step_advanced_options_task_template
            :project_string_id="project_string_id"
            :job="job"
            :loading_steps="loading"
            @previous_step="go_to_step(steps_configuration['advanced'].number - 1)"
            @next_step="go_to_step(steps_configuration['advanced'].number + 1)"
          ></step_advanced_options_task_template>

        </v-stepper-content>

        <v-stepper-content
          v-if="!steps_configuration['credentials'].hide"
          :step="steps_configuration['credentials'].number">
          <step_credentials_task_template
            :project_string_id="project_string_id"
            :job="job"
            :loading_steps="loading"
            @previous_step="go_to_step(steps_configuration['credentials'].number - 1)"
            @next_step="launch_task_template">

          </step_credentials_task_template>
        </v-stepper-content>
      </v-stepper-items>
    </v-stepper>
  </v-container>
</template>

<script lang="ts">
import axios from "../../../../services/customAxiosInstance";
import step_name_task_template from "./step_name_task_template";
import step_advanced_options_task_template from "./step_advanced_options_task_template";
import step_guides_task_template from "./step_guides_task_template";
import step_upload_files_task_template from "./step_upload_files_task_template";
import step_label_selection_task_template from "./step_label_selection_task_template";
import step_ui_schema_task_template from "./step_ui_schema_task_template";
import step_credentials_task_template from "./step_credentials_task_template";
import step_users_selection from "./step_users_selection";
import step_attach_directories_task_template from "./step_attach_directories_task_template";
import step_reviewers_selection from "./step_reviewers_selection.vue";

import Vue from "vue";

export default Vue.extend({
  name: "task_template_new_wizard",
  props: {
    project_string_id: {
      default: null,
    },
    job: {
      default: null,
    },
    job_id_route: {
      default: null,
    },
    mode: {
      default: null,
    },
    steps_config_overwrite:{
      default: null
    }
  },

  components: {
    step_name_task_template,
    step_upload_files_task_template,
    step_credentials_task_template,
    step_guides_task_template,
    step_users_selection,
    step_ui_schema_task_template,
    step_advanced_options_task_template,
    step_label_selection_task_template,
    step_attach_directories_task_template,
    step_reviewers_selection,
  },
  created: async function () {
    this.steps_configuration = {
      ...this.steps_configuration,
      ...this.$props.steps_config_overwrite
    }
  },
  data() {
    return {
      step: 1,
      total_steps: 9,
      loading: false,
      steps_configuration: {
        name: {
          header_title: 'Start',
          number: 1,
          title: 'New Task Template',
          message: 'The following steps will guide you on the creation of a new task group.\n' + 'Give a name to your Tasks:',
          hide: false
        },
        labels: {
          header_title: 'Labels',
          number: 2,
          hide: false
        },
        members: {
          header_title: 'Members',
          number: 3,
          hide: false,
          message: 'Select the Users assigned to the tasks.',
          title: 'Who is assigned to work on these tasks?'
        },
        reviewers: {
          header_title: 'Reviewers',
          number: 4,
          hide: false
        },
        upload: {
          header_title: 'Upload',
          number: 5,
          hide: false
        },
        datasets: {
          header_title: 'Datasets',
          number: 6,
          hide: false
        },
        ui_schema: {
          header_title: 'UI Schema',
          number: 7,
          hide: false
        },
        guides: {
          header_title: 'Guides',
          number: 8,
          hide: false
        },
        advanced: {
          header_title: 'Advanced Settings',
          number: 9,
          hide: false
        },
        credentials: {
          header_title: 'Credentials',
          number: 10,
          hide: false
        },
      },
      error: {},
    };
  },
  computed: {
    global_progress: function () {
      return (this.step * 100) / this.total_steps;
    },
    bread_crumb_list: function () {
      return [
        {
          text: "Tasks",
          disabled: false,
          to: "/job/list",
        },
        {
          text: "New Template",
          disabled: true,
        },
      ];
    },
  },
  methods: {
    job_update: async function () {
      this.loading = true;
      const job = this.$props.job;
      this.error = {};
      try {
        const response = await axios.post(
          `/api/v1/project/${this.project_string_id}/job/update`,
          {
            ...job,
            job_id: job.id,
          }
        );
        // Handle job hash / draft / job status
        if (response.data.log.success == true) {
          this.loading = false;
          this.$emit("job-updated", job);
          return response;
        }
      } catch (error) {
        this.loading = false;
        this.error = this.$route_api_errors(error);
        return false;
      }
    },
    launch_task_template: async function () {

      await this.job_update();
      this.error = {};

      this.loading = true;

      try {
        // const response_output_dirs = await this.add_output_actions_to_job();
        // if (!response_output_dirs) {
        //   return
        // }
        // const response_dirs_update = await this.add_dirs_to_job_api();
        // if (!response_dirs_update) {
        //   return
        // }
        const response = await axios.post("/api/v1/job/launch", {
          job_id: this.job.id,
        });
        // Push to success / stats page?
        // Show success?

        if(this.job.type != 'exam_template'){
          this.$router.push("/job/list?success_launch=true");
        }
        else{
          this.$router.push(`/${this.$props.project_string_id}/exam/${this.job.id}`);

        }
      } catch (error) {
        console.error(error);
        this.error = this.$route_api_errors(error);
        if (this.error.job_id) {
          this.error.info = "Please complete all the steps to launch the job.";
        }
      } finally {
        this.loading = false;
      }
    },
    step_is_hidden: function(step){
      for(let key of Object.keys(this.steps_configuration)){
        let config = this.steps_configuration[key];
        if(config.number === step && config.hide){
          return true
        }
      }
      return false
    },
    go_to_step: async function (step) {
      await this.job_update();
      let new_step = step;
      if(this.step_is_hidden(step)){
        let new_step = step + 1;
        while(this.step_is_hidden(step)){
          new_step += 1
        }
      }
      this.step = new_step;
    },
    on_change_step: function () {},
  },
});
</script>
