<template>
<div v-if="child_file_list" style="display: flex; flex-direction: row">
    <v_annotation_core
                v-if="!changing_file"
                class="pt-1 pl-1"
                ref="annotation_core"
                accesskey="full"
                :project_string_id="computed_project_string_id"
                :label_schema="current_label_schema"
                :model_run_id_list="model_run_id_list"
                :model_run_color_list="model_run_color_list"
                :task="task"
                :file="child_file_list[0]"
                :task_id_prop="task_id_prop"
                :request_save="request_save"
                :job_id="job_id"
                :view_only_mode="view_only"
                :label_list="label_list"
                :label_file_colour_map="label_file_colour_map"
                :enabled_edit_schema="enabled_edit_schema"
                :finish_annotation_show="show_snackbar"
                :global_attribute_groups_list="global_attribute_groups_list"
                :per_instance_attribute_groups_list="per_instance_attribute_groups_list"
            />
    <v_annotation_core
                v-if="!changing_file"
                class="pt-1 pl-1"
                ref="annotation_core"
                accesskey="full"
                :project_string_id="computed_project_string_id"
                :label_schema="current_label_schema"
                :model_run_id_list="model_run_id_list"
                :model_run_color_list="model_run_color_list"
                :task="task"
                :file="child_file_list[1]"
                :task_id_prop="task_id_prop"
                :request_save="request_save"
                :job_id="job_id"
                :view_only_mode="view_only"
                :label_list="label_list"
                :label_file_colour_map="label_file_colour_map"
                :enabled_edit_schema="enabled_edit_schema"
                :finish_annotation_show="show_snackbar"
                :global_attribute_groups_list="global_attribute_groups_list"
                :per_instance_attribute_groups_list="per_instance_attribute_groups_list"
            />
</div>
</template>

<script lang="ts">

import Vue from "vue";
import { get_child_files } from "../../../services/fileServices";
import axios from "../../../services/customInstance";
import { create_event } from "../../event/create_event";
import { UI_SCHEMA_TASK_MOCK } from "../../ui_schema/ui_schema_task_mock";
import { user_has_credentials } from '../../../services/userServices'
import { get_labels } from '../../../services/labelServices';
import { get_schemas } from "../../../services/labelServices";
import { fetchNextTask, fetchSingleTask } from "../../../services/tasksServices";


