<template>

    <div class="d-flex" style="height: 100%; width: 100%; overflow-y: scroll" id="annotation_factory_container">
        <ui_schema_context_menu
              v-if="show_ui_schema_context_menu && annotation_ui_context.label_schema"
              :schema_id="annotation_ui_context.label_schema.id"
              :show_context_menu="show_ui_schema_context_menu"
              :project_string_id="computed_project_string_id"
              :label_settings="annotation_ui_context.current_image_annotation_ctx.label_settings"
              @close_context_menu="show_ui_schema_context_menu = false"
              @start_edit_ui_schema="edit_ui_schema()"
              @set_ui_schema="on_set_ui_schema()"
        >
        </ui_schema_context_menu>
        <toolbar_factory
              v-if="annotation_ui_context.working_file && annotation_ui_context.command_manager"
              :platform="platform"
              :task="annotation_ui_context.task"
              :show_ui_schema_context_menu="show_ui_schema_context_menu"
              :annotation_ui_context="annotation_ui_context"
              :project_string_id="computed_project_string_id"
              :working_file="annotation_ui_context.working_file"
              :command_manager="annotation_ui_context.command_manager"
              :history="annotation_ui_context.history"
              :label_settings="annotation_ui_context.current_image_annotation_ctx.label_settings"
              :label_schema="annotation_ui_context.label_schema"
              :draw_mode="annotation_ui_context.current_image_annotation_ctx.draw_mode"
              :instance_type="annotation_ui_context.instance_type"
              :video_parent_file_instance_list="annotation_ui_context.current_image_annotation_ctx.video_parent_file_instance_list"
              :label_file_colour_map="label_file_colour_map"
              :label_list="label_list"
              :interface_type="interface_type"
              :instance_type_list="instance_type_list"
              :filtered_instance_type_list_function="filtered_instance_type_list"
              :show_default_navigation="show_default_navigation"
              :current_label_file="annotation_ui_context.current_label_file"
              :has_changed="has_changed"
              :save_loading="annotation_ui_context.current_image_annotation_ctx.video_mode ?
        annotation_ui_context.current_image_annotation_ctx.save_loading_frames_list.length > 0 : annotation_ui_context.get_current_ann_ctx() && annotation_ui_context.get_current_ann_ctx().save_loading"
              :annotations_loading="annotation_ui_context.current_image_annotation_ctx.annotations_loading"
              :canvas_scale_local="annotation_ui_context.current_image_annotation_ctx.zoom_value"
              :bulk_mode="annotation_ui_context.get_current_ann_ctx() && annotation_ui_context.get_current_ann_ctx().bulk_mode"
              :search_mode="annotation_ui_context.get_current_ann_ctx() && annotation_ui_context.get_current_ann_ctx().search_mode"
              @save="save"
              @execute_button_actions="execute_button_actions"
              @redo="redo"
              @undo="undo"
              @clear_unsaved="clear_unsaved"
              @rotate_image="rotate_image"
              @change_file="request_file_change"
              @copy_all_instances="copy_all_instances"
              @edit_mode_toggle="on_draw_mode_changed"
              @change_instance_type="change_instance_type"
              @change_label_schema="on_change_label_schema"
              @smooth_canvas_changed="update_smooth_canvas($event)"
              @change_label_file="change_current_label_file_template($event)"
              @update_label_file_visibility="update_label_file_visible($event)"
              @task_update_toggle_incomplete="() => task_update('incomplete')"
              @task_update_toggle_deferred="() => task_update('toggle_deferred')"
              @change_task="(event) => trigger_task_change(event, annotation_ui_context.task, false)"
              @on_task_annotation_complete_and_save="on_task_annotation_complete_and_save"
              @annotation_show="annotation_show($event)"
        />
        <!--  Temporal v-if condition while other sidebars are migrated inside sidebar factory  -->
        <sidebar_factory
              v-if="(interface_type === 'image' || interface_type === 'video' || interface_type === 'text' || interface_type === 'audio') && !task_error.task_request && !changing_file && !changing_task && annotation_ui_context.current_image_annotation_ctx != undefined"
              :annotation_ui_context="annotation_ui_context"
              :interface_type="interface_type"
              :root_file="root_file"
              :label_file_colour_map="label_file_colour_map"
              :label_list="label_list"
              :project_string_id="computed_project_string_id"
              :current_global_instance="annotation_ui_context.current_global_instance"
              :compound_global_instance="annotation_ui_context.compound_global_instance"
              :video_parent_file_instance_list="annotation_ui_context.current_image_annotation_ctx.video_parent_file_instance_list"
              :instance_list="current_instance_list"
              @toggle_instance_focus="handle_focus_image_instance"
              @close_instance_history_panel="annotation_ui_context.selected_instance_for_history= undefined"
              @focus_instance_show_all="handle_focus_instance_show_all"
              @update_canvas="handle_update_canvas"
              @instance_update="handle_instance_update"
              @clear_selected_instances_image="handle_clear_selected_instances_image"
              @open_view_edit_panel="handle_open_view_edit_panel"
              @global_compound_attribute_change="on_global_compound_attribute_change"

              @hover_text_instance="hover_text_instance"
              @stop_hover_text_instance="stop_hover_text_instance"

              @on_delete_instance="delete_instance"
              @on_select_instance="select_instance"
              @on_change_instance_label="change_instance_label"
              @on_update_attribute="update_attribute"

              ref="sidebar_factory"
        />

        <div
              :style="`height: 100%; width: ${annotation_area_container_width}; overflow-y: auto`"
              :class="{'ma-auto': (interface_type === 'compound' && annotation_ui_context.working_file_list.length === 0 && !initializing) || loading || !interface_type,}"

              id="annotation_ui_factory" tabindex="0">
            <v_error_multiple :error="error"/>

            <div v-if="!interface_type && !initializing && loading" class="ma-auto">
                <empty_file_editor_placeholder
                      class="ma-auto"
                      style="width: 800px"
                      :loading="true"
                      :title="'Loading Annotation UI...'"
                />
            </div>
            <div v-if="!interface_type && !initializing && !loading">
                <empty_file_editor_placeholder
                      :message="`File ID: ${annotation_ui_context.working_file ? annotation_ui_context.working_file.id : 'N/A'}. File Type: ${annotation_ui_context.working_file ? annotation_ui_context.working_file.type : 'N/A'}`"
                      :title="'No File Loaded'"
                />
            </div>
            <div
                  v-else-if="interface_type === 'compound' && annotation_ui_context.working_file_list.length === 0 && !initializing && !loading">
                <empty_file_editor_placeholder
                      :message="'Try adding child files to this compound file.'"
                      :title="'This compound file has no child files.'"/>
            </div>
            <div v-else-if="!credentials_granted && !initializing">
                <empty_file_editor_placeholder
                      icon="mdi-account-cancel"
                      :loading="false"
                      :project_string_id="project_string_id"
                      :title="`Invalid credentials`"
                      :message="`You need more credentials to work on this task.`"
                      :show_upload="false"
                />
            </div>

            <panel_manager
                  v-else-if="annotation_ui_context &&
          annotation_ui_context.working_file_list &&
          annotation_ui_context.working_file_list.length > 0 &&
          child_annotation_ctx_list &&
          annotation_ui_context.global_attribute_groups_list"
                  :layout_direction="layout_direction"
                  :num_columns="annotation_ui_context.panel_settings.columns"
                  :root_file="root_file"
                  :child_annotation_ctx_list="child_annotation_ctx_list"
                  :panel_settings="annotation_ui_context.panel_settings"
                  :selected_row="annotation_ui_context.working_file.row"
                  :selected_col="annotation_ui_context.working_file.column"
                  :num_rows="annotation_ui_context.panel_settings.rows"
                  :working_file_list="annotation_ui_context.working_file_list"
                  @cols_resized="on_panes_columns_resized"
                  @rows_resized="on_panes_rows_resized"
                  @ready="on_panes_ready"
                  @pane-click="on_panes_clicked"
                  @grid_changed="on_grid_changed"
                  ref="panels_manager"
            >
                <template
                      v-for="(file, index) in annotation_ui_context.working_file_list"
                      v-slot:[`panel_${file.row}:${file.column}`]=""
                >
                    <panel_metadata
                          :file="file"
                          class="panel-metadata"
                          :key="`area_metadata_${file.id}`"
                    />
                    <div
                          :key="`area_factory_container_${file.id}`"
                          style="width: 100%;"
                          :class="`${file.id === annotation_ui_context.working_file.id
                         && annotation_ui_context.working_file_list.length > 1 ? 'selected-file': 'unselected-file'} annotation-area-container`">
                        <annotation_area_factory
                              :key="`annotation_area_factory_${file.id}`"
                              :ref="`annotation_area_factory_${file.id}`"
                              :is_active="file.id === annotation_ui_context.working_file.id"
                              :container_height="child_annotation_ctx_list[index].container_height"
                              :container_width="child_annotation_ctx_list[index].container_width"
                              :use_full_window="annotation_ui_context.working_file_list.length === 1"
                              :interface_type="file.type"
                              :show_toolbar="index === 0"
                              :annotation_ui_context="annotation_ui_context"
                              :image_annotation_ctx="child_annotation_ctx_list[index]"
                              :child_annotation_ctx_list="child_annotation_ctx_list"
                              :working_file="file"
                              :file="file"
                              :credentials_granted="credentials_granted"
                              :initializing="initializing"
                              :save_loading="annotation_ui_context.current_image_annotation_ctx.video_mode ?
                  annotation_ui_context.current_image_annotation_ctx.save_loading_frames_list.length > 0 : annotation_ui_context.get_current_ann_ctx() && annotation_ui_context.get_current_ann_ctx().save_loading"
                              :url_instance_buffer="get_url_instance_buffer()"
                              :submitted_to_review="submitted_to_review"
                              :annotations_loading="child_annotation_ctx_list[index].annotations_loading"
                              :loading="child_annotation_ctx_list[index].loading"
                              :filtered_instance_type_list_function="filtered_instance_type_list"
                              :get_userscript="get_userscript"
                              :instance_type_list="instance_type_list"
                              :save_loading_frames_list="child_annotation_ctx_list[index].save_loading_frames_list"
                              :has_changed="has_changed"
                              :instance_buffer_metadata="child_annotation_ctx_list[index].instance_buffer_metadata"
                              :create_instance_template_url="create_instance_template_url"
                              :has_pending_frames="has_pending_frames"
                              :instance_store="annotation_ui_context.instance_store"
                              :project_string_id="computed_project_string_id"
                              :label_schema="annotation_ui_context.label_schema"
                              :model_run_id_list="model_run_id_list"
                              :model_run_color_list="model_run_color_list"
                              :task="annotation_ui_context.task"
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
                              :draw_mode="annotation_ui_context.current_image_annotation_ctx.draw_mode"
                              :instance_type="annotation_ui_context.instance_type"
                              :bulk_mode="annotation_ui_context.get_current_ann_ctx() && annotation_ui_context.get_current_ann_ctx().bulk_mode"
                              :search_mode="annotation_ui_context.get_current_ann_ctx() && annotation_ui_context.get_current_ann_ctx().search_mode"
                              :annotation_show_event="annotation_show_event"
                              :hotkey_listener="hotkey_listener"
                              @activate_hotkeys="activate_hotkeys"
                              @request_file_change="request_file_change"
                              @change_label_schema="on_change_label_schema"
                              @set_file_list="set_file_list"
                              @request_new_task="change_task"
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
                              @change_video_playing="annotation_ui_context.current_image_annotation_ctx.video_playing = $event"
                              @change_current_label_file="annotation_ui_context.current_label_file = $event"
                              @trigger_refresh_current_instance="annotation_ui_context.current_image_annotation_ctx.trigger_refresh_current_instance = $event"
                              @selected_instance_for_history="annotation_ui_context.selected_instance_for_history = $event"
                              @event_create_instance="annotation_ui_context.current_image_annotation_ctx.event_create_instance = $event"
                              @refresh="annotation_ui_context.current_image_annotation_ctx.refresh = $event"
                              @open_issue_panel="handle_open_issue_panel"
                              @instance_list_updated="update_current_instance_list"
                              @instance_buffer_dict_updated="update_current_frame_buffer_dict"
                              @save_multiple_frames="save_multiple_frames"
                              @global_instance_changed="on_global_instance_changed"
                              @change_task="(event) => trigger_task_change(event, annotation_ui_context.task, false)"
                              @trigger_listeners_setup="trigger_listeners_setup"
                              @open_label_change_dialog="open_change_label_dialog_sidebar"
                              @file_rendered="on_file_rendered"
                        />
                    </div>

                </template>
            </panel_manager>

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
              v-if="dialog"
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
import Vue from 'vue';
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
import CommandManager from "../../helpers/command/command_manager"
import History from "../../helpers/history"
import ui_schema_context_menu from "../ui_schema/ui_schema_context_menu.vue";
import annotation_area_factory from "./annotation_area_factory.vue"
import toolbar_factory from "./toolbar_factory.vue"
import sidebar_factory from "./sidebar_factory.vue";
import panel_metadata from "./panel_metadata.vue";

import {
  duplicate_instance,
  initialize_instance_object
  }
from "../../utils/instance_utils";

import {
  HotkeyListener
} from "../../utils/hotkey_listener";
import TaskPrefetcher from "../../helpers/task/TaskPrefetcher"
import IssuesAnnotationUIManager from "./issues/IssuesAnnotationUIManager"
import InstanceStore from "../../helpers/InstanceStore"
import * as AnnotationSavePrechecks from '../annotation/image_and_video_annotation/utils/AnnotationSavePrechecks'
import {
    BaseAnnotationUIContext,
    GeoAnnotationUIContext,
    TextAnnotationUIContext,
    AudioAnnotationUIContext,
    SensorFusion3DAnnotationUIContext,
    ImageAnnotationUIContext
} from '../../types/AnnotationUIContext'
import panel_manager from "./panel_manager.vue";
import {saveTaskAnnotations, saveFileAnnotations} from "../../services/saveServices"
import {get_instance_list_from_file, get_instance_list_from_task} from "../../services/instanceServices.js"
import {get_child_files} from "../../services/fileServices";
import empty_file_editor_placeholder from "./image_and_video_annotation/empty_file_editor_placeholder.vue"
import HotKeyManager from "./hotkeys/HotKeysManager"
import {GlobalInstance} from "../vue_canvas/instances/GlobalInstance";
import {postInstanceList} from "../../services/instanceList"
import {CustomButton} from "../../types/ui_schema/Buttons";

export default Vue.extend({
    name: "annotation_ui_factory",
    components: {
        file_manager_sheet,
        ui_schema_context_menu,
        panel_manager,
        no_credentials_dialog,
        sidebar_factory,
        annotation_area_factory,
        toolbar_factory,
        panel_metadata,
        empty_file_editor_placeholder
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
    data: function () {
        return {
            task_error: {
                task_request: null,
            },
            show_ui_schema_context_menu: false,
            hotkey_manager: null,
            platform: {
              default: 'win'
            },
            hotkey_listener: null,
            window_width: 0,
            window_height: 0,
            annotation_ui_context: new BaseAnnotationUIContext(),
            child_annotation_ctx_list: [],
            root_file: {},
            task_prefetcher: null,
            columns_panes_size: {},
            rows_panes_size: {},
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
            layout_direction: 'horizontal',
            show_default_navigation: true,
            context: null,
            error: null,
            request_save: false,
            model_run_id_list: [],

            missing_credentials: [],
            label_schema_list: [],

            annotation_show_event: null,

            view_only: false,

            labels_list_from_project: null,
            model_run_color_list: null,
            label_file_colour_map_from_project: null,
            save_loading_image: false,
            submitted_to_review: false,
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
          current_ann_ctx: {
            container_height: null,
            container_width: null,
            has_changed: null,
          },
        }
    },
    watch: {
        'annotation_ui_context.working_file': function () {

            if (this.interface_type === 'image' || this.interface_type === 'video') {
                this.annotation_ui_context.command_manager = new CommandManagerAnnotationCore()
            }

            if (this.interface_type === 'text' || this.interface_type === 'audio') {
                this.annotation_ui_context.history = new History()
                this.annotation_ui_context.command_manager = new CommandManager(this.annotation_ui_context.history)
            }

            if (
                this.annotation_ui_context &&
                this.hotkey_manager &&
                this.listeners_map() &&
                this.annotation_ui_context.working_file_list.length >= 1
            ) {
                this.hotkey_manager.activate(this.listeners_map())
            }
        },
        async '$route'(to, from) {
            if (from.name === 'task_annotation' && to.name === 'studio') {
                await this.fetch_project_file_list();
                this.annotation_ui_context.task = null;
                if (this.$refs.file_manager_sheet) {
                    this.$refs.file_manager_sheet.display_file_manager_sheet();
                }
            }
            if (from.name === 'studio' && to.name === 'task_annotation') {
                this.annotation_ui_context.working_file = null;
                this.fetch_single_task(this.task_id_prop);
                this.$refs.file_manager_sheet.hide_file_manager_sheet()
            }
            this.get_model_runs_from_query(to.query);
        },
        root_file: {
            handler(newVal, oldVal) {
                if (newVal && newVal != oldVal) {
                    Vue.set(this.annotation_ui_context, 'instance_store', new InstanceStore())
                    this.$addQueriesToLocation({file: newVal.id});
                }
            },
        },
        'annotation_ui_context.task': async function (newVal) {
            await this.update_root_file(newVal.file)
            if (newVal && this.task_prefetcher && newVal.file.type === 'image') {
                Vue.set(this.annotation_ui_context, 'instance_store', new InstanceStore())
                this.task_prefetcher.update_tasks(newVal)
            }
            await this.$nextTick();

        }
    },
    created() {
        if (this.$route && this.$route.query.edit_schema) {
            this.enabled_edit_schema = true;
        }
        if (this.$route && this.$route.query.view_only) {
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
            if (this.task_id_prop) {
                this.context = 'task'
                this.add_visit_history_event("task");
            } else if (this.file_id_prop) {
                this.add_visit_history_event("file");
            } else {
                this.add_visit_history_event("page");
            }
        } else {
            this.view_only = true;
        }
        if (this.enabled_edit_schema == true) {
            this.edit_ui_schema()
        }
        this.hotkey_listener = HotkeyListener.getInstance()
        this.platform = this.hotkey_listener.getPlatform()

        this.hotkey_listener.addFilter((event) => {
          return !this.$store.state.user.is_typing_or_menu_open
        })
    },
    beforeDestroy() {
        this.hotkey_manager.deactivate()
        window.removeEventListener(
            "resize",
            this.update_window_size_from_listener
        );
        this.hotkey_listener.clear()
        this.hotkey_listener.restoreDefaultFilters()
    },

    async mounted() {
        if (window.Cypress) {
            window.AnnotationUIFactory = this;
        }
        this.window_width = window.innerWidth
        this.window_height = window.innerHeight
        window.addEventListener("resize", this.update_window_size_from_listener);
        this.annotation_ui_context.get_userscript = this.get_userscript
        Vue.set(this.annotation_ui_context, 'instance_store', new InstanceStore())
        this.annotation_ui_context.issues_ui_manager = new IssuesAnnotationUIManager()
        if (!this.task_id_prop) {
            await this.get_project();
        } else {
            this.loading_project = false; // caution some assumptions around this flag for media loading
        }

        this.initializing = true
        let query = this.$route ? this.$route.query : undefined
        this.get_model_runs_from_query(query);
        if (query && query.view_only) {
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
            if (this.task_id_prop) {
                this.changing_task = true
                await this.fetch_single_task(this.task_id_prop);
                await this.update_root_file(this.annotation_ui_context.task.file)
                await this.check_credentials();
                await this.$nextTick()
                this.credentials_granted = this.has_credentials_or_admin();
                if (!this.credentials_granted) {
                    this.show_missing_credentials_dialog();
                }
                this.changing_task = false
            } else if (this.file_id_prop) {
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

        this.hotkey_manager = new HotKeyManager()
        this.activate_hotkeys()
        this.initializing = false
    },
    computed: {
        has_changed() {
          return this.current_ann_ctx && this.current_ann_ctx.has_changed
        },
        annotation_area_container_max_height: function () {
            let heightWindow = this.window_height && document.documentElement.clientHeight ?
                Math.min(this.window_height, document.documentElement.clientHeight) :
                this.window_height ||
                document.documentElement.clientHeight ||
                document.getElementsByTagNameget_child_annotation_ctx('body')[0].clientHeight;

            let result = heightWindow - 200;
            return `${result}px`
        },
        annotation_area_container_width: function () {
            let result;
            if (!this.annotation_ui_context.current_image_annotation_ctx.label_settings || !this.interface_type || !this.interface_type && !this.initializing && this.loading) {
                return '100%'
            }

            if (this.interface_type !== 'image' || this.interface_type !== 'video') return "100%"

            let widthWindow = this.window_width && document.documentElement.clientWidth ?
                Math.min(this.window_width, document.documentElement.clientWidth) :
                this.window_width ||
                document.documentElement.clientWidth ||
                document.getElementsByTagName('body')[0].clientWidth;
            // TODO: Create a generic logic for each interface rendering
            if (this.annotation_ui_context.working_file.type === 'sensor_fusion') {
                return '100%'
            }
            if (!this.loading) {
                let elm = document.getElementById('annotation_factory_container')
                if (elm) {
                    result = elm.clientWidth - this.annotation_ui_context.current_image_annotation_ctx.label_settings.left_nav_width;
                }

            }

            return `${result}px`
        },
        interface_type: function (): string | null {
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
            return this.annotation_ui_context.current_image_annotation_ctx.current_frame

        },
        has_pending_frames: function () {
            if (!this.annotation_ui_context) {
                return false
            }
            if (!this.annotation_ui_context.current_image_annotation_ctx) {
                return false
            }
            if (!this.annotation_ui_context.current_image_annotation_ctx.unsaved_frames) {
                return false
            }
            return this.annotation_ui_context.current_image_annotation_ctx.unsaved_frames.length > 0
        },
        save_request: function (): Function {
            if (this.annotation_ui_context.task) {
                return (payload) => saveTaskAnnotations(this.annotation_ui_context.task.id, payload)
            }
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
            let file_id = this.file_id_prop;
            if (this.$route && this.$route.query.file) {
                file_id = this.$route.query.file;
            }
            return file_id;
        },
        computed_project_string_id: function () {
            if (this.project_string_id) {
                this.$store.commit(
                    "set_project_string_id",
                    this.project_string_id
                );
                return this.project_string_id;
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

      annotation_show: function (event){
        this.annotation_show_event = event
      },

        execute_button_actions: async function(custom_button: CustomButton){
          if(!custom_button.workflow){
            return
          }
          custom_button.workflow.start(this.annotation_ui_context, this)
        },
        on_set_global_attribute: async function (attribute_data) {
            let sidebar = this.$refs.sidebar_factory.get_current_sidebar_ref();
            if (sidebar && sidebar.$refs.instance_detail_list) {
                sidebar = sidebar.$refs.instance_detail_list
            }
            // Find attribute: only search on global and compound attributes.
            let file_global_attribute = this.annotation_ui_context.global_attribute_groups_list.find(attr =>
                attr.id === attribute_data.attribute_template_id
            )
            if (file_global_attribute) {
                let attr_ref = sidebar.$refs.global_attributes_list.$refs.attribute_group_list.$refs[`attribute_group_${file_global_attribute.id}`]
                if (!attr_ref) {
                    await sidebar.$refs.global_attributes_list.$refs.attribute_group_list.open_panel_for_attribute_id(file_global_attribute.id)
                    await this.$nextTick()
                    attr_ref = sidebar.$refs.global_attributes_list.$refs.attribute_group_list.$refs[`attribute_group_${file_global_attribute.id}`]
                }
                if (attr_ref && attr_ref.length > 0) {
                    attr_ref[0].set_attribute_value(attribute_data.attribute_value_id)
                }

            }
        },
        on_file_rendered: function () {
            this.on_panes_ready()
        },
        trigger_listeners_setup: function () {
            if (this.hotkey_manager) this.hotkey_manager.activate(this.listeners_map())
        },
        open_change_label_dialog_sidebar: function (instance_id: number) {
            let sidebar = this.$refs.sidebar_factory.get_current_sidebar_ref()
            if (sidebar && sidebar.$refs.instance_detail_list) {
                let instance_detail_list = sidebar.$refs.instance_detail_list
                instance_detail_list.open_change_label_menu(instance_id)
            }
        },
        on_grid_changed: function () {
            this.set_working_file_list(this.annotation_ui_context.working_file_list)
            this.on_panes_ready()

            if (this.listeners_map()) this.listeners_map()['resize']()
        },
        on_global_compound_attribute_change: function (attribute_payload) {
            let group = attribute_payload[0];
            let value = attribute_payload[1];
            let idx = this.annotation_ui_context.compound_global_instance_index
            let instance = this.annotation_ui_context.compound_global_attributes_instance_list[idx]
            this.annotation_ui_context.compound_global_instance = instance
            instance.set_attribute(group.id, value)
            this.set_has_changed(true)
        },
        initialize_ui_schema_data: function () {
            let ui_schema_loaded = this.$store.state.ui_schema.current;
            if (ui_schema_loaded && ui_schema_loaded.label_settings && ui_schema_loaded.label_settings.default_settings) {
                this.label_settings = ui_schema_loaded.label_settings.default_settings
            }

        },
        on_set_ui_schema: function (ui_schema) {
            this.initialize_ui_schema_data();
        },
        edit_ui_schema: function (event) {
            this.$store.commit("set_ui_schema_editing_state", true);
            this.show_ui_schema_context_menu = true;

        },


        activate_hotkeys: function () {
            if (this.hotkey_manager && this.listeners_map()) {
                this.hotkey_manager.activate(this.listeners_map())
            }
        },
        remove_hotkeys: function () {
            if (this.hotkey_manager) {
                this.hotkey_manager.activate(this.listeners_map())
            }
        },
        listeners_map: function () {
            let listener_map = null;

            if (!this.annotation_ui_context) return listener_map
            if (!this.annotation_ui_context.working_file) return listener_map

            let file_id = this.annotation_ui_context.working_file.id
            let file_type = this.annotation_ui_context.working_file.type

            if (!this.$refs[`annotation_area_factory_${file_id}`]) return listener_map
            if (!this.$refs[`annotation_area_factory_${file_id}`][0]) return listener_map


            if (file_type === 'image' || file_type === 'video') {
                let ref = this.$refs[`annotation_area_factory_${file_id}`][0].$refs[`annotation_core_${file_id}`]
                if (!ref) return listener_map

                listener_map = {
                    "beforeunload": ref.warn_user_unload,
                    "keydown": ref.keyboard_events_global_down,
                    "keyup": ref.keyboard_events_global_up,
                    "mousedown": ref.mouse_events_global_down,
                    "resize": ref.update_window_size_from_listener,
                }
            } else if (file_type === 'text') {
                const file_ids = this.annotation_ui_context.working_file_list.map(working_file => working_file.id)

                const refs = []
                file_ids.map(working_file_id => {
                    if (this.$refs[`annotation_area_factory_${working_file_id}`] && this.$refs[`annotation_area_factory_${working_file_id}`][0]) {
                        const ref = this.$refs[`annotation_area_factory_${working_file_id}`][0].$refs[`text_annotation_core_${working_file_id}`]
                        if (ref) refs.push(ref)
                    }
                })

                if (this.$refs[`annotation_area_factory_${file_id}`][0]) {
                    let ref = this.$refs[`annotation_area_factory_${file_id}`][0].$refs[`text_annotation_core_${file_id}`]

                    const text_resize_listener = () => refs.map(refrence => refrence.resize_listener())

                    listener_map = {
                        "beforeunload": ref ? ref.leave_listener : undefined,
                        "keydown": ref ? ref.keydown_event_listeners : undefined,
                        "keyup": ref ? ref.keyup_event_listeners : undefined,
                        "resize": text_resize_listener,
                    }


                }
            }

            return listener_map
        },
        update_window_size_from_listener: function () {
            this.window_width = window.innerWidth
            this.window_height = window.innerHeight
            for (let key_row of Object.keys(this.columns_panes_size)) {
                this.recalculate_pane_column_dimensions(key_row, this.columns_panes_size[key_row])
            }
            this.recalculate_pane_rows_dimensions(this.rows_panes_size)

            if (this.listeners_map()) this.listeners_map()['resize']()
        },
        update_label_file_visible: function (label_file) {
            if (this.annotation_ui_context.hidden_label_id_list.includes(label_file.id)) {
                const index = this.annotation_ui_context.hidden_label_id_list.indexOf(label_file.id);
                this.annotation_ui_context.hidden_label_id_list.splice(index, 1);
            } else {
                this.annotation_ui_context.hidden_label_id_list.push(label_file.id)
            }
        },
        on_global_instance_changed: function (file_id, global_instance) {
            this.annotation_ui_context.instance_store.set_global_instance(file_id, global_instance)
            if (file_id === this.annotation_ui_context.working_file.id) {
                this.annotation_ui_context.current_global_instance = global_instance
            }
        },
        on_panes_clicked: async function (row_index, panel) {
            let selected_file = this.annotation_ui_context.working_file_list.find(file => {
                return file.row === row_index && file.column === panel.index
            })
            if (selected_file) {
                await this.change_active_working_file(selected_file)
            }

        },
        recalculate_pane_rows_dimensions: function (panes_list) {
            if (!this.$refs.panels_manager) {
                return
            }

            let total_height = this.$refs.panels_manager.$el.clientHeight
            let total_rows = this.annotation_ui_context.panel_settings.rows
            for (let row_index = 0; row_index < panes_list.length; row_index++) {
                let row_files = this.annotation_ui_context.working_file_list.filter(file => file.row === row_index)
                for (let file of row_files) {
                    let i = this.annotation_ui_context.working_file_list.indexOf(file)
                    // Set default initial values.
                    if (this.child_annotation_ctx_list[i].container_height === 0) {
                        // We substract 50 px to leave a small padding when calculating new scale of images
                        if (total_rows === 1) {
                            this.child_annotation_ctx_list[i].container_height = Math.round(total_height);

                        } else {
                            this.child_annotation_ctx_list[i].container_height = 500
                        }
                    }
                    this.child_annotation_ctx_list[i].container_height = total_height * (panes_list[row_index].size / 100)

                }
            }
        },
        recalculate_pane_column_dimensions: function (row_index, panes_list) {
            if (!this.$refs.panels_manager) return

            let total_width = this.$refs.panels_manager.$el.clientWidth;
            if (!total_width) return

            // This is for text initial rendering. The sidebar width is fixed and equal to 350 and initially not rendered
            if (
                this.annotation_ui_context.working_file.type == "text" &&
                (!this.$refs.sidebar_factory || !this.$refs.sidebar_factory.$refs.sidebar_text)
            ) {
                total_width -= 350
            }
            let row_files = this.annotation_ui_context.working_file_list.filter(f => f.row === parseInt(row_index))
            for (let file_index = 0; file_index < row_files.length; file_index++) {
                let file = row_files[file_index]
                let i = this.annotation_ui_context.working_file_list.indexOf(file)
                // Set default initial values.
                if (this.child_annotation_ctx_list[i].container_width === 0) {
                    this.child_annotation_ctx_list[i].container_width = total_width * (panes_list[file_index].size / 100) - 50
                }
                this.child_annotation_ctx_list[i].container_width = total_width * (panes_list[file_index].size / 100) - 50
            }

        },
        on_panes_ready: async function () {
            await this.$nextTick()

            for (let i = 0; i < this.annotation_ui_context.panel_settings.rows; i++) {
                // TODO: filter this by row
                let default_pane_sizes_cols = this.child_annotation_ctx_list.map(elm => {
                    return {size: 100 / this.annotation_ui_context.panel_settings.columns}
                })
                this.columns_panes_size[i] = default_pane_sizes_cols
                this.recalculate_pane_column_dimensions(i, default_pane_sizes_cols)
            }
            let default_pane_sizes_rows = this.child_annotation_ctx_list.map(elm => {
                return {size: 100 / this.annotation_ui_context.panel_settings.rows}
            })
            this.rows_panes_size = default_pane_sizes_rows
            this.recalculate_pane_rows_dimensions(default_pane_sizes_rows)
            this.$forceUpdate()
        },
        on_panes_rows_resized: function (panes_list) {
            this.rows_panes_size = panes_list
            this.recalculate_pane_rows_dimensions(panes_list)

            if (this.listeners_map()) this.listeners_map()['resize']()
        },
        on_panes_columns_resized: function (row_index, panes_list) {
            this.columns_panes_size = {[row_index]: panes_list}
            this.recalculate_pane_column_dimensions(row_index, panes_list)

            if (this.listeners_map()) this.listeners_map()['resize']()
        },
        populate_child_context_list: function (child_files) {
            let new_child_list = []
            for (let file of child_files) {
                if (file.type === 'image' || file.type === 'video') {
                    this.annotation_ui_context.current_image_annotation_ctx.video_mode = file && file.type === 'video'
                    new_child_list.push(new ImageAnnotationUIContext())
                } else if (file.type === 'text') {
                    // Other type don't have context yet.
                    new_child_list.push(new TextAnnotationUIContext(file))
                } else if (file.type === 'audio') {
                    // Other type don't have context yet.
                    new_child_list.push(new AudioAnnotationUIContext())
                } else if (file.type === 'geospatial') {
                    // Other type don't have context yet.
                    new_child_list.push(new GeoAnnotationUIContext())
                } else if (file.type === 'sensor_fusion') {
                    // Other type don't have context yet.
                    new_child_list.push(new SensorFusion3DAnnotationUIContext())
                } else {
                    new_child_list.push({})
                }

            }
            this.child_annotation_ctx_list = new_child_list
        },
        get_slot_name(row, column) {
            return `panel_${row}:${column}`
        },
        handle_open_issue_panel: function (mouse_position) {
            if (!this.$refs.sidebar_factory) {
                return
            }
            let sidebar = this.$refs.sidebar_factory.get_current_sidebar_ref()
            if (sidebar) {
                sidebar.open_issue_panel(mouse_position)
            }
        },
        copy_all_instances: function () {
            const new_instance_list = this.annotation_ui_context.instance_store.get_instance_list(this.annotation_ui_context.working_file.id)

            this.$store.commit("set_clipboard", {
                instance_list: new_instance_list.filter(instance => !instance.soft_delete),
                file_id: this.annotation_ui_context.working_file.id,
            });

            this.show_snackbar = true;
            this.snackbar_message = "All Instances copied into clipboard."
        },
        redo: function () {
            if (!this.annotation_ui_context.command_manager) return
            const redone = this.annotation_ui_context.command_manager.redo()
            if (redone) this.set_has_changed(true)
            this.handle_update_canvas()
        },
        undo: function () {
            if (!this.annotation_ui_context.command_manager) return
            const undone = this.annotation_ui_context.command_manager.undo()
            if (undone) this.set_has_changed(true)
            this.handle_update_canvas()
        },
        clear_unsaved: function () {
            this.$refs[`annotation_area_factory_${this.annotation_ui_context.working_file.id}`][0].$refs[`annotation_core_${this.annotation_ui_context.working_file.id}`].clear_unsaved()
        },
        rotate_image: function (event) {
            this.$refs[`annotation_area_factory_${this.annotation_ui_context.working_file.id}`][0].$refs[`annotation_core_${this.annotation_ui_context.working_file.id}`].on_image_rotation(event)
        },
        update_smooth_canvas: function (event) {
            this.$refs[`annotation_area_factory_${this.annotation_ui_context.working_file.id}`][0].$refs[`annotation_core_${this.annotation_ui_context.working_file.id}`].update_smooth_canvas(event)
        },
        change_instance_type: function (instance_type: string): void {
            this.$store.commit("finish_draw");
            this.annotation_ui_context.instance_type = instance_type
            this.$store.commit("set_last_selected_tool", instance_type);
        },
        change_current_label_file_template: function (label_file) {
            this.annotation_ui_context.current_label_file = label_file;
            this.$emit('change_current_label_file', this.annotation_ui_context.current_label_file)
        },

        update_current_instance_list: function (instance_list, file_id, file_type) {
            if (file_id !== this.annotation_ui_context.working_file.id) {
                return
            }
            let inst_list = this.annotation_ui_context.instance_store.get_instance_list(file_id)

            this.current_instance_list = inst_list ? inst_list : []
            this.annotation_ui_context.current_global_instance = this.annotation_ui_context.instance_store.get_global_instance(file_id)
        },
        get_child_annotation_ctx: function (file): ImageAnnotationUIContext {
            if (!file) {
                return
            }
            let file_index = -1;
            let i = 0
            for (let wf of this.annotation_ui_context.working_file_list) {
                if (wf.id === file.id) {
                    file_index = i
                }
                i += 1
            }

            return this.child_annotation_ctx_list[file_index]
        },
        update_current_frame_buffer_dict: function (instance_buffer_dict, file_id, file_type) {
            if (file_id !== this.annotation_ui_context.working_file.id) {
                return
            }
            this.current_instance_buffer_dict = this.annotation_ui_context.instance_store.get_instance_list(file_id)

            let ins_list = this.current_instance_buffer_dict[this.annotation_ui_context.current_image_annotation_ctx.current_frame]
            this.current_instance_list = ins_list ? ins_list : []
            this.annotation_ui_context.current_global_instance = this.annotation_ui_context.instance_store.get_global_instance(file_id)
        },
        on_draw_mode_changed: function (draw_mode: boolean = undefined): void {
            if (draw_mode !== undefined) {
                this.annotation_ui_context.current_image_annotation_ctx.draw_mode = draw_mode
            } else {
                this.annotation_ui_context.current_image_annotation_ctx.draw_mode = !this.annotation_ui_context.current_image_annotation_ctx.draw_mode
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
            let ann_ctx = this.annotation_ui_context.get_current_ann_ctx()
            ann_ctx.has_changed = value

            if ( this.current_ann_ctx ) {
              this.current_ann_ctx.has_changed = value
            }
        },

        get_current_annotation_area_ref: function () {
            // For now just return computed prop. More complex logic might need to be added with file_id once compound file exists.
            let ref_name_map = {
                'image': `annotation_core_${this.annotation_ui_context.working_file.id}`,
                'video': `annotation_core_${this.annotation_ui_context.working_file.id}`,
                'audio': `audio_annotation_core_${this.annotation_ui_context.working_file.id}`,
                'text': `text_annotation_core_${this.annotation_ui_context.working_file.id}`,
                'geospatial': `geo_annotation_core_${this.annotation_ui_context.working_file.id}`,
                'sensor_fusion': `3d_annotation_core_${this.annotation_ui_context.working_file.id}`
            }
            let ref_name = ref_name_map[this.annotation_ui_context.working_file.type]
            let ann_factory_ref = this.$refs[`annotation_area_factory_${this.annotation_ui_context.working_file.id}`][0]
            return ann_factory_ref.$refs[ref_name]
        },

        save_multiple_frames: async function (frames_list) {
            try {
                this.annotation_ui_context.current_image_annotation_ctx.save_multiple_frames_error = {};
                for (let frame_number of frames_list) {
                    let inst_list = this.annotation_ui_context.instance_store.get_instance_list(
                        this.annotation_ui_context.working_file.id,
                        frame_number
                    )
                    await this.save(false, frame_number, inst_list)
                }
                return true

            } catch (err) {
                this.annotation_ui_context.current_image_annotation_ctx.save_multiple_frames_error = this.$route_api_errors(err);
                console.error(err);
            }
        },

        save_compound_global_attributes: async function (and_complete, video_data) {
            const payload = {
                instance_list: this.annotation_ui_context.compound_global_attributes_instance_list,
                and_complete: and_complete,
                directory_id: this.$store.state.project.current_directory.directory_id,
                video_data,
            }
            const [result, error] = await saveFileAnnotations(this.computed_project_string_id, this.root_file.id, payload)

            AnnotationSavePrechecks.add_ids_to_new_instances_and_delete_old(
              result,
              false,
              this.annotation_ui_context.compound_global_attributes_instance_list,
              false,
              false
            )

            this.root_file.instance_list = this.annotation_ui_context.compound_global_attributes_instance_list
            if (error) {
                console.error(error)
                return
            }
            return result
        },

        process_audio_save: async function () {

          const file_id = this.annotation_ui_context.working_file.id

          const {
              instance_list
          } = this.annotation_ui_context.instance_store.get_instance_list(file_id) || {}

          if (!instance_list) {
            return
          }

          this.set_has_changed(false)
          this.set_save_loading(true)

          const task = this.annotation_ui_context.task

          let url;
          if ( task && task.id ) {
            url = `/api/v1/task/${task.id}/annotation/update`;
          } else {
            url = `/api/project/${this.project_string_id}/file/${file_id}/annotation/update`
          }

          const res = await postInstanceList(url, instance_list, file_id)

          const { added_instances } = res

          instance_list.map(instance => {
            const instance_uuid = instance.creation_ref_id
            const updated_instance = added_instances.find(added_instance => added_instance.creation_ref_id === instance_uuid)
            if (updated_instance) {
                instance.id = updated_instance.id
            }
          })

          this.set_save_loading(false)
        },

        process_text_save: async function (and_complete = false) {
            // TODO: Move out of component and into a class.
            this.set_has_changed(false)
            this.set_save_loading(true)
            const file_id = this.annotation_ui_context.working_file.id
            let url
            if (this.annotation_ui_context.task && this.annotation_ui_context.task.id) {
                url = `/api/v1/task/${this.annotation_ui_context.task.id}/annotation/update`;
            } else {
                url = `/api/project/${this.project_string_id}/file/${file_id}/annotation/update`
            }

            const {
                global_instance,
                instance_list
            } = this.annotation_ui_context.instance_store.get_instance_list(file_id)

            const res = await postInstanceList(url, [...instance_list, global_instance], file_id)

            if (res) {
                const {added_instances} = res

                this.$refs[`annotation_area_factory_${file_id}`][0].$refs[`text_annotation_core_${file_id}`].after_save(added_instances)
            }

            if (this.root_file && this.root_file.type === 'compound') {
                await this.save_compound_global_attributes(and_complete)
            }

            this.set_save_loading(false)

        },

        save: async function (
            and_complete = false,
            frame_number_param = undefined,
            instance_list_param = undefined
        ) {
            // TODO: Move out of component into a InstanceListSaver class

            if (this.annotation_ui_context.get_current_ann_ctx().save_loading == true){
              return
            }
            if (this.any_loading) return

            if (this.annotation_ui_context.working_file.type === 'text') {
                await this.process_text_save(and_complete)
                return
            }

            if (this.annotation_ui_context.working_file.type === 'audio') {
              await this.process_audio_save()
              return
            }

            this.save_error = {}
            this.annotation_ui_context.current_image_annotation_ctx.save_warning = {}
            if (this.annotation_ui_context.current_image_annotation_ctx.go_to_keyframe_loading) {
                return
            }
            if (this.view_only_mode) {
                return
            }
            this.set_has_changed(false)
            this.set_save_loading(true)
            let frame_number;
            let instance_list;

            if (this.annotation_ui_context.current_image_annotation_ctx.video_mode) {
                if (!frame_number_param) {
                    frame_number = parseInt(this.current_frame, 10);
                } else frame_number = parseInt(frame_number_param, 10);

                if (instance_list_param) instance_list = instance_list_param;
                else instance_list = this.annotation_ui_context.instance_store.get_instance_list(this.annotation_ui_context.working_file.id, frame_number)
            } else {
                const inst_list = this.annotation_ui_context.instance_store.get_instance_list(this.annotation_ui_context.working_file.id)
                if(inst_list){
                  instance_list = inst_list.map(elm => {
                    if (elm.type === 'keypoints') return elm.get_instance_data()
                    else return elm
                  });
                }

            }

            if (!instance_list) {
                return
            }
            if (this.video_mode && frame_number && this.get_save_loading(frame_number)) return

            if (
                this.annotation_ui_context.current_image_annotation_ctx.video_mode &&
                (
                    !this.annotation_ui_context.instance_store.get_instance_list(this.annotation_ui_context.working_file.id, frame_number) ||
                    this.annotation_ui_context.current_image_annotation_ctx.annotations_loading
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
                this.annotation_ui_context.current_image_annotation_ctx.save_warning = {
                    duplicate_instances: `Instance list has duplicates: ${dup_ids}. Please move the instance before saving.`,
                };
                // We want to focus the most recent instance, if we focus the older one we can produce an error.
                this.$refs.sidebar_factory.get_current_sidebar_ref().$refs.instance_detail_list.toggle_instance_focus(
                    dup_instance_list[0].original_index,
                    undefined
                );

                this.set_save_loading(false, frame_number);

                return
            }

            let video_data = null;

            if (this.annotation_ui_context.current_image_annotation_ctx.video_mode) {
                video_data = {
                    video_mode: this.annotation_ui_context.current_image_annotation_ctx.video_mode,
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
                child_file_save_id: this.root_file.type === 'compound' ? this.annotation_ui_context.working_file.id : undefined
            }
            const [result, error] = await this.save_request(payload)
            if (result) {
                // Save global instances video
                if (this.annotation_ui_context.current_image_annotation_ctx.video_mode && this.annotation_ui_context.current_image_annotation_ctx.video_parent_file_instance_list.length > 0
                    && this.annotation_ui_context.current_image_annotation_ctx.video_global_attribute_changed) {
                    video_data.set_parent_instance_list = true

                    const video_payload = {
                        ...payload,
                        instance_list: this.annotation_ui_context.current_image_annotation_ctx.video_parent_file_instance_list
                    }
                    const [parent_result, parent_error] = await this.save_request(video_payload);

                    if (parent_result) {
                        this.annotation_ui_context.current_image_annotation_ctx.video_global_attribute_changed = false;
                    }
                }

                this.set_save_loading(false)
                this.annotation_ui_context.current_image_annotation_ctx.has_changed = false
                this.save_count += 1;

                AnnotationSavePrechecks.add_ids_to_new_instances_and_delete_old(
                    result,
                    video_data,
                    instance_list,
                    this.annotation_ui_context.instance_store.get_instance_list(this.annotation_ui_context.working_file.id),
                    this.annotation_ui_context.current_image_annotation_ctx.video_mode
                )

                this.annotation_ui_context.current_image_annotation_ctx.has_changed = AnnotationSavePrechecks.check_if_pending_created_instance(instance_list)

                // Update Sequence ID's and Keyframes.
                if ((result.data.sequence || result.data.new_sequence_list) && this.annotation_ui_context.current_image_annotation_ctx.video_mode) {
                    this.get_current_annotation_area_ref().update_sequence_data(instance_list, frame_number, result);
                }
                // Save Global Compound Instance
                if (this.root_file && this.root_file.type === 'compound') {
                    await this.save_compound_global_attributes(and_complete, video_data)
                }

                this.set_save_loading(false, frame_number);
                this.set_frame_pending_save(false, frame_number)
                this.annotation_ui_context.current_image_annotation_ctx.has_changed = false;
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
                this.annotation_ui_context.current_image_annotation_ctx.has_changed = AnnotationSavePrechecks.check_if_pending_created_instance(instance_list)

                if (this.annotation_ui_context.current_image_annotation_ctx.video_mode) {
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
            if (this.annotation_ui_context.current_image_annotation_ctx.video_mode) {
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
            for (let frame_num of Object.keys(this.annotation_ui_context.current_image_annotation_ctx.instance_buffer_metadata)) {
                let frame_metadata = this.annotation_ui_context.current_image_annotation_ctx.instance_buffer_metadata[frame_num]
                if (frame_metadata.pending_save) {
                    result.push(parseInt(frame_num, 10))
                }
            }
            return result;
        },
        set_frame_pending_save: function (value, frame_number) {
            if (!frame_number) return

            if (this.annotation_ui_context.current_image_annotation_ctx.instance_buffer_metadata[frame_number]) {
                // We need to recreate object so that computed props get triggered
                this.annotation_ui_context.current_image_annotation_ctx.instance_buffer_metadata[frame_number].pending_save = value;
            } else {
                this.annotation_ui_context.current_image_annotation_ctx.instance_buffer_metadata[frame_number] = {
                    pending_save: value
                }
            }
            // Keep unsaved_frames list to enable/disable save button
            if (value) {
                this.annotation_ui_context.current_image_annotation_ctx.unsaved_frames.push(frame_number)
            } else {
                this.annotation_ui_context.current_image_annotation_ctx.unsaved_frames = this.annotation_ui_context.current_image_annotation_ctx.unsaved_frames.filter(elm => elm != frame_number)
            }

        },
        get_save_loading: function (frame_number: number) {
            if (this.annotation_ui_context.current_image_annotation_ctx.video_mode) {
                if (!this.annotation_ui_context.image_annotation_ctx) {
                    return false
                }
                return this.current_image_annotation_ctx.save_loading_frames_list.includes(frame_number)
            } else return this.annotation_ui_context.get_current_ann_ctx().save_loading
        },
        set_save_loading: function (value, frame) {
            if (this.annotation_ui_context.current_image_annotation_ctx.video_mode) {
                if (value) {
                    this.annotation_ui_context.current_image_annotation_ctx.save_loading_frames_list.push(frame)
                } else {
                    this.annotation_ui_context.current_image_annotation_ctx.save_loading_frames_list = this.annotation_ui_context.current_image_annotation_ctx.save_loading_frames_list.filter(elm => elm != frame)
                }

            } else {
                const ann_ctx = this.annotation_ui_context.get_current_ann_ctx()
                ann_ctx.save_loading = value
            }

            this.$forceUpdate();
        },
        filtered_instance_type_list: function (instance_type_list) {
            const schema_allowed_types = (): string[] | null => {
                if (
                    !this.annotation_ui_context.task ||
                    !this.annotation_ui_context.task.job ||
                    !this.annotation_ui_context.task.job.ui_schema ||
                    !this.annotation_ui_context.task.job.ui_schema.instance_selector ||
                    !this.annotation_ui_context.task.job.ui_schema.instance_selector.allowed_instance_types
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
                this.annotation_ui_context.current_image_annotation_ctx.annotations_loading === true
            ) return


            if (this.annotation_ui_context.current_image_annotation_ctx.has_changed) {
              await this.save();
            }
            await this.change_task(direction, task, assign_to_user);
        },

        on_task_annotation_complete_and_save: async function () {
            await this.save(true);
            const response = await finishTaskAnnotation(this.annotation_ui_context.task.id);
            const new_status = response.data.task.status;

            if (new_status !== "complete") {
              this.submitted_to_review = true;
            }

            // if (this.annotation_ui_context.task && this.annotation_ui_context.task.id) {
            //     this.set_save_loading(false)
            //     await this.trigger_task_change("next", this.annotation_ui_context.task, true);
            // }
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
        set_working_file_from_child_file_list: async function (file_to_set) {
            let i = 0;
            for (let file of this.annotation_ui_context.working_file_list) {
                if (file.id === file_to_set.id) {
                    this.change_active_working_file(file)
                }
                i += 1;
            }
        },
        set_working_file_list: function (file_list) {
            let num_rows = this.annotation_ui_context.panel_settings.rows;
            let num_cols = this.annotation_ui_context.panel_settings.columns;
            let current_row = 0
            let current_col = 0
            for (let i = 0; i < file_list.length; i++) {
                file_list[i].column = current_col
                file_list[i].row = current_row

                if (current_col > 0 && (current_col % (num_cols - 1)) === 0) {
                    current_row += 1
                    current_col = 0
                } else {
                    current_col += 1
                    if (num_cols === 1) {
                        current_col = 0;
                        current_row += 1
                    }
                }

            }
            this.annotation_ui_context.working_file_list = file_list
        },
        set_layout_panels: function (rows, cols) {
            this.annotation_ui_context.panel_settings.rows = rows
            this.annotation_ui_context.panel_settings.columns = cols

            if (this.listeners_map()) this.listeners_map()['resize']()
        },
        change_active_working_file: async function (file) {
            this.annotation_ui_context.working_file = file

            await this.$nextTick()
            let ann_ctx = this.get_child_annotation_ctx(file)
            if (file.type === 'video' || file.type === 'image') {
                let frame_num;
                if (file.type === 'video') {
                    frame_num = ann_ctx.current_frame
                }
                this.current_instance_list = this.annotation_ui_context.instance_store.get_instance_list(file.id, frame_num)
                this.annotation_ui_context.current_image_annotation_ctx = ann_ctx
                this.annotation_ui_context.current_global_instance = this.annotation_ui_context.instance_store.get_global_instance(file.id)
            } else if (file.type === 'audio') {
                this.current_instance_list = this.annotation_ui_context.instance_store.get_instance_list(file.id)
                this.annotation_ui_context.current_global_instance = this.annotation_ui_context.instance_store.get_global_instance(file.id)
                this.annotation_ui_context.current_audio_annotation_ctx = ann_ctx
            } else if (file.type === 'text') {
                this.current_instance_list = this.annotation_ui_context.instance_store.get_instance_list(file.id)
                this.annotation_ui_context.current_global_instance = this.annotation_ui_context.instance_store.get_global_instance(file.id)
                this.annotation_ui_context.current_text_annotation_ctx = ann_ctx
            } else if (file.type === 'geospatial') {
                this.current_instance_list = this.annotation_ui_context.instance_store.get_instance_list(file.id)
                this.annotation_ui_context.current_global_instance = this.annotation_ui_context.instance_store.get_global_instance(file.id)
                this.annotation_ui_context.current_geo_annotation_ctx = ann_ctx
            } else if (file.type === 'sensor_fusion') {
                this.current_instance_list = this.annotation_ui_context.instance_store.get_instance_list(file.id)
                this.annotation_ui_context.current_global_instance = this.annotation_ui_context.instance_store.get_global_instance(file.id)
                this.annotation_ui_context.current_sensor_fusion_annotation_ctx = ann_ctx
            }

            this.current_ann_ctx = this.annotation_ui_context.get_current_ann_ctx()
        },
        set_compound_global_attributes_instance_list: async function (file) {
            let file_data
            if (this.annotation_ui_context.task) {
                file_data = await get_instance_list_from_task(this.computed_project_string_id, this.annotation_ui_context.task.id)
            } else {
                file_data = await get_instance_list_from_file(this.computed_project_string_id, file.id)
            }

            let instance_list = []
            if (file_data.file_serialized && file_data.file_serialized.instance_list) {
                instance_list = file_data.file_serialized.instance_list
            }
            if (instance_list.length >= 1) {
                this.annotation_ui_context.compound_global_attributes_instance_list = instance_list;
                this.annotation_ui_context.compound_global_instance_id = instance_list[0].id
                this.annotation_ui_context.compound_global_instance_index = 0
                this.annotation_ui_context.compound_global_instance = instance_list[0]
                for (let i = 0; i < this.annotation_ui_context.compound_global_attributes_instance_list.length; i++) {
                    let inst = this.annotation_ui_context.compound_global_attributes_instance_list[i]
                    this.annotation_ui_context.compound_global_attributes_instance_list[i] = initialize_instance_object(inst, this)
                }


            } else {
                let instance = new GlobalInstance()
                this.annotation_ui_context.compound_global_attributes_instance_list = [instance]
                this.annotation_ui_context.compound_global_instance_id = instance.id
                this.annotation_ui_context.compound_global_instance_index = 0
                this.annotation_ui_context.compound_global_instance = instance
            }
            file.instance_list = this.annotation_ui_context.compound_global_attributes_instance_list
        },
        set_default_layout_for_child_files: function (child_files, root_file = null) {
            let cols = child_files.length < 4 ? child_files.length : 4

            if (root_file && root_file.subtype === 'conversational') cols = 1
            this.annotation_ui_context.panel_settings.set_cols_and_rows_from_total_items(cols, child_files.length)
        },
        update_root_file: async function (raw_file) {
            if (!raw_file) {
                return
            }

            const file_type_arrya = raw_file.type.split('/')

            const file = {...raw_file, type: file_type_arrya[0], subtype: file_type_arrya[1]}
            this.annotation_ui_context.subtype = file_type_arrya[1]

            if (file.type === 'compound') {
                let [child_files, err] = await get_child_files(this.computed_project_string_id, file.id)
                if (err) {
                    console.error(err)
                    return
                }
                child_files = child_files.sort((a, b) => {
                    return a.ordinal - b.ordinal
                })

                this.set_default_layout_for_child_files(child_files, file)
                this.set_working_file_list(child_files)
                this.populate_child_context_list(this.annotation_ui_context.working_file_list)
                await this.set_working_file_from_child_file_list(this.annotation_ui_context.working_file_list[0])
                await this.set_compound_global_attributes_instance_list(file)
            } else {
                // Set single layout
                this.set_layout_panels(1, 1)
                this.set_working_file_list([file])
                this.populate_child_context_list(this.annotation_ui_context.working_file_list)
                await this.set_working_file_from_child_file_list(file)

            }
            await this.$nextTick()
            this.on_panes_ready()
            await this.$nextTick()
            this.root_file = file
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
            this.loading = true
            await this.update_root_file(file)
            this.loading = false
            await this.$nextTick();
            let model_runs_data = "";
            if (model_runs) {
                model_runs_data = encodeURIComponent(model_runs);
            }
            this.get_model_runs_from_query(model_runs_data);
            if (this.listeners_map()) this.listeners_map()['resize']()
            this.changing_file = false;
            await this.$nextTick();
            if (this.annotation_ui_context.working_file && this.annotation_ui_context.working_file.type !== 'text') {
                this.update_window_size_from_listener()
            }


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
                this.annotation_ui_context.global_attribute_groups_list = result.global_attribute_groups_list
                this.annotation_ui_context.global_attribute_groups_list_compound = result.global_attribute_groups_list_compound
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
                    await this.update_root_file(file)
                }
            } else {
                if (this.$refs.file_manager_sheet) {
                    let file = await this.$refs.file_manager_sheet.get_media();
                    await this.update_root_file(file)
                }
            }
            this.loading = false;
            if (this.$refs.file_manager_sheet) {
                this.$refs.file_manager_sheet.display_file_manager_sheet();
            }
            await this.update_window_size_from_listener()
        },

        fetch_single_file: async function () {
            this.loading = true;

            if (this.$refs.file_manager_sheet) {
                let file = await this.$refs.file_manager_sheet.get_media();
                await this.update_root_file(file);
            }

            this.loading = false;
            if (this.$refs.file_manager_sheet) {
                this.$refs.file_manager_sheet.display_file_manager_sheet();
            }
            await this.update_window_size_from_listener()
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
                    this.annotation_ui_context.task = response.data.task;
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
                        const new_task = response.data.task
                        if (response.data.task.id !== task.id) {
                            this.$router.replace(`/task/${response.data.task.id}`);
                            history.replaceState({}, "", `/task/${response.data.task.id}`);
                            this.annotation_ui_context.task = new_task;
                            this.task_image = new_task.image
                            this.task_instances = new_task.instances
                            this.task_loading = false
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
            if (this.file_id_prop) {
                page_name = "file_detail";
            }
            if (this.task_id_prop) {
                page_name = "task_detail";
            }
            if (this.task_id_prop === -1 || this.task_id_prop === '-1') {
                return
            }
            const event_data = await create_event(this.computed_project_string_id, {
                file_id: this.file_id_prop,
                task_id: this.task_id_prop,
                page_name: page_name,
                object_type: object_type,
                user_visit: "user_visit",
            });
        },


        delete_instance: function (instance) {
            const { id, type } = this.annotation_ui_context.working_file

            this.$refs[`annotation_area_factory_${id}`][0].$refs[`${type}_annotation_core_${id}`].delete_instance(instance)
        },

        select_instance: function (instance) {
            const { id, type } = this.annotation_ui_context.working_file
            this.$refs[`annotation_area_factory_${id}`][0].$refs[`${type}_annotation_core_${id}`].on_select_instance(instance)
        },

        change_instance_label: function (instance) {
            const { id, type } = this.annotation_ui_context.working_file
            this.$refs[`annotation_area_factory_${id}`][0].$refs[`${type}_annotation_core_${id}`].change_instance_label(instance)
        },

        update_attribute: function (instance) {
            const { id, type } = this.annotation_ui_context.working_file
            this.$refs[`annotation_area_factory_${id}`][0].$refs[`${type}_annotation_core_${id}`].update_attribute(instance)
        },

        hover_text_instance: function (instance_id) {
            const file_id = this.annotation_ui_context.working_file.id

            this.$refs[`annotation_area_factory_${file_id}`][0].$refs[`text_annotation_core_${file_id}`].on_instance_hover(instance_id)
        },

        stop_hover_text_instance: function () {
            const file_id = this.annotation_ui_context.working_file.id

            this.$refs[`annotation_area_factory_${file_id}`][0].$refs[`text_annotation_core_${file_id}`].on_instance_stop_hover()
        },
    }
});
</script>

<style>
.selected-file {
    transition: ease 0.1s;
    border: 6px solid #1565c0;
}

.unselected-file:hover {
    cursor: pointer !important;
}

.annotation-area-container {
    position: relative;
}

.panel-metadata {
    position: absolute;
    right: 0;
    bottom: 0;
}
</style>
