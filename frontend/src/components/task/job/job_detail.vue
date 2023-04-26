<template>
  <div class="job-detail-container">
    <div class="d-flex justify-space-between align-center mb-1">
      <v-col>
      <h1 class="pa-2">
        <v-layout>
          <div
            class="font-weight-light clickable"
            @click="$router.push('/job/list')"
          >
            {{ $store.state.project.current.name }} /
          </div>

          <div
            v-if="
              $store.state.job.current.id == this.job_id && edit_name != true
            "
            class="font-weight-normal pl-2 d-flex align-center"
            @dblclick="edit_name = true"
          >
            {{ job_name }}
            <standard_button
              v-if="edit_name == false"
              tooltip_message="Edit Name"
              tooltip_direction="bottom"
              @click="edit_name = true"
              icon="edit"
              :icon_style="true"
              color="primary"
            >
            </standard_button>
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

          <standard_button
            v-if="edit_name == true"
            tooltip_message="Cancel Name Edit"
            datacy="cancel_edit_name"
            @click="edit_name = false"
            icon="mdi-cancel"
            :icon_style="true"
            color="primary"
            :disabled="loading"
          >
          </standard_button>
        </v-layout>
      </h1>

      <tag_display_and_select
          :project_string_id="project_string_id"
          :object_id="parseInt(job_id)"
          :object_type="'job'"
      >
      </tag_display_and_select>

      </v-col>

      <v-btn
        @click="api_get_next_task_scoped_to_job(job_id)"
        :loading="next_task_loading"
        :disabled="next_task_loading"
        color="primary"
        large
      >
        Start Annotating
      </v-btn>
    </div>

    <v-tabs v-model="tab" color="primary" style="height: 100%" v-if="show_job">
      <v-tab v-for="item in items" :key="item.text">
        <v-icon left>{{ item.icon }}</v-icon>
        {{ item.text }}
      </v-tab>

      <v-tabs-items v-model="tab">
        <v-tab-item class="pt-2">

          <v_job_detail_builder
            v-if="$store.state.builder_or_trainer.mode == 'builder'"
            :job_id="job_id"
          >
          </v_job_detail_builder>

          <v_job_detail_trainer
            v-if="$store.state.builder_or_trainer.mode == 'trainer'"
            :job_id="job_id"
          >
          </v_job_detail_trainer>
        </v-tab-item>



        <v-tab-item>
          <task_template_discussions
            :project_string_id="$store.state.project.current.project_string_id"
            :task_template_id="job_id"
          ></task_template_discussions>
        </v-tab-item>

        <v-tab-item>

          <stats_panel :project_string_id="project_string_id" :job_id="job_id"/>

          <v_stats_task :job_id="job_id"
                        :project_string_id="$store.state.project.current.project_string_id">
          </v_stats_task>
        </v-tab-item>

        <v-tab-item>
          <job_edit_schema :job_id="job_id" :project_string_id="$store.state.project.current.project_string_id">

          </job_edit_schema>
        </v-tab-item>

        <v-tab-item>
          <job_pipeline_mxgraph
            :job_id="job_id"
            :show_output_jobs="true"
            class="mt-4 mb-4 pb-8 pt-8"
          >
          </job_pipeline_mxgraph>
        </v-tab-item>

        <v-tab-item>
          <v-container fluid>


            <task_template_ui_schema_editor
              :project_string_id="project_string_id"
              :job_id="job_id">

            </task_template_ui_schema_editor>
          </v-container>
        </v-tab-item>
        <v-tab-item>
          <v-container fluid>
            <task_template_member_editor
              :project_string_id="project_string_id"
              :job_id="job_id"
            ></task_template_member_editor>

          </v-container>
        </v-tab-item>
        <v-tab-item>
          <!-- Settings -->
          <v_info_multiple :info="info"></v_info_multiple>


          <v-layout>
            <v-spacer></v-spacer>

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
            :job_id="job_id"
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
    <no_credentials_dialog ref="no_credentials_dialog"
                           :missing_credentials="missing_credentials"></no_credentials_dialog>
    <v-snackbar v-model="no_task_snackbar" color="red">
      No tasks available
    </v-snackbar>
  </div>
</template>

<script lang="ts">
import v_job_detail_builder from "./job_detail_builder";
import job_edit_schema from "./job_edit_schema";
import no_credentials_dialog from "./no_credentials_dialog";
import v_job_cancel_actions_button_container from "./job_cancel_actions_button_container";
import v_job_detail_trainer from "./job_detail_trainer";

import task_template_discussions from "../../discussions/task_template_discussions";
import job_pipeline_mxgraph from "./job_pipeline_mxgraph";
import label_select_only from "../../label/label_select_only.vue";
import {user_has_credentials} from '../../../services/userServices'
import axios from "../../../services/customInstance";
import job_type from "./job_type";
import stats_panel from "../../stats/stats_panel.vue";
import {nextTask} from "../../../services/tasksServices";