export default Vue.extend({
    name: 'compound_annotation_core',
    // props: {
    //     project_string_id: {
    //         type: String,
    //         required: true
    //     },
    //     file: {
    //         type: Object,
    //         required: true
    //     }
    // },
  props: {
    project_string_id: {
        type: String,
        default: null,
    },
    file_id_prop: {
        type: Number,
        default: null,
    },
    job_id: {
        type: Number,
        default: null,
    },
    task_id_prop: {
        type: Number,
        default: null,
    },
    show_explorer_full_screen: {
        type: Boolean,
        default: false,
    },
  },
    // data() {
    //     return {
    //         child_file_list: null as File[]
    //     }
    // },
      data() {
        return {
            show_snackbar: false as Boolean,
            schema_list_loading: false as Boolean,
            dialog: false as Boolean,
            changing_file: false as Boolean,
            enabled_edit_schema: false as Boolean,
            user_has_credentials: false as Boolean,
            credentials_granted: true as Boolean,
            initializing: true as Boolean,
            loading: false as Boolean,
            loading_project: true as Boolean,
            request_save: false as Boolean,
            view_only: false as Boolean,
            snackbar_message: "" as String,
            current_label_schema: null as Object,
            task: null as Object,
            current_file: null as Object,
            error: null as Object,
            label_file_colour_map_from_project: null as Object,
            model_run_id_list: [] as Array<any>,
            per_instance_attribute_groups_list: [] as Array<any>,
            missing_credentials: [] as Array<any>,
            label_schema_list: [] as Array<any>,
            labels_list_from_project: null as Array<any>,
            model_run_color_list: null  as Array<any>,
            global_attribute_groups_list: [] as Array<any>,
            child_file_list: null
        }
    },
    // async mounted() {
    //     const { result, error } = await get_child_files(this.project_string_id, this.file.id)
    //     if (error) {
    //         console.log(error)
    //     }
    //     if (result) {
    //         this.child_file_list = result
    //     }
    // },
    watch: {
    '$route'(to, from): void {
      if (from.name === 'task_annotation' && to.name === 'studio') {
        this.fetch_project_file_list();
        this.task = null;
        if (this.$refs.file_manager_sheet) {
          this.$refs.file_manager_sheet.display_file_manager_sheet();
        }
      }
      if (from.name === 'studio' && to.name === 'task_annotation') {
        this.current_file = null;
        this.fetch_single_task(this.task_id_prop);
        this.$refs.file_manager_sheet.hide_file_manager_sheet()
      }
      this.get_model_runs_from_query(to.query);
    },
    current_file: {
      handler(newVal, oldVal): void {
        if (newVal && newVal != oldVal) {
          this.$addQueriesToLocation({file: newVal.id});
        }
      },
    },
  },
  created() {
    if (this.$route.query.edit_schema) {
      this.enabled_edit_schema = true;
    }
    if (this.$route.query.view_only) {
      if (this.$route.query.view_only === 'false') {
        this.view_only = false;
      } else {
        this.view_only = true;
      }
    }
    if (
      !this.$store.getters.is_on_public_project ||
      this.$store.state.user.current.is_super_admin == true
    ) {
      if (this.task_id_prop) {
        this.add_visit_history_event("task");
      } else if (this.file_id_prop) {
        this.add_visit_history_event("file");
      } else {
        this.add_visit_history_event("page");
      }
    } else {
      this.view_only = true;
    }
  },
  async mounted() {
    if (!this.task_id_prop) {
      await this.get_project();
    } else {
      this.loading_project = false; // caution some assumptions around this flag for media loading
    }
    this.initializing = true

    this.get_model_runs_from_query(this.$route.query);
    if (this.$route.query.view_only) {
      this.view_only = true;
      if (this.$route.query.view_only === 'false') {
        this.view_only = false;
      } else {
        this.view_only = true;
      }
    }
    if (this.enabled_edit_schema) {
      this.task = {
        ...UI_SCHEMA_TASK_MOCK,
      };
      this.current_label_schema = this.task.job.label_schema;
      if (this.$refs.file_manager_sheet) {
        this.$refs.file_manager_sheet.set_file_list([this.task.file]);
        this.$refs.file_manager_sheet.hide_file_manager_sheet();
      }

    } else {
      if (this.task_id_prop) {
        await this.fetch_single_task(this.task_id_prop);
        await this.check_credentials();
        this.credentials_granted = this.has_credentials_or_admin();
        if (!this.credentials_granted) {
          this.show_missing_credentials_dialog();
        }
      } else if (this.file_id_prop) {
        await this.fetch_schema_list()
        await this.fetch_single_file();
      } else {
        await this.fetch_schema_list()
        await this.fetch_project_file_list();
      }
      await this.get_labels_from_project();
    }

    const { result, error } = await get_child_files(this.project_string_id, this.file_id)
        if (error) {
            console.log(error)
        }
        if (result) {
            this.child_file_list = result
        }

    this.initializing = false
  },
  computed: {
    any_loading: function (): boolean {
        return this.loading || this.loading_project || this.initializing
    },
    file_id: function (): number {
        let file_id = this.file_id_prop;
        if (this.$route.query.file) file_id = this.$route.query.file;
        
        return file_id;
    },
    annotation_interface: function (): string | null {
        if (!this.current_file && !this.task) return null

        let interface_type: string;

        if (this.current_file) interface_type = this.current_file.type
        else interface_type = this.task.file.type

        if (interface_type === 'image' || interface_type === 'video') return 'image_or_video'
        else return interface_type 
    },
    computed_project_string_id: function (): string {
        if (this.project_string_id) {
            this.$store.commit("set_project_string_id", this.project_string_id);
            return this.project_string_id;
        }

        return this.$store.state.project.current.project_string_id;
    },
    label_file_colour_map: function (): object {
        if (this.task && this.task.label_file_colour_map) {
            return this.task.label_dict.label_file_colour_map;
        }
        else if (this.label_file_colour_map_from_project) {
            return this.label_file_colour_map_from_project;
        }
        return {};
    },
    label_list: function (): Array<any> {
        if (this.task && this.task.label_list) {
            return this.task.label_dict.label_file_list_serialized;
        }
        else if (this.labels_list_from_project) {
            return this.labels_list_from_project;
        }
        return [];
    },
  },
  methods: {
    on_change_label_schema: function (schema: object): void {
        this.current_label_schema = schema;
        this.labels_list_from_project = null;
        this.get_labels_from_project()
    },
    fetch_schema_list: async function (): Promise<void> {
        this.schema_list_loading = true
        const [result, error] = await get_schemas(this.project_string_id);
        if (error) {
            this.error = this.$route_api_errors(error);
            this.schema_list_loading = false;
        }
        if (result) {
            this.label_schema_list = result;
            this.current_label_schema = this.label_schema_list[0];
        }
        this.schema_list_loading = false;
    },
    show_missing_credentials_dialog: function (): void {
        if (this.$refs.no_credentials_dialog) {
            this.$refs.no_credentials_dialog.open()
        }
    },
    has_credentials_or_admin: function (): boolean {
        const project_string_id = this.$store.state.project.current.project_string_id;
        if (this.$store.state.user.current.is_super_admin) return true
        else if (this.user_has_credentials) return true

        const roles = this.$store.getters.get_project_roles(project_string_id);
        if (roles && roles.includes('admin')) return true
        
        return false
    },
    check_credentials: async function (): Promise<void> {
        const project_string_id = this.$store.state.project.current.project_string_id;
        const user_id = this.$store.state.user.current.id;
        const task_id = this.task.job.id

        const [result, error] = await user_has_credentials(
            project_string_id,
            user_id,
            task_id,
        )

        if (error) this.error = this.$route_api_errors(error)
        else if (result) {
            this.user_has_credentials = result.has_credentials;
            this.missing_credentials = result.missing_credentials;
        }
    },
    get_model_runs_from_query: function (query: any): void {
        this.model_run_id_list = [];
        this.model_run_color_list = [];

        if (query.model_runs) {
            this.model_run_id_list = decodeURIComponent(query.model_runs).split(",");
            
            if (query.color_list) {
                this.model_run_color_list = decodeURIComponent(query.color_list).split(",");
            }
        }
    },
    request_file_change: function (direction: string, file: object): void {
        this.$refs.file_manager_sheet.request_change_file(direction, file);
    },
    change_file: async function (file: object, model_runs: any): Promise<void> {
        this.changing_file = true
        this.current_file = file;
        let model_runs_data = "";

        await this.$nextTick();

        if (model_runs) {
            model_runs_data = encodeURIComponent(model_runs);
        }

        this.get_model_runs_from_query(model_runs_data);
        this.changing_file = false;
    },
    get_labels_from_project: async function (): Promise<null> {
        if (
            this.labels_list_from_project &&
            this.computed_project_string_id == this.$store.state.project.current.project_string_id
        ) return

        if (!this.computed_project_string_id) return

        if (!this.current_label_schema) {
            this.error = {
                current_label_schema: 'Please set the curret label schema'
            }

            return
        }
        const [result, error] = await get_labels(this.computed_project_string_id, this.current_label_schema.id)
        
        if (error) {
            console.error(error)
            return
        }
        if (result) {
            this.labels_list_from_project = result.labels_out
            this.label_file_colour_map_from_project = result.label_file_colour_map
            this.global_attribute_groups_list = result.global_attribute_groups_list
            this.per_instance_attribute_groups_list = result.attribute_groups
        }
    },
    fetch_project_file_list: async function (): Promise<void> {
        this.loading = true;

        if (this.$route.query.file) {
            if (this.$refs.file_manager_sheet) {
            this.current_file = await this.$refs.file_manager_sheet.get_media(true, this.$route.query.file);
            }
        } else {
            if (this.$refs.file_manager_sheet) {
            this.current_file = await this.$refs.file_manager_sheet.get_media();
            }
        }
        this.loading = false;

        if (this.$refs.file_manager_sheet) {
            this.$refs.file_manager_sheet.display_file_manager_sheet();
        }
    },
    fetch_single_file: async function (): Promise<void> {
      this.loading = true;

      if (this.$refs.file_manager_sheet) {
        this.current_file = await this.$refs.file_manager_sheet.get_media();
      }

      this.loading = false;
      if (this.$refs.file_manager_sheet) {
        this.$refs.file_manager_sheet.display_file_manager_sheet();
      }
    },
    fetch_single_task: async function (task_id: number): Promise<void> {
        this.media_sheet = false;
        this.task_error = {
            task_request: null,
        };
        this.loading = true;
        this.error = {};
        this.media_loading = true;

        if (!task_id) {
            throw Error("Provide task ID");
        }

        const [result, error] = await fetchSingleTask(task_id, this.$store.state.builder_or_trainer.mode)

        
        if (error) {
            this.error = this.$route_api_errors(error);
            this.loading = false;
        }

        if (result) {
            if (result.log.success == true) {
                if (this.$refs.file_manager_sheet) {
                    this.$refs.file_manager_sheet.set_file_list([
                    result.task.file,
                ]);
            this.$refs.file_manager_sheet.hide_file_manager_sheet();
          }

          this.task = result.task;
          this.current_label_schema = this.task.job.label_schema;
          await this.get_project(this.task.project_string_id);
        }
        this.task_error = result.log.error;
        }
    },
    change_task: async function (direction: string, task: object, assign_to_user: boolean = false): Promise<void> {
      if (!task) {
        throw new Error("Provide task ");
      }

      const [result, error] = await fetchNextTask(this.computed_project_string_id, direction, task, assign_to_user)

      if (error) {
        console.debug(error);
      } 

      if (result) {
        if (result.task && result.task.id !== task['id']) {
            this.$router.push(`/task/${result.task.id}`);
            history.pushState({}, "", `/task/${result.task.id}`);

            if (this.$refs.file_manager_sheet) {
              this.$refs.file_manager_sheet.set_file_list([this.task.file]);
            }
            
            this.task = result.task;
        }
        else {
            this.show_snackbar = true;
            this.snackbar_message = 
                `This is the ${direction === 'next' ? 'last': 'first'} task of the list. Please go to previous tasks.`;
        }

      }
    },
    get_project: async function (project_string_id: string = undefined): Promise<void> {
      try {
        this.loading_project = true;
        let local_project_string_id = this.project_string_id;

        if (!local_project_string_id) local_project_string_id = project_string_id;

        if (
          local_project_string_id === this.$store.state.project.current.project_string_id
        ) return

        if (!local_project_string_id) return

        const response = await axios.get(`/api/project/${local_project_string_id}/view`);
        
        if (response.data["none_found"] == true) {
          this.none_found = true;
        } else {
          this.$store.commit("set_project_name", response.data["project"]["name"]);
          this.$store.commit("set_project", response.data["project"]);

          if (response.data.user_permission_level) {
            this.$store.commit("set_current_project_permission_level", response.data.user_permission_level[0]);
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
    set_file_list: function (new_file_list: Array<any>): void {
        this.$refs.file_manager_sheet.set_file_list(new_file_list);
    },
    add_visit_history_event: async function (object_type: any): Promise<void> {
        let page_name = "data_explorer";

        if (this.file_id_prop) page_name = "file_detail";
        if (this.task_id_prop)page_name = "task_detail";

        if (this.task_id_prop === -1 || this.task_id_prop === '-1') return

        await create_event(this.computed_project_string_id, {
            file_id: this.file_id_prop,
            task_id: this.task_id_prop,
            page_name: page_name,
            object_type: object_type,
            user_visit: "user_visit",
        });
    },
  },
})
</script>