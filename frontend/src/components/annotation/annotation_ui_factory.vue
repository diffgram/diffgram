<template>
  <div>
    <div id="annotation_ui_factory" tabindex="0">
      <div v-if="annotation_interface === 'image_or_video'">
        <v_annotation_core
          class="pt-1 pl-1"
          :project_string_id="computed_project_string_id"
          :model_run_id_list="model_run_id_list"
          :model_run_color_list="model_run_color_list"
          :task="task"
          :file="current_file"
          :task_id_prop="task_id_prop"
          :request_save="request_save"
          :accesskey="'full'"
          :job_id="job_id"
          :view_only_mode="view_only"
          :label_list="label_list"
          :label_file_colour_map="label_file_colour_map"
          :enabled_edit_schema="enabled_edit_schema"
          :finish_annotation_show="show_snackbar"
          @save_response_callback="save_response_callback()"
          @request_file_change="request_file_change"
          @set_file_list="set_file_list"
          @request_new_task="change_task"
          @replace_file="current_file = $event"
          ref="annotation_core"
        >
        </v_annotation_core>
      </div>
      <div v-else-if="annotation_interface === 'sensor_fusion'">
        <sensor_fusion_editor
          :project_string_id="computed_project_string_id"
          :label_file_colour_map="label_file_colour_map"
          :label_list="label_list"
          :task="task"
          :file="current_file"
          :view_only_mode="view_only"
          @request_file_change="request_file_change"
          @request_new_task="change_task"
          ref="sensor_fusion_editor"
        >
        </sensor_fusion_editor>
      </div>
      <div v-else-if="annotation_interface === 'text'">
        <text_annotation_core 
          :file="current_file" 
          :label_list="label_list"
        />
      </div>
      <div v-else-if="!annotation_interface">
        <empty_file_editor_placeholder
          :loading="any_loading"
          :project_string_id="project_string_id"
        ></empty_file_editor_placeholder>
      </div>

      <file_manager_sheet
        v-show="!loading_project"
        :show_sheet="!loading_project"
        ref="file_manager_sheet"
        :project_string_id="computed_project_string_id"
        :task="task"
        :view_only="view_only"
        :enabled_edit_schema="enabled_edit_schema"
        :show_explorer_full_screen="show_explorer_full_screen"
        :file_id_prop="file_id_prop"
        :job_id="job_id"
        @change_file="change_file"
      >
      </file_manager_sheet>
    </div>
    <v-snackbar
      v-if="show_snackbar"
      color="secondary"
      dark
      v-model="show_snackbar"
    >
      {{ snackbar_message }}
      <template v-slot:action="{ attrs }">
        <v-btn color="white" text v-bind="attrs" @click="show_snackbar = false">
          Ok.
        </v-btn>
      </template>
    </v-snackbar>
  </div>
</template>


<script lang="ts">
import axios from "axios";
import { create_event } from "../event/create_event";
import { UI_SCHEMA_TASK_MOCK } from "../ui_schema/ui_schema_task_mock";
import empty_file_editor_placeholder from "./empty_file_editor_placeholder";
import file_manager_sheet from "../source_control/file_manager_sheet";
import sensor_fusion_editor from '../3d_annotation/sensor_fusion_editor'
import text_annotation_core from "../text_annotation/text_annotation_core.vue"
import Vue from "vue";


