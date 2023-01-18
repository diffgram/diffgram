<template>
  <div class="d-flex">
    <toolbar_factory
      v-if="annotation_ui_context.working_file && annotation_ui_context.command_manager"
      :project_string_id="project_string_id"
      :working_file="annotation_ui_context.working_file"
      :command_manager="annotation_ui_context.command_manager"
      :label_settings="annotation_ui_context.image_annotation_ctx.label_settings"
      :label_schema="annotation_ui_context.label_schema"
      :draw_mode="annotation_ui_context.image_annotation_ctx.draw_mode"
      :instance_type="annotation_ui_context.instance_type"
      :label_file_colour_map="label_file_colour_map"
      :label_list="label_list"
      :interface_type="interface_type"
      :instance_type_list="instance_type_list"
      :filtered_instance_type_list_function="filtered_instance_type_list"
      :show_default_navigation="show_default_navigation"
      :current_label_file="annotation_ui_context.current_label_file"
      :has_changed="has_changed || has_pending_frames"
      :save_loading="annotation_ui_context.image_annotation_ctx.video_mode ? any_frame_saving : save_loading_image"
      :annotations_loading="annotation_ui_context.image_annotation_ctx.annotations_loading"
      @save="save"
      @redo="redo"
      @undo="undo"
      @rotate_image="rotate_image"
      @change_file="request_file_change"
      @edit_mode_toggle="on_draw_mode_changed"
      @change_instance_type="change_instance_type"
      @change_label_schema="on_change_label_schema"
      @smooth_canvas_changed="update_smooth_canvas($event)"
      @change_label_file="change_current_label_file_template($event)"
    />
    <!--  Temporal v-if condition while other sidebars are migrated inside sidebar factory  -->
    <sidebar_factory
      v-if="(interface_type === 'image' || interface_type === 'video') && !task_error.task_request && !changing_file && !changing_task && annotation_ui_context.image_annotation_ctx != undefined"
      :annotation_ui_context="annotation_ui_context"
      :interface_type="interface_type"
      :label_file_colour_map="label_file_colour_map"
      :label_list="label_list"
      :project_string_id="project_string_id"
      :current_global_instance="annotation_ui_context.current_global_instance"
      :instance_list="current_instance_list"
      @toggle_instance_focus="handle_focus_image_instance"
      @close_instance_history_panel="annotation_ui_context.selected_instance_for_history= undefined"
      @focus_instance_show_all="handle_focus_instance_show_all"
      @update_canvas="handle_update_canvas"
      @instance_update="handle_instance_update"
      @clear_selected_instances_image="handle_clear_selected_instances_image"
      @open_view_edit_panel="handle_open_view_edit_panel"
      ref="sidebar_factory"
    />

    <div 
      :class="{'ma-auto': interface_type === 'compound' && annotation_ui_context.working_file_list.length === 0 && !initializing}"
      id="annotation_ui_factory" 
      tabindex="0"
    >
      <annotation_area_factory
        v-if="annotation_ui_context && annotation_ui_context.working_file"
        ref="annotation_area_factory"
        :interface_type="interface_type"
        :annotation_ui_context="annotation_ui_context"
        :working_file="annotation_ui_context.working_file"
        :credentials_granted="credentials_granted"
        :initializing="initializing"
        :save_loading_image="save_loading_image"
        :url_instance_buffer="get_url_instance_buffer()"
        :submitted_to_review="submitted_to_review"
        :annotations_loading="annotation_ui_context.image_annotation_ctx.annotations_loading"
        :loading="annotation_ui_context.image_annotation_ctx.loading"
        :filtered_instance_type_list_function="filtered_instance_type_list"
        :instance_type_list="instance_type_list"
        :get_userscript="get_userscript"
        :save_loading_frames_list="save_loading_frames_list"
        :has_changed="has_changed"
        :instance_buffer_metadata="annotation_ui_context.image_annotation_ctx.instance_buffer_metadata"
        :create_instance_template_url="create_instance_template_url"
        :video_parent_file_instance_list="video_parent_file_instance_list"
        :has_pending_frames="has_pending_frames"
        :instance_store="annotation_ui_context.instance_store"
        :project_string_id="computed_project_string_id"
        :label_schema="annotation_ui_context.label_schema"
        :model_run_id_list="model_run_id_list"
        :model_run_color_list="model_run_color_list"
        :task="annotation_ui_context.task"
        :file="annotation_ui_context.working_file"
        :task_id_prop="task_id_prop"
        :request_save="request_save"
        :job_id="job_id"
        :view_only_mode="view_only"
        :label_list="label_list"
        :label_file_colour_map="label_file_colour_map"
        :enabled_edit_schema="enabled_edit_schema"
        :finish_annotation_show="show_snackbar"
        :global_attribute_groups_list="annotation_ui_context.global_attribute_groups_list"
        :per_instance_attribute_groups_list="annotation_ui_context.per_instance_attribute_groups_list"
        :task_image="task_image"
        :task_instances="task_instances"
        :task_loading="task_loading"
        :changing_file="changing_file"
        :changing_task="changing_task"
        :task_error="task_error"
        :error="error"
        :issues_ui_manager="annotation_ui_context.issues_ui_manager"
        :draw_mode="annotation_ui_context.image_annotation_ctx.draw_mode"
        :instance_type="annotation_ui_context.instance_type"
        @request_file_change="request_file_change"
        @change_label_schema="on_change_label_schema"
        @set_file_list="set_file_list"
        @request_new_task="change_task"
        @replace_file="annotation_ui_context.working_file = $event"
        @get_userscript="get_userscript"
        @save_time_tracking="save_time_tracking"
        @trigger_task_change="trigger_task_change"
        @set_ui_schema="set_ui_schema"
        @set_save_loading="set_save_loading"
        @save="save"
        @set_frame_pending_save="set_frame_pending_save"
        @task_update="task_update"
        @set_has_changed="set_has_changed"
        @on_task_annotation_complete_and_save="on_task_annotation_complete_and_save"
        @model_run_list_loaded="annotation_ui_context.model_run_list = $event"
        @draw_mode_change="on_draw_mode_changed"
        @change_video_playing="annotation_ui_context.image_annotation_ctx.video_playing = $event"
        @change_current_label_file="annotation_ui_context.current_label_file = $event"
        @request_change_current_instance="annotation_ui_context.image_annotation_ctx.request_change_current_instance = $event"
        @trigger_refresh_current_instance="annotation_ui_context.image_annotation_ctx.trigger_refresh_current_instance = $event"
        @selected_instance_for_history="annotation_ui_context.selected_instance_for_history = $event"
        @event_create_instance="annotation_ui_context.image_annotation_ctx.event_create_instance = $event"
        @refresh="annotation_ui_context.image_annotation_ctx.refresh = $event"
        @open_issue_panel="handle_open_issue_panel"
        @instance_list_updated="update_current_instance_list"
        @instance_buffer_dict_updated="update_current_frame_buffer_dict"
        @save_multiple_frames="save_multiple_frames"
      />

      <file_manager_sheet
        v-if="!annotation_ui_context.task && context === 'file'"
        v-show="!loading_project && !initializing"
        :show_sheet="!loading_project"
        ref="file_manager_sheet"
        :request_media_on_mount="false"
        :project_string_id="computed_project_string_id"
        :task="annotation_ui_context.task"
        :context="context"
        :view_only="view_only"
        :enabled_edit_schema="enabled_edit_schema"
        :show_explorer_full_screen="show_explorer_full_screen"
        :file_id_prop="file_id_prop"
        :initializing="initializing"
        :job_id="job_id"
        @change_file="change_file"
      >
      </file_manager_sheet>
    </div>
    <v-dialog
      v-model="dialog"
      max-width="290"
    >
      <v-card>
        <v-card-title class="text-h5">
          This is the last task!
        </v-card-title>

        <v-card-text>
          <p>
            You've finished your work! Please go to the previous task or go back to the task list.
          </p>
          <p class="text-center">
            <v-icon size="96" color="success">mdi-check</v-icon>
          </p>
        </v-card-text>

        <v-card-actions>
          <v-spacer></v-spacer>

          <v-btn
            color="error darken-1"
            text
            @click="dialog = false"
          >
            Close
          </v-btn>

          <v-btn
            color="secondary darken-1"
            text
            @click="$router.push(`/job/${annotation_ui_context.task.job.id}/`)"
          >
            Task List
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
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
    <no_credentials_dialog ref="no_credentials_dialog"
                           :missing_credentials="missing_credentials"></no_credentials_dialog>
    <v-snackbar
      v-model="snackbar_success"
      v-if="snackbar_success"
      top
      :timeout="2000"
      color="success"
    >
      {{ snackbar_success_text }}
    </v-snackbar>
    <v-snackbar timeout="5000" v-model="submitted_to_review">
      Task has been submitted to review
    </v-snackbar>
  </div>