import Vue from "vue";
import No_credentials_dialog from "./no_credentials_dialog.vue";
import task_template_ui_schema_editor from "./task_template_ui_schema_editor.vue";
import Label_schema_selector from "../../label/label_schema_selector.vue";
import tag_display_and_select from '@/components/tag/tag_display_and_select.vue'
import Task_template_member_editor from "./task_template_member_editor.vue";


export default Vue.extend({
  name: "job_detail",
  props: ["job_id"],
  components: {
    Task_template_member_editor,
    Label_schema_selector,
    No_credentials_dialog,
    job_edit_schema,
    v_job_detail_builder,
    v_job_cancel_actions_button_container,
    task_template_ui_schema_editor,
    no_credentials_dialog,
    task_template_discussions,
    v_job_detail_trainer,
    job_pipeline_mxgraph,
    label_select_only,
    job_type,
    stats_panel,
    tag_display_and_select
  },

  data() {
    return {
      tab: null,
      no_task_snackbar: false,
      items: [
        {text: "Oveview", icon: "mdi-view-dashboard"},
        {text: "Discussions", icon: "mdi-comment-multiple"},
        {text: "Insights", icon: "mdi-chart-areaspline"},
        {text: "Schema", icon: "mdi-format-paint"},
        {text: "Pipeline", icon: "mdi-folder-network"},
        {text: "UI Schema", icon: "mdi-puzzle-edit"},
        {text: "Members", icon: "mdi-account-multiple"},
        {text: "Credentials & Settings", icon: "mdi-cog"},
      ],
      update_label_file_list: null,
      has_changes: false,
      show_job: false,
      user_has_credentials: false,
      missing_credentials: [],

      edit_name: false,

      job_name: undefined,
      ui_schema_id: undefined,


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
  async created() {
    if (this.$route.path.endsWith("discussions")) {
      this.tab = 1;
    }
    await this.check_credentials();
    this.show_job = this.has_credentials_or_admin();
    if (!this.show_job) {
      this.show_missing_credentials_dialog()
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
  computed: {
    project_string_id: function () {
      return this.$store.state.project.current.project_string_id;
    }
  },
  beforeDestroy() {
    this.job_current_watcher();
  },
  methods: {
    has_credentials_or_admin: function () {
      let project_string_id = this.$store.state.project.current.project_string_id;
      if (this.$store.state.user.current.is_super_admin) {
        return true
      }
      if (this.user_has_credentials) {
        return true
      }
      let roles = this.$store.getters.get_project_roles(project_string_id);
      if (roles && roles.includes('admin')) {
        return true
      }
      return false
    },
    show_missing_credentials_dialog: function () {
      if (this.$refs.no_credentials_dialog) {
        this.$refs.no_credentials_dialog.open()
      }
    },
    check_credentials: async function () {
      let project_string_id = this.$store.state.project.current.project_string_id;
      let user_id = this.$store.state.user.current.id;
      let [result, error] = await user_has_credentials(
        project_string_id,
        user_id,
        this.job_id,
      )
      if (error) {
        this.error = this.$route_api_errors(error)
        return
      }
      if (result) {
        this.user_has_credentials = result.has_credentials;
        this.missing_credentials = result.missing_credentials;
      }
    },
    reset_local_info() {
      this.job_name = this.$store.state.job.current.name;
      this.set_document_title();
    },
    set_document_title() {
      document.title = this.job_name;
    },
    api_get_next_task_scoped_to_job: async function (job_id) {
      this.next_task_loading = true;
      const response = await nextTask(job_id);
      if (response.status === 200 && response.data.task) {
        let task = response.data.task;
        const routeData = `/task/${task.id}`;
        this.$router.push(routeData);
      } else {
        this.no_task_snackbar = true
      }
      this.next_task_loading = false;
    },
    api_update_job: async function () {
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
      try {
        const response = await axios.post(
          "/api/v1/project/" +
          this.$store.state.project.current.project_string_id +
          "/job/update",
          {
            job_id: parseInt(this.job_id),
            label_file_list: this.update_label_file_list, // see assumptions on null in note above
            name: this.job_name,
            ui_schema_id: this.ui_schema_id,
          }
        )
        this.loading = false;
        this.info = response.data.log.info;
        this.edit_name = false;
        this.has_changes = false;
        this.update_label_file_list = null;
        this.$store.commit("set_job", response.data.job);
        this.set_document_title();
        return true
      } catch (e) {
        this.loading = false;
        this.error = this.$route_api_errors(e);
        return false
      }
    },
  },
});
</script>

<style>
.job-detail-container {
  padding: 0 10rem;
  margin-top: 2rem;
  height: 100%;
}
</style>