export default Vue.extend({
  name: "annotation_ui_factory",
  components: {
    file_manager_sheet,
    empty_file_editor_placeholder,
    sensor_fusion_editor,
    text_annotation_core
  },
  props: {
    project_string_id: {
      default: null,
    },
    file_id_prop: {
      default: null,
    },
    job_id: {
      default: null,
    },
    task_id_prop: {
      default: null,
    },
    show_explorer_full_screen: {
      default: false,
    },
  },
  data() {
    return {
      show_snackbar: false,
      enabled_edit_schema: false,
      initializing: false,
      snackbar_message: "",
      loading: false,
      loading_project: true,
      task: null,
      current_file: null,
      request_save: false,
      model_run_id_list: [],

      view_only: false,

      labels_list_from_project: null,
      model_run_color_list: null,
      label_file_colour_map_from_project: null,
    };
  },
  watch: {
    $route(to, from) {
      if (from.name === "task_annotation" && to.name === "studio") {
        this.fetch_project_file_list();
        this.task = null;
        this.$refs.file_manager_sheet.display_file_manager_sheet();
      }
      if (from.name === "studio" && to.name === "task_annotation") {
        this.current_file = null;
        this.fetch_single_task(this.$props.task_id_prop);
        this.$refs.file_manager_sheet.hide_file_manager_sheet();
      }
      this.get_model_runs_from_query(to.query);
    },
    current_file: {
      handler(newVal, oldVal) {
        if (newVal && newVal != oldVal) {
          this.$addQueriesToLocation({ file: newVal.id });
        }
      },
    },
  },
  created() {
    if (this.$route.query.edit_schema) {
      this.enabled_edit_schema = true;
    }
    if (this.$route.query.view_only) {
      this.view_only = true;
    }

    if (
      !this.$store.getters.is_on_public_project ||
      this.$store.state.user.current.is_super_admin == true
    ) {
      if (this.$props.task_id_prop) {
        this.add_visit_history_event("task");
      } else if (this.$props.file_id_prop) {
        this.add_visit_history_event("file");
      } else {
        this.add_visit_history_event("page");
      }
    } else {
      this.view_only = true;
    }
  },
  async mounted() {
    if (!this.$props.task_id_prop) {
      await this.get_project();
    } else {
      this.loading_project = false; // caution some assumptions around this flag for media loading
    }
    this.initializing = true
    await this.get_labels_from_project();
    this.get_model_runs_from_query(this.$route.query);
    if (this.$route.query.view_only) {
      this.view_only = true;
    }
    if (this.enabled_edit_schema) {
      this.task = {
        ...UI_SCHEMA_TASK_MOCK,
      };
      this.$refs.file_manager_sheet.set_file_list([this.task.file]);
      this.$refs.file_manager_sheet.hide_file_manager_sheet();
    } else {
      if (this.$props.task_id_prop) {
        await this.fetch_single_task(this.$props.task_id_prop);
      } else if (this.$props.file_id_prop) {
        await this.fetch_single_file();
      } else {
        await this.fetch_project_file_list();
      }
    }
    this.initializing = false
  },
  computed: {
    any_loading: function(){
      return this.loading || this.loading_project || this.initializing
    },
    file_id: function () {
      let file_id = this.$props.file_id_prop;
      if (this.$route.query.file) {
        file_id = this.$route.query.file;
      }
      return file_id;
    },
    annotation_interface: function(){
      if(!this.current_file && !this.task){
        return
      }
      if(this.current_file){
        if(this.current_file.type === 'image' || this.current_file.type === 'video'){
          return 'image_or_video';
        }
        else if(this.current_file.type === 'sensor_fusion'){
          return 'sensor_fusion';
        }
        else if(this.current_file.type === 'text'){
          return 'text'
        }
      }
      if(this.task){
        if(this.task.file.type === 'image' || this.task.file.type === 'video'){
          return 'image_or_video';
        }
        else if(this.task.file.type === 'sensor_fusion'){
          return 'sensor_fusion';
        }
        else if(this.task.file.type === 'text'){
          return 'text';
        }
      }



    },
    computed_project_string_id: function () {
      if (this.$props.project_string_id) {
        this.$store.commit(
          "set_project_string_id",
          this.$props.project_string_id
        );
        return this.$props.project_string_id;
      }
      return this.$store.state.project.current.project_string_id;
    },

    show_annotation_core: function () {
      return true;
    },

    label_file_colour_map: function () {
      if (this.task && this.task.label_file_colour_map) {
        return this.task.label_dict.label_file_colour_map;
      }
      if (this.label_file_colour_map_from_project) {
        return this.label_file_colour_map_from_project;
      }
      return {};
    },

    label_list: function () {
      if (this.task && this.task.label_list) {
        return this.task.label_dict.label_file_list_serialized;
      }
      if (this.labels_list_from_project) {
        return this.labels_list_from_project;
      }
      return [];
    },
  },
  methods: {
    get_model_runs_from_query: function (query) {
      this.model_run_id_list = [];
      this.model_run_color_list = [];
      if (query.model_runs) {
        this.model_run_id_list = decodeURIComponent(query.model_runs).split(
          ","
        );
        if (query.color_list) {
          this.model_run_color_list = decodeURIComponent(
            query.color_list
          ).split(",");
        }
      }
    },
    request_file_change: function (direction, file) {
      this.$refs.file_manager_sheet.request_change_file(direction, file);
    },

    change_file: function (file, model_runs, color_list) {
      this.current_file = file;
      let model_runs_data = "";
      if (model_runs) {
        model_runs_data = encodeURIComponent(model_runs);
      }
      this.get_model_runs_from_query(model_runs_data);
    },

    get_labels_from_project: async function () {
      try {
        if (
          this.labels_list_from_project &&
          this.computed_project_string_id ==
            this.$store.state.project.current.project_string_id
        ) {
          return;
        }
        if (!this.computed_project_string_id) {
          return;
        }
        var url =
          "/api/project/" + this.computed_project_string_id + "/labels/refresh";
        const response = await axios.get(url, {});
        this.labels_list_from_project = response.data.labels_out;
        this.label_file_colour_map_from_project =
          response.data.label_file_colour_map;
      } catch (e) {
        console.error(e);
      }
    },

    fetch_project_file_list: async function () {
      this.loading = true;
      if (this.$route.query.file) {
        this.current_file = await this.$refs.file_manager_sheet.get_media(
          true,
          this.$route.query.file
        );
      } else {
        this.current_file = await this.$refs.file_manager_sheet.get_media();
      }
      this.loading = false;
      this.$refs.file_manager_sheet.display_file_manager_sheet();
    },

    fetch_single_file: async function () {
      this.loading = true;
      this.current_file = await this.$refs.file_manager_sheet.get_media();
      this.loading = false;
      this.$refs.file_manager_sheet.display_file_manager_sheet();
    },

    fetch_single_task: async function (task_id) {
      this.media_sheet = false;
      this.task_error = {
        task_request: null,
      };
      this.loading = true;
      this.error = {}; // reset
      this.media_loading = true; // gets set to false in shared file_update_core()
      if (!task_id) {
        throw Error("Provide task ID");
      }
      try {
        const response = await axios.post("/api/v1/task", {
          task_id: parseInt(task_id, 10),
          builder_or_trainer_mode: this.$store.state.builder_or_trainer.mode,
        });
        if (response.data.log.success == true) {
          this.$refs.file_manager_sheet.set_file_list([
            response.data.task.file,
          ]);
          this.$refs.file_manager_sheet.hide_file_manager_sheet();
          this.task = response.data.task;
          await this.get_project(this.task.project_string_id);
        }
        this.task_error = response.data.log.error;
      } catch (error) {
        console.error(error);
        this.loading = false;
        // this.logout()
      }
    },

    change_task: async function (direction, task, assign_to_user = false) {
      // Assumes it does NOT assign the user
      if (!task) {
        throw new Error("Provide task ");
      }

      try {
        const response = await axios.post(
          `/api/v1/job/${task.job_id}/next-task`,
          {
            project_string_id: this.computed_project_string_id,
            task_id: task.id,
            direction: direction,
            assign_to_user: assign_to_user,
          }
        );
        if (response.data) {
          if (response.data.task && response.data.task.id !== task.id) {
            this.$router.push(`/task/${response.data.task.id}`);
            history.pushState({}, "", `/task/${response.data.task.id}`);
            // Refresh task Data. This will change the props of the annotation_ui and trigger watchers.
            // In the task context we reset the file list on media core to keep only the current task's file.
            this.$refs.file_manager_sheet.set_file_list([this.task.file]);
            this.task = response.data.task;
          } else {
            if (direction === "next") {
              this.show_snackbar = true;
              this.snackbar_message =
                "This is the last task of the list. Please go to previous tasks.";
            } else {
              this.show_snackbar = true;
              this.snackbar_message =
                "This is the first task of the list. Please go to the next tasks.";
            }
          }
        }
      } catch (error) {
        console.debug(error);
      } finally {
      }
    },

    get_project: async function (project_string_id = undefined) {
      try {
        this.loading_project = true;

        let local_project_string_id = this.project_string_id;
        if (!local_project_string_id) {
          local_project_string_id = project_string_id;
        }

        if (
          local_project_string_id ==
          this.$store.state.project.current.project_string_id
        ) {
          return;
        }

        if(!local_project_string_id){
          return
        }

        const response = await axios.get(
          "/api/project/" + local_project_string_id + "/view"
        );
        if (response.data["none_found"] == true) {
          this.none_found = true;
        } else {
          this.$store.commit(
            "set_project_name",
            response.data["project"]["name"]
          );
          this.$store.commit("set_project", response.data["project"]);

          if (response.data.user_permission_level) {
            this.$store.commit(
              "set_current_project_permission_level",
              response.data.user_permission_level[0]
            );

            if (response.data.user_permission_level[0] == "Viewer") {
              this.view_only = true;
            }
          }

          this.show_snackbar = true;
          this.snackbar_message =
            "Changed project now in " + response.data["project"]["name"];
        }
      } catch (error) {
        console.error(error);
      } finally {
        this.loading_project = false;
      }
    },

    set_file_list: function (new_file_list) {
      this.$refs.file_manager_sheet.set_file_list(new_file_list);
    },

    add_visit_history_event: async function (object_type) {
      let page_name = "data_explorer";
      if (this.$props.file_id_prop) {
        page_name = "file_detail";
      }
      if (this.$props.task_id_prop) {
        page_name = "task_detail";
      }
      const event_data = await create_event(this.computed_project_string_id, {
        file_id: this.$props.file_id_prop,
        task_id: this.$props.task_id_prop,
        page_name: page_name,
        object_type: object_type,
        user_visit: "user_visit",
      });
    },

    save_response_callback: function (result) {},
  },
});
</script>