</template>


<script lang="ts">
import Vue from "vue";
import moment from "moment";
import axios from "../../services/customInstance/index.js";
import {create_event} from "../event/create_event";
import {UI_SCHEMA_TASK_MOCK} from "../ui_schema/ui_schema_task_mock.js";
import no_credentials_dialog from '../task/job/no_credentials_dialog.vue';
import file_manager_sheet from "../source_control/file_manager_sheet.vue";
import {user_has_credentials} from '../../services/userServices.js'
import {Task} from "../../types/Task";
import {get_labels, get_schemas} from '../../services/labelServices.js';
import {trackTimeTask, finishTaskAnnotation} from "../../services/tasksServices.js";
import {CommandManagerAnnotationCore} from "./image_and_video_annotation/annotation_core_command_manager";

import annotation_area_factory from "./annotation_area_factory.vue"
import toolbar_factory from "./toolbar_factory.vue"
import sidebar_factory from "./sidebar_factory.vue";

import {duplicate_instance} from "../../utils/instance_utils";
import TaskPrefetcher from "../../helpers/task/TaskPrefetcher"
import IssuesAnnotationUIManager from "./issues/IssuesAnnotationUIManager"
import InstanceStore from "../../helpers/InstanceStore"
import * as AnnotationSavePrechecks from '../annotation/image_and_video_annotation/utils/AnnotationSavePrechecks'
import {BaseAnnotationUIContext} from '../../types/AnnotationUIContext'

import {saveTaskAnnotations, saveFileAnnotations} from "../../services/saveServices"
import {createDefaultLabelSettings} from "../../types/image_label_settings";
import {get_child_files} from "../../services/fileServices";

export default Vue.extend({
  name: "annotation_ui_factory",
  components: {
    file_manager_sheet,
    no_credentials_dialog,
    sidebar_factory,
    annotation_area_factory,
    toolbar_factory
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
      task_error: {
        task_request: null,
      },
      annotation_ui_context: {
        working_file: null,
        command_manager: null,
        task: null,
        instance_type: 'box',
        instance_store: null,
        per_instance_attribute_groups_list: [],
        global_attribute_groups_list: [],
        current_global_instance: undefined,
        label_schema: null,
        current_label_file: null,
        selected_instance_for_history: undefined,
        model_run_list: null,
        issues_ui_manager: null,
        image_annotation_ctx: {
          show_context_menu: false,
          loading: false,
          refresh: new Date(),
          video_mode: false,
          draw_mode: true,
          current_frame: 0,
          video_playing: false,
          request_change_current_instance: null,
          trigger_refresh_current_instance: new Date(),
          event_create_instance: null,
          get_userscript: this.get_userscript,
          label_settings: createDefaultLabelSettings(),
          instance_buffer_metadata: {},
          annotations_loading: false,
        },

      } as BaseAnnotationUIContext,
      annotation_ui_context: new BaseAnnotationUIContext(),
      task_prefetcher: null,
      task_image: null,
      task_instances: null,
      task_loading: false,
      issues_expansion_panel: true,
      show_snackbar: false,
      schema_list_loading: false,
      changing_task: false,
      dialog: false,
      changing_file: false,
      enabled_edit_schema: false,
      user_has_credentials: false,

      credentials_granted: true,
      initializing: true,
      snackbar_message: "",
      loading: true,
      loading_project: true,
      show_default_navigation: true,

      context: null,
      error: null,
      request_save: false,
      model_run_id_list: [],

      missing_credentials: [],
      label_schema_list: [],


      view_only: false,

      labels_list_from_project: null,
      model_run_color_list: null,
      label_file_colour_map_from_project: null,
      save_loading_image: false,
      submitted_to_review: false,
      has_changed: false,
      save_loading_frames_list: [],
      video_parent_file_instance_list: [],
      unsaved_frames: [],
      snackbar_success: false,
      snackbar_success_text: null,
      current_instance_list: [],
      current_instance_buffer_dict: {},
      instance_type_list: [
        {name: "box", display_name: "Box", icon: "mdi-checkbox-blank"},
        {name: "polygon", display_name: "Polygon", icon: "mdi-vector-polygon"},
        {name: "point", display_name: "Point", icon: "mdi-circle-slice-8"},
        {name: "line", display_name: "Fixed Line", icon: "mdi-minus"},
        {name: "cuboid", display_name: "Cuboid 2D", icon: "mdi-cube-outline"},
        {name: "ellipse", display_name: "Ellipse & Circle", icon: "mdi-ellipse-outline"},
        {name: "curve", display_name: "Curve Quadratic", icon: "mdi-chart-bell-curve-cumulative"},
      ],
    }
  },
  watch: {
    'annotation_ui_context.working_file': function() {
      this.annotation_ui_context.command_manager = new CommandManagerAnnotationCore()
    },
    '$route'(to, from) {
      if (from.name === 'task_annotation' && to.name === 'studio') {
        this.fetch_project_file_list();
        this.annotation_ui_context.task = null;
        if (this.$refs.file_manager_sheet) {
          this.$refs.file_manager_sheet.display_file_manager_sheet();
        }
      }
      if (from.name === 'studio' && to.name === 'task_annotation') {
        this.working_file = null;
        this.fetch_single_task(this.$props.task_id_prop);
        this.$refs.file_manager_sheet.hide_file_manager_sheet()
      }
      this.get_model_runs_from_query(to.query);
    },
    working_file: {
      handler(newVal, oldVal) {
        if (newVal && newVal != oldVal) {
          Vue.set(this.annotation_ui_context, 'instance_store', new InstanceStore())
          this.$addQueriesToLocation({file: newVal.id});
        }
      },
    },
    'annotation_ui_context.task'(newVal) {
      this.update_working_file(newVal.file)
      if (newVal && this.task_prefetcher && newVal.file.type === 'image') {
        Vue.set(this.annotation_ui_context, 'instance_store', new InstanceStore())
        this.task_prefetcher.update_tasks(newVal)
      }
    }
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
    this.context = 'file'
    if (
      !this.$store.getters.is_on_public_project ||
      this.$store.state.user.current.is_super_admin == true
    ) {
      if (this.$props.task_id_prop) {
        this.context = 'task'
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
    this.annotation_ui_context.get_userscript = this.get_userscript
    Vue.set(this.annotation_ui_context, 'instance_store', new InstanceStore())
    this.annotation_ui_context.issues_ui_manager = new IssuesAnnotationUIManager()
    if (!this.$props.task_id_prop) {
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
      this.annotation_ui_context.task = {
        ...UI_SCHEMA_TASK_MOCK,
      } as Task;
      this.annotation_ui_context.label_schema = this.annotation_ui_context.task.job.label_schema;
      if (this.$refs.file_manager_sheet) {
        this.$refs.file_manager_sheet.set_file_list([this.annotation_ui_context.task.file]);
        this.$refs.file_manager_sheet.hide_file_manager_sheet();
      }

    } else {
      if (this.$props.task_id_prop) {
        this.changing_task = true
        await this.fetch_single_task(this.$props.task_id_prop);
        await this.check_credentials();
        await this.$nextTick()
        this.credentials_granted = this.has_credentials_or_admin();
        if (!this.credentials_granted) {
          this.show_missing_credentials_dialog();
        }
        this.changing_task = false
      } else if (this.$props.file_id_prop) {
        await this.fetch_schema_list()
        await this.fetch_single_file();
      } else {
        await this.fetch_schema_list()
        await this.fetch_project_file_list();
      }
      await this.get_labels_from_project();
    }

    if (this.annotation_ui_context.task && this.annotation_ui_context.task.file.type === 'image') {
      this.task_prefetcher = new TaskPrefetcher(this.computed_project_string_id)
      this.task_prefetcher.update_tasks(this.annotation_ui_context.task)
    }

    this.initializing = false
  },
  computed: {
    interface_type: function(): string | null {
      if (!this.annotation_ui_context.working_file && !this.annotation_ui_context.task) return

      if (this.annotation_ui_context.working_file)
        return this.annotation_ui_context.working_file.type

      if (this.task && this.task.file)
        return this.task.file
    },
    current_frame: function () {
      // let current_interface = this.get_current_annotation_area_ref()
      // if(current_interface){
      //   return current_interface.current_frame
      // }
      return this.annotation_ui_context.image_annotation_ctx.current_frame

    },
    has_pending_frames: function () {
      return this.unsaved_frames.length > 0
    },
    save_request: function (): Function {
      if (this.annotation_ui_context.task) return (payload) => saveTaskAnnotations(this.annotation_ui_context.task.id, payload)

      return (payload) => saveFileAnnotations(this.project_string_id, this.annotation_ui_context.working_file.id, payload)
    },
    create_instance_template_url: function (): string {
      if (this.annotation_ui_context.task && this.annotation_ui_context.task.id) return `/api/v1/task/${this.annotation_ui_context.task.id}/instance-template/new`
      else return `/api/v1/project/${this.computed_project_string_id}/instance-template/new`
    },
    any_loading: function () {
      return this.loading || this.loading_project || this.initializing
    },
    file_id: function () {
      let file_id = this.$props.file_id_prop;
      if (this.$route.query.file) {
        file_id = this.$route.query.file;
      }
      return file_id;
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
      if (this.annotation_ui_context.task && this.annotation_ui_context.task.label_file_colour_map) {
        return this.annotation_ui_context.task.label_dict.label_file_colour_map;
      }
      if (this.label_file_colour_map_from_project) {
        return this.label_file_colour_map_from_project;
      }
      return {};
    },

    label_list: function () {
      if (this.annotation_ui_context.task && this.annotation_ui_context.task.label_list) {
        return this.annotation_ui_context.task.label_dict.label_file_list_serialized;
      }
      if (this.labels_list_from_project) {
        return this.labels_list_from_project;
      }
      return [];
    },
  },
  methods: {
    redo: function () {
      if (!this.command_manager) return
      const redone = this.command_manager.redo()
      if (redone) this.set_has_changed(true)
      this.update_canvas();
    },
    undo: function () {
      if (!this.command_manager) return
      const undone = this.command_manager.undo()
      if (undone) this.set_has_changed(true)
      this.update_canvas();
    },
    rotate_image: function(event) {
      this.$refs.annotation_area_factory.$refs.annotation_core.on_image_rotation(event)
    },
    update_smooth_canvas: function (event) {
      this.$refs.annotation_area_factory.$refs.annotation_core.update_smooth_canvas(event)
    },
    change_instance_type: function(instance_type: string): void {
      this.$store.commit("finish_draw");
      this.$store.commit("set_last_selected_tool", this.instance_type);
      this.annotation_ui_context.instance_type = instance_type
    },
    change_current_label_file_template: function (label_file) {
      this.annotation_ui_context.current_label_file = label_file;
      this.$emit('change_current_label_file', this.annotation_ui_context.current_label_file)
    },
    handle_open_issue_panel: function(mouse_position){
      if(!this.$refs.sidebar_factory){
        return
      }
      let sidebar = this.$refs.sidebar_factory.get_current_sidebar_ref()
      if(sidebar){
        sidebar.open_issue_panel(mouse_position)
      }
    },
    update_current_instance_list: function (instance_list, file_id, file_type) {
      this.current_instance_list = this.annotation_ui_context.instance_store.get_instance_list(file_id)
    },
    update_current_frame_buffer_dict: function (instance_buffer_dict, file_id, file_type) {
      this.current_instance_buffer_dict = this.annotation_ui_context.instance_store.get_instance_list(file_id)
      let ins_list = this.current_instance_buffer_dict[this.annotation_ui_context.image_annotation_ctx.current_frame]
      this.current_instance_list = ins_list ? ins_list : []
    },
    on_draw_mode_changed: function (draw_mode: boolean = undefined): void {
      if (draw_mode !== undefined) {
        this.annotation_ui_context.image_annotation_ctx.draw_mode = draw_mode
      } else {
        this.annotation_ui_context.image_annotation_ctx.draw_mode = !this.annotation_ui_context.image_annotation_ctx.draw_mode
      }
    },
    handle_open_view_edit_panel: function (issue) {
      if (this.interface_type != 'image' && this.interface_type != 'video') {
        return
      }
      let current_interface = this.get_current_annotation_area_ref()
      if (current_interface) {
        current_interface.open_view_edit_panel(issue)
      }
    },
    handle_clear_selected_instances_image: function () {
      if (this.interface_type != 'image' && this.interface_type != 'video') {
        return
      }
      let current_interface = this.get_current_annotation_area_ref()
      if (current_interface) {
        current_interface.clear_selected()
      }
    },
    handle_instance_update: function (update_data) {
      if (this.interface_type != 'image' && this.interface_type != 'video') {
        return
      }
      let current_interface = this.get_current_annotation_area_ref()
      if (current_interface) {
        current_interface.instance_update(update_data)
      }
    },
    handle_update_canvas: function () {
      if (this.interface_type != 'image' && this.interface_type != 'video') {
        return
      }
      let current_interface = this.get_current_annotation_area_ref()
      if (current_interface) {
        current_interface.update_canvas()
      }
    },
    handle_focus_instance_show_all: function () {
      if (this.interface_type != 'image' && this.interface_type != 'video') {
        return
      }
      let current_interface = this.get_current_annotation_area_ref()
      if (current_interface) {
        current_interface.focus_instance_show_all()
      }

    },
    handle_focus_image_instance: function (focus) {
      if (this.interface_type != 'image' && this.interface_type != 'video') {
        return
      }
      let current_interface = this.get_current_annotation_area_ref()
      if (current_interface) {
        current_interface.focus_instance(focus)
      }

    },
    set_has_changed: function (value) {
      this.has_changed = value
    },
    get_current_annotation_area_ref(file_id, file_type){
      // For now just return computed prop. More complex logic might need to be added with file_id once compound file exists.
      return this.$refs.annotation_area_factory.current_interface_ref
    },
    save_multiple_frames: async function (frames_list) {
      try {

        this.annotation_ui_context.image_annotation_ctx.save_multiple_frames_error = {};
        for (let frame_number of frames_list){
          let inst_list = this.annotation_ui_context.instance_store.get_instance_list(
            this.annotation_ui_context.working_file.id,
            frame_number
          )

          await this.save(false, frame_number, inst_list)
        }
        return true

      } catch (err) {
        this.annotation_ui_context.image_annotation_ctx.save_multiple_frames_error = this.$route_api_errors(err);
        console.error(err);
      }
    },
    save: async function (
      and_complete = false,
      frame_number_param = undefined,
      instance_list_param = undefined
    ) {
      this.save_error = {}
      this.save_warning = {}
      if (this.annotation_ui_context.image_annotation_ctx.go_to_keyframe_loading) return
      if (this.view_only_mode) return

      let frame_number;
      let instance_list;
      if (this.annotation_ui_context.image_annotation_ctx.video_mode) {
        if (!frame_number_param) {
          frame_number = parseInt(this.current_frame, 10);
        }
        else frame_number = parseInt(frame_number_param, 10);

        if (instance_list_param) instance_list = instance_list_param;
        else instance_list = this.annotation_ui_context.instance_store.get_instance_list(this.annotation_ui_context.working_file.id, frame_number)
      } else {
        instance_list = this.annotation_ui_context.instance_store.get_instance_list(this.annotation_ui_context.working_file.id).map(elm => {
          if (elm.type === 'keypoints') return elm.get_instance_data()
          else return elm
        });
      }

      if (this.get_save_loading(frame_number)) return
      if (this.any_loading) return
      if (
        this.annotation_ui_context.image_annotation_ctx.video_mode &&
        (
          !this.annotation_ui_context.instance_store.get_instance_list(this.annotation_ui_context.working_file.id, frame_number) ||
          this.annotation_ui_context.image_annotation_ctx.annotations_loading
        )
      ) return
      this.set_save_loading(true, frame_number);
      let [has_duplicate_instances, dup_ids, dup_indexes] =
        AnnotationSavePrechecks.has_duplicate_instances(instance_list);
      let dup_instance_list = dup_indexes.map((i) => ({
        ...instance_list[i],
        original_index: i,
      }));

      dup_instance_list.sort(function (a, b) {
        return (
          moment(b.client_created_time, "YYYY-MM-DD HH:mm") -
          moment(a.client_created_time, "YYYY-MM-DD HH:mm")
        );
      });

      if (has_duplicate_instances) {
        this.save_warning = {
          duplicate_instances: `Instance list has duplicates: ${dup_ids}. Please move the instance before saving.`,
        };
        // We want to focus the most recent instance, if we focus the older one we can produce an error.
        this.get_current_annotation_area_ref().$refs.instance_detail_list.toggle_instance_focus(
          dup_instance_list[0].original_index,
          undefined
        );

        this.set_save_loading(false, frame_number);

        return
      }

      let video_data = null;

      if (this.annotation_ui_context.image_annotation_ctx.video_mode) {
        video_data = {
          video_mode: this.annotation_ui_context.image_annotation_ctx.video_mode,
          video_file_id: this.annotation_ui_context.working_file.id,
          current_frame: frame_number,
          set_parent_instance_list: false
        };
      }

      const payload = {
        instance_list,
        and_complete,
        directory_id: this.$store.state.project.current_directory.directory_id,
        gold_standard_file: this.gold_standard_file,
        video_data,
      }

      const [result, error] = await this.save_request(payload)

      if (result) {
        if (this.annotation_ui_context.image_annotation_ctx.video_mode && this.video_parent_file_instance_list.length > 0 && this.video_global_attribute_changed) {
          video_data.set_parent_instance_list = true

          const video_payload = {...payload, instance_list: this.video_parent_file_instance_list}
          const [parent_result, parent_error] = await this.save_request(video_payload);

          if (parent_result) {
            this.video_global_attribute_changed = false;
          }
        }

        this.save_loading_image = false
        this.has_changed = false
        this.save_count += 1;

        AnnotationSavePrechecks.add_ids_to_new_instances_and_delete_old(
          result,
          video_data,
          instance_list,
          this.annotation_ui_context.instance_store.get_instance_list(this.annotation_ui_context.working_file.id),
          this.annotation_ui_context.image_annotation_ctx.video_mode
        )

        this.has_changed = AnnotationSavePrechecks.check_if_pending_created_instance(instance_list)

        // Update Sequence ID's and Keyframes.
        if ((result.data.sequence || result.data.new_sequence_list) && this.annotation_ui_context.image_annotation_ctx.video_mode) {
          this.get_current_annotation_area_ref().update_sequence_data(instance_list, frame_number, result);
        }

        this.set_save_loading(false, frame_number);
        this.set_frame_pending_save(false, frame_number)
        this.has_changed = false;
        if (and_complete == true) {
          // now that complete completes whole video, we can move to next as expected.
          this.snackbar_success = true;
          this.snackbar_success_text = "Saved and completed. Moved to next.";

          if (this.annotation_ui_context.task && this.annotation_ui_context.task.id) {
            this.trigger_task_change("next", this.annotation_ui_context.task, true);
          } else {
            this.trigger_task_change("next", "none", true); // important
          }
        }
        this.has_changed = AnnotationSavePrechecks.check_if_pending_created_instance(instance_list)

        if (this.annotation_ui_context.image_annotation_ctx.video_mode) {
          const pending_frames = this.get_pending_save_frames();
          if (pending_frames.length > 0) {
            await this.save_multiple_frames(pending_frames)
          }
        }

        this.ghost_refresh_instances();

        if (this.annotation_ui_context.task) this.save_time_tracking()

        return true;
      }

      if (error) {
        this.set_save_loading(false, frame_number);
        if (
          error.response &&
          error.response.data &&
          error.response.data.log &&
          error.response.data.log.error &&
          error.response.data.log.error.missing_ids
        ) {
          this.display_refresh_cache_button = true;
          clearInterval(this.interval_autosave);
        }
        this.save_error = this.$route_api_errors(error);

        return false;
      }
    },
    task_update: function (mode) {
      /*
       *
       *
       *  Hijacks save_error for now so we trigger other loading stuff?
       *
       */

      this.save_error = {};

      let current_frame = undefined;
      if (this.annotation_ui_context.image_annotation_ctx.video_mode) {
        current_frame = parseInt(this.current_frame, 10);
      }

      this.set_save_loading(true, current_frame)

      axios
        .post("/api/v1/task/update", {
          task_id: this.annotation_ui_context.task.id,
          mode: mode,
        })
        .then((response) => {
          this.set_save_loading(false, current_frame);
          if (mode == "toggle_deferred") {
            this.snackbar_success = true;
            this.snackbar_success_text = "Deferred for review. Moved to next.";

            this.trigger_task_change("next", this.annotation_ui_context.task, true);
          }
          if (mode === 'incomplete') {
            this.annotation_ui_context.task.status = 'in_progress'
            this.$store.commit('display_snackbar', {
              text: 'Task marked as incomplete.',
              color: 'primary'
            })
          }
        })
        .catch((error) => {
          this.set_save_loading(false, current_frame);
          if (error.response.status == 400) {
            this.save_error = error.response.data.log.error;
          }
        });
    },
    ghost_refresh_instances: function () {
      this.ghost_instance_list = [];
      if (!this.sequence_list_local_copy) return

      let keyframes_to_sequences = this.build_keyframes_to_sequences_dict();
      this.populate_ghost_list_with_most_recent_instances_from_keyframes(
        keyframes_to_sequences
      );

      // this.may_fire_user_ghost_canvas_available_alert();
    },
    populate_ghost_list_with_most_recent_instances_from_keyframes: function (
      keyframes_to_sequences
    ) {
      if (!keyframes_to_sequences) return

      for (const [keyframe, sequence_numbers] of Object.entries(
        keyframes_to_sequences
      )) {
        let instance_list = this.annotation_ui_context.instance_store.get_instance_list(this.annotation_ui_context.working_file.id, keyframe);
        if (!instance_list) {
          continue;
        }

        for (let instance of instance_list) {
          if (sequence_numbers.includes(instance.number)) {
            // if it's the last object then we don't show ghost
            if (instance.pause_object == true) {
              continue;
            }

            if (
              this.ghost_determine_if_no_conflicts_with_existing(instance) ==
              false
            ) {
              continue;
            }

            this.duplicate_instance_into_ghost_list(instance);
          }
        }
      }
    },
    ghost_determine_if_no_conflicts_with_existing: function (ghost_instance) {
      if (this.instance_list == undefined) {
        return
      }
      for (let existing_instance of this.instance_list) {
        if (existing_instance.sequence_id == ghost_instance.sequence_id) {
          return false;
        }
        if (
          existing_instance.label_file_id == ghost_instance.label_file_id &&
          existing_instance.number == ghost_instance.number
        ) {
          return false;
        }
      }
      return true;
    },
    duplicate_instance_into_ghost_list: function (instance) {
      if (!instance) {
        return;
      }
      let instance_clipboard = duplicate_instance(instance, this);
      instance_clipboard.id = null;
      instance_clipboard.created_time = null; //
      instance_clipboard.creation_ref_id = null; // we expect this will be set once user accepts it
      this.ghost_instance_list.push(instance_clipboard);
    },
    build_keyframes_to_sequences_dict: function () {
      /*
       * build dict of keyframes with sequences
       * context that searching each instance_list might as well do all at once.
       * returns example like
       * frame: [list of sequence ids]
       * 351: [3619]
         355: [3620, 3621]
       *
       */
      let keyframes_to_sequences = {};
      for (let sequence of this.sequence_list_local_copy) {
        if (!sequence.keyframe_list) {
          continue;
        }
        if (!sequence.keyframe_list.frame_number_list) {
          continue;
        }

        let frame_number_list = sequence.keyframe_list.frame_number_list;
        let last_keyframe = frame_number_list[frame_number_list.length - 1];
        if (last_keyframe == undefined) {
          continue;
        } // careful, 0th frame is ok

        if (!keyframes_to_sequences[last_keyframe]) {
          keyframes_to_sequences[last_keyframe] = [sequence.number];
        } else {
          keyframes_to_sequences[last_keyframe].push(sequence.number);
        }
      }
      return keyframes_to_sequences;
    },
    get_pending_save_frames: function () {
      let result = [];
      for (let frame_num of Object.keys(this.annotation_ui_context.image_annotation_ctx.instance_buffer_metadata)) {
        let frame_metadata = this.annotation_ui_context.image_annotation_ctx.instance_buffer_metadata[frame_num]
        if (frame_metadata.pending_save) {
          result.push(parseInt(frame_num, 10))
        }
      }
      return result;
    },
    set_frame_pending_save: function (value, frame_number) {
      if (!frame_number) return

      if (this.annotation_ui_context.image_annotation_ctx.instance_buffer_metadata[frame_number]) {
        // We need to recreate object so that computed props get triggered
        this.annotation_ui_context.image_annotation_ctx.instance_buffer_metadata[frame_number].pending_save = value;
      } else {
        this.annotation_ui_context.image_annotation_ctx.instance_buffer_metadata[frame_number] = {
          pending_save: value
        }
      }
      // Keep unsaved_frames list to enable/disable save button
      if (value) {
        this.unsaved_frames.push(frame_number)
      } else {
        this.unsaved_frames = this.unsaved_frames.filter(elm => elm != frame_number)
      }

    },
    get_save_loading: function (frame_number: number) {
      if (this.annotation_ui_context.image_annotation_ctx.video_mode) return this.save_loading_frames_list.includes(frame_number)
      else return this.save_loading_image
    },
    set_save_loading: function (value, frame) {
      if (this.annotation_ui_context.image_annotation_ctx.video_mode) {
        if (value) {
          this.save_loading_frames_list.push(frame)
        } else {
          this.save_loading_frames_list = this.save_loading_frames_list.filter(elm => elm != frame)
        }

      } else {
        this.save_loading_image = value;
      }

      this.$forceUpdate();
    },
    filtered_instance_type_list: function (instance_type_list) {
      const schema_allowed_types = (): string[] | null => {
        if (
          !this.annotation_ui_context.task ||
          !this.annotation_ui_context.task.job ||
          !this.annotation_ui_context.task.job.ui_schema ||
          !this.annotation_ui_context.task.job.ui_schema.instance_selector
        ) return null


        const allowed_types = this.annotation_ui_context.task.job.ui_schema.instance_selector.allowed_instance_types.map(elm => elm.name)

        if (allowed_types.length === 0) return null

        return null
      }

      let allowed_types = schema_allowed_types() as Array<string>
      allowed_types = allowed_types as Array<string>

      if (!allowed_types) return instance_type_list

      return instance_type_list.filter((elm) => allowed_types.includes(elm.name))
    },
    set_ui_schema() {
      if (
        this.annotation_ui_context.task &&
        this.annotation_ui_context.task.job &&
        this.annotation_ui_context.task.job.ui_schema
      ) {
        this.$store.commit("set_ui_schema", this.annotation_ui_context.task.job.ui_schema);
      } else {
        this.$store.commit("clear_ui_schema");
      }
    },
    trigger_task_change: async function (
      direction,
      task,
      assign_to_user = false
    ) {
      if (
        this.loading === true ||
        this.annotation_ui_context.image_annotation_ctx.annotations_loading === true
      ) return


      if (this.has_changed) await this.save();

      this.change_task(direction, task, assign_to_user);
    },

    on_task_annotation_complete_and_save: async function () {
      await this.save(true);
      const response = await finishTaskAnnotation(this.annotation_ui_context.task.id);

      const new_status = response.data.annotation_ui_context.task.status;
      this.annotation_ui_context.task.status = new_status;

      if (new_status !== "complete") this.submitted_to_review = true;

      if (this.annotation_ui_context.task && this.annotation_ui_context.task.id) {
        this.save_loading_image = false;
        this.trigger_task_change("next", this.annotation_ui_context.task, true);
      }
    },
    save_time_tracking: async function () {
      if (!this.annotation_ui_context.task) return

      const current_user_id = this.$store.state.user.current.id;
      const record = this.annotation_ui_context.task.time_tracking.find(elm => elm.user_id === current_user_id)
      const [result, error] = await trackTimeTask(
        record.time_spent,
        this.annotation_ui_context.task.id,
        this.annotation_ui_context.task.status,
        this.annotation_ui_context.task.job.id,
        this.annotation_ui_context.working_file.id,
        null
      )

      if (error) {
        this.error = this.$route_api_errors(error);
      }

      if (result) {
        record.id = result.id;
        record.task_id = result.task_id;
        record.job_id = result.job_id;
      }
    },
    get_userscript: function (userscript_ref) {
      if (this.job && this.job.default_userscript) {
        return this.job.default_userscript;
      }
      if (this.annotation_ui_context.task && this.annotation_ui_context.task.default_userscript) {
        return this.annotation_ui_context.task.default_userscript;
      }
      if (userscript_ref && userscript_ref.userscript_literal) {
        return userscript_ref.userscript_literal;
      }
      return undefined;
    },
    get_url_instance_buffer: function () {
      if (this.annotation_ui_context.task && this.annotation_ui_context.task.id) return `/api/v1/task/${this.annotation_ui_context.task.id}/video/file_from_task`

      return `/api/project/${this.project_string_id}/video/${this.annotation_ui_context.working_file.id}`
    },
    set_working_file_from_child_file_list: function(file_to_set){
      for(let file of this.annotation_ui_context.working_file_list){
        if(file.id === file_to_set.id){
          this.annotation_ui_context.working_file = file
        }
      }
    },
    update_working_file: async function  (file) {
      this.annotation_ui_context.working_file = file
      this.annotation_ui_context.image_annotation_ctx.video_mode = file && file.type === 'video'
      if(file.type === 'compound'){
        let [child_files, err] = await get_child_files(this.project_string_id, file.id)
        if (err) {
          console.error(err)
          return
        }
        this.annotation_ui_context.working_file_list = child_files
        this.set_working_file_from_child_file_list(child_files[0])
      }
    },

    on_change_label_schema: function (schema) {
      if (schema.id === this.annotation_ui_context.label_schema.id) {
        return
      }
      this.annotation_ui_context.label_schema = schema;
      this.labels_list_from_project = null;
      this.get_labels_from_project()
    },
    fetch_schema_list: async function () {
      this.schema_list_loading = true
      let [result, error] = await get_schemas(this.project_string_id);
      if (error) {
        this.error = this.$route_api_errors(error);
        this.schema_list_loading = false;
      }
      if (result) {
        this.label_schema_list = result;
        this.annotation_ui_context.label_schema = this.label_schema_list[0];
      }
      this.schema_list_loading = false;
    },
    show_missing_credentials_dialog: function () {
      if (this.$refs.no_credentials_dialog) {
        this.$refs.no_credentials_dialog.open()
      }
    },
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
    check_credentials: async function () {
      let project_string_id = this.$store.state.project.current.project_string_id;
      let user_id = this.$store.state.user.current.id;
      let [result, error] = await user_has_credentials(
        project_string_id,
        user_id,
        this.annotation_ui_context.task.job.id,
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

    change_file: async function (file, model_runs, color_list) {
      this.changing_file = true
      this.update_working_file(file)
      await this.$nextTick();
      let model_runs_data = "";
      if (model_runs) {
        model_runs_data = encodeURIComponent(model_runs);
      }
      this.get_model_runs_from_query(model_runs_data);
      this.changing_file = false;
    },

    get_labels_from_project: async function () {
      if (this.labels_list_from_project &&
        this.computed_project_string_id == this.$store.state.project.current.project_string_id) {
        return
      }
      if (!this.computed_project_string_id) {
        return
      }
      if (!this.annotation_ui_context.label_schema) {
        this.error = {
          label_schema: 'Please set the current label schema'
        }
        return
      }
      let [result, error] = await get_labels(this.computed_project_string_id, this.annotation_ui_context.label_schema.id)
      if (error) {
        console.error(error)
        return
      }
      if (result) {

        this.labels_list_from_project = result.labels_out
        this.label_file_colour_map_from_project = result.label_file_colour_map
        this.global_attribute_groups_list = result.global_attribute_groups_list
        this.annotation_ui_context.per_instance_attribute_groups_list = result.attribute_groups
      }


    },

    fetch_project_file_list: async function () {
      this.loading = true;
      if (this.$route.query.file) {
        if (this.$refs.file_manager_sheet) {
          let file = await this.$refs.file_manager_sheet.get_media(
            true,
            this.$route.query.file
          );
          this.update_working_file(file)
        }
      } else {
        if (this.$refs.file_manager_sheet) {
          let file = await this.$refs.file_manager_sheet.get_media();
          this.update_working_file(file)
        }
      }
      this.loading = false;
      if (this.$refs.file_manager_sheet) {
        this.$refs.file_manager_sheet.display_file_manager_sheet();
      }

    },

    fetch_single_file: async function () {
      this.loading = true;

      if (this.$refs.file_manager_sheet) {
        let file = await this.$refs.file_manager_sheet.get_media();
        this.update_working_file(file);
      }

      this.loading = false;
      if (this.$refs.file_manager_sheet) {
        this.$refs.file_manager_sheet.display_file_manager_sheet();
      }
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
          if (this.$refs.file_manager_sheet) {
            this.$refs.file_manager_sheet.set_file_list([
              response.data.task.file,
            ]);
            this.$refs.file_manager_sheet.hide_file_manager_sheet();
          }
          this.annotation_ui_context.task = response.data.annotation_ui_context.task;
          this.annotation_ui_context.label_schema = this.annotation_ui_context.task.job.label_schema;
          await this.get_project(this.annotation_ui_context.task.project_string_id);
        }
        this.task_error = response.data.log.error;
      } catch (error) {
        console.error(error);
        this.error = this.$route_api_errors(error);
        // this.logout()
      }
      this.loading = false;
    },

    change_task: async function (direction, task, assign_to_user = false) {
      // Assumes it does NOT assign the user
      if (!task) {
        throw new Error("Provide task ");
      }

      // This should be refactored, for now this prefecting is only for images
      try {
        let success = true;

        this.task_image = null
        this.task_instances = null

        if (this.annotation_ui_context.task.file.type !== 'image') {
          const response = await axios.post(
            `/api/v1/job/${task.job_id}/next-task`,
            {
              project_string_id: this.computed_project_string_id,
              task_id: task.id,
              direction: direction,
              assign_to_user: assign_to_user,
            }
          );

          if (response.data && response.data.task) {
            if (response.data.task.id !== task.id) {
              this.$router.push(`/task/${response.data.task.id}`);
              history.pushState({}, "", `/task/${response.data.task.id}`);
              this.annotation_ui_context.task = response.data.task;
              this.annotation_ui_context.task_loading = false
            }
          } else {
            success = false
          }
        } else {
          if (this.task_prefetcher.has_next(direction)) {
            this.task_loading = true
            const new_task = await this.task_prefetcher.change_task(direction)
            if (new_task) {
              if (new_task.task && new_task.task.id !== task.id) {
                this.$router.push(`/task/${new_task.task.id}`);
                history.pushState({}, "", `/task/${new_task.task.id}`);
                // Refresh task Data. This will change the props of the annotation_ui and trigger watchers.
                // In the task context we reset the file list on media core to keep only the current task's file.
                if (this.$refs.file_manager_sheet) {
                  this.$refs.file_manager_sheet.set_file_list([this.annotation_ui_context.task.file]);
                }

                this.annotation_ui_context.task = new_task.task;
                this.task_image = new_task.image
                this.task_instances = new_task.instances
                this.task_loading = false
              }
            } else {
              success = false
            }
          } else {
            success = false
          }
        }

        if (!success) {
          if (direction === "next") {
            this.dialog = true;
            this.snackbar_message =
              "This is the last task of the list. Please go to previous tasks.";
          } else {
            this.show_snackbar = true;
            this.snackbar_message =
              "This is the first task of the list. Please go to the next tasks.";
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

        if (!local_project_string_id) {
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
      if (this.$props.task_id_prop === -1 || this.$props.task_id_prop === '-1') {
        return
      }
      const event_data = await create_event(this.computed_project_string_id, {
        file_id: this.$props.file_id_prop,
        task_id: this.$props.task_id_prop,
        page_name: page_name,
        object_type: object_type,
        user_visit: "user_visit",
      });
    },
  },
});
</script>
