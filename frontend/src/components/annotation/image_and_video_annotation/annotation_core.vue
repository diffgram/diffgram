<template>
  <div id="annotation_core" class="pa-0">


    <div style="position: relative">
      <!-- Errors / info -->
      <v-alert v-if="task_error.task_request" type="info">
        {{ task_error.task_request }}
      </v-alert>

      <div v-if="working_file && working_file.image && working_file.image.error">
        <v-alert type="info">
          {{ working_file.image.error}}
        </v-alert>
      </div>
      <v_error_multiple :error="save_error"></v_error_multiple>
      <v_error_multiple :error="image_annotation_ctx.save_multiple_frames_error"></v_error_multiple>
      <v_error_multiple :error="image_annotation_ctx.save_warning"
                        type="warning"
                        data-cy="save_warning">
      </v_error_multiple>
      <div fluid v-if="display_refresh_cache_button">
        <v-btn small
               color="warning"
               @click="regenerate_file_cache"
               :loading="regenerate_file_cache_loading">
          <v-icon>mdi-refresh</v-icon>
          Refresh File Data
        </v-btn>
      </div>
      <v_error_multiple :error="error"></v_error_multiple>

      <v_error_multiple :error="instance_buffer_error"></v_error_multiple>
    </div>
    <v-snackbar
      v-if="snackbar_merge_polygon"
      v-model="snackbar_merge_polygon"
      :multi-line="true"
      :timeout="-1"
    >
      Please select the Polygons to merge with.

      <template v-slot:action="{ attrs }">
        <v-btn color="red" text v-bind="attrs" @click="cancel_merge">
          Cancel
        </v-btn>
        <v-btn
          :disabled="polygon_merge_tool && polygon_merge_tool.instances_to_merge.length === 0"
          color="success"
          text
          v-bind="attrs"
          @click="merge_polygons_v2"
        >
          Merge Polygons
        </v-btn>
      </template>
    </v-snackbar>
    <v-snackbar
      v-if="issues_ui_manager.snackbar_issues"
      v-model="issues_ui_manager.snackbar_issues"
      :multi-line="true"
      :timeout="-1"
    >
      Please select the instances to attach to the issue.

      <template v-slot:action="{ attrs }">
        <v-btn
          color="red"
          text
          v-bind="attrs"
          @click="done_selecting_instaces_issues"
        >
          Ok.
        </v-btn>
      </template>
    </v-snackbar>
    <div v-if="instance_type === 'polygon'">
      <v-snackbar v-if="alert_info_drawing" dismissible type="info" v-model="alert_info_drawing">
        To complete polygon click first point again, or
        <kbd>Enter</kbd> key, or hover in turbo mode.
      </v-snackbar>
    </div>
    <v-snackbar
      v-if="show_custom_snackbar"
      v-model="show_custom_snackbar"
      :multi-line="true"
      :timeout="custom_snackbar_timeout"
      :color="custom_snackbar_color"
      top
      left
    >
      <h1 class="font-weight-bold" :style="`color: ${custom_snackbar_text_color}`">
        {{ snackbar_message }}
      </h1>
      <p class="font-weight-light font-italic pt-3" :style="`color: ${custom_snackbar_text_color}`">
        {{ snackbar_message_secondary }}
      </p>

      <template v-slot:action="{ attrs }">
        <v-btn
          v-if="custom_snackbar_show_close_button"
          :color="custom_snackbar_text_color"
          text
          v-bind="attrs"
          @click="show_custom_snackbar = false"
        >
          Ok.
        </v-btn>
      </template>
    </v-snackbar>
    <v-snackbar
      v-if="auto_border_context && auto_border_context.show_snackbar_auto_border"
      v-model="auto_border_context.show_snackbar_auto_border"
      :multi-line="true"
      :timeout="-1"
      data-cy="auto_border_first_point_selected_usage_prompt"
    >
      Select the second point of the same polygon for autobordering (or press
      "x" key to cancel)

      <template v-slot:action="{ attrs }">
        <v-btn
          color="red"
          text
          v-bind="attrs"
          @click="auto_border_context.show_snackbar_auto_border = false"
        >
          Ok.
        </v-btn>
      </template>
    </v-snackbar>
    <v-snackbar
      v-if="show_snackbar_paste"
      v-model="show_snackbar_paste"
      :multi-line="true"
    >
      {{ snackbar_paste_message }}

      <template v-slot:action="{ attrs }">
        <v-btn
          color="red"
          text
          v-bind="attrs"
          @click="show_snackbar_paste = false"
        >
          Ok.
        </v-btn>
      </template>
    </v-snackbar>

    <v-sheet style="outline: none">
      <v-layout style="outline: none">
        <v-container v-if="error_no_permissions.data">
          <v_error_multiple
            class="ma-auto"
            :error="error_no_permissions"
          ></v_error_multiple>
          <v-container class="d-flex">
            <v-btn
              @click="go_to_login"
              v-if="!this.$store.state.user.logged_in"
              type="primary"
              color="primary"
              class="mr-4"
            >
              <v-icon>mdi-login-variant</v-icon>
              Login
            </v-btn
            >
            <v-btn
              v-if="this.$store.state.user.logged_in"
              @click="go_to_projects"
              type="primary"
              color="primary"
            >
              <v-icon>mdi-folder-move</v-icon>
              Change Project
            </v-btn
            >
          </v-container>
        </v-container>
        <div id="annotation" tabindex="0" v-if="!error_no_permissions.data">
          <!-- Must wrap canvas to detect events in this context
              Careful, the slider needs to be in this context too
              in order for the canvas render to detect it -->

          <div
            :id="`canvas_wrapper_${working_file.id}`"
            style="position: relative"
            @mousemove="mouse_move"
            @mousedown="mouse_down"
            @dblclick="double_click"
            @mouseup="mouse_up"
            @contextmenu="contextmenu"
            :style="canvas_style"
          >
            <!-- Diffgram loading loading your data -->
            <v-container v-if="show_place_holder" style="width: 100%">
              <h2 class="font-weight-light">Loading File...</h2>
              <v-progress-linear indeterminate></v-progress-linear>
              <v-img
                src="https://storage.googleapis.com/diffgram_public/app/Empty_state_card.svg"
                alt=""
                style="max-width: 100%; width: 100%"
              ></v-img>
              <!-- https://storage.googleapis.com/diffgram_public/app/Copy-of-Loading-Placeholder.png -->
            </v-container>
            <autoborder_avaiable_alert
              :x_position="canvas_alert_x"
              :y_position="canvas_alert_y"
              ref="autoborder_alert"
            >
            </autoborder_avaiable_alert>
            <ghost_canvas_available_alert
              :x_position="canvas_alert_x"
              :y_position="canvas_alert_y"
              ref="ghost_canvas_available_alert"
            >
            </ghost_canvas_available_alert>

            <div v-if="file_cant_be_accessed && !image_annotation_ctx.loading"
                 class="d-flex flex-column justify-center align-center"
                 style="min-width: 750px; min-height: 750px; border: 1px solid #e0e0e0">
              <v-icon size="450">mdi-download-off</v-icon>
              <div v-if="working_file && working_file.image" style="max-width: 500px">
                <p class="primary--text font-weight-medium">
                  URL Attempted To be Used:
                <div>
                  <a target="_blank" v-if="working_file.image.url_signed" class="secondary--text font-weight-medium"
                     :href="working_file.image.url_signed">
                    {{ working_file.image.url_signed ? working_file.image.url_signed : "null" }}
                  </a>
                  <p v-else> {{ working_file.image.url_signed ? working_file.image.url_signed : "null" }}</p>
                </div>
              </div>
              <v_error_multiple :error="file_cant_be_accessed_error"></v_error_multiple>
            </div>

            <canvas
              data-cy="canvas"
              ref="canvas"
              v-show="!show_place_holder && !file_cant_be_accessed && !image_annotation_ctx.loading"
              :id="canvas_id"
              v-canvas:cb="onRendered"
              :height="canvas_height_scaled"
              :width="canvas_width_scaled"
            >
              <v_bg
                :auto_scale_bg="false"
                :image="html_image"
                :current_file="working_file"
                :refresh="refresh"
                @update_canvas="update_canvas"
                :canvas_filters="canvas_filters"
                :canvas_element="canvas_element"
                :ord="1"
                :annotations_loading="any_loading"
                :canvas_width="original_media_width"
                :canvas_height="original_media_height"
                :degrees="degrees"
              >
              </v_bg>

              <target_reticle
                :is_active="is_active"
                :ord="2"
                :x="mouse_position.x"
                :y="mouse_position.y"
                :height="original_media_height"
                :width="original_media_width"
                :degrees="degrees"
                :canvas_element="canvas_element"
                :show="show_target_reticle && is_active && annotation_ui_context && !annotation_ui_context.show_context_menu"
                :target_colour="
                  current_label_file ? current_label_file.colour : undefined
                "
                :text_color="
                  this.$get_sequence_color(this.current_instance.sequence_id)
                "
                :target_text="this.current_instance.number"
                :target_type="target_reticle_type"
                :canvas_transform="canvas_transform"
                :reticle_size="label_settings.target_reticle_size"
                :zoom_value="image_annotation_ctx.zoom_value"
              >
              </target_reticle>

              <canvas_instance_list
                :ord="3"
                :instance_list="instance_list"
                :default_instance_opacity="default_instance_opacity"
                :vertex_size="label_settings.vertex_size"
                :cuboid_corner_move_point="cuboid_corner_move_point"
                :video_mode="image_annotation_ctx.video_mode"
                :auto_border_polygon_p1="auto_border_context.auto_border_polygon_p1"
                :auto_border_polygon_p2="auto_border_context.auto_border_polygon_p2"
                :issues_list="issues_ui_manager.issues_list"
                :current_frame="image_annotation_ctx.current_frame"
                :label_settings="label_settings"
                :current_instance="current_instance"
                :is_actively_drawing="is_actively_drawing"
                :height="original_media_height"
                :width="original_media_width"
                :refresh="refresh"
                :draw_mode="draw_mode"
                :mouse_position="mouse_position"
                @instance_hover_update="
                  instance_hover_update(
                    $event[0],
                    $event[1],
                    $event[2],
                    $event[3]
                  )
                "
                @cuboid_face_hover_update="cuboid_face_hover_update"
                @issue_hover_update="issue_hover_update"
                :canvas_transform="canvas_transform"
                :show_annotations="show_annotations"
                :annotations_loading="image_annotation_ctx.annotations_loading"
                :label_file_colour_map="label_file_colour_map"
                :instance_focused_index="instance_focused_index"
                :hidden_label_id_list="annotation_ui_context.hidden_label_id_list"
                :is_actively_resizing="is_actively_resizing"
                :emit_instance_hover="!draw_mode || emit_instance_hover"
                :zoom_value="image_annotation_ctx.zoom_value"
              >
              </canvas_instance_list>

              <ghost_instance_list_canvas
                :ord="4"
                :show="label_settings.show_ghost_instances"
                :instance_list="ghost_instance_list"
                :vertex_size="label_settings.vertex_size"
                :video_mode="image_annotation_ctx.video_mode"
                :current_frame="image_annotation_ctx.current_frame"
                :label_settings="label_settings"
                :is_actively_drawing="is_actively_drawing"
                :refresh="refresh"
                :draw_mode="draw_mode"
                :mouse_position="mouse_position"
                :canvas_transform="canvas_transform"
                :show_annotations="show_annotations"
                :annotations_loading="image_annotation_ctx.annotations_loading"
                :label_file_colour_map="label_file_colour_map"
                :hidden_label_id_list="annotation_ui_context.hidden_label_id_list"
                :is_actively_resizing="is_actively_resizing"
                :emit_instance_hover="true"
                @instance_hover_update="
                  ghost_instance_hover_update($event[0], $event[1], $event[2])
                "
                :zoom_value="image_annotation_ctx.zoom_value"
              >
              </ghost_instance_list_canvas>

              <!-- Careful, must have this object exist
                  prior to loading instance list otherwise it won't update
                  If there are no instance sit doesn't render anything so that's ok...-->
              <canvas_instance_list
                v-if="gold_standard_file"
                :ord="4"
                :vertex_size="label_settings.vertex_size"
                :default_instance_opacity="default_instance_opacity"
                :cuboid_corner_move_point="cuboid_corner_move_point"
                :mode="'gold_standard'"
                :instance_list="gold_standard_file.instance_list"
                :auto_border_polygon_p1="auto_border_context.auto_border_polygon_p1"
                :auto_border_polygon_p2="auto_border_context.auto_border_polygon_p2"
                :video_mode="image_annotation_ctx.video_mode"
                :is_actively_drawing="is_actively_drawing"
                :current_frame="image_annotation_ctx.current_frame"
                :label_settings="label_settings"
                :current_instance="current_instance"
                :refresh="refresh"
                :draw_mode="draw_mode"
                :mouse_position="mouse_position"
                :canvas_transform="canvas_transform"
                :show_annotations="show_annotations"
                :annotations_loading="image_annotation_ctx.annotations_loading"
                :label_file_colour_map="label_file_colour_map"
                :is_actively_resizing="is_actively_resizing"
                :hidden_label_id_list="annotation_ui_context.hidden_label_id_list"
              >
              </canvas_instance_list>

              <canvas_current_instance
                :ord="5"
                :current_instance="current_instance"
                :mouse_position="mouse_position"
                :canvas_transform="canvas_transform"
                :draw_mode="draw_mode"
                :is_actively_drawing="is_actively_drawing"
                :label_file_colour_map="label_file_colour_map"
                :zoom_value="image_annotation_ctx.zoom_value"
              >
              </canvas_current_instance>
              <current_instance_template
                :ord="6"
                :current_instance_template="actively_drawing_instance_template"
                :vertex_size="label_settings.vertex_size"
                :instance_template_start_point="instance_template_start_point"
                :instance_template_draw_started="instance_template_draw_started"
                :mouse_position="mouse_position"
                :canvas_transform="canvas_transform"
                :draw_mode="draw_mode"
                :is_actively_drawing="is_actively_drawing"
                :label_file_colour_map="label_file_colour_map"
              >
              </current_instance_template>
            </canvas>

            <polygon_borders_context_menu
              :show_context_menu="auto_border_context.show_polygon_border_context_menu"
              :mouse_position="mouse_position"
              :project_string_id="project_string_id"
              @start_auto_bordering="perform_auto_bordering_v2"
              @close_context_menu="auto_border_context.show_polygon_border_context_menu = false"
            ></polygon_borders_context_menu>

            <context_menu
              :mouse_position="mouse_position"
              :show_context_menu="annotation_ui_context.show_context_menu"
              :instance_clipboard="instance_clipboard"
              :instance_focused_index="instance_focused_index"
              :draw_mode="draw_mode"
              :selected_instance_index="selected_instance_index"
              :project_string_id="project_string_id"
              :polygon_point_hover_index="polygon_point_hover_index"
              :task="task"
              :instance_hover_index="instance_hover_index"
              :hovered_figure_id="hovered_figure_id"
              :instance_list="instance_list"
              :sequence_list="sequence_list_local_copy"
              :video_mode="image_annotation_ctx.video_mode"
              :label_file_list="label_list"
              @instance_update="instance_update($event)"
              @share_dialog_open="open_share_dialog"
              @focus_instance="focus_instance({index: $event})"
              @stop_focus_instance="focus_instance_show_all()"
              @open_issue_panel="$emit('open_issue_panel', $event)"
              @on_click_polygon_unmerge="polygon_unmerge"
              @on_click_polygon_merge="start_polygon_select_for_merge"
              @delete_polygon_point="polygon_delete_point_click_callback"
              @copy_instance="on_context_menu_copy_instance"
              @paste_instance="(num_frames, index_instance) => paste_instance(num_frames, index_instance, image_annotation_ctx.current_frame)"
              @paste_instance_on_next_frames="(num_frames, index_instance) => paste_instance(num_frames, index_instance, image_annotation_ctx.current_frame)"
              @create_instance_template="create_instance_template"
              @open_instance_history_panel="show_instance_history_panel"
              @close_instance_history_panel="close_instance_history_panel"
              ref="context_menu"
              @share_dialog_close="close_share_dialog"
              @close_context_menu="annotation_ui_context.show_context_menu = false"
              @hide_context_menu="hide_context_menu"
            />
          </div>

          <v_video
            v-if="image_annotation_ctx.video_mode"
            :style="style_max_width"
            v-show="!show_place_holder"
            class="pb-0"
            :current_video="current_video"
            :video_mode="image_annotation_ctx.video_mode"
            :max_num_image_buffer="label_settings.max_image_buffer"
            :player_height="'80px'"
            :parent_save="this.detect_is_ok_to_save"
            :video_primary_id="'video_primary'"
            @playing="video_playing = true"
            @pause="video_playing = false"
            @seeking_update="seeking_update($event)"
            :project_string_id="project_string_id"

            @go_to_keyframe_loading_started="set_keyframe_loading(true)"
            @go_to_keyframe_loading_ended="on_key_frame_loaded"
            @video_animation_unit_of_work="video_animation_unit_of_work($event)"
            @video_current_frame_guess="image_annotation_ctx.current_frame = parseInt($event)"
            @slide_start="detect_is_ok_to_save()"
            @request_save="detect_is_ok_to_save()"
            @go_to_keyframe="go_to_key_frame_handler()"
            @set_canvas_dimensions="set_canvas_dimensions()"
            @update_canvas="update_canvas"
            :current_video_file_id="current_video_file_id"
            :video_pause_request="video_pause"
            :video_play_request="video_play"
            :task="task"
            :loading="any_loading"
            :any_frame_saving="any_frame_saving"
            :view_only_mode="view_only_mode"
            :has_changed="has_changed"
            :canvas_width_scaled="canvas_width_scaled"
            ref="video_controllers"
          >
          </v_video>

          <v_sequence_list
            v-show="!show_place_holder"
            :video_mode="image_annotation_ctx.video_mode"
            class="pl-4"
            :project_string_id="
              project_string_id
                ? project_string_id
                : this.project_string_id
            "
            :view_only_mode="view_only_mode"
            :current_video_file_id="current_video_file_id"
            :current_frame="annotation_ui_context.current_image_annotation_ctx.current_frame"
            :label_file_id="annotation_ui_context.current_label_file ? annotation_ui_context.current_label_file.id : undefined"
            :current_sequence_annotation_core_prop="
              current_sequence_annotation_core_prop
            "
            @highest_sequence_number="highest_sequence_number = $event"
            @current_sequence_changed="
              current_sequence_from_sequence_component = $event
            "
            @loading_sequences="set_loading_sequences"
            @keyframe_click="change_keyframe"
            @sequence_list="sequence_list_local_copy = $event"
            :task="task"
            :current_label_file="annotation_ui_context.current_label_file"
            :video_playing="video_playing"
            :force_new_sequence_request="force_new_sequence_request"
            :label_file_list="label_list"
            :request_clear_sequence_list_cache="
              request_clear_sequence_list_cache
            "
            :label_settings="label_settings"
            ref="sequence_list"
          >
          </v_sequence_list>
        </div>
      </v-layout>
    </v-sheet>

    <instance_template_creation_dialog
      :schema_id="label_schema.id"
      :project_string_id="project_string_id"
      :instance_template="current_instance_template"
      ref="instance_template_creation_dialog"
    ></instance_template_creation_dialog>

    <v-snackbar
      v-model="snackbar_warning"
      v-if="snackbar_warning"
      top
      :timeout="5000"
      color="warning"
    >
      {{ snackbar_warning_text }}
      <v-btn color="primary" text @click="snackbar_warning = false">
        Close
      </v-btn>
    </v-snackbar>
    <v-snackbar
      v-model="show_snackbar_occlude_direction"
      v-if="show_snackbar_occlude_direction"
      top
      :timeout="5000"
      color="primary"
    >
      {{ snackbar_message }}
      <v-btn color="error" text @click="cancel_occlude_direction">
        Cancel
      </v-btn>
    </v-snackbar>
    <qa_carousel
      v-if="instance_list != undefined"
      ref="qa_carrousel"
      :annotation_show_on="annotation_show_on"
      :loading="image_annotation_ctx.loading || image_annotation_ctx.annotations_loading || full_file_loading"
      :instance_list="instance_list"
      :annotation_show_duration="annotation_show_duration_per_instance"
      @focus_instance="(index) => focus_instance({ index })"
      @change_item="annotation_show_change_item"
      @stop_carousel="annotation_show_activate"
    />


  </div>
</template>

<script lang="ts">
// @ts-nocheck
import axios from "../../../services/customInstance/index.js";
import Vue from "vue";
import * as SequenceUpdateHelpers from './utils/SequenceUpdateHelpers'
import autoborder_avaiable_alert from "./autoborder_avaiable_alert";
import ghost_canvas_available_alert from "./ghost_canvas_available_alert";
import canvas_current_instance from "../../vue_canvas/current_instance";
import canvas_instance_list from "../../vue_canvas/instance_list";
import ghost_instance_list_canvas from "../../vue_canvas/ghost_instance_list";
import v_bg from "../../vue_canvas/v_bg";
import v_text from "../../vue_canvas/v_text";
import target_reticle from "../../vue_canvas/target_reticle";
import context_menu from "../../context_menu/context_menu.vue";
import polygon_borders_context_menu from "../../context_menu/polygon_borders_context_menu.vue";

import current_instance_template from "../../vue_canvas/current_instance_template.vue";
import instance_template_creation_dialog from "../../instance_templates/instance_template_creation_dialog";


import {getContrastColor} from '../../../utils/colorUtils.js'
import {ellipse} from "../../vue_canvas/ellipse.js";
import {CommandManagerAnnotationCore} from "./annotation_core_command_manager.js";
import {CreateInstanceCommand} from "./commands/create_instance_command";
import {UpdateInstanceCommand} from "./commands/update_instance_command.ts";
import {
  ImageAnnotationCoordinatorRouter,
} from "../../vue_canvas/coordinators/ImageAnnotationCoordinatorRouter";
import {ImageAnnotationCoordinator} from "../../vue_canvas/coordinators/coordinator_types/ImageAnnotationCoordinator";
import {polygon} from "../../vue_canvas/polygon.js";
import {v4 as uuidv4} from "uuid";
import {cloneDeep} from "lodash";
import {Instance, SUPPORTED_IMAGE_CLASS_INSTANCE_TYPES} from "../../vue_canvas/instances/Instance";
import userscript from "./userscript/userscript.vue";
import {InstanceContext} from "../../vue_canvas/instances/InstanceContext";
import {CanvasMouseTools} from "../../vue_canvas/CanvasMouseTools";
import pLimit from "p-limit";
import qa_carousel from "./qa_carousel.vue";
import {File} from "../../../types/files";
import {update_file_metadata} from "../../../services/fileServices";
import {getInstanceTemplatesFromProject} from "../../../services/instanceTemplateService.js";
import {File} from "../../../types/files";
import v_sequence_list from "../../video/sequence_list"
import {
  initialize_instance_object,
  duplicate_instance,
  duplicate_instance_template,
  post_init_instance
} from '../../../utils/instance_utils.ts';
import {
  InteractionEvent,
  genImageAnnotationEvent,
  ImageAnnotationEventCtx, ImageInteractionEvent
} from "../../../types/InteractionEvent";
import {CoordinatorProcessResult} from "../../vue_canvas/coordinators/Coordinator";
import {Interaction} from "../../../types/Interaction";
import {BoxInstance} from "../../vue_canvas/instances/BoxInstance";
import {GlobalInstance} from "../../vue_canvas/instances/GlobalInstance";
import {LabelColourMap} from "../../../types/label_colour_map";
import {CanvasMouseCtx, MousePosition} from "../../../types/mouse_position";
import {ImageCanvasTransform} from "../../../types/CanvasTransform";
import {LabelFile} from "../../../types/label";
import {regenerate_cache} from "../../../services/fileServices"
import {get_model_run_list} from "../../../services/modelServices"
import {PolygonInstance} from "../../vue_canvas/instances/PolygonInstance";
import {PolygonAutoBorderTool} from "../../vue_canvas/advanced_tools/PolygonAutoBorderTool";
import {PolygonInstanceCoordinator} from "../../vue_canvas/coordinators/coordinator_types/PolygonInstanceCoordinator";
import {PolygonMergeTool} from "../../vue_canvas/advanced_tools/PolygonMergeTool";
import IssuesAnnotationUIManager from "./../issues/IssuesAnnotationUIManager";
import {BaseAnnotationUIContext, ImageAnnotationUIContext} from "../../../types/AnnotationUIContext";
import {AutoBorderContext} from "../../vue_canvas/advanced_tools/PolygonAutoBorderTool";
import { HotkeyListener } from "../../../utils/hotkey_listener";

Vue.prototype.$ellipse = new ellipse();
Vue.prototype.$polygon = new polygon();

/**
 * @vue-prop {string} project_string_id - Project id
 * @vue-prop {number} job_id - Job id
 * @vue-prop {object} job - An instance of a job
 * @vue-data {number} context_menu_hover_index - Instance index of hovered object in context_menu
 * @vue-data {boolean} show_context_menu - Flag to show or hide context_menu
 * @vue-event {boolean} hide_context_menu - Hides the visible context menu
 * @vue-event {boolean} context_menu_hover - Sets context_menu_hover_index when mousing over an instance object in canvas
 */

export default Vue.extend({
  name: "annotation_core",
  components: {
    v_sequence_list,
    autoborder_avaiable_alert,
    instance_template_creation_dialog,
    polygon_borders_context_menu,
    canvas_current_instance,
    current_instance_template,
    canvas_instance_list,
    ghost_instance_list_canvas,
    v_bg,
    v_text,
    target_reticle,
    context_menu,
    userscript,
    ghost_canvas_available_alert,
    qa_carousel,
  },
  props: {
    draw_mode: {
      type: Boolean,
      default: true
    },
    instance_type_list: {
      type: Array,
      default: []
    },
    instance_type: {
      type: String,
      default: "box"
    },
    project_string_id: {default: null, type: String},
    use_full_window: {type: Boolean, default: true},
    container_width: {type: Number, default: 500},
    container_height: {type: Number, default: 500},
    has_pending_frames: {type: Boolean, default: false},
    show_toolbar: {type: Boolean, default: false},
    create_instance_template_url: {type: String, required: true},
    instance_buffer_metadata: {type: Object, default: {}},
    get_userscript: {type: Function, required: true},
    save_loading_frames_list: {type: Array, default: []},
    filtered_instance_type_list_function: {type: Function, default: () => []},
    loading: {type: Boolean, default: false},
    has_changed: {type: Boolean, default: false},
    annotations_loading: {type: Boolean, default: false},
    url_instance_buffer: {required: true, type: String},
    working_file: {required: true, type: Object},
    instance_store: {required: true},
    task_image: {type: HTMLImageElement, default: null},
    task_instances: {type: Object, default: null},
    task_loading: {type: Boolean, default: null},
    label_schema: {required: true},
    // TODO review job_id being a prop vs job...
    job_id: {default: null},
    job: {default: null},
    task: {default: null},
    label_file_colour_map: {},
    label_list: {},
    task_mode_prop: {default: null},
    request_save: {},
    model_run_id_list: {default: null},
    model_run_color_list: {default: null},
    view_only_mode: {default: false,},
    finish_annotation_show: {default: false},
    global_attribute_groups_list: {type: Array, required: true},
    per_instance_attribute_groups_list: {type: Array, required: true},
    task_error: {type: Object, required: true},
    issues_ui_manager: {type: Object as IssuesAnnotationUIManager, required: true},
    annotation_ui_context: {type: Object as BaseAnnotationUIContext, required: true},
    image_annotation_ctx: {type: Object as ImageAnnotationUIContext, required: true},
    is_active: {type: Boolean, required: true, default: true},
    annotation_show_event: {default: null},
    hotkey_listener: {type: Object as HotkeyListener, required: true}
  },
  watch: {
    is_active: function (){
      this.canvas_element.style.cursor = ''
      if ( !this.hotkeyListenerScope ) {
        return
      }
      if ( this.is_active) {
        this.hotkey_listener.setScopes([this.hotkeyListenerScope])
      } else {
        this.hotkey_listener.removeScope(this.hotkeyListenerScope)
      }
    },
    global_instance: function(){
      this.$emit('global_instance_changed', this.working_file.id,  this.global_instance)
    },
    container_height: function(){
      this.update_canvas()
    },
    container_width: function(){
      this.update_canvas()
    },
    event_create_instance: function (newVal) {
      this.$emit('event_create_instance', newVal)
    },
    selected_instance_for_history: function (newVal) {
      this.$emit('selected_instance_for_history', newVal)
    },
    video_playing: function (newVal) {
      this.$emit('change_video_playing', newVal)
    },
    refresh: function (newVal) {
      this.$emit('refresh', this.refresh)
    },
    instance_list: function (newVal) {
      if (this.working_file.type === "image") {
        this.instance_store.set_instance_list(this.working_file.id, newVal)
        this.instance_store.set_file_type(this.working_file.id, this.working_file.type)
      }
    },
    instance_buffer_dict: {
      deep: true,
      handler: function (newVal, old) {
        if (this.working_file.type === "video") {
          this.instance_store.set_instance_list(this.working_file.id, newVal)
          this.instance_store.set_file_type(this.working_file.id, this.working_file.type)
        }
      },
    },
    finish_annotation_show: function (val) {
      if (val) this.annotation_show_on = false;
    },
    global_attribute_groups_list: function () {
      this.get_and_set_global_instance(this.instance_list)
    },
    canvas_scale_global: function (newVal, oldVal) {
      this.on_canvas_scale_global_changed(newVal);
    },
    task: {
      handler(newVal, oldVal) {
        if (newVal != oldVal) {
          this.on_change_current_task();
        }
      },
    },
    model_run_id_list(newVal, oldVal) {
      if (newVal && newVal.length > 0) {
        this.fetch_model_run_list();
      } else {
        this.model_run_list = [];
      }
    },
    mouse_computed(newval, oldval) {
      // We don't want to create a new object here since the reference is used on all instance types.
      // If we create a new object we'll lose the reference on our class InstanceTypes

      this.mouse_down_delta_event.x = parseInt(newval.delta_x - oldval.delta_x);
      this.mouse_down_delta_event.y = parseInt(newval.delta_y - oldval.delta_y);
    },

    // This is in part when annotation_core is used by say verison viewer
    // should we be watching current_file_prop?
    instance_select_for_issue(newval, oldval) {
      if (newval) {
        this.update_canvas();
        this.issues_ui_manager.snackbar_issues = true;
        this.$emit('draw_mode_change', false)
        this.label_settings.allow_multiple_instance_select = true;
      } else {
        this.issues_ui_manager.snackbar_issues = false;
      }
    },
    instance_select_for_merge(newval, oldval) {
      if (newval) {
        this.update_canvas();
        this.snackbar_merge_polygon = true;
        this.$emit('draw_mode_change', false)
        this.instances_to_merge = [];
        this.label_settings.allow_multiple_instance_select = true;
      } else {
        this.snackbar_merge_polygon = false;
        this.label_settings.allow_multiple_instance_select = false;
        this.instances_to_merge = [];
        this.clear_selected();
      }
    },
    request_save: function (bool) {
      if (bool == true) {
        this.$emit('save');
      }
    },
    $route: "page_refresh",
    draw_mode: function (newVal) {
      this.polygon_point_hover_index = null;
      this.clear_selected();
      this.$emit('draw_mode_change', newVal)
    },
    show_modify_an_issue: function () {
      if (this.show_modify_an_issue == true) {
        this.label_settings.show_ghost_instances = false;
        this.label_settings.ghost_instances_closed_by_open_view_edit_panel = true;
      } else {
        if (this.label_settings.ghost_instances_closed_by_open_view_edit_panel == true) {
          this.label_settings.show_ghost_instances = true;
          this.label_settings.ghost_instances_closed_by_open_view_edit_panel = false;
        }
      }
    },
    annotation_show_event: function (event) {
      this.annotation_show_activate(event)
    }

  },
  data: function() {
    return {
      degrees: 0,
      mouse_wheel_button: false,
      global_instance: undefined,

      locked_editing_instance: null as Instance,
      current_interaction: null as Interaction,
      current_drawing_box_instance: new BoxInstance(),
      current_drawing_polygon_instance: new PolygonInstance(),
      show_snackbar_occlude_direction: false,
      guided_nodes_ordinal: 1,
      instance_rotate_control_mouse_hover: null,
      actively_drawing_instance_template: null,
      z_key: false,
      shift_key: false,
      snapped_to_instance: undefined,
      canvas_wrapper: undefined,

      file_cant_be_accessed: null,
      file_cant_be_accessed_error: null,

      snackbar_paste_message: '',
      ghost_instance_hover_index: null,
      default_instance_opacity: 0.25,
      model_run_list: null,
      ghost_instance_hover_type: null,
      ghost_instance_list: [],
      selected_instance_list: [],

      show_default_navigation: true,
      snackbar_merge_polygon: false,

      parent_merge_instance: null,
      hovered_figure_id: null,
      parent_merge_instance_index: null,
      instances_to_merge: [],

      event_create_instance: undefined,

      selected_instance_for_history: undefined,
      show_instance_history: false,
      regenerate_file_cache_loading: false,
      display_refresh_cache_button: false,
      canvas_mouse_tools: undefined as CanvasMouseTools,
      show_custom_snackbar: false,
      custom_snackbar_timeout: -1,
      custom_snackbar_text_color: 'white',
      custom_snackbar_color: -1,
      snackbar_message_secondary: '',
      custom_snackbar_show_close_button: true,
      snackbar_message: undefined,
      selected_instance_template: undefined,
      instance_template_start_point: undefined,
      is_moving_cuboid_corner: false,
      instance_context: new InstanceContext(),
      instance_template_draw_started: false,
      mouse_down_delta_event: {x: 0, y: 0},
      canvas_alert_x: undefined,
      canvas_alert_y: undefined,
      original_edit_instance: undefined,
      original_edit_instance_index: undefined,
      loading_sequences: false,
      command_manager: undefined,

      show_snackbar_paste: false,

      sequence_list_local_copy: null,
      current_issue: undefined,
      share_dialog_open: false,
      show_modify_an_issue: false,
      ellipse_hovered_corner: undefined,
      ellipse_hovered_corner_key: undefined,
      ellipse_hovered_instance: undefined,
      ellipse_hovered_instance_index: undefined,

      drawing_curve: false,
      curve_hovered_point: undefined,

      request_clear_sequence_list_cache: null,

      user_requested_file_id: null,

      instance_clipboard: undefined,
      media_core_height: 0,
      emit_instance_hover: true, // ie can set to true to get hover updates

      // Sequence design doc https://docs.google.com/document/d/1EVvPke7Ms25KsmDKpwrQcqB1k6pgB5SNs5WDbwGmLCo/edit#heading=h.oo1xxxn8bkpp

      // sending data from this component to sequence component
      current_sequence_annotation_core_prop: {
        id: null,
        number: null,
      },

      // canonical source, we always use this ie to see current sequence
      current_sequence_from_sequence_component: {
        id: null,
        number: null,
      },

      force_new_sequence_request: null,
      issue_mouse_position: undefined,

      lock_point_hover_change: false,

      space_bar: false,

      mouse_down_limits_result: true,

      highest_sequence_number: 0,

      instance_buffer_dict: {},

      is_editing_ui_schema: true,

      // Order here is important for corner moving. First one keeps y coord fixed and second one keeps x coord fixed.
      lateral_edges: {
        bot_right: ["top_right", "bot_left"],
        bot_left: ["top_left", "bot_right"],

        top_left: ["bot_left", "top_right"],
        top_right: ["bot_right", "top_left"],
      },
      opposite_edges_map: {
        bot_left: "top_right",
        bot_right: "top_left",
        top_left: "bot_right",
        top_right: "bot_left",
      },

      cuboid_force_move_face: false,
      cuboid_current_drawing_face: undefined,
      ellipse_current_drawing_face: undefined,

      is_actively_drawing: false,
      is_actively_resizing: false,

      save_count: 0,

      save_error: {},
      error: {},
      instance_buffer_error: {},


      current_version: null,
      source_control_menu: false,

      show_annotations: true,

      snackbar_warning: false,
      snackbar_warning_text: null, // "text" or "message" better name?

      gold_standard_file: {
        instance_list: [], // careful, need this to not be null for vue canvas to work as expected
        id: null,
      },

      annotation_show_on: false,
      annotation_show_type: "file",
      annotation_show_current_instance: 0,
      annotation_show_duration_per_instance: 2000,
      finish_annotation_show_local: false,
      annotation_show_progress: 0,
      annotation_show_timer: null,
      annotation_show_revert: 2,

      polygon_type_list: ["closed"],

      instance_sub_type: "closed",

      // this gets set from image or video
      // additionall used as a nuetral reference when it applies to both types
      original_media_width: 1,
      original_media_height: 1,

      seeking: false,

      video_playing: false, // bool of if playing or paused
      video_play: null, // work around for requests being sent to video.vue
      video_pause: null,

      current_video: {
        frame_count: 0,
        current_frame: 0,
      },

      cuboid_current_rear_face: undefined,
      cuboid_face_hover: undefined,
      alert_info_drawing: true,

      brightness_menu: false,

      // Contains the index position in the array this.instance_list, corresponding to the instance that
      // the mouse is hovering at any given time.
      instance_hover_index: null,
      issue_hover_index: null,

      // Contains the instance type that's being hovered at any given time.
      // Can be any of ['polygon', 'box', 'line', 'point', 'cuboid']
      instance_hover_type: null,

      // some instances types still need second level hover concept
      box_edit_point_hover: null,
      cuboid_corner_move_point: null,
      polygon_point_hover_index: null,

      polygon_point_click_index: null,
      polygon_click_index: null,

      message: "",
      refresh: null,
      canvas_element: null,

      current_label_file: {
        id: null,
        label: {},
      },

      html_image: new Image(), // our canvas expects an image at init

      save_on_change: true,
      complete_on_change: true,
      mouse_position: {
        raw: {
          x: 0,
          y: 0,
        },
        x: 150,
        y: 150,
      },

      instance_list: [],
      show_text_file_place_holder: false,

      current_polygon_point_list: [],

      current_video_file_id: null,

      zoom_settings: {
        ratio: 2,
        size: 50,
        location: "target_reticle",
        on: false,
      },

      mouse_request_time: null,

      mouse_down_position: {
        request_time: null,
        x: 0,
        y: 0,
        raw: {
          x: 0,
          y: 0,
        },
      },

      instance_frame_start: 0,
      canvas_rectangle: null,
      loading_instance_templates: false,
      instance_template_list: [],
      auto_border_context: {
        auto_border_polygon_p1: undefined,
        auto_border_polygon_p1_index: undefined,
        auto_border_polygon_p1_figure: undefined,
        auto_border_polygon_p1_instance_index: undefined,
        auto_border_polygon_p2: undefined,
        auto_border_polygon_p2_index: undefined,
        auto_border_polygon_p2_figure: undefined,
        auto_border_polygon_p2_instance_index: undefined,
        show_polygon_border_context_menu: false,
        show_snackbar_auto_border: false,
      } as AutoBorderContext,

      interval_autosave: null,
      full_file_loading: false, // For controlling the loading of the entire file + instances when changing a file.

      canvas_scale_local: 1, // for actually scaling dimensions within canvas

      canvas_translate: {
        x: 0,
        y: 0,
      },

      zoom_canvas: 1,
      error_no_permissions: {},
      snap_to_edges: 5,

      metadata: {
        length: null,
      },

      instance_focused_index: null,
      instance_selection_hotkeys_index: null,

      window_width_from_listener: 1280,
      window_height_from_listener: 650,
      hotkeyListenerScope: null,
    };
  },
  computed: {
    is_fully_zoomed_out() {
      return this.image_annotation_ctx.zoom_value === this.canvas_mouse_tools.canvas_scale_global
    },
    canvas_id: function(){
      return `my_canvas_${this.working_file.id}`
    },
    label_settings: {
      get: function () {
        return this.image_annotation_ctx.label_settings
      },
      set: function (settings) {
        return settings
      }
    },
    filtered_instance_type_list: function () {
      const filtered_instance_type_list = this.filtered_instance_type_list_function(this.instance_type_list)
      return filtered_instance_type_list
    },
    label_file_map: function () {
      let result = {}
      for (let elm of this.label_list) {
        result[elm.id] = elm
      }
      return result
    },
    actively_drawing_keypoints_instance: function () {
      if (this.actively_drawing_instance_template && this.actively_drawing_instance_template.instance_list) {
        return this.actively_drawing_instance_template.instance_list[0]
      }

    },
    current_keypoints_instance: function () {
      if (this.current_instance_template && this.current_instance_template.instance_list) {
        return this.current_instance_template.instance_list[0]
      }

    },
    any_frame_saving: function () {
      return this.save_loading_frames_list.length > 0;
    },
    clipboard: function () {
      return this.$store.getters.get_clipboard;
    },
    instance_template_dict: function () {
      let result = {};
      for (let i = 0; i < this.instance_template_list.length; i++) {
        const curr = this.instance_template_list[i];
        result[curr.id] = {
          ...curr,
        };
      }
      return result;
    },
    current_instance_template: function () {
      return this.instance_template_dict[this.instance_type];
    },
    is_keypoint_template: function () {
      if (!this.current_instance_template) {
        return false;
      }

      if (
        this.current_instance_template.instance_list.filter(
          (i) => i.type === "keypoints"
        ).length > 0
      ) {
        return true;
      }

      return false;
    },
    instance_template_selected: function () {
      let result = false;
      this.instance_template_list.forEach((inst) => {
        if (inst.id === this.instance_type) {
          result = true;
        }
      });
      return result;
    },
    target_reticle_type: function () {
      if (["box", "cuboid"].includes(this.instance_type)) {
        return "canvas_cross";
      } else if (
        ["polygon", "point", "line", "ellipse", "curve"].includes(
          this.instance_type
        )
      ) {
        return "small_cross";
      } else {
        return "canvas_cross";
      }
    },
    show_target_reticle: function () {
      if (
        this.view_only_mode == true ||
        this.space_bar == true ||
        this.any_loading == true
      ) {
        return false;
      }

      if (this.seeking) {
        return false;
      }

      if (!this.draw_mode) {
        return false;
      }

      return true;
    },
    is_mouse_down() {
      return this.$store.state.annotation_state.mouse_down
    },
    mouse_computed: function () {
      if (this.$store.state.annotation_state.mouse_down == false) {
        // Becuase we only want this to update when the mouse is down, otherwise for example starting point for event is misaligned.
        return {
          delta_x: 0,
          delta_y: 0,
        };
      }
      let delta_x = this.mouse_position.x - this.mouse_down_position.x;
      let delta_y = this.mouse_position.y - this.mouse_down_position.y;
      delta_x = parseInt(delta_x);
      delta_y = parseInt(delta_y);

      return {
        delta_x: delta_x,
        delta_y: delta_y,
      };
    },

    instance_select_for_issue: function () {
      return this.$store.getters.get_instance_select_for_issue;
    },
    instance_select_for_merge: function () {
      return this.$store.getters.get_instance_select_for_merge;
    },
    hovered_instance: function () {
      if (!this.instance_list) {
        return;
      }
      if (this.instance_hover_index != undefined) {
        return;
      }
    },
    selected_instance: function () {
      if (!this.instance_list) {
        return;
      }
      if (
        this.selected_instance_list &&
        this.selected_instance_list.length > 0
      ) {
        return this.selected_instance_list[0];
      }
      for (let i = 0; i < this.instance_list.length; i++) {
        if (this.instance_list[i].selected) {
          return this.instance_list[i];
        }
      }
    },
    selected_instance_index: function () {
      if (!this.instance_list) {
        return;
      }
      for (let i = 0; i < this.instance_list.length; i++) {
        if (this.instance_list[i].selected) {
          return i;
        }
      }
    },
    view_issue_mode: function () {
      return this.$store.getters.get_view_issue_mode;
    },

    show_place_holder() {
      // task_image is preloaded image on teh task context
      if (this.task_loading) return true
      if (this.task_image) return false

      return this.full_file_loading;
    },
    any_loading() {
      /* Does not include save_loading because we currently
       * pass this to v_bg which flashes screen when showing loading
       * Something to review.
       */
      return (
        this.full_file_loading ||
        this.image_annotation_ctx.annotations_loading ||
        this.image_annotation_ctx.loading ||
        this.loading_sequences
      );
    },

    canvas_scale_global() {
      // https://diffgram.readme.io/docs/canvas_scale_global

      if (this.label_settings.canvas_scale_global_is_automatic == false) {
        return this.label_settings.canvas_scale_global_setting;
      }

      let image_size_width = 1920; // default
      let image_size_height = 1280;


      if (this.original_media_width) {
        image_size_width = this.original_media_width;
        image_size_height = this.original_media_height;
      }

      let toolbar_height = 80;

      if (document.getElementById("media_core")) {
        this.media_core_height =
          document.getElementById("media_core").__vue__.height;
      } else {
        this.media_core_height = 0;
      }
      if (this.task) {
        this.media_core_height = 0;
      }

      let middle_pane_height, middle_pane_width;
      if(this.use_full_window){

        let extra_spacer = 60;

        middle_pane_width =
          this.window_width_from_listener -
          this.label_settings.left_nav_width -
          extra_spacer;

        middle_pane_height =
          this.window_height_from_listener -
          toolbar_height -
          this.media_core_height;

      } else{
        middle_pane_width = this.container_width
        middle_pane_height = this.container_height
      }

      if (this.image_annotation_ctx.video_mode == true) {
        // TEMP this is solving wrong problem
        // In preview mode it def makes more sense for sequences to be to the right of video
        let video_offset = 80;
        if (this.media_core_height) {
          video_offset = 200;
        } else {
          video_offset = 80;
        }
        if(this.use_full_window){
          middle_pane_height = middle_pane_height - video_offset;
        }

      }
      // careful height comparison middle_pane_width to height, width to width
      let height_scaled = middle_pane_height / image_size_height;
      let width_scaled = middle_pane_width / image_size_width;

      // careful to do the scale first, so we do the min of scaled values
      let lowest_size = Math.min(height_scaled, width_scaled);
      let new_size = Math.round(lowest_size * 100) / 100;

      this.label_settings.canvas_scale_global_setting = new_size;

      return new_size;

    },

    canvas_width_scaled: function (): number {
      if(this.use_full_window){
        return this.original_media_width * this.canvas_scale_global;
      } else{
        return this.original_media_width * this.canvas_scale_global;
        // return this.container_width;
      }

    },

    canvas_height_scaled: function (): number {
      if(this.use_full_window){
        return this.original_media_height * this.canvas_scale_global;
      } else{
        // return this.container_height;
        return this.original_media_height * this.canvas_scale_global;
      }

    },

    canvas_scale_combined: function (): number {
      return this.canvas_scale_local * this.canvas_scale_global;
    },

    canvas_transform: function (): ImageCanvasTransform {
      let transform: ImageCanvasTransform = {
        canvas_scale_global: this.canvas_scale_global,
        canvas_scale_local: this.canvas_scale_local,
        canvas_scale_combined: this.canvas_scale_local * this.canvas_scale_global,
        translate: this.canvas_translate,
        canvas_width: this.original_media_width,
        canvas_height: this.original_media_height,
        zoom: this.zoom_canvas,
      }
      return transform
    },

    canvas_filters: function () {
      return {
        brightness: this.label_settings.filter_brightness,
        contrast: this.label_settings.filter_contrast,
        grayscale: this.label_settings.filter_grayscale,
      };
    },

    current_polygon_point: function () {
      var x = parseInt(this.mouse_down_position.x);
      var y = parseInt(this.mouse_down_position.y);

      return {
        x: x,
        y: y,
        selected: false,
      };
    },

    current_instance: function () {

      if (SUPPORTED_IMAGE_CLASS_INSTANCE_TYPES.includes(this.instance_type)) {
        return this.build_current_instance_class()
      }
      // Do we actually need to cast this as Int here if db handles it?
      var x_min = parseInt(this.mouse_down_position.x);
      var y_min = parseInt(this.mouse_down_position.y);
      var x_max = parseInt(this.mouse_position.x);
      var y_max = parseInt(this.mouse_position.y);

      // Handle inverting origin point
      if (x_max < x_min) {
        x_max = parseInt(this.mouse_down_position.x);
        x_min = parseInt(this.mouse_position.x);
      }

      if (y_max < y_min) {
        y_max = parseInt(this.mouse_down_position.y);
        y_min = parseInt(this.mouse_position.y);
      }

      if (x_min < 0) {
        x_min = 0;
      }
      if (y_min < 0) {
        y_min = 0;
      }

      // testing
      //x_max = 99999
      //y_max = 99999

      // 480 is from 0 to 479.
      if (this.original_media_width) {
        if (x_max >= this.original_media_width) {
          x_max = this.original_media_width - 1;
        }

        if (y_max >= this.original_media_height) {
          y_max = this.original_media_height - 1;
        }
      }

      var width = x_max - x_min;
      var height = y_max - y_min;

      // Maybe if != cuboid this is null?

      if (this.instance_type == "cuboid") {
        let front_face_width = width;
        let front_face_height = height;
        if (
          this.cuboid_current_drawing_face === "second" &&
          this.cuboid_current_rear_face
        ) {
          front_face_width = this.cuboid_current_rear_face.width;
          front_face_height = this.cuboid_current_rear_face.height;
        }
        var front_face = {
          width: front_face_width,
          height: front_face_height,
          top_left: {
            x: parseInt(this.mouse_position.x) - front_face_width,
            y: parseInt(this.mouse_position.y) - front_face_height,
          },
          top_right: {
            x: parseInt(this.mouse_position.x),
            y: parseInt(this.mouse_position.y) - front_face_height,
          },
          bot_left: {
            x: parseInt(this.mouse_position.x) - front_face_width,
            y: parseInt(this.mouse_position.y),
          },
          bot_right: {
            x: parseInt(this.mouse_position.x),
            y: parseInt(this.mouse_position.y),
          },
        };

        // default rear face to front face?
        // or "hide it"?
        // setting = to front face directly links in way we don't want
        // Lock rear face after first face has been drawn.
        if (
          this.cuboid_current_drawing_face === "second" &&
          this.cuboid_current_rear_face
        ) {
          var rear_face = this.cuboid_current_rear_face;
        } else {
          var rear_face = {
            width: width,
            height: height,
            top_left: {
              x: x_min,
              y: y_min,
            },
            top_right: {
              x: x_min + width,
              y: y_min,
            },
            bot_left: {
              x: x_min,
              y: y_min + height,
            },
            bot_right: {
              x: x_max,
              y: y_max,
            },
          };
        }
      } else {
        var front_face = null;
        var rear_face = null;
      }

      let number = null;
      let sequence_id = null;
      if (this.image_annotation_ctx.video_mode == true) {
        number = this.current_sequence_from_sequence_component.number;
        sequence_id = this.current_sequence_from_sequence_component.id;
      }
      let p1, cp, p2;
      if (
        this.instance_type === "curve" &&
        this.current_polygon_point_list.length > 0
      ) {
        p1 = {
          x: this.current_polygon_point_list[0].x,
          y: this.current_polygon_point_list[0].y,
        };
        if (this.current_polygon_point_list.length >= 2) {
          cp = {
            x:
              (this.current_polygon_point_list[0].x +
                this.current_polygon_point_list[1].x) /
              2,
            y:
              (this.current_polygon_point_list[0].y +
                this.current_polygon_point_list[1].y) /
              2,
          };
          p2 = {
            x: this.current_polygon_point_list[1].x,
            y: this.current_polygon_point_list[1].y,
          };
        }
      }

      let instance_data = {
        x_min: x_min,
        y_min: y_min,
        center_x: this.instance_type === "ellipse" ? x_min : undefined,
        center_y: this.instance_type === "ellipse" ? y_min : undefined,
        x_max: x_max,
        y_max: y_max,
        p1: p1,
        cp: cp,
        p2: p2,
        edges: [],
        nodes: [],
        auto_border_polygon_p1: this.auto_border_context.auto_border_polygon_p1,
        auto_border_polygon_p2: this.auto_border_context.auto_border_polygon_p2,
        cuboid_current_drawing_face: this.cuboid_current_drawing_face,
        front_face: front_face,
        angle: 0,
        rear_face: rear_face,
        width: width,
        height: height,
        label_file: this.annotation_ui_context.current_label_file,
        label_file_id: this.annotation_ui_context.current_label_file ? this.annotation_ui_context.current_label_file.id : null,
        selected: "false",
        number: number,
        machine_made: false,
        type: this.instance_type,
        points: this.current_polygon_point_list,
        sequence_id: sequence_id,
        soft_delete: false, // default for new instances
      };
      this.calculate_min_max_points(instance_data);
      return instance_data;
    },

    current_label_file_id: function () {
      if (this.annotation_ui_context.current_label_file) {
        return this.annotation_ui_context.current_label_file.id;
      } else {
        return null;
      }
    },

    save_text() {
      if (this.save_on_change == true) {
        return "Saving automatically";
      } else {
        return "Saving manually";
      }
    },

    canvas_style: function () {
      return `width: ${this.canvas_width_scaled}px; height: ${this.canvas_height_scaled}px`;
    },

    style_max_width: function () {
      return "max-width:" + this.canvas_width_scaled + "px";
    },
  },

  created() {
    this.created();
    // put all created stuff in here, workaround so we can call created internal refresh concept
  },

  beforeDestroy() {

    clearInterval(this.interval_autosave);
    this.detect_is_ok_to_save();
    this.remove_event_listeners();

    // watcher removal
    this.save_watcher();
    this.save_and_complete_watcher();
    this.refresh_video_buffer_watcher();

    this.hotkey_listener.deleteScope(this.hotkeyListenerScope)

    this.cleanUpHotkeys(this.hotkeyListenerScope)
  },

  mounted() {
    if (window.Cypress) {
      window.AnnotationCore = this;
    }
    this.mounted();

    this.hotkeyListenerScope = `image ${this.working_file.hash}`

    this.setupHotkeys(this.hotkeyListenerScope)

    if(this.is_active && this.hotkey_listener) {
      this.hotkey_listener.setScopes([this.hotkeyListenerScope])
    }

    if (
      this.annotation_ui_context.working_file_list[0].id === this.annotation_ui_context.working_file.id
    ) {
      this.$emit('activate_hotkeys')
    }
  },
  // TODO 312 Methods!! refactor in multiple files and classes.
  methods: {

    cleanUpHotkeys(scope) {
      this.hotkey_listener.deleteScope(scope)
      this.hotkey_listener.removeFilter(this.hotkeyListenerFilter)
    },

    hotkeyListenerFilter() {
      return !this.annotation_ui_context.show_context_menu
    },

    setupHotkeys(scope) {

      this.hotkey_listener.addFilter(this.hotkeyListenerFilter)

      this.hotkey_listener.onKeydown({ keys: 's', scope }, () => {
        this.$emit('save');
      })

      this.hotkey_listener.onKeydown({ keys: 'f', scope }, () => {
        this.trigger_instance_focus()
      })

      this.hotkey_listener.onKeydown({ keys: 'left,a', scope }, () => {
        this.toggle_shift_frame_left()
      })

      this.hotkey_listener.onKeydown({ keys: 'shift+left,shift+a', scope }, () => {
        this.toggle_file_change_left()
      })

      this.hotkey_listener.onKeydown({ keys: 'right,d', scope }, () => {
        this.toggle_shift_frame_right()
      })

      this.hotkey_listener.onKeydown({ keys: 'shift+right,shift+d', scope }, () => {
        this.toggle_file_change_right()
      })

      this.hotkey_listener.onKeydown({ keys: 'shift+t', scope }, () => {
        this.toggle_instance_transparency()
      })

      this.hotkey_listener.onKeydown({ keys: 'shift+o,o', scope }, () => {
        this.toggle_show_hide_occlusion()
      })

      this.hotkey_listener.onKeydown({ keys: 'shift+n', scope }, () => {
        this.jump_to_next_instance_frame()
      })

      this.hotkey_listener.onKeydown({ keys: 'x', scope }, () => {
        this.reset_drawing()
      })

      this.hotkey_listener.onKeydown({ keys: 'shift+c', scope }, () => {
        this.complete_and_move()
      })

      this.hotkey_listener.onKeydown({ keys: 'esc', scope }, () => {
        this.toggle_escape_key()
      })

      this.hotkey_listener.onKeydown({ keys: 'ctrl+c', scope, platformDependent: true }, () => {
        this.copy_instance(true)
      })

      this.hotkey_listener.onKeydown({ keys: 'ctrl+v', scope, platformDependent: true }, () => {
        this.paste_instance(undefined, undefined, this.image_annotation_ctx.current_frame)
      })

      this.hotkey_listener.onKeydown({ keys: 'shift+r', scope }, () => {
        this.annotation_show_activate(
          !this.task && this.working_file && this.working_file.id ? 'file' : 'task'
        )
      })

      this.hotkey_listener.onKeydown({ keys: 'ctrl+z', scope, platformDependent: true }, () => {
        this.undo();
      })

      this.hotkey_listener.onKeydown({ keys: 'ctrl+y', scope, platformDependent: true }, () => {
        this.redo();
      })

      this.hotkey_listener.onKeydown({ keys: 'n', scope }, () => {
        this.force_new_sequence_request = Date.now();
      })

      this.hotkey_listener.onKeydown({ keys: 'h', scope }, () => {
        this.show_annotations = !this.show_annotations;
      })

      this.hotkey_listener.onKeydown({ keys: 'g', scope }, () => {
        this.label_settings.show_ghost_instances =
          !this.label_settings.show_ghost_instances;
      })

      this.hotkey_listener.onKeydown({ keys: 't', scope }, () => {
        this.insert_tag_type();
      })

      this.hotkey_listener.onKeydown({ keys: 'r', scope }, () => {
        const file = this.working_file
        if ( !file.image ) {
          return
        }
        let current_rotation_degrees = file.image.rotation_degrees
        current_rotation_degrees += 90
        if (current_rotation_degrees == 360) {
          current_rotation_degrees = 0
        }
        this.on_image_rotation(current_rotation_degrees);
      })

      this.hotkey_listener.onKeydown({ keys: 'enter', scope }, () => {
        if (this.instance_type == "polygon") {
          this.finish_polygon_drawing(event)
        }
      })

      this.hotkey_listener.onKeydown({ keys: 'ctrl+left', scope, platformDependent: true }, (event) => {
        this.rotate_instance_selection_hotkeys_index('previous')
      })

      this.hotkey_listener.onKeydown({ keys: 'ctrl+right', scope, platformDependent: true }, () => {
        this.rotate_instance_selection_hotkeys_index('next')
      })

      this.hotkey_listener.onKeydown({ keys: 'l', scope }, () => {
        let instance = this.selected_instance
        if(instance){
          this.$emit('open_label_change_dialog', instance.id)
        }
      })

      this.hotkey_listener.onKeydown({ keys: 'space', scope }, () => {
        if (this.annotation_show_on) {
          return
        }
        this.toggle_pause_play();
        this.canvas_element.style.cursor = "pointer";
      })

      this.hotkey_listener.onKeydown({ keys: 'del', scope }, () => {
        this.delete_instance();
      })

      this.hotkey_listener.onKeydown({ keys: 'z', scope }, () => {
        this.z_key = true
      })

      this.hotkey_listener.onKeyup({ keys: 'z', scope }, () => {
        this.z_key = false
      })

      this.hotkey_listener.onSpecialKeydown({ keys: 'shift', scope }, () => {
        this.shift_key = true
      })

      this.hotkey_listener.onSpecialKeyup({ keys: 'shift', scope }, () => {
        this.shift_key = false
      })
    },


    rotate_instance_selection_hotkeys_index: function(dir: string = 'next'){
      if(this.draw_mode){
        this.$emit('draw_mode_change', false)
      }
      if(this.instance_selection_hotkeys_index == undefined){
        this.instance_selection_hotkeys_index = 0
      }
      else if(this.instance_selection_hotkeys_index < this.instance_list.length - 1){
        if(dir === 'next'){
          this.instance_selection_hotkeys_index += 1
        } else{
          if(this.instance_selection_hotkeys_index === 0){
            this.instance_selection_hotkeys_index = this.instance_list.length - 1
          } else{
            this.instance_selection_hotkeys_index -= 1
          }

        }

      } else if(this.instance_selection_hotkeys_index === this.instance_list.length - 1){
        if(dir === 'next'){
          this.instance_selection_hotkeys_index = 0
        } else{
          this.instance_selection_hotkeys_index -= 1
        }

      }
      let instance = this.instance_list[this.instance_selection_hotkeys_index]

      if (SUPPORTED_IMAGE_CLASS_INSTANCE_TYPES.includes(instance.type)) {
        let annotation_ctx = this.build_ann_event_ctx()
        let coord_router: ImageAnnotationCoordinatorRouter = this.create_coordinator_router()
        let coordinator = coord_router.generate_from_instance(instance, instance.type)
        // Simulate select() interaction
        let dummyInteractionCtx = new ImageInteractionEvent({annotation_ctx: annotation_ctx})
        coordinator.select(dummyInteractionCtx)
      } else{
        instance.selected = true
      }
      this.instance_selected(instance)
    },
    clear_unsaved: function() {
      this.instance_list = this.annotation_ui_context.instance_store.clear_unsaved(this.working_file.id)
    },
    cancel_polygon_merge: function () {
      this.polygon_merge_tool = null
    },
    change_keyframe: function (keyframe) {
      if (this.image_annotation_ctx.video_mode) {
        if (this.image_annotation_ctx.current_frame !== keyframe && this.$refs.video_controllers) {
          this.$refs.video_controllers.go_to_keyframe(keyframe);
        }
      }
    },
    build_current_instance_class: function (): Instance {
      let instance_type_mapper = {
        'box': this.current_drawing_box_instance,
        'polygon': this.current_drawing_polygon_instance
      }
      return instance_type_mapper[this.instance_type]
    },
    on_image_rotation: async function (rotation_degrees: number) {
      try {
        await this.detect_is_ok_to_save()
        this.image_annotation_ctx.loading = true
        const file = this.working_file
        let [updated_file, err] = await update_file_metadata(
          this.project_string_id,
          file.id,
          {rotation_degrees: rotation_degrees}
        )
        if (err) {
          console.error(err)
          return
        }
        file.image.rotation_degrees = updated_file.image.rotation_degrees
        this.$store.commit('display_snackbar', {
          text: 'Image rotated.',
          color: 'success'
        })
        await this.image_update_core(file)
        this.image_annotation_ctx.loading = false
      } catch (e) {
        console.error(e)
      }
    },
    on_change_label_schema: function (schema) {
      this.$emit('change_label_schema', schema)
    },
    on_keypoints_mode_set: function (mode) {
      this.instance_context.keypoints_draw_mode = mode;
      this.current_instance_template.mode = mode;
      if (this.current_instance_template.mode === 'guided' && this.draw_mode) {
        this.show_snackbar_guided_keypoints_drawing(1)
      }
    },
    show_snackbar_guided_keypoints_drawing(ordinal) {
      let instance = this.current_keypoints_instance;
      if (!instance) {
        return
      }
      let has_undefined_ordinals = instance.nodes.find(elm => elm.ordinal == undefined);
      if (has_undefined_ordinals) {
        instance.nodes = instance.nodes.map((n, i) => {
          return {
            ...n,
            ordinal: i
          }
        })
      }

      let node = instance.nodes.find(elm => elm.ordinal === ordinal);
      if (!node) {
        return
      }
      let color = node.color ? node.color.hex : 'primary';
      let textColor = node.color ? getContrastColor(node.color.hex) : 'white';
      this.show_snackbar(`${node.ordinal}. "${node.name}"`,
        color,
        -1,
        false,
        textColor,
        'Hold "N" while drawing to mark occluded. Esc to exit.'
      )
    },

    on_canvas_scale_global_changed: async function (new_scale) {
      if (!new_scale) {
        return;
      }
      // Force a canvas reset when changing global scale.
      if (!this.canvas_element) {
        return;
      }
      this.label_settings.canvas_scale_global_setting = new_scale;
      this.canvas_mouse_tools.canvas_scale_global = new_scale;
      this.canvas_mouse_tools.scale = new_scale;
      this.canvas_element_ctx.clearRect(
        0,
        0,
        this.canvas_element.width,
        this.canvas_element.height
      );
      this.canvas_element_ctx.resetTransform();
      this.canvas_element_ctx.scale(new_scale, new_scale);
      this.canvas_element.width += 0;
      this.canvas_mouse_tools.canvas_width = this.original_media_width;
      this.canvas_mouse_tools.canvas_height = this.original_media_height;
      this.refresh_instances_in_viewport(this.instance_list)

      await this.$nextTick();
      this.canvas_mouse_tools.reset_transform_with_global_scale();
      this.image_annotation_ctx.zoom_value = this.canvas_mouse_tools.scale;
      this.update_canvas();
    },

    update_smooth_canvas: function (event) {
      if (!this.canvas_element_ctx) {
        return
      }
      this.canvas_element_ctx.imageSmoothingEnabled = event
    },
    update_large_annotation_volume_performance_mode: function (event) {
      if (event === true) {
        this.set_performance_optimizations_on()
      } else {
        this.set_performance_optimizations_off()
      }
    },
    cancel_merge: function () {
      this.$store.commit("set_instance_select_for_merge", false);
      this.polygon_merge_tool = null
      let polygons = this.instance_list.filter(inst => inst.type === 'polygon')
      for (let poly of polygons) {
        this.deselect_instance(poly)
      }
    },
    delete_instances_and_add_to_merged_instance: function (
      parent_instance,
      instances_to_merge
    ) {
      // For instance to merge, delete it and add al points to parent instance with a new figure ID.
      for (const instance of instances_to_merge) {
        let figure_id = uuidv4();
        let new_points = parent_instance.points.map((p) => p);
        for (const point of instance.points) {
          let new_figure_id = figure_id;
          if (point.figure_id) {
            new_figure_id = point.figure_id;
          }
          new_points.push({
            ...point,
            figure_id: new_figure_id,
          });
        }

        let instance_index = this.instance_list.indexOf(instance);
        if (instance_index > -1) {
          this.delete_single_instance(instance_index);
        }
        parent_instance.points = new_points;
      }
    },
    merge_polygons_v2: function () {
      let deleted_instance_indexes = this.polygon_merge_tool.merge_polygons(this.instance_list)
      this.$store.commit("set_instance_select_for_merge", false);
      for (let index of deleted_instance_indexes) {
        this.delete_single_instance(this.instance_list[index])
      }
      this.$store.commit("set_instance_select_for_merge", false);
      for (let index of deleted_instance_indexes) {
        this.delete_single_instance(this.instance_list[index])
      }
      this.polygon_merge_tool = null
      this.$emit('set_has_changed', true)
    },
    // userscript (to be placed in class once context figured)
    set_instance_human_edited: function (instance) {
      if (!instance) {
        return;
      }
      instance.change_source = "ui_diffgram_frontend";
      instance.machine_made = false;
    },
    get_roi_canvas_from_instance: function (instance, ghost_canvas) {
      // https://developer.mozilla.org/en-US/docs/Web/API/CanvasRenderingContext2D/getImageData

      let ghost_canvas_context = ghost_canvas.getContext("2d");

      let region_of_interest_image_data = ghost_canvas_context.getImageData(
        instance.x_min,
        instance.y_min,
        instance.width,
        instance.height
      );

      var roi_canvas = document.createElement("canvas");
      var roi_canvas_ctx = roi_canvas.getContext("2d");
      roi_canvas.width = instance.width;
      roi_canvas.height = instance.height;

      roi_canvas_ctx.putImageData(region_of_interest_image_data, 0, 0);

      return roi_canvas;
    },
    regenerate_file_cache: async function () {
      this.regenerate_file_cache_loading = true;
      let frame_number = this.image_annotation_ctx.current_frame;
      const file_id = this.working_file.id;
      let project_string = this.project_string_id;
      if (!project_string) {
        project_string = this.$store.state.project.current.project_string_id;
      }

      const [result] = await regenerate_cache(project_string, file_id, frame_number)

      if (result) {
        this.$emit('set_has_changed', false);
        location.reload();
      }
    },
    get_new_canvas: function () {
      this.html_image.crossOrigin = "Anonymous";

      let ghostcanvas = document.createElement("canvas");
      let metadata = this.get_metadata();

      ghostcanvas.height = metadata.height;
      ghostcanvas.width = metadata.width;
      let context = ghostcanvas.getContext("2d");

      context.drawImage(this.html_image, 0, 0);
      return ghostcanvas;
    },

    get_metadata: function () {
      let metadata;
      if (this.working_file.type == "video") {
        metadata = {...this.working_file.video};
      } else {
        metadata = {...this.working_file.image};
      }
      return metadata;
    },
    go_to_key_frame_handler: function () {
      this.close_instance_history_panel();
      this.detect_is_ok_to_save();
    },
    show_instance_history_panel: function (instance_index) {
      this.selected_instance_for_history = this.instance_list[instance_index];
    },
    close_instance_history_panel: function (e) {
      this.selected_instance_for_history = undefined;
    },
    warn_user_unload: function (e) {
      let pending_changes_frames = false;
      for (let key of Object.keys(this.image_annotation_ctx.instance_buffer_metadata)) {
        if (this.image_annotation_ctx.instance_buffer_metadata[key].pending_save) {
          pending_changes_frames = true;
          break;
        }
      }
      if (this.has_changed || pending_changes_frames) {
        // Cancel the event
        e.preventDefault();
        // Chrome requires returnValue to be set
        e.returnValue = "";
      }
    },

    get_userscript_id_string: function (userscript_id) {

      if (!userscript_id) {
        this.userscript = this.get_userscript(this.$refs.userscript)
        if (this.userscript.id) {
          userscript_id = this.userscript.id.toString()
        }
      }
      return userscript_id

    },

    get_and_set_global_instance: function (instance_list) {

      if (!this.global_attribute_groups_list) {
        return
      }
      if (this.global_attribute_groups_list.length === 0) {
        return
      }
      let existing_global_instance = instance_list.find(inst => inst.type === 'global');
      if (existing_global_instance) {
        this.global_instance = existing_global_instance;
      } else {
        this.global_instance = this.new_global_instance();
        instance_list.push(this.global_instance)
      }
      this.annotation_ui_context.instance_store.set_global_instance(this.working_file.id, this.global_instance)

    },
    new_global_instance: function () {

      let new_instance = new GlobalInstance();
      return new_instance

    },

    create_box: function (
      x_min,
      y_min,
      x_max,
      y_max,
      userscript_id = undefined,
      frame_number = undefined
    ) {
      /*
      * Used in context of userscripts.
      * TODO: Might need to be moved to a separate userscript functions file.
      * */
      if (
        x_min == undefined ||
        y_min == undefined ||
        x_max == undefined ||
        y_max == undefined
      ) {
        throw new Error("Must have x_min, y_min, x_max, y_max");
      }

      // current_instance is computed
      // TODO use function in create instance command
      let new_instance = duplicate_instance(this.current_drawing_box_instance, this)
      new_instance = this.initialize_instance(new_instance) as Instance
      new_instance = post_init_instance(new_instance,
        this.label_file_map,
        this.canvas_element,
        this.label_settings,
        this.canvas_transform,
        this.instance_hovered,
        this.instance_unhovered,
        this.canvas_mouse_tools
      )
      new_instance.set_la
      new_instance.x_min = parseInt(x_min);
      new_instance.x_max = parseInt(x_max);
      new_instance.y_min = parseInt(y_min);
      new_instance.y_max = parseInt(y_max);

      new_instance.width = parseInt(x_max - x_min);
      new_instance.height = parseInt(y_max - y_min);

      new_instance.change_source =
        "userscript_" + this.get_userscript_id_string(userscript_id);

      let reasonable = this.check_reasonableness(new_instance);
      if (reasonable != true) {
        console.warn(
          "Instance not reasonable: ",
          reasonable,
          "Instance was ignored."
        );
        return;
      }

      const command = new CreateInstanceCommand(new_instance, this, this.image_annotation_ctx.current_frame);
      this.annotation_ui_context.command_manager.executeCommand(command);

      this.event_create_instance = new_instance;

      //this.$emit('created_instance', new_instance)
    },

    check_reasonableness: function (instance) {
      // returns true if reasonable otherwise string reason
      // a lot of ways we could expand this in the future to be more descriptive

      let reasonable = 7;
      let values_to_check = [
        instance.x_min,
        instance.x_max,
        instance.y_min,
        instance.y_max,
      ];
      for (let value of values_to_check) {
        if (value < 0) {
          return "min/max value < 0";
        }
      }
      if (instance.width < reasonable) {
        return "instance.width < reasonable";
      }
      if (instance.height < reasonable) {
        return "instance.height < reasonable";
      }
      if (instance.points) {
        for (let point of instance.points) {
          if (point.x < 0) {
            return "point.x < 0";
          }
          if (point.y < 0) {
            return "point.y < 0";
          }
        }
      }
      if (instance.type == "polygon") {
        if (!instance.points) {
          return "no polygon points key";
        }
        if (instance.points.length < 2) {
          return "not enough points for polygon";
        }
      }
      return true;
    },

    slice_of_canvas: function (x_min, y_min, x_max, y_max) {
      // idea of taking a slice of canvas from instance
      // then running algorithm that wants more "full" resolution
      // eg to improve performance
      // maybe something like this https://stackoverflow.com/questions/45234492/copy-a-part-of-canvas-to-image
      // but translation back and forth I'm not sure
    },

    create_instance_from_keypoints: function (x, y) {
      /*
      * Used in context of userscripts.
      * */
      let new_instance = {
        ...this.current_instance,
        points: [...this.current_instance.points.map((p) => ({...p}))],
      };
      new_instance.type = "point";
      new_instance.points = [{x: x, y: y}];
      const command = new CreateInstanceCommand(new_instance, this, this.image_annotation_ctx.current_frame);
      this.annotation_ui_context.command_manager.executeCommand(command);
      return new_instance
    },

    update_polygon_width_height: function (instance) {
      // assumes instance passed by reference

      if (!instance.points) {
        return;
      }

      instance.x_min = 99999;
      instance.x_max = 0;
      instance.y_min = 99999;
      instance.y_max = 0;
      const x = "x";
      const y = "y";

      for (let i = 0; i < instance.points.length; i++) {
        let point = instance.points[i];

        if (point[x] <= instance.x_min) {
          instance.x_min = parseInt(point[x]);
        }
        if (point[x] >= instance.x_max) {
          instance.x_max = parseInt(point[x]);
        }
        if (point[y] <= instance.y_min) {
          instance.y_min = parseInt(point[y]);
        }
        if (point[y] >= instance.y_max) {
          instance.y_max = parseInt(point[y]);
        }
      }

      instance.width = parseInt(instance.x_max - instance.x_min);
      instance.height = parseInt(instance.y_max - instance.y_min);
    },

    create_polygon: function (points_list, userscript_id = undefined) {
      /*
      * Used in context of userscripts
      * */
      let new_instance = duplicate_instance(this.current_drawing_polygon_instance, this)
      new_instance = this.initialize_instance(new_instance)
      new_instance.type = "polygon";
      new_instance.points = points_list;
      new_instance.change_source =
        "userscript_" + this.get_userscript_id_string(userscript_id);

      this.update_polygon_width_height(new_instance);
      //console.debug(new_instance.width, new_instance.height)

      let reasonable = this.check_reasonableness(new_instance);
      if (reasonable != true) {
        console.warn("Instance not reasonable: ", reasonable);
        return;
      }

      const command = new CreateInstanceCommand(new_instance, this, this.image_annotation_ctx.current_frame);
      this.annotation_ui_context.command_manager.executeCommand(command);
      this.event_create_instance = new_instance;
      return new_instance;
    },

    __bodypix_points_to_instances: function (keypoints_list) {
      /*
      * Used in context of userscripts.
      * */

      // TODO also need to set instance type

      for (let keypoint of keypoints_list) {
        this.current_instance.points = [keypoint.position];
        const command = new CreateInstanceCommand(this.current_instance, this, this.image_annotation_ctx.current_frame);
        this.annotation_ui_context.command_manager.executeCommand(command);
      }
    },

    create_instance_template: async function (instance_index, name) {
      try {
        this.error = {};
        let instance = this.instance_list[instance_index];
        if (instance.type === 'keypoints') {
          instance = instance.get_instance_data();
        }
        if (!instance) {
          return;
        }
        if (!name) {
          this.error = {
            name: "Please provide a name for the instance template.",
          };
          return;
        }
        const response = await axios.post(this.create_instance_template_url, {
          name: name,
          reference_height: this.original_media_height,
          schema_id: this.label_schema.id,
          reference_width: this.original_media_width,
          instance_list: [instance],
        });

        if (response.status === 200) {
          this.instance_template_list.push(response.data.instance_template);
          this.instance_type_list.push({
            icon: "mdi-shape",
            display_name: response.data.instance_template.name,
            name: response.data.instance_template.id,
          });
          this.show_snackbar("Instance template created successfully.");
        }
      } catch (error) {
        console.error(error);
        this.error = this.$route_api_errors(error);
      } finally {
        this.image_annotation_ctx.loading = false;
      }
    },
    show_snackbar: function (message, color = 'primary',
                             timeout = -1,
                             show_close_button = true,
                             text_color = 'white',
                             text_secondary = '') {
      this.snackbar_message = message;
      this.custom_snackbar_color = color;
      this.custom_snackbar_timeout = timeout;
      this.snackbar_message_secondary = text_secondary;
      this.custom_snackbar_text_color = text_color;
      this.show_close_button = show_close_button;
      this.show_custom_snackbar = true;
    },
    show_snackbar_occlusion: function (message) {
      this.snackbar_message = message;
      this.show_snackbar_occlude_direction = true;
    },
    cancel_occlude_direction: function () {
      this.show_snackbar_occlude_direction = false;
      if (this.selected_instance && this.selected_instance.type === 'keypoints') {
        this.selected_instance.stop_occlude_direction()
      }

    },
    open_instance_template_dialog: function () {
      this.$refs.instance_template_creation_dialog.open();
    },

    trigger_instance_changed() {
      // Callback for when an instance is changed
      // This is a WIP that will be used for all the class Instance Types
      // For now we only have Kepoints instance using this.
      this.$emit('set_has_changed', true);
    },
    deselect_instance: function (instance) {

      if (SUPPORTED_IMAGE_CLASS_INSTANCE_TYPES.includes(instance.type)) {
        let coord_router: ImageAnnotationCoordinatorRouter = this.create_coordinator_router()
        let instance_coordinator: ImageAnnotationCoordinator = coord_router.generate_from_instance(instance, instance.type)
        instance_coordinator.deselect({} as ImageInteractionEvent)
      } else {
        instance.selected = false
      }
      this.unset_instance_list_sidebar()

    },
    instance_selected: function (instance) {
      // Callback for when an instance is selected
      // This is a WIP that will be used for all the class Instance Types
      // For now we only have Keypoints instance using this.
      let instances_to_merge_creation_refs = []
      if (this.polygon_merge_tool) {
        instances_to_merge_creation_refs = this.polygon_merge_tool.instances_to_merge.map(inst => inst.creation_ref_id)
      }


      for (let elm of this.instance_list) {
        if (elm.creation_ref_id != instance.creation_ref_id) {
          // Case when polygon merge tool is active.
          if (this.polygon_merge_tool && this.polygon_merge_tool.parent_merge_instance
            && elm.creation_ref_id != this.polygon_merge_tool.parent_merge_instance.creation_ref_id) {
            if (instances_to_merge_creation_refs.includes(elm.creation_ref_id)) {
              continue
            }
            if (this.polygon_merge_tool && this.polygon_merge_tool.is_allowed_instance_to_merge(elm)) {
              continue
            }
            this.deselect_instance(elm)
          } else if (!this.polygon_merge_tool ||
            !this.polygon_merge_tool.parent_merge_instance ||
            this.polygon_merge_tool.parent_merge_instance.length === 0) {
            if(this.label_settings.allow_multiple_instance_select){
              continue
            }
            this.deselect_instance(elm)
          }

        }
      }

      let index = this.instance_list.indexOf(instance)
      if (index === this.instance_hover_index || this.instance_hover_index == undefined) {
        this.refresh_instance_list_sidebar(index)
        this.image_annotation_ctx.trigger_refresh_current_instance = Date.now(); // decouple, for case of file changing but instance list being the same index
      }


    },
    instance_deselected: function (instance) {
      //TODO: implement when all instances have callbacks
    },


    test_instance_list_and_list_in_buffer_by_ref: function () {
      for (let i = 0; i < this.instance_list.length; i++) {
        let is_valid_by_ref =
          this.instance_list[i] ==
          this.instance_buffer_dict[this.image_annotation_ctx.current_frame][i];
        if (!is_valid_by_ref) {
          return false;
        }
      }
      return true;
    },
    instance_hovered: function (instance) {
      /** Callback for when an instance is hovered
       This is a WIP that will be used for all the class Instance Types
       For now we only have Kepoints & Box instance using this
       */
      if(!this.is_active){
        return;
      }
      if (!this.instance_list) {
        return;
      }
      for (let i = 0; i < this.instance_list.length; i++) {
        if (
          instance.creation_ref_id === this.instance_list[i].creation_ref_id
        ) {
          this.instance_hover_index = i;
          this.instance_hover_type = instance.type
          if(!this.draw_mode){
            if (instance.type === 'box') {
              let box: BoxInstance = instance
              box.set_default_hover_in_style(box)
            } else if(instance.type === 'polygon'){
              let poly: PolygonInstance = instance
              poly.set_default_hover_in_style(poly)
            }
          }

        }
      }
    },
    instance_unhovered: function (instance) {
      if(!this.is_active){
        return;
      }
      if (this.instance_hover_index == undefined) {
        return;
      }
      if (instance.type === 'global') {
        return;
      }
      let index = null;
      for(let i = 0; i <  this.instance_list.length; i++){
        let inst = this.instance_list[i];
        if(inst.creation_ref_id === instance.creation_ref_id){
          index = i
        }
      }
      if (index === this.instance_hover_index) {
        this.instance_list[this.instance_hover_index].is_hovered = false;
        this.instance_hover_index = null;
        this.instance_hover_type = null;
      }
      if (instance.type === 'box' && !instance.selected) {
        let box: BoxInstance = instance
        box.set_default_hover_out_style(box)
      } else if(instance.type === 'polygon'){
        let poly: PolygonInstance = instance
        poly.set_default_hover_out_style(poly)
      }
    },

    refresh_instances_in_viewport: function (instance_list) {

      if (this.label_settings.large_annotation_volume_performance_mode === false) { return }

      for (let i = 0; i < instance_list.length; i++) {
        instance_list[i].in_viewport = this.canvas_mouse_tools.check_is_instance_in_viewport(instance_list[i])
      }
    },

    create_instance_list_with_class_types: function (instance_list) {
      const result = [];
      if (!instance_list) {
        return result;
      }
      for (let i = 0; i < instance_list.length; i++) {
        let current_instance = instance_list[i];
        // Note that this variable may now be one of any of the classes on vue_canvas/instances folder.
        // Or (for now) it could also be a vanilla JS object (for those types) that haven't been refactored.
        let initialized_instance = initialize_instance_object(current_instance, this);
        initialized_instance = post_init_instance(initialized_instance,
          this.label_file_map,
          this.canvas_element,
          this.label_settings,
          this.canvas_transform,
          this.instance_hovered,
          this.instance_unhovered,
          this.canvas_mouse_tools,
        )
        if (initialized_instance) {
          result.push(initialized_instance);
        }
      }
      return result;
    },
    initialize_instance_buffer_dict_frame: function (frame_number) {
      /**
       * This function initializes the instances of a frame's instance list.
       * We just do this once per frame, so this function should only be executed
       * one time per frame number. To control this we have the instance_buffer_metadata
       * to know which ones have been initialized.
       * */
      if (frame_number == undefined) {
        return;
      }
      // We don't initialize again if we already initialized the frame.
      if (!this.instance_buffer_dict[frame_number]) {
        return;
      }


      // Perform the instance_buffer_dict initialization.
      let initialized_instance_list = this.create_instance_list_with_class_types(this.instance_buffer_dict[frame_number])
      this.instance_buffer_dict[frame_number] = initialized_instance_list

      // Set the metadata to prevent initializing again in the future
      if (this.image_annotation_ctx.instance_buffer_metadata[frame_number]) {
        this.image_annotation_ctx.instance_buffer_metadata[frame_number].initialized = true;
      } else {
        this.image_annotation_ctx.instance_buffer_metadata[frame_number] = {initialized: true};
      }
    },
    populate_canvas_element: function () {
      if (!this.canvas_element) {
        this.canvas_element = document.getElementById(this.canvas_id);
      }
    },
    fetch_instance_template: async function () {
      if (this.label_schema.id === -1) {
        return
      }
      this.loading_instance_templates = true;
      this.canvas_element = document.getElementById(this.canvas_id);
      this.canvas_element_ctx = this.canvas_element.getContext("2d");
      const [data, error] = await getInstanceTemplatesFromProject(this.project_string_id, this.label_schema.id);
      if (data && data.instance_template_list) {
        this.instance_template_list =
          data.instance_template_list.map((instance_template) => {
            instance_template.instance_list =
              instance_template.instance_list.map((instance) => {
                instance.reference_width = instance_template.reference_width;
                instance.reference_height = instance_template.reference_height;
                let initialized_instance = initialize_instance_object(instance, this);
                return initialized_instance;
              });
            // Note that here we are creating a new object for the instance list, all references are lost.
            instance_template.instance_list =
              this.create_instance_list_with_class_types(
                instance_template.instance_list
              );

            return instance_template;
          });
        this.instance_template_list.forEach((inst) => {
          let icon = "mdi-shape";
          if (
            inst.instance_list &&
            inst.instance_list[0].type == "keypoints"
          ) {
            icon = "mdi-vector-polyline-edit";
          }
          this.instance_type_list.push({
            name: inst.id,
            display_name: inst.name,
            icon: icon,
          });
        });
        await this.$nextTick();
        if (this.filtered_instance_type_list && this.filtered_instance_type_list[0]) {
          this.set_default_tool()

        }
      }
      if (error) {
        console.error(error)
      }
      this.loading_instance_templates = false;
    },
    redo: function () {
      if (!this.annotation_ui_context.command_manager) {
        return;
      }
      let redone = this.annotation_ui_context.command_manager.redo();
      if (redone) {
        this.$emit('set_has_changed', true);
      }
      this.update_canvas();
    },
    undo: function () {
      if (!this.annotation_ui_context.command_manager) {
        return;
      }
      let undone = this.annotation_ui_context.command_manager.undo();
      if (undone) {
        this.$emit('set_has_changed', true);
      }
      this.update_canvas();
    },
    set_loading_sequences: function (loading_sequences) {
      this.loading_sequences = loading_sequences;
    },
    set_canvas_dimensions: function () {
      if (!this.working_file) {
        throw new Error("Must provide task or file in props.");
      }

      this.original_media_width = this.working_file.video.width;
      this.original_media_height = this.working_file.video.height;
    },

    open_view_edit_panel(issue) {
      // This boolean controls if issues create/edit panel is shown or hidden.
      this.annotation_ui_context.issues_ui_manager.show_modify_an_issue = true;

      // Case for edit/view mode.
      this.annotation_ui_context.issues_ui_manager.current_issue = issue;
      this.$emit('draw_mode_change', false)
      this.label_settings.allow_multiple_instance_select = true;
      this.$store.commit("set_view_issue_mode", true);
      if (this.image_annotation_ctx.video_mode) {
        if (this.image_annotation_ctx.current_frame !== issue.marker_frame_number) {
          this.$refs.video_controllers.go_to_keyframe(
            issue.marker_frame_number
          );
        }
      }
    },
    polygon_unmerge(unmerge_instance_index, figure_id) {
      let instance = this.instance_list[unmerge_instance_index];
      // Remove All points from the polygon with the give figure id
      let figure_points = instance.points
        .filter((p) => p.figure_id == figure_id)
        .map((p) => ({...p, figure_id: undefined}));
      instance.points = instance.points.filter((p) => p.figure_id != figure_id);

      // Check if only 1 figure remains, and delete figure id.
      let figure_list = this.get_polygon_figures(instance);
      if (figure_list.length === 1) {
        instance.points = instance.points.map((p) => ({
          ...p,
          figure_id: undefined,
        }));
      }

      // Create the previously merged figure as a new instance.
      let instance_to_unmerge = duplicate_instance(instance, this);
      // Remove point and just leave the points in the figure
      instance_to_unmerge.points = figure_points;
      this.add_instance_to_file(
        instance_to_unmerge,
        this.image_annotation_ctx.current_frame
      );
      // Auto select on label view detail for inmediate attribute edition.
      this.refresh_instance_list_sidebar();
    },
    start_polygon_select_for_merge(merge_instance_index) {
      // Close context menu and set select instance mode
      if (merge_instance_index == undefined) {
        return;
      }
      this.polygon_merge_tool = new PolygonMergeTool(this.instance_list[merge_instance_index])
      this.annotation_ui_context.show_context_menu = false;
      this.$store.commit("set_instance_select_for_merge", true);
    },


    done_selecting_instaces_issues() {
      this.issues_ui_manager.snackbar_issues = false;
    },
    open_share_dialog: function () {
      this.share_dialog_open = true;
    },
    close_share_dialog: function () {
      this.share_dialog_open = false;
    },
    clear_selected: function (except_instance = undefined) {

      for (let i in this.instance_list) {
        let elm = this.instance_list[i]
        if (i == this.parent_merge_instance_index) {
          continue
        }
        if (except_instance && (elm.creation_ref_id === except_instance.creation_ref_id)) {
          continue
        }

        if (SUPPORTED_IMAGE_CLASS_INSTANCE_TYPES.includes(elm.type)) {

          if (elm.is_hovered) {
            continue
          }
          let coord_router: ImageAnnotationCoordinatorRouter = this.create_coordinator_router()
          let coordinator: ImageAnnotationCoordinator = coord_router.generate_from_instance(elm, elm.type)
          coordinator.deselect({} as ImageInteractionEvent)
          this.image_annotation_ctx.trigger_refresh_current_instance = new Date()

        } else {

          elm.selected = false;
        }


      }
    },

    shift_frame_via_store: function (direction) {
      // direction is an int where: -1 to go back, 1 go forward
      if (this.image_annotation_ctx.current_frame === 0 && direction === -1) {
        return;
      }

      if (
        this.image_annotation_ctx.current_frame >= this.current_video.frame_count - 1 &&
        direction === 1
      ) {
        return;
      }

      let new_frame = direction + this.image_annotation_ctx.current_frame;
      this.$refs.video_controllers.move_frame(direction)
    },

    hide_context_menu: function () {    //  close close_context
      this.annotation_ui_context.show_context_menu = false;
    },

    open_context_menu: function () {
      this.annotation_ui_context.show_context_menu = true;
      this.update_canvas()
    },

    detect_clicks_outside_context_menu: function (e) {
      // skip clicks on the actual context menu
      if (e.target.matches(".context-menu, .context-menu *")) {
        return;
      }
      // assume if not on context menu, then it's outside and we want to hide it
      this.hide_context_menu();
    },

    mouse_events_global_down: function (e) {
      this.detect_clicks_outside_context_menu(e);
    },

    contextmenu: function (e) {
      if(!this.is_active){
        return
      }
      e.preventDefault();
      this.open_context_menu();
    },

    start_autosave: function () {
      this.interval_autosave = setInterval(
        this.detect_is_ok_to_save,
        15 * 1000
      );
    },

    detect_is_ok_to_save: async function () {
      if (this.has_changed || this.has_pending_frames) {
        await this.$emit('save');
      }
    },

    focus_instance: function (focus) {
      // Do we want to support focusing more than one at a time?
      // If we only want one can just pass that singluar instance as the "focus" one
      // this.instance_list[index].focused = True
      // careful can't use id, since newly created instances won't have an ID!
      this.instance_focused_index = focus.index;
      let instance_to_focus = this.instance_list[this.instance_focused_index]
      this.selected_instance_list = [
        instance_to_focus,
      ];
      this.snap_to_instance(instance_to_focus);
      this.$forceUpdate();
    },

    focus_instance_show_all() {
      console.log("Stop")
      this.instance_focused_index = null;
      this.snapped_to_instance = undefined;
      this.selected_instance_list = [];
      this.reset_to_full();
      this.update_canvas()
    },

    instance_update: function (update) {
      /*
       * update, an object like:
       *
       *  index, number
       *  mode, string, ie one of [delete, delete_undo, toggle_missing, ... etc.]
       *  list_type, instance_list type, string  [gold_standard, default]  defaults to default
       *  payload, object, relative to mode
       *
       * ie
       *  index: 1
       *  mode: "delete"
       *
       */
      // Main communication point for actions taken on instance list
      // propagating to main
      // Once the list is updated here it filters back to instance_list component
      if (this.view_only_mode == true) {
        return;
      }

      let index = update.index
      if (index == undefined) {
        return
      }  // careful 0 is ok.
      let initial_instance = {...this.instance_list[index], initialized: false}
      initial_instance = initialize_instance_object(initial_instance, this);
      // since sharing list type component need to determine which list to update
      // could also use render mode but may be different contexts
      let instance;
      if (!update.list_type || update.list_type == "default") {
        instance = this.instance_list[index]
      } else if (update.list_type == "gold_standard") {
        instance = this.gold_standard_file.instance_list[index]
      } else if (update.list_type == "global") {
        if (this.image_annotation_ctx.video_mode) {
          instance = this.image_annotation_ctx.video_parent_file_instance_list[index]
        } else {
          instance = this.instance_list[index]
        }

      }

      if (!instance) {
        console.debug("Invalid index");
        return;
      }

      if (update.mode == "pause_object") {
        instance.pause_object = true;
      }

      if (update.mode == "on_click_update_point_attribute") {
        instance.toggle_occluded(update.node_hover_index);
      }

      if (update.mode == "on_click_occlude_all_direction") {
        instance.activate_select_edge_occlusion(update.node_hover_index);
        this.show_snackbar_occlusion('Select another Node to occlude all nodes in that direction')
        // We are not yet updating at this point, so we return
        return
      }

      if (update.mode == "occlude_all_children") {
        instance.occlude_all_children(update.node_hover_index);
      }

      // instance update
      if (update.mode == "update_label") {
        // not 100% sure if we need both here
        instance.label_file = update.payload;
        instance.label_file_id = update.payload.id;
      }

      if (update.mode == "change_sequence") {
        instance.sequence_id = update.sequence.id;
        instance.number = update.sequence.number;
      }

      if (update.mode == "rating_update") {
        instance.rating = update.payload;
      }

      if (update.mode == "delete") {
        instance.soft_delete = true;
        this.deselect_instance(instance)
      }

      if (update.mode == "delete_undo") {
        instance.soft_delete = false;
      }

      if (update.mode == "delete" || update.mode == "delete_undo") {
        // sequence related, design https://docs.google.com/document/d/1HVY_Y3NsVQgHyQAH-NfsKnVL4XZyBssLz2fgssZWFYc/edit#heading=h.121li5q14mt2
        if (instance.label_file_id != this.current_lable_file_id) {
          // this.$emit('save')
          this.$emit('set_has_changed', true);
          this.request_clear_sequence_list_cache = Date.now();
        }
      }

      if (update.mode == "toggle_missing") {
        if (instance.missing) {
          instance.missing = !instance.missing;
        } else {
          instance.missing = true;
        }
      }


      if (update.mode == "attribute_change") {
        /*
         *   We expect the event to supply a group_id
         *   which we use as the key to set this.
         *   The value should be a dictionary of the form
         *   ie similar to
         *      136: {archived: false, display_order: null, group_id: 136, id: 173, kind: "select", name: "select",…
         *    which is stored under attribute groups ie
         *    attribute_groups: { 136, 190, 253 …}
         *
         *    For the event to propogate this we must set a key
         *    ie :key="attribute_template.id"
         */
        // TODO: REFACTOR THIS CODE to instance.set_attribute_value() when all instances have class types.
        if (!instance.attribute_groups) {
          instance.attribute_groups = {};
        }

        let group = update.payload[0];
        let value = update.payload[1];

        // we assume this represents a group
        initial_instance.prev_attribute = {
          group: group.id,
          value: {...instance.attribute_groups[group.id]},
        };
        instance.attribute_groups[group.id] = value;

        if (instance.type === "global") {
          this.global_instance = instance
          this.annotation_ui_context.instance_store.set_global_instance(this.working_file.id, this.global_instance)
        }
      }

      // end instance update
      if (instance.type === 'global' && this.image_annotation_ctx.video_mode) {
        this.image_annotation_ctx.video_global_attribute_changed = true;
      }
      if (!this.image_annotation_ctx.video_mode) {
        let insert_instance_result = this.insert_instance(
          index,
          instance,
          initial_instance,
          update
        );
      }
      if (this.image_annotation_ctx.video_mode && instance.type !== 'global') {
        let insert_instance_result = this.insert_instance(
          index,
          instance,
          initial_instance,
          update
        );
      }
      this.$emit('set_has_changed', true);
      this.trigger_refresh_with_delay();
    },

    clone_instance(instance) {
      // WIP
      let new_instance = cloneDeep(instance);
      new_instance.id = null;
      return new_instance;
    },

    insert_instance(index, instance, initial_instance, update) {
      // Use index = ` -1 ` if New instnace
      // use splice to update, directly updating propery doesn't detect change vue js stuff
      //  question, this extra update step is only needed for the attribute stuff right?
      const command = new UpdateInstanceCommand(
        instance,
        index,
        initial_instance,
        this
      );
      this.annotation_ui_context.command_manager.executeCommand(command);

      if (update.list_type == "gold_standard") {
        this.gold_standard_file.instance_list.splice(index, 1, instance);
      }

      return true;
    },
    created: async function () {
      this.update_label_settings_from_schema()
      this.update_user_settings_from_store();

      this.annotation_ui_context.command_manager = new CommandManagerAnnotationCore();
      // Initial File Set
      if (this.working_file) {
        await this.on_change_current_file();
      } else if (this.task) {
        await this.on_change_current_task();
      }
      if(this.instance_list.length > 100){
        this.set_performance_optimizations_on()
      } else {
        this.set_performance_optimizations_off()
      }
      this.$emit('instance_list_updated', this.instance_list, this.working_file.id, this.working_file.type)
    },

    set_performance_optimizations_on: function () {
      this.label_settings.large_annotation_volume_performance_mode = true

      this.label_settings.show_text = false;
      this.label_settings.left_nav_width = 300

    },

    set_performance_optimizations_off: function () {
      this.label_settings.large_annotation_volume_performance_mode = false

      this.label_settings.show_text = true;

    },

    update_label_settings_from_schema: function () {
      if (!this.task) {
        return
      }
      let job = this.task.job;
      if (!job) {
        return
      }
      let ui_schema = job.ui_schema;
      if (!ui_schema) {
        return
      }
      if (!ui_schema.label_settings || !ui_schema.label_settings.default_settings) {
        return;
      }
      this.label_settings = ui_schema.label_settings.default_settings;
    },

    update_user_settings_from_store() {   // label_settings
      for (const [key, value] of Object.entries(this.$store.state.user.settings)) {
        this.label_settings[key] = value
      }

    },

    update_window_size_from_listener() {
      if(!this.use_full_window){
        return
      }
      // function so we can destroy it after
      this.window_width_from_listener = window.innerWidth;
      this.window_height_from_listener = window.innerHeight;
    },

    restore_event_listeners: function () {
      this.remove_event_listeners();
      this.add_event_listeners();
    },

    remove_event_listeners() {
      /*
       * Careful needs to match ie up and up || down and down
       *
       */

      // global
      // window.removeEventListener("beforeunload", this.warn_user_unload);
      // document.removeEventListener("mousedown", this.mouse_events_global_down);
      // window.removeEventListener("keydown", this.keyboard_events_global_down);

      // window.removeEventListener("keyup", this.keyboard_events_global_up);
      window.removeEventListener(
        "resize",
        this.update_window_size_from_listener
      );

      this.canvas_wrapper.removeEventListener("wheel", this.wheel);
    },

    add_event_listeners() {
      /* Can call getEventListeners(window)
       * to get list of them
       *
       */

      this.canvas_wrapper = document.getElementById(`canvas_wrapper_${this.working_file.id}`);
      // rather have canvas_wrapper inside this functionsss in case it needs to "refresh" it

      this.annotation_area = document.getElementById("annotation");

      // window.addEventListener("keydown", this.keyboard_events_global_down);
      // document.addEventListener("mousedown", this.mouse_events_global_down);
      // window.addEventListener("keyup", this.keyboard_events_global_up);
      window.addEventListener("resize", this.update_window_size_from_listener);

      this.update_window_size_from_listener(); // Initial size (resize doesn't fire on first load)

      this.canvas_wrapper.addEventListener("wheel", this.wheel);
    },

    async mounted() {
      //console.debug("mounted")
      // Reset issue mode
      this.$store.commit("set_instance_select_for_issue", false);
      this.$store.commit("set_instance_select_for_merge", false);
      this.$store.commit("set_view_issue_mode", false);
      this.$store.commit("set_user_is_typing_or_menu_open", false);
      this.add_event_listeners();
      this.fetch_model_run_list();
      this.fetch_instance_template();

      this.update_canvas()
      this.populate_canvas_element()
      this.canvas_mouse_tools = new CanvasMouseTools(
        this.mouse_position,
        this.canvas_translate,
        this.canvas_element,
        this.canvas_scale_global,
        this.original_media_width,
        this.original_media_height
      );
      this.on_canvas_scale_global_changed();
      // assumes canvas wrapper available
      this.canvas_wrapper.style.display = "";

      var self = this;

      this.refresh_video_buffer_watcher = this.$store.watch(
        (state) => {
          return this.$store.state.annotation_state.refresh_video_buffer;
        },
        (new_val, old_val) => {
          self.get_video_instance_buffer();
        }
      );

      this.save_watcher = this.$store.watch(
        (state) => {
          return this.$store.state.annotation_state.save;
        },
        (new_val, old_val) => {
          self.save();
        }
      );
      this.save_and_complete_watcher = this.$store.watch(
        (state) => {
          return this.$store.state.annotation_state.save_and_complete;
        },
        (new_val, old_val) => {
          if (this.task && this.task.id) return;
          self.save(true);
        }
      );

      if (this.task || this.job_id) {
        this.task_mode_mounted();
      }

      this.start_autosave(); // created() gets called again when the task ID changes eg "go to next"

    },
    set_default_tool: function () {
      // Add Default Selected tool.
      let last_selected_tool = this.$store.getters.get_last_selected_tool
      if (!this.filtered_instance_type_list.map(elm => elm.name).includes(last_selected_tool)) {
        return
      }
    },
    fetch_model_run_list: async function () {
      if (!this.model_run_id_list || this.model_run_id_list.length === 0) return

      this.image_annotation_ctx.loading = true;
      const [response] = await get_model_run_list(this.project_string_id, this.model_run_id_list)

      if (response && response.data.model_run_list !== undefined) {
        this.model_run_list = response.data.model_run_list;
        for (let i = 0; i < this.model_run_list.length; i++) {
          this.model_run_list[i].color = this.model_run_color_list[i];
        }
      }

      this.image_annotation_ctx.loading = false;
      this.$emit('model_run_list_loaded', this.model_run_list)
    },
    task_mode_mounted: function () {
      // Default because can be timing issues with how it loads new value
      // from media_core

      this.media_core_height = 0;
      this.show_default_navigation = false;
    },
    go_to_login: function () {
      this.$router.push("/user/login");
    },

    go_to_projects: function () {
      this.$router.push("/projects");
    },

    // WIP doesn't quite refresh as expected
    go_to_file: function () {
      this.$router.push("/file/" + this.user_requested_file_id);
      this.get_media(); //
    },

    page_refresh: function () {
      this.created();
      this.mounted();
      this.$store.commit("init_label_refresh");
    },

    async refresh_all_instances() {
      await this.get_instances();
      this.update_canvas();
      this.$forceUpdate();
    },
    update_canvas: async function () {
      this.refresh = new Date();
      this.canvas_element = document.getElementById(this.canvas_id);
      if (!this.canvas_element) {
        return
      }
      this.canvas_element_ctx = this.canvas_element.getContext("2d");

      this.refresh_instances_in_viewport(this.instance_list)

      this.update_smooth_canvas(this.label_settings.smooth_canvas)
      this.update_large_annotation_volume_performance_mode(this.label_settings.large_annotation_volume_performance_mode)
      await this.$forceUpdate();
    },

    validate_sequences: function () {
      /* Constraints
       *    Check if the sequence already exists in the instance list
       *
       * In prior contexts we had this runnning "after the fact"
       * so it was trying to detect 2
       * now we are running it "on demand" so a single one is wrong.
       * TODO consider optimizing this by returning the moment count == 1
       * I don't want to jump to this yet in case there's a need for the prior
       * setup.
       *
       *  strange we did not seem
       * to be checking the single file flag ones
       */

      let count = 0;

      for (let i in this.instance_list) {
        if (this.instance_list[i].soft_delete == true) {
          continue;
        }
        // careful need to check on label id too
        if (
          this.instance_list[i].number ==
          this.current_sequence_from_sequence_component.number &&
          this.instance_list[i].label_file_id == this.annotation_ui_context.current_label_file.id
        ) {
          count += 1;
        }
      }

      // We allow 2,
      // But if we run check proactively then only can be one.
      if (count != 0) {
        this.snackbar_warning = true;
        this.snackbar_warning_text =
          "Edit existing Instance, or go to a new frame, or create a new Sequence.";
        return false;
      } else {
        return true;
      }
    },

    /*  We accept it's possible
     *  to have a sequence selected that's "wrong"
     *  and we validate this at save instead of trying
     *  to prevent it. Because,
     *  trying to prevent it creates the ill posed problem
     *  of guessing what sequence a user wants,
     *  where as this makes it simple for the user, they
     *  are on whatever sequence they select.
     */

    video_animation_unit_of_work: function (image) {
      /*
       *  From animation in the context of getting
       *  passed an image from a video
       *  And NOT for pulling a single frame
       *
       *
       *  Refresh workaround note:
       *    it appears to not be
       *    since perhaps instance_list is changing?
       *
       *    Question, is "refresh" a heavy operation?
       *    the date thing shouldn't be, but not clear if the
       *    settimeout and/or it's relation to animation from does
       *    anthing?
       *
       */

      this.html_image = image;
      //this.trigger_refresh_with_delay()
      // also this could be a lot smarter ie getting instances
      // while still some buffer left etc.
      if (this.image_annotation_ctx.current_frame in this.instance_buffer_dict) {
        // We want to initialize the buffer dict before assinging the pointer on instance_list.
        this.initialize_instance_buffer_dict_frame(this.image_annotation_ctx.current_frame);
        // IMPORTANT  This is a POINTER not a new object. This is a critical assumption.
        // See https://docs.google.com/document/d/1KkpccWaCoiVWkiit8W_F5xlH0Ap_9j4hWduZteU4nxE/edit
        this.instance_list = this.instance_buffer_dict[this.image_annotation_ctx.current_frame];
      } else {
        this.video_pause = Date.now();
        this.get_instances(true);
      }
      this.add_override_colors_for_model_runs();
    },

    toggle_pause_play: function () {
      if (this.video_playing) {
        this.video_pause = Date.now();
      } else {
        this.video_play = Date.now();
      }
    },

    seeking_update: function (seeking) {
      this.seeking = seeking;
    },
    may_fire_user_ghost_canvas_available_alert: function () {
      if (
        this.$store.state.user.settings.hide_ghost_canvas_available_alert ==
        true
      ) {
        return;
      }
      if (this.label_settings.show_ghost_instances == false) {
        return;
      }
      if (this.ghost_instance_list.length >= 1) {
        this.canvas_alert_x = this.mouse_position.x;
        this.canvas_alert_y = this.mouse_position.y;
        this.$refs.ghost_canvas_available_alert.show_alert();
      }
    },
    set_keyframe_loading: function (value) {
      this.image_annotation_ctx.go_to_keyframe_loading = value
    },
    on_key_frame_loaded: async function (url, frame_number) {
      let existing_image = null;
      if (this.$refs.video_controllers) {
        existing_image = this.$refs.video_controllers.frame_image_buffer[frame_number];
      }
      if (existing_image) {
        this.set_new_image_on_canvas(existing_image)
      } else {
        if (url) {
          await this.add_image_process(url);
        }
      }
      await this.load_frame_instances(url)
      this.set_keyframe_loading(false);
      this.seeking = false;
    },
    load_frame_instances: async function (url) {
      /* Careful to call get_instances() since this handles
       * if we are on a keyframe and  don't need to call instance buffer
       * this method supercedes the old video_file_update()
       */
      await this.get_instances();
      this.$emit('ghost_refresh_instances');

    },
    set_new_image_on_canvas: function (image) {
      // this gets instances if it needs to
      this.html_image = image;
      this.canvas_wrapper.style.display = "";
      this.image_annotation_ctx.loading = false;
      this.trigger_refresh_with_delay();
    },
    add_image_process: async function (url) {
      const image = await this.addImageProcess(url);
      this.set_new_image_on_canvas(image);
    },

    current_file_updates: async function (file) {
      if (!file) {
        throw new Error("Provide file.");
      }
      if (file.type == "image") {
        this.image_annotation_ctx.video_mode = false;
        this.original_media_width = file.image.width;
        this.original_media_height = file.image.height;
        this.canvas_mouse_tools.set_canvas_width_height(this.original_media_width, this.original_media_height)
        const new_image = await this.addImageProcess(file.image.url_signed);
        this.html_image = new_image;
        this.loading = false;
        this.refresh = Date.now();
      }

      if (file.type == "video") {
        this.image_annotation_ctx.video_mode = true;
        this.current_video = file.video;
        this.current_video_file_id = file.id;

        this.original_media_width = file.video.width;
        this.original_media_height = file.video.height;
        this.canvas_mouse_tools.set_canvas_width_height(this.original_media_width, this.original_media_height)
        this.$refs.video_controllers.reset_cache();
        await this.$refs.video_controllers.get_video_single_image();
      }
    },
    // todo why not make this part of rest of event stuff
    wheel: function (event) {
      if(!this.is_active){
        return
      }
      if (this.annotation_ui_context.show_context_menu == true) {
        return;
      } // becasue could have own menus that scroll

      this.zoom_wheel_scroll_canvas_transform_update(event);
    },

    clamp_values: function (val, min, max) {
      //https://stackoverflow.com/questions/11409895/whats-the-most-elegant-way-to-cap-a-number-to-a-segment
      return Math.min(Math.max(val, min), max);
    },

    zoom_wheel_scroll_canvas_transform_update: function (event) {
      this.hide_context_menu();
      this.canvas_mouse_tools.zoom_wheel(event);
      this.image_annotation_ctx.zoom_value = this.canvas_mouse_tools.scale;

      if ( this.instance_hover_index == null ) {
        this.canvas_element.style.cursor = this.is_fully_zoomed_out ? "default" : "grab";
      }

      this.update_canvas();
    },

    reset_to_full: function () {
      this.canvas_mouse_tools.reset_transform_with_global_scale();
      this.canvas_mouse_tools.scale = this.canvas_mouse_tools.canvas_scale_global;
      this.image_annotation_ctx.zoom_value = this.canvas_mouse_tools.scale;
      if ( this.instance_hover_index == null ) {
        this.canvas_element.style.cursor = "default";
      }
      this.update_canvas();
    },

    get_center_point_of_instance: function (instance) {
      if (instance == undefined) {
        return
      }
      let x = instance.x_max - instance.width / 2;
      let y = instance.y_max - instance.height / 2;
      return {x: x, y: y};
    },

    get_focus_point_of_instance: function (instance) {
      if (!instance) {
        return
      }
      let point = {x: 0, y: 0};
      let center_point = this.get_center_point_of_instance(instance);
      let center_of_frame = {
        x: this.original_media_width / 2,
        y: this.original_media_height / 2,
      };

      if (
        this.point_is_intersecting_circle(center_point, center_of_frame, 100)
      ) {
        return center_point;
      }

      if (instance.x_max > this.original_media_width / 2) {
        point.x = instance.x_max;
      } else {
        point.x = instance.x_min;
      }
      if (instance.y_max > this.original_media_height / 2) {
        point.y = instance.y_max;
      } else {
        point.y = instance.y_min;
      }
      return point;
    },

    clamp_values(val, min, max) {
      return Math.min(Math.max(val, min), max);
    },

    auto_revert_snapped_to_instance_if_unchanged: function (instance) {
      if (this.snapped_to_instance == instance) {
        if (this.$refs.instance_detail_list) {
          this.$refs.instance_detail_list.show_all();
        }
        return true;
      }
      return false;
    },

    get_zoom_region_of_instance: function (instance) {
      if (!instance) {
        return
      }
      let max_zoom = 10;
      let padding = -2;
      let max_x = this.clamp_values(
        max_zoom,
        this.canvas_scale_global,
        this.original_media_width / instance.width
      );
      let max_y = this.clamp_values(
        max_zoom,
        this.canvas_scale_global,
        this.original_media_height / instance.height
      );
      let max_zoom_to_show_all = this.clamp_values(max_zoom, max_x, max_y);
      max_zoom_to_show_all += padding;
      max_zoom_to_show_all = this.clamp_values(
        max_zoom_to_show_all,
        this.canvas_scale_global,
        max_zoom
      );
      return max_zoom_to_show_all;
    },

    snap_to_instance: function (instance) {
      if (!instance) {
        return
      }
      if (this.label_settings.enable_snap_to_instance == false) {
        return;
      }

      if (this.auto_revert_snapped_to_instance_if_unchanged(instance) == true) {
        return;
      }

      // this.$refs.instance_detail_list.focus_mode = true;
      // this.$refs.instance_detail_list.change_instance(
      //   instance,
      //   this.instance_focused_index
      // );

      this.snapped_to_instance = instance;

      let point = this.get_focus_point_of_instance(instance);

      let scale = this.get_zoom_region_of_instance(instance);
      this.canvas_mouse_tools.zoom_to_point(point, scale);
      this.image_annotation_ctx.zoom_value = this.canvas_mouse_tools.scale;
      this.update_canvas();
    },

    issue_hover_update: function (index: Number) {
      if (index != null) {
        this.issue_hover_index = parseInt(index);
      } else {
        this.issue_hover_index = null;
      }
    },
    cuboid_face_hover_update: function (cuboid_face) {
      this.cuboid_face_hover = cuboid_face;
    },

    ghost_instance_hover_update: function (
      index: Number,
      type: String,
      figure_id: String
    ) {
      //if (this.lock_point_hover_change == true) {return}
      if (index != null) {
        this.ghost_instance_hover_index = parseInt(index);
        this.ghost_instance_hover_type = type; // ie polygon, box, etc.
      } else {
        this.ghost_instance_hover_index = null;
        this.ghost_instance_hover_type = null;
      }
    },

    instance_hover_update: function (
      index: Number,
      type: String,
      figure_id: String,
      instance_rotate_control_mouse_hover: Boolean
    ) {
      if (this.lock_point_hover_change == true) {
        return;
      }
      // important, we don't change the value if it's locked
      // otherwise it's easy for user to get "off" of the point they want
      if (index != null) {
        this.instance_hover_index = parseInt(index);
        this.hovered_figure_id = figure_id;
        this.instance_hover_type = type; // ie polygon, box, etc.
        this.instance_rotate_control_mouse_hover =
          instance_rotate_control_mouse_hover;
      } else {
        this.instance_hover_index = null;
        this.hovered_figure_id = null;
        this.instance_hover_type = null;
        this.instance_rotate_control_mouse_hover = null;
      }
    },

    remove_file_request(file) {
      if (file.type == "image" || file.type == "video") {
        for (var i in this.File_list) {
          if (this.File_list[i].id == file.id) {
            this.File_list.splice(i, 1);

            if (this.File_list.length > 0) {
              if (this.File_list[i].id == this.working_file.id) {
                this.working_file = this.File_list[0];
                this.change_file("none", this.File_list[0]);
              }
            }
          }
        }
      }
    },
    delete_single_instance: function (index: Number) {
      /* Given an index of instance in instance_list delete it
       *
       * Shorthand wrapper around instance_update
       *
       * ie try with selecting annotation_core
       * go to edit mode and:
       * $vm0.delete_single_instance($vm0.instance_hover_index)
       */

      this.instance_update({
        index: index,
        mode: "delete",
      });
    },

    delete_instance: function () {
      if (this.view_only_mode == true) {
        return;
      }

      for (var i in this.instance_list) {
        if (this.instance_list[i].selected == true) {
          this.delete_single_instance(i);
        }
      }
    },

    insert_tag_type: function () {
      this.add_instance_to_file(
        this.current_instance,
        this.image_annotation_ctx.current_frame
      );
    },
    add_instance_to_frame_buffer: async function (instance, frame_number) {
      if (!this.image_annotation_ctx.video_mode) {
        return;
      }
      if (frame_number == undefined) {
        throw "frame number undefined in video mode (add_instance_to_frame_buffer)";
      }
      if (instance == undefined) {
        throw "instance is undefined in add_instance_to_frame_buffer()";
      }
      instance.creation_ref_id = uuidv4();
      instance.client_created_time = new Date().toISOString();
      if (this.instance_buffer_dict[frame_number]) {
        this.instance_buffer_dict[frame_number].push(instance);
      } else {
        this.instance_buffer_dict[frame_number] = [instance];
      }
      if (this.$refs.sequence_list &&
        instance.number != undefined &&
        (instance.number === this.$refs.sequence_list.highest_sequence_number || this.$refs.sequence_list.highest_sequence_number === 0)) {
        if (this.$refs.sequence_list.highest_sequence_number === 0) {
          this.$refs.sequence_list.may_auto_advance_sequence()
          this.$refs.sequence_list.may_auto_advance_sequence()
        } else {
          this.$refs.sequence_list.may_auto_advance_sequence()
        }
      }
      this.$emit('ghost_refresh_instances');
      // Set Metadata to manage saving frames
      this.$emit('set_frame_pending_save', true, frame_number)
    },

    // TODO rename? / refactor? in contect of more awareness of ref/by value for buffer
    add_instance_to_file: async function (instance, frame_number = undefined) {
      if (this.image_annotation_ctx.video_mode) {
        if (frame_number == undefined) {
          console.error('Please provide a frame number to call add_instance_to_file()')
          return
        }
        this.add_instance_to_frame_buffer(instance, frame_number)
      } else {
        this.push_instance_to_image_file(instance)
      }

    },

    push_instance_to_image_file: async function (instance = undefined) {
      instance.creation_ref_id = uuidv4();
      instance.client_created_time = new Date().toISOString();

      if (!instance.change_source) {
        instance.change_source = "ui_diffgram_frontend";
      }

      this.instance_list.push(instance);

      this.$emit('set_has_changed', true);

      // Caution, this feeds into current instance, so it can look like it's dramatically not working
      // if this is set incorrectly.
      this.is_actively_drawing = false;
    },

    point_is_intersecting_circle: function (mouse, point, radius = 8) {
      if (!point) {
        return
      }
      if (!mouse) {
        return
      }
      // Careful this is effected by scale
      // bool, true if point if intersecting circle
      let radius_scaled = radius / this.image_annotation_ctx.zoom_value;
      const result =
        Math.sqrt((point.x - mouse.x) ** 2 + (mouse.y - point.y) ** 2) <
        radius_scaled; // < number == circle.radius
      return result;
    },
    detect_hover_on_curve: function () {
      if (!this.instance_list) {
        return;
      }
      if (this.lock_point_hover_change) {
        return;
      }
      if (this.draw_mode) {
        return;
      }

      let instance_index = this.instance_hover_index;
      let instance = this.instance_list[instance_index];
      if (instance && instance.type === "curve") {
        this.canvas_element.style.cursor = "all-scroll";
      }
    },
    detect_hover_on_curve_control_points: function () {
      if (!this.instance_list) {
        return;
      }
      if (this.lock_point_hover_change) {
        return;
      }
      //caution this needs to be before we change the hover point

      let instance_index = this.instance_hover_index;
      let instance = this.instance_list[instance_index];

      if (!instance || instance.type !== "curve") {
        this.curve_hovered_point = undefined;
        return;
      }

      if (
        this.point_is_intersecting_circle(this.mouse_position, instance.p1, 10)
      ) {
        this.curve_hovered_point = "p1";
        this.canvas_element.style.cursor = "all-scroll";
      }
      if (
        this.point_is_intersecting_circle(this.mouse_position, instance.cp, 10)
      ) {
        this.curve_hovered_point = "cp";
        this.canvas_element.style.cursor = "all-scroll";
      }
      if (
        this.point_is_intersecting_circle(this.mouse_position, instance.p2, 10)
      ) {
        this.curve_hovered_point = "p2";
        this.canvas_element.style.cursor = "all-scroll";
      }
    },
    detect_hover_on_ellipse_corners: function () {

      if (this.is_actively_resizing) {
        return;
      }
      if (this.instance_select_for_issue) {
        return;
      }
      if (this.instance_select_for_merge) {
        return;
      }
      if (!this.instance_list) {
        return;
      }
      // avoid having a check for every point?
      let instance_index = this.instance_hover_index;
      let instance = this.instance_list[instance_index];
      // If theres no hovered instance instance try to get the selected instance.
      if (!instance || instance.type !== "ellipse") {
        instance = this.selected_instance;
        instance_index = this.selected_instance_index;
      }

      // Fallback case when we are currently resizing on an instance.
      if (!instance || instance.type !== "ellipse") {
        instance = this.ellipse_hovered_instance;
        instance_index = this.ellipse_hovered_instance_index;
        if (instance) {
          instance.selected = true;
        }
        return;
      }

      if (!instance || instance.type !== "ellipse") {
        this.ellipse_hovered_corner = undefined;
        return;
      }
      let result = undefined;
      let result_key = undefined;
      for (let key in instance.corners) {
        if (
          this.point_is_intersecting_circle(
            this.mouse_position,
            instance.corners[key],
            16
          )
        ) {
          result = instance.corners[key];
          result_key = key;
        }
      }

      this.ellipse_hovered_corner_key = result_key;

      this.ellipse_hovered_instance = instance;
      this.ellipse_hovered_instance_index = instance_index;

      // Set Mouse Style and hover data key.
      if (result && (result_key === "right" || result_key === "left")) {
        this.ellipse_hovered_corner = result;
        this.canvas_element.style.cursor = "col-resize";
      }

      if (result && result_key === "top_right") {
        this.ellipse_hovered_corner = result;
        this.canvas_element.style.cursor = "ne-resize";
      }
      if (result && result_key === "bot_right") {
        this.ellipse_hovered_corner = result;
        this.canvas_element.style.cursor = "se-resize";
      }
      if (result && result_key === "top_left") {
        this.ellipse_hovered_corner = result;
        this.canvas_element.style.cursor = "nw-resize";
      }
      if (result && result_key === "bot_left") {
        this.ellipse_hovered_corner = result;
        this.canvas_element.style.cursor = "sw-resize";
      }

      if (result && (result_key === "bot" || result_key === "top")) {
        this.ellipse_hovered_corner = result;
        this.canvas_element.style.cursor = "row-resize";
      }
      if (result && result_key === "rotate") {
        this.ellipse_hovered_corner = result;
        this.canvas_element.style.cursor = "help";
      }
      if (!result) {
        this.ellipse_hovered_corner = undefined;
      }

      return result;
    },

    detect_hover_on_cuboid_corners: function () {
      if (!this.selected_instance) {
        return;
      }
      if (this.selected_instance.type != "cuboid") {
        return;
      }

      // avoid having a check for every point?
      let instance = this.selected_instance;

      let face_result = null;
      face_result = this.is_on_cuboid_corner(instance.front_face, "front_face");

      // false means none found, if is found we skip to save computation
      // null means force rear was trigged
      // this setup feels a bit awkward
      if (face_result == false || face_result == null) {
        face_result = this.is_on_cuboid_corner(instance.rear_face, "rear_face");
      }
    },

    build_middle_point: function (a_point, b_point) {
      return {
        x: (a_point.x + b_point.x) / 2,
        y: (a_point.y + b_point.y) / 2,
      };
    },

    is_on_cuboid_corner: function (face, name) {
      if (this.is_moving_cuboid_corner) {
        return;
      }
      // takes a face with multiple points
      // and then sees if any are intersecting
      // then does current expected stuff
      // returns true if found to allow early exit
      for (let key in face) {
        if (key === "width" || key === "height") {
          continue;
        }
        // corners
        if (
          this.point_is_intersecting_circle(this.mouse_position, face[key], 12)
        ) {
          this.canvas_element.style.cursor = "all-scroll";
          let cuboid_corner_move_point = {};
          cuboid_corner_move_point["point"] = key;
          cuboid_corner_move_point["face"] = name;
          cuboid_corner_move_point["type"] = "corner";
          this.cuboid_corner_move_point = cuboid_corner_move_point;
          return true;
        }
      }
      this.cuboid_corner_move_point = {};
      return false;
    },

    find_midpoint_index: function (instance, midpoints_polygon) {
      let midpoint_hover = undefined;
      let count = 0;

      for (const point of midpoints_polygon) {
        // TODO use user set param here
        let result = this.point_is_intersecting_circle(
          this.mouse_position,
          point,
          parseInt(this.label_settings.vertex_size * 4)
        );

        if (result) {
          midpoint_hover = count;
          this.canvas_element.style.cursor = "all-scroll";
        }
        count += 1;
      }
      if (midpoint_hover != undefined) {
        instance.midpoint_hover = midpoint_hover;

        this.instance_list.splice(this.selected_instance_index, 1, instance);
      } else {
        instance.midpoint_hover = undefined;
      }
      return midpoint_hover;
    },
    detect_hover_polygon_midpoints: function () {

      if (!this.selected_instance) {
        return;
      }
      const instance = this.selected_instance;
      if (!instance.selected) {
        return;
      }
      if (!instance.midpoints_polygon) {
        return;
      }

      // Check for hover on any middle point
      let midpoints_polygon = instance.midpoints_polygon;
      if (!Array.isArray(midpoints_polygon)) {
        for (let figure_id of Object.keys(midpoints_polygon)) {
          let figure_midpoints = midpoints_polygon[figure_id];
          let midpoint_hovered_point = this.find_midpoint_index(
            instance,
            figure_midpoints
          );
          if (midpoint_hovered_point != undefined) {
            break;
          }
        }
      } else {
        this.find_midpoint_index(instance, midpoints_polygon);
      }
    },
    detect_other_polygon_points: function () {
      if (!this.is_actively_drawing) {
        return;
      }
      if (!this.instance_type == "polygon") {
        return;
      }
      const polygons_list = this.instance_list.filter(
        (x) => x.type == "polygon"
      );

      for (const polygon of polygons_list) {
        for (const point of polygon.points) {
          if (
            this.point_is_intersecting_circle(this.mouse_position, point, 8)
          ) {
            point.hovered_while_drawing = true;
          } else {
            point.hovered_while_drawing = false;
          }
        }
      }
    },
    // TODO clarify this does more than update styling
    update_mouse_style: function () {
      if (this.view_only_mode == true) {
        return;
      }

      if (this.draw_mode == false) {
        if (this.lock_point_hover_change == false) {
          let hovered_instance = this.instance_list[this.instance_hover_index]
          if (this.canvas_element && (!hovered_instance || !SUPPORTED_IMAGE_CLASS_INSTANCE_TYPES.includes(hovered_instance.type))) {
            this.canvas_element.style.cursor = this.is_fully_zoomed_out ? "default" : "grab";
          }

        }

        this.detect_hover_on_cuboid_corners();

        this.detect_hover_on_ellipse_corners();

        this.detect_hover_on_curve();
        this.detect_hover_on_curve_control_points();


        this.detect_nearest_polygon_point();
        this.detect_hover_polygon_midpoints();

        this.detect_issue_hover();

        this.style_mouse_if_rotation();
      } else {
        if (this.canvas_element) {
          this.canvas_element.style.cursor = "default";
        }
      }
    },

    style_mouse_if_rotation: function () {
      if (this.instance_rotate_control_mouse_hover == true) {
        this.canvas_element.style.cursor = "help";
      }
    },
    detect_issue_hover: function () {
      if (
        this.issue_hover_index != undefined &&
        !isNaN(this.issue_hover_index)
      ) {
        this.canvas_element.style.cursor = "pointer";
      }
    },

    check_polygon_intersection_on_points: function (instance, points) {
      for (var j in points) {
        let result = this.point_is_intersecting_circle(
          this.mouse_position,
          instance["points"][j]
        );

        if (result == true) {
          this.canvas_element.style.cursor = "all-scroll";
          this.polygon_point_hover_index = parseInt(j);
          return true;
        }
      }
      return false;
    },
    detect_nearest_polygon_point: function () {
      this.polygon_point_hover_index = null;

      if (
        this.instance_hover_index != undefined &&
        ["polygon", "line", "point"].includes(this.instance_hover_type)
      ) {
        var instance = this.instance_list[this.instance_hover_index];
      }

      if (instance != undefined) {
        let has_figures =
          instance.points.filter((p) => p.figure_id != undefined).length > 0;
        if (!this.annotation_ui_context.hidden_label_id_list.includes(instance.label_file_id)) {
          // Polygon might have multiple figures.
          if (!has_figures) {
            this.check_polygon_intersection_on_points(
              instance,
              instance.points
            );
          } else {
            let figures_list = [];
            for (const p of instance.points) {
              if (!figures_list.includes(p.figure_id)) {
                figures_list.push(p.figure_id);
              }
            }
            for (const figure_id of figures_list) {
              let points = instance.points.filter(
                (p) => p.figure_id === figure_id
              );
              let intersects = this.check_polygon_intersection_on_points(
                instance,
                points
              );
              if (intersects) {
                break;
              }
            }
          }
        }
      }
    },
    select_issue: function () {
      if (this.view_only_mode == true) {
        return;
      }
      if (!this.issues_ui_manager || !this.issues_ui_manager.issues_list) { return }
      if (
        this.issue_hover_index == undefined ||
        isNaN(this.issue_hover_index)
      ) {
        return;
      } // careful 0 index is ok
    
      if (!this.issues_ui_manager.issues_list[this.issue_hover_index]) {
        return;
      }
  
      if (this.draw_mode) {
        return;
      }
      if (this.view_issue_mode && this.instance_select_for_issue) {
        return;
      }
      if (this.view_issue_mode && this.instance_select_for_merge) {
        return;
      }
      const issue = this.issues_ui_manager.issues_list[this.issue_hover_index];
      this.open_view_edit_panel(issue);
    },


    select_something: function () {
      if (this.view_only_mode == true) {
        return;
      }
      if (this.ellipse_hovered_corner_key) {
        return;
      }
      if (this.show_snackbar_occlude_direction) {
        return
      }
      if (
        this.selected_instance &&
        this.selected_instance.midpoint_hover != undefined
      ) {
        return;
      }
      if (
        this.instance_hover_index === undefined &&
        this.issue_hover_index === undefined
      ) {
        return;
      } // careful 0 index is ok
      if (this.draw_mode) {
        return;
      }
      if (this.view_issue_mode && !this.instance_select_for_issue) {
        return;
      }

      const instance_to_select = this.instance_list[this.instance_hover_index];
      if (instance_to_select && !SUPPORTED_IMAGE_CLASS_INSTANCE_TYPES.includes(instance_to_select.type)) {
        this.image_annotation_ctx.request_change_current_instance = this.instance_hover_index;
        this.image_annotation_ctx.trigger_refresh_current_instance = Date.now(); // decouple, for case of file changing but instance list being the same index

      }

      if (this.label_settings.allow_multiple_instance_select == false) {
        this.clear_selected(this.instance_list[this.instance_hover_index]);
        if (this.instance_hover_index == null) {
          this.refresh_instance_list_sidebar(null)
        }
      }

      if (this.instance_select_for_merge && this.polygon_merge_tool) {
        // Allow only selection of polygon with the same label file ID.
        if (!this.polygon_merge_tool.is_allowed_instance_to_merge(instance_to_select)) {
          return;
        }
      }


      if (instance_to_select && !SUPPORTED_IMAGE_CLASS_INSTANCE_TYPES.includes(instance_to_select.type)) {
        instance_to_select.selected = !instance_to_select.selected;
        instance_to_select.status = "updated";
        Vue.set(
          this.instance_list,
          this.instance_hover_index,
          instance_to_select
        );
        if (this.box_edit_point_hover != null) {
          // Logic for selecting box data.
          instance_to_select.box_edit_point_hover = this.box_edit_point_hover;
        }
      }

    },

    move_curve: function (event) {
      if (this.is_actively_resizing == false) {
        return;
      }
      if (this.instance_hover_index == undefined) {
        return;
      }
      const instance = this.instance_list[this.instance_hover_index];
      if (instance.type !== "curve") {
        return;
      }
      if (this.curve_hovered_point) {
        let x_new = parseInt(this.mouse_position.x);
        let y_new = parseInt(this.mouse_position.y);
        const instance = this.instance_list[this.instance_hover_index];
        if (!this.original_edit_instance) {
          this.original_edit_instance = {
            ...instance,
            p1: {...instance.p1},
            p2: {...instance.p2},
            cp: {...instance.cp},
          };
          this.original_edit_instance_index = this.instance_hover_index;
        }
        instance[this.curve_hovered_point].x = x_new;
        instance[this.curve_hovered_point].y = y_new;
      } else {
        // Move Entire curve
        let x_move = this.mouse_down_delta_event.x;
        let y_move = this.mouse_down_delta_event.y;
        instance.p1.x += x_move;
        instance.p1.y += y_move;

        instance.p2.x += x_move;
        instance.p2.y += y_move;

        instance.cp.x += x_move;
        instance.cp.y += y_move;
      }

      return true;
    },
    move_ellipse: function (event) {
      if (this.is_actively_resizing == false) {
        return;
      }
      if (
        !this.ellipse_hovered_corner_key &&
        this.instance_hover_index == undefined
      ) {
        return;
      }
      let x_move = this.mouse_down_delta_event.x;
      let y_move = this.mouse_down_delta_event.y;

      let instance = this.ellipse_hovered_instance;
      let instance_index = this.ellipse_hovered_instance_index;
      if (!instance) {
        return;
      }
      if (!this.original_edit_instance) {
        this.original_edit_instance = {
          ...this.instance_list[instance_index],
          points: [
            ...this.instance_list[instance_index].points.map((p) => ({...p})),
          ],
        };
        this.original_edit_instance_index = instance_index;
      }

      if (["right"].includes(this.ellipse_hovered_corner_key)) {
        instance.width += x_move;
      }
      if (["left"].includes(this.ellipse_hovered_corner_key)) {
        instance.width -= x_move;
      }
      if (["top"].includes(this.ellipse_hovered_corner_key)) {
        instance.height -= y_move;
      }
      if (["bot"].includes(this.ellipse_hovered_corner_key)) {
        instance.height += y_move;
      }
      if (["top_right"].includes(this.ellipse_hovered_corner_key)) {
        instance.height -= y_move;
        instance.width += x_move;
      }
      if (["top_left"].includes(this.ellipse_hovered_corner_key)) {
        instance.height -= y_move;
        instance.width -= x_move;
      }
      if (["bot_right"].includes(this.ellipse_hovered_corner_key)) {
        instance.height += y_move;
        instance.width += x_move;
      }
      if (["bot_left"].includes(this.ellipse_hovered_corner_key)) {
        instance.height += y_move;
        instance.width -= x_move;
      }

      if (["rotate"].includes(this.ellipse_hovered_corner_key)) {
        instance.angle = this.get_angle_of_rotated_ellipse(instance);
      }

      // Translation

      if (
        this.instance_hover_index != undefined &&
        !this.ellipse_hovered_corner_key
      ) {
        instance.center_x += x_move;
        instance.center_y += y_move;
        instance.center_x = parseInt(instance.center_x);
        instance.center_y = parseInt(instance.center_y);
      }

      instance.width = parseInt(instance.width);
      instance.height = parseInt(instance.height);
      instance.status = "updated";
      this.instance_list.splice(instance_index, 1, instance);
      return true;
    },

    get_angle_of_rotated_ellipse: function (instance) {
      // Read: https://math.stackexchange.com/questions/361412/finding-the-angle-between-three-points
      let a = instance.width;
      let b = instance.height;
      let t = Math.atan(-b * Math.tan(0)) / a;
      let centered_x = this.$ellipse.get_x_of_rotated_ellipse(t, instance, 0);
      let centered_y = this.$ellipse.get_y_of_rotated_ellipse(t, instance, 0);
      let A = {x: centered_x, y: centered_y};
      let B = {x: instance.center_x, y: instance.center_y};
      let C = {x: this.mouse_position.x, y: this.mouse_position.y};
      let BA = {x: A.x - B.x, y: A.y - B.y};
      let BC = {x: C.x - B.x, y: C.y - B.y};
      let BA_len = Math.sqrt(BA.x ** 2 + BA.y ** 2);
      let BC_len = Math.sqrt(BC.x ** 2 + BC.y ** 2);
      let BA_dot_BC = BA.x * BC.x + BA.y * BC.y;
      let theta = Math.acos(BA_dot_BC / (BA_len * BC_len));
      let angle = 0;
      if (this.mouse_position.y < B.y) {
        angle = Math.PI / 2 - theta;
      } else {
        if (theta <= Math.PI / 2 && theta > 0) {
          // First cuadrant.
          angle = Math.PI / 2 + theta;
        } else if (theta > Math.PI / 2 && theta > 0) {
          // Second Cuadrant
          angle = Math.PI / 2 + theta;
        }
      }
      return angle;
    },

    move_cuboid: function (event) {
      // Would prefer this to be part of general "move" something thing.
      if (this.is_actively_resizing == false) {
        return;
      }
      let cuboid_did_move = false;
      let instance = this.instance_list[this.instance_hover_index];
      if (!instance) {
        return;
      }

      // Feel like this is duplicated with mouse style thing
      let force_move_face = false;

      if (
        instance.cuboid_force_move_face == true ||
        this.cuboid_force_move_face == true
      ) {
        force_move_face = true;
      }
      let x_move = this.mouse_down_delta_event.x;
      let y_move = this.mouse_down_delta_event.y;
      let type = this.cuboid_corner_move_point
        ? this.cuboid_corner_move_point.type
        : undefined;
      let face_key = this.cuboid_corner_move_point
        ? this.cuboid_corner_move_point.face
        : undefined;
      let point = this.cuboid_corner_move_point
        ? this.cuboid_corner_move_point.point
        : undefined;
      let face;
      if (face_key) {
        face = instance[face_key];
      }
      if (this.cuboid_face_hover && type != "corner") {
        cuboid_did_move = this.move_cuboid_face(
          this.cuboid_face_hover,
          x_move,
          y_move
        );
      }
      if (force_move_face == false) {
        if (type == "corner" || this.is_moving_cuboid_corner) {
          if (face) {
          }
          this.is_moving_cuboid_corner = true;
          cuboid_did_move = this.move_cuboid_edge(face, point, x_move, y_move);
        }
      }
      return cuboid_did_move;
    },

    move_cuboid_face: function (hovered_face, x_move, y_move) {
      if (
        !["right", "left", "top", "bottom", "rear", "front"].includes(
          hovered_face
        )
      ) {
        return false;
      }

      const instance = this.instance_list[this.instance_hover_index];
      if (!this.original_edit_instance) {
        this.original_edit_instance = {
          ...this.instance_list[this.polygon_click_index],
          points: [
            ...this.instance_list[this.polygon_click_index].points.map((p) => ({
              ...p,
            })),
          ],
        };
        this.original_edit_instance.rear_face = {
          ...instance.rear_face,
          top_right: {...instance.rear_face.top_right},
          top_left: {...instance.rear_face.top_left},
          bot_left: {...instance.rear_face.bot_left},
          bot_right: {...instance.rear_face.bot_right},
        };
        this.original_edit_instance.front_face = {
          ...instance.front_face,
          top_right: {...instance.front_face.top_right},
          top_left: {...instance.front_face.top_left},
          bot_left: {...instance.front_face.bot_left},
          bot_right: {...instance.front_face.bot_right},
        };
        this.original_edit_instance_index = this.polygon_click_index;
      }
      let is_updated = true;
      if (hovered_face === "rear") {
        const instance = this.instance_list[this.instance_hover_index];
        const face = instance["rear_face"];
        for (let key in face) {
          if (key === "height" || key === "width") {
            continue;
          }
          let point = face[key];
          point.x += x_move;
          point.y += y_move;
          face[key] = point;
        }
      } else if (hovered_face === "right") {
        instance.front_face.top_right.x += x_move;
        instance.front_face.bot_right.x += x_move;
        instance.rear_face.bot_right.x += x_move;
        instance.rear_face.top_right.x += x_move;
        instance.rear_face.width = Math.abs(
          instance.rear_face.top_right.x - instance.rear_face.top_left.x
        );
        instance.front_face.width = Math.abs(
          instance.front_face.top_right.x - instance.front_face.top_left.x
        );
      } else if (hovered_face === "left") {
        instance.front_face.top_left.x += x_move;
        instance.front_face.bot_left.x += x_move;
        instance.rear_face.bot_left.x += x_move;
        instance.rear_face.top_left.x += x_move;
        instance.rear_face.width = Math.abs(
          instance.rear_face.top_right.x - instance.rear_face.top_left.x
        );
        instance.front_face.width = Math.abs(
          instance.front_face.top_right.x - instance.front_face.top_left.x
        );
      } else if (hovered_face === "bottom") {
        instance.front_face.bot_right.y += y_move;
        instance.front_face.bot_left.y += y_move;
        instance.rear_face.bot_right.y += y_move;
        instance.rear_face.bot_left.y += y_move;
        instance.rear_face.height = Math.abs(
          instance.rear_face.top_right.y - instance.rear_face.bot_right.y
        );
        instance.front_face.height = Math.abs(
          instance.front_face.top_right.y - instance.front_face.bot_right.y
        );
      } else if (hovered_face === "top") {
        instance.front_face.top_right.y += y_move;
        instance.front_face.top_left.y += y_move;
        instance.rear_face.top_right.y += y_move;
        instance.rear_face.top_left.y += y_move;
        instance.rear_face.height = Math.abs(
          instance.rear_face.top_right.y - instance.rear_face.bot_right.y
        );
        instance.front_face.height = Math.abs(
          instance.front_face.top_right.y - instance.front_face.bot_right.y
        );
      } else {
        is_updated = false;
      }
      if (is_updated) {
        instance.status = "updated";
      }
      this.instance_list.splice(this.instance_hover_index, 1, instance);
      return is_updated;
    },

    move_cuboid_edge: function (face, edge_name, x_move, y_move) {
      /* Define which points are mapped to which edge
       * Given an edge, adjust all points in maping appropirately
       */
      const opposite_edge = this.opposite_edges_map[edge_name];
      const lateral_edges = this.lateral_edges[edge_name];
      const instance = this.instance_list[this.instance_hover_index];
      if (!this.original_edit_instance) {
        this.original_edit_instance = {
          ...this.instance_list[this.polygon_click_index],
          points: [
            ...this.instance_list[this.polygon_click_index].points.map((p) => ({
              ...p,
            })),
          ],
        };
        this.original_edit_instance.rear_face = {
          ...instance.rear_face,
          top_right: {...instance.rear_face.top_right},
          top_left: {...instance.rear_face.top_left},
          bot_left: {...instance.rear_face.bot_left},
          bot_right: {...instance.rear_face.bot_right},
        };
        this.original_edit_instance.front_face = {
          ...instance.front_face,
          top_right: {...instance.front_face.top_right},
          top_left: {...instance.front_face.top_left},
          bot_left: {...instance.front_face.bot_left},
          bot_right: {...instance.front_face.bot_right},
        };
        this.original_edit_instance_index = this.polygon_click_index;
      }
      // First Move select Point
      let selected_point = face[edge_name];
      selected_point.x += x_move;
      selected_point.y += y_move;
      selected_point.x = parseInt(selected_point.x, 10);
      selected_point.y = parseInt(selected_point.y, 10);
      face[edge_name] = selected_point;
      // Now move lateral edges.

      for (let i = 0; i < lateral_edges.length; i++) {
        const key = lateral_edges[i];
        let point = face[key];
        if (i === 0) {
          point.x += x_move;
          point.x = parseInt(point.x, 10);
        } else {
          point.y += y_move;
          point.y = parseInt(point.y, 10);
        }
        face[key] = point;
      }

      instance.status = "updated";
      this.instance_list.splice(this.instance_hover_index, 1, instance);
      return true;
    },
    drag_polygon: function (event) {
      if (this.is_actively_resizing == false) {
        return;
      }
      if (this.polygon_point_click_index) {
        return;
      }
      if (this.instance_hover_index == undefined) {
        return;
      }
      if (this.instance_hover_type !== "polygon") {
        return;
      }
      const instance = this.instance_list[this.instance_hover_index];
      if (!instance.selected) {
        return;
      }
      if (!this.original_edit_instance) {
        this.original_edit_instance = {
          ...this.instance_list[this.polygon_click_index],
          points: [
            ...this.instance_list[this.polygon_click_index].points.map((p) => ({
              ...p,
            })),
          ],
        };
        this.original_edit_instance_index = this.polygon_click_index;
      }
      let points = instance.points;
      if (this.hovered_figure_id) {
        points = instance.points.filter(
          (p) => p.figure_id === this.hovered_figure_id
        );
      }
      let x_move = this.mouse_down_delta_event.x;
      let y_move = this.mouse_down_delta_event.y;
      for (const point of points) {
        point.x += x_move;
        point.y += y_move;
      }
      if (!this.hovered_figure_id) {
        this.instance_list.splice(this.instance_hover_index, 1, instance);
      } else {
        let rest_of_points = instance.points.filter(
          (p) => p.figure_id !== this.hovered_figure_id
        );
        instance.points = points.concat(rest_of_points);
        this.instance_list.splice(this.instance_hover_index, 1, instance);
      }

      return true;
    },

    ghost_clear_for_file_change_context: function () {
      this.ghost_clear_hover_index();
      this.ghost_clear_list();
    },

    ghost_clear_hover_index: function () {
      this.ghost_instance_hover_index = null;
      this.ghost_instance_hover_type = null;
    },

    ghost_clear_list: function () {
      this.ghost_instance_list = [];
    },

    ghost_promote_instance_to_actual: function (ghost_index) {
      this.$emit('set_has_changed', true); // otherwise user click event won't trigger change detection

      let instance = this.ghost_instance_list[ghost_index];
      instance = this.initialize_instance(instance)
      instance = post_init_instance(instance,
        this.label_file_map,
        this.canvas_element,
        this.label_settings,
        this.canvas_transform,
        this.instance_hovered,
        this.instance_unhovered,
        this.canvas_mouse_tools
      )
      this.add_instance_to_file(instance, this.image_annotation_ctx.current_frame); // this handles the creation_ref_id stuff too
      this.ghost_instance_list.splice(ghost_index, 1); // remove from ghost list
    },

    ghost_may_promote_instance_to_actual: function () {
      if (this.label_settings.show_ghost_instances == false) {
        return;
      }
      if (this.ghost_instance_hover_index != undefined) {
        // may be 0!
        this.instance_hover_index = this.ghost_instance_hover_index;
        this.instance_hover_type = this.ghost_instance_hover_type;
        this.ghost_promote_instance_to_actual(this.ghost_instance_hover_index);
        this.ghost_clear_hover_index();
      }
    },
    calculate_min_max_points: function (instance) {
      if (!instance) {
        return;
      }
      if (["polygon", "point"].includes(instance.type)) {
        if (!instance.points) {
          return
        }
        instance.x_min = Math.min(...instance.points.map((p) => p.x));
        instance.y_min = Math.min(...instance.points.map((p) => p.y));
        instance.x_max = Math.max(...instance.points.map((p) => p.x));
        instance.y_max = Math.max(...instance.points.map((p) => p.y));
      } else if (["cuboid"].includes(instance.type)) {
        if (!instance.front_face || !instance.rear_face) {
          return
        }
        instance.x_min = Math.min(
          instance.front_face["top_right"]["x"],
          instance.front_face["bot_right"]["x"],
          instance.front_face["top_left"]["x"],
          instance.front_face["bot_right"]["x"],
          instance.rear_face["top_right"]["x"],
          instance.rear_face["bot_right"]["x"],
          instance.rear_face["top_left"]["x"],
          instance.rear_face["bot_right"]["x"]
        );
        instance.x_max = Math.max(
          instance.front_face["top_right"]["x"],
          instance.front_face["bot_right"]["x"],
          instance.front_face["top_left"]["x"],
          instance.front_face["bot_right"]["x"],
          instance.rear_face["top_right"]["x"],
          instance.rear_face["bot_right"]["x"],
          instance.rear_face["top_left"]["x"],
          instance.rear_face["bot_right"]["x"]
        );
        instance.y_min = Math.min(
          instance.front_face["top_right"]["y"],
          instance.front_face["bot_right"]["y"],
          instance.front_face["top_left"]["y"],
          instance.front_face["bot_right"]["y"],
          instance.rear_face["top_right"]["y"],
          instance.rear_face["bot_right"]["y"],
          instance.rear_face["top_left"]["y"],
          instance.rear_face["bot_right"]["y"]
        );
        instance.y_max = Math.max(
          instance.front_face["top_right"]["y"],
          instance.front_face["bot_right"]["y"],
          instance.front_face["top_left"]["y"],
          instance.front_face["bot_right"]["y"],
          instance.rear_face["top_right"]["y"],
          instance.rear_face["bot_right"]["y"],
          instance.rear_face["top_left"]["y"],
          instance.rear_face["bot_right"]["y"]
        );
      } else if (["ellipse"].includes(instance.type)) {
        if (!instance.center_x || !instance.center_y || !instance.width || !instance.height) {
          return
        }
        instance.x_min = instance.center_x - instance.width;
        instance.y_min = instance.center_y - instance.height;
        instance.x_max = instance.center_x + instance.width;
        instance.y_max = instance.center_y + instance.height;
      } else if (["curve"].includes(instance.type)) {
        if (!instance.p1 || !instance.p2) {
          return
        }
        instance.x_min = Math.min(instance.p1.x, instance.p2.x);
        instance.x_max = Math.max(instance.p1.x, instance.p2.x);
        instance.y_min = Math.min(instance.p1.y, instance.p2.y);
        instance.y_max = Math.max(instance.p1.y, instance.p2.y);
      } else {
        instance.x_min = parseInt(instance.x_min);
        instance.y_min = parseInt(instance.y_min);
        instance.x_max = parseInt(instance.x_max);
        instance.y_max = parseInt(instance.y_max);
      }
    },
    move_keypoints: function () {
      let key_points_did_move = false;
      let instance = this.instance_list[this.instance_hover_index];
      if (instance && this.is_actively_resizing) {
        if (!this.original_edit_instance) {
          this.original_edit_instance = instance.duplicate_for_undo();
          this.original_edit_instance_index = this.instance_hover_index;
        }
        key_points_did_move = instance.move();
      }
      return key_points_did_move;
    },

    move_something: function (event) {
      if (this.draw_mode == true) {
        return;
      }
      if (this.view_only_mode == true) {
        return;
      }
      if (this.instance_select_for_issue == true) {
        return;
      }
      if (this.instance_select_for_merge == true) {
        return;
      }
      if (this.view_issue_mode) {
        return;
      }
      let cuboid_did_move = false;
      let ellipse_did_move = false;
      let curve_did_move = false;
      let key_points_did_move = false;

      if (
        (this.instance_hover_index != undefined &&
          this.instance_hover_type == "cuboid") ||
        (this.selected_instance && this.selected_instance.type === "cuboid")
      ) {
        cuboid_did_move = this.move_cuboid(event);
      }
      if (
        this.ellipse_hovered_corner ||
        (this.instance_hover_index != undefined &&
          this.instance_hover_type === "ellipse")
      ) {
        ellipse_did_move = this.move_ellipse(event);
      }
      if (
        this.instance_hover_index != undefined &&
        this.instance_hover_type === "curve"
      ) {
        curve_did_move = this.move_curve(event);
      }
      // want this seperate from other conditinos for now
      // this is similar to that "activel drawing" concept
      // not 100% sure how to explain difference between it
      if (this.$store.state.annotation_state.mouse_down == true) {
        this.lock_point_hover_change = true;
      } else {
        // release lock
        this.lock_point_hover_change = false;
      }

      // let polygon_did_move = this.move_polygon_line_or_point(event);
      // let polygon_dragged = false;
      // if (!polygon_did_move) {
      //   polygon_dragged = this.drag_polygon(event);
      // }

      if (
        // box_did_move ||
        // polygon_did_move ||
        cuboid_did_move ||
        ellipse_did_move ||
        curve_did_move ||
        // polygon_dragged ||
        key_points_did_move
      ) {
        this.calculate_min_max_points(
          this.instance_list[this.instance_hover_index]
        );
        this.set_instance_human_edited(
          this.instance_list[this.instance_hover_index]
        );
        this.$emit('set_has_changed', true);
      }
    },

    move_polygon_line_or_point: function (event) {
      /*
      Returns true if moved something. This handles the movement of
      any of the following instances: point, polygon, line.

     */
      if (!this.instance_list) {
        return;
      }

      if (this.polygon_point_click_index != null) {
        if (this.$store.state.annotation_state.mouse_down == true) {
          var i = this.polygon_click_index;
          var j = this.polygon_point_click_index;

          if (this.instance_list[i] == true) {
            this.snackbar_warning = true;
            this.snackbar_warning_text = "Undo delete first.";
            return;
          }
          if (
            !this.original_edit_instance &&
            this.instance_list[this.polygon_click_index]
          ) {
            this.original_edit_instance = {
              ...this.instance_list[this.polygon_click_index],
              points: [
                ...this.instance_list[this.polygon_click_index].points.map(
                  (p) => ({...p})
                ),
              ],
            };
            this.original_edit_instance_index = this.polygon_click_index;
          }
          if (this.instance_list[i] && this.instance_list[i]["points"][j]) {
            let x_new = parseInt(this.mouse_position.x);
            let y_new = parseInt(this.mouse_position.y);
            if (this.instance_list[i])
              this.instance_list[i]["points"][j].x = x_new;
            this.instance_list[i]["points"][j].y = y_new;

            return true;
          }
        }
      }
    },
    get_media_promise: function () {
      return new Promise((resolve) => {
        resolve(this.get_media());
      });
    },

    addImageProcess: function (src) {
      return new Promise((resolve, reject) => {
        let image = new Image();
        image.src = src;
        if (process.env.NODE_ENV === "testing") {
          image.crossOrigin = "anonymous";
        }
        image.onload = () => {
          resolve(image)
        };
        image.onerror = reject;
      });
    },
    video_update_core: async function (file: File) {
      // TODO change this to update video component?

      this.original_media_width = file.video.width;
      this.original_media_height = file.video.height;
      this.canvas_mouse_tools.set_canvas_width_height(this.original_media_width, this.original_media_height)
      this.image_annotation_ctx.video_mode = true;
      this.current_video = file.video;
      this.current_video_file_id = file.id;
      await this.get_instances();
      // We need to trigger components and DOM updates before updating frames and sequences.
      // To read more: https://medium.com/javascript-in-plain-english/what-is-vue-nexttick-89d6878c1162
      await this.$nextTick();

      //console.debug('VIDEO UPDATE COREE', this.current_file.video);
      await this.$refs.video_controllers.current_video_update();
      // Update the frame data.
      if (this.$refs.clear_sequence_list_cache) {
        await this.$refs.sequence_list.clear_sequence_list_cache();
        await this.$refs.sequence_list.get_sequence_list();
      }

      // We need to update sequence lists synchronously to know when to remove the placeholder.
    },
    prepare_canvas_for_new_file: async function (file: File) {
      if (file != undefined) {
        if (file.type == "image") {
          await this.image_update_core(file);
        }
        if (file.type == "video") {
          await this.video_update_core(file);
        }
      } else {
        this.image_annotation_ctx.loading = false;
        this.image_annotation_ctx.annotations_loading = false;
        // The two different loading flags relate to differential between loading files,
        // and loading annotations which need to be different in current design
      }

      // Even though we call update_canvas on multiple places, it doesnt always update as expected because we have to
      // wait for the next tick to happen
      await this.$nextTick();
      this.update_canvas();
    },

    logout() {
      if (this.$store.state.user.current.is_super_admin != true) {
        this.$store.dispatch("log_out");
        this.$router.push("/user/login");
      }
    },

    image_update_core: async function (file: File) {

      if (!file) {
        this.image_annotation_ctx.loading = false;
      } else {
        this.$emit("current_file", file);
      }

      this.canvas_wrapper.style.display = "";
      await this.get_instances();
      let determineSize = function (width, height, degrees) {
        let w, h;
        degrees = Math.abs(degrees)
        if (degrees === 90 || degrees === 270) { // values for width and height are swapped for these rotation positions
          w = height
          h = width
        } else {
          w = width
          h = height
        }
        return {width: w, height: h}
      }
      this.degrees = file.image.rotation_degrees
      if (this.degrees == undefined) {
        this.degrees = 0
      }
      let newSize = determineSize(file.image.width, file.image.height, this.degrees)
      this.original_media_width = newSize.width;
      this.original_media_height = newSize.height;
      this.canvas_mouse_tools.set_canvas_width_height(this.original_media_width, this.original_media_height)
      await this.addImageProcess_with_canvas_refresh(file);
    },

    addImageProcess_with_canvas_refresh: async function (file: Files) {
      try {
        const new_image = await this.addImageProcess(
          file.image.url_signed
        );
        this.html_image = new_image;
        this.update_canvas();
        this.image_annotation_ctx.loading = false;
        this.refresh = Date.now();
      } catch (error) {
        console.error(error);
      }
    },
    toInt: function (n) {
      return Math.round(Number(n));
    },
    onRendered: function (ctx) {
    },
    test: function () {
      console.debug(Date.now());
    },
    mouse_transform: function (event, mouse_position) {
      this.populate_canvas_element();
      return this.canvas_mouse_tools.mouse_transform(
        event,
        mouse_position,
        this.canvas_element
      );
    },

    move_position_based_on_mouse: function (movementX, movementY) {
      if (this.canvas_mouse_tools.scale === this.canvas_scale_global) {
        return;
      }

      // Map Bounds to World
      var transform = this.canvas_mouse_tools.canvas_ctx.getTransform();

      let min_point = this.canvas_mouse_tools.map_point_from_matrix(
        1,
        1,
        transform
      );

      let max_point = this.canvas_mouse_tools.map_point_from_matrix(
        this.original_media_width - 1,
        this.original_media_height - 1,
        transform
      );

      // Propose Position with Movement
      let x_min_proposed = Math.max(0 + movementX, 0);
      let y_min_proposed = Math.max(0 + movementY, 0);

      let x_max_proposed = Math.min(
        this.canvas_width_scaled + movementX,
        this.canvas_width_scaled
      );
      let y_max_proposed = Math.min(
        this.canvas_height_scaled + movementY,
        this.canvas_height_scaled
      );

      // Test if proposed position will break world mapped bounds
      if (x_min_proposed > min_point.x && x_max_proposed < max_point.x) {
        let new_bounds =
          this.canvas_mouse_tools.get_new_bounds_from_translate_x(
            movementX,
            this.original_media_width - 1,
            this.original_media_height - 1
          );

        if (movementX < 0 && new_bounds.x_min > 0) {
          movementX = movementX + new_bounds.x_min;
        }
        if (movementX > 0 && new_bounds.x_max < x_max_proposed) {
          movementX = movementX - (x_max_proposed - new_bounds.x_max);
        }
        this.canvas_mouse_tools.pan_x(movementX);
      }

      if (y_min_proposed > min_point.y && y_max_proposed < max_point.y) {
        let new_bounds =
          this.canvas_mouse_tools.get_new_bounds_from_translate_y(
            movementY,
            this.original_media_width - 1,
            this.original_media_height - 1
          );

        if (movementY < 0 && new_bounds.y_min > 0) {
          movementY = movementY + new_bounds.y_min;
        }
        if (movementY > 0 && new_bounds.y_max < y_max_proposed) {
          movementY = movementY - (y_max_proposed - new_bounds.y_max);
        }

        this.canvas_mouse_tools.pan_y(movementY);
      }

      this.refresh_instances_in_viewport(this.instance_list)

    },

    mouse_move: function (event) {

      const is_panning = this.is_mouse_down
        && this.instance_hover_index == null
        && !this.draw_mode

      if(!this.is_active){
        return
      }

      if ( !this.is_fully_zoomed_out && ( this.z_key === true || this.mouse_wheel_button ) ) {
        this.move_position_based_on_mouse(event.movementX, event.movementY);
        this.canvas_element.style.cursor = "move";
        this.$forceUpdate();
        return;
      } else if (is_panning && !this.is_fully_zoomed_out ) {
        this.move_position_based_on_mouse(-event.movementX, -event.movementY);
        this.canvas_element.style.cursor = "grabbing";
        this.$forceUpdate();
      }

      this.mouse_position = this.mouse_transform(event, this.mouse_position);

      this.move_something(event);

      this.update_mouse_style();

      // For refactored instance types (eventually all should be here)
      this.mouse_move_v2_handler(event)
      //console.debug(this.mouse_position)
    },

    line_and_curve_point_limits: function () {
      // snap to edges
      let current_point = this.current_polygon_point;
      // Set Autoborder point if exists
      if (
        this.is_actively_drawing &&
        this.auto_border_polygon_p1 &&
        !this.auto_border_polygon_p2
      ) {
        current_point.x = this.auto_border_polygon_p1.x;
        current_point.y = this.auto_border_polygon_p1.y;
        current_point.point_set_as_auto_border = true;
      }
      if (
        this.is_actively_drawing &&
        this.auto_border_polygon_p1 &&
        this.auto_border_polygon_p2
      ) {
        current_point.x = this.auto_border_polygon_p2.x;
        current_point.y = this.auto_border_polygon_p2.y;
        current_point.point_set_as_auto_border = true;
      }
      // TODO look at if this should be 0 or 1  and width or width -1
      if (this.current_polygon_point.x <= this.snap_to_edges) {
        current_point.x = 1;
      }
      if (this.current_polygon_point.y <= this.snap_to_edges) {
        current_point.y = 1;
      }
      if (
        this.current_polygon_point.x >=
        this.original_media_width - this.snap_to_edges
      ) {
        current_point.x = this.original_media_width - 1;
      }
      if (
        this.current_polygon_point.y >=
        this.original_media_height - this.snap_to_edges
      ) {
        current_point.y = this.original_media_height - 1;
      }
      return current_point;
    },
    perform_auto_bordering_v2: function (path_type: string) {
      const auto_border_tool = new PolygonAutoBorderTool(this.auto_border_context)
      auto_border_tool.perform_auto_bordering(path_type, this.instance_list, this.current_drawing_polygon_instance)
    },
    perform_auto_bordering: function (path_type) {
      const auto_border_polygon =
        this.instance_list[this.auto_border_context.auto_border_polygon_p2_instance_index];
      let points = auto_border_polygon.points;
      if (this.auto_border_context.auto_border_polygon_p1_figure) {
        points = auto_border_polygon.points.filter(
          (p) => p.figure_id === this.auto_border_context.auto_border_polygon_p1_figure
        );
      }

      // Forward Path
      let current_index = this.auto_border_context.auto_border_polygon_p1_index;
      let forward_count = 0;
      let forward_index_list = [];
      while (current_index != this.auto_border_context.auto_border_polygon_p2_index) {
        // Don't add p1 index
        if (current_index !== this.auto_border_context.auto_border_polygon_p1_index) {
          forward_index_list.push(current_index);
        }
        if (current_index >= points.length) {
          current_index = 0;
          forward_count += 1;
          continue;
        }
        current_index += 1;
        forward_count += 1;
      }

      // Backwards path
      current_index = this.auto_border_context.auto_border_polygon_p1_index;
      let backward_count = 0;
      let backward_index_list = [];
      while (current_index != this.auto_border_context.auto_border_polygon_p2_index) {
        // Don't add p1 index
        if (current_index !== this.auto_border_context.auto_border_polygon_p1_index) {
          backward_index_list.push(current_index);
        }
        if (current_index < 0) {
          current_index = points.length;
          backward_count += 1;
          continue;
        }
        current_index -= 1;
        backward_count += 1;
      }
      const longest = forward_count > backward_count ? "forward" : "backward";
      const shortest = forward_count <= backward_count ? "forward" : "backward";
      if (path_type === "long_path") {
        if (longest === "forward") {
          for (const index of forward_index_list) {
            if (points[index] == undefined) {
              continue;
            }
            this.current_polygon_point_list.push({
              ...points[index],
              figure_id: undefined,
            });
          }
        } else {
          for (const index of backward_index_list) {
            if (points[index] == undefined) {
              continue;
            }
            this.current_polygon_point_list.push({
              ...points[index],
              figure_id: undefined,
            });
          }
        }
      } else {
        if (shortest === "forward") {
          for (const index of forward_index_list) {
            if (points[index] == undefined) {
              continue;
            }
            //console.debug('indexx2', index, auto_border_polygon.points[index]);
            this.current_polygon_point_list.push({
              ...points[index],
              figure_id: undefined,
            });
          }
        } else {
          for (const index of backward_index_list) {
            if (points[index] == undefined) {
              continue;
            }
            //console.debug('indexx', index, auto_border_polygon.points[index]);
            this.current_polygon_point_list.push({
              ...points[index],
              figure_id: undefined,
            });
          }
        }
      }

      this.current_polygon_point_list.push({
        ...this.auto_border_context.auto_border_polygon_p2,
        figure_id: undefined,
      });
      this.auto_border_context.auto_border_polygon_p1 = undefined;
      this.auto_border_context.auto_border_polygon_p1_index = undefined;
      this.auto_border_context.auto_border_polygon_p1_figure = undefined;
      this.auto_border_context.auto_border_polygon_p1_instance_index = undefined;
      this.auto_border_context.auto_border_polygon_p2 = undefined;
      this.auto_border_context.auto_border_polygon_p2_index = undefined;
      this.auto_border_context.auto_border_polygon_p2_figure = undefined;
      this.auto_border_context.auto_border_polygon_p2_instance_index = undefined;
      this.auto_border_context.show_polygon_border_context_menu = false;
    },
    finish_polygon_drawing: function (event: Event) {
      let ann_ctx = this.build_ann_event_ctx()
      let ann_tool_event: InteractionEvent = genImageAnnotationEvent(event, ann_ctx)
      const coordinator = this.generate_interaction_coordinator(ann_tool_event);
      let result = coordinator.perform_action_from_event(ann_tool_event)
      if (result) {
        this.is_actively_drawing = result.is_actively_drawing
      }
      if (result.new_instance_index != undefined) {
        post_init_instance(this.instance_list[result.new_instance_index],
          this.label_file_map,
          this.canvas_element,
          this.label_settings,
          this.canvas_transform,
          this.instance_hovered,
          this.instance_unhovered,
          this.canvas_mouse_tools
        )
        this.new_instance_refresh(result.new_instance_index)
      }

    },
    instance_insert_point: function (frame_number = undefined) {
      const current_point = this.line_and_curve_point_limits();

      if (this.auto_border_context.auto_border_polygon_p1 && this.auto_border_context.auto_border_polygon_p2) {
        this.auto_border_context.show_polygon_border_context_menu = true;
      } else {
        this.current_polygon_point_list.push(current_point); // points only
      }
    },

    curve_mouse_up: function (frame_number = undefined) {
      if (
        this.instance_type == "curve" &&
        this.current_polygon_point_list.length == 2
      ) {
        const command = new CreateInstanceCommand(this.current_instance, this, frame_number);
        this.annotation_ui_context.command_manager.executeCommand(command);
        this.original_edit_instance = undefined;
        this.original_edit_instance_index = undefined;
        this.is_actively_drawing = false;
        this.current_polygon_point_list = [];
      }
    },
    polygon_mouse_up_edit: function () {
      if (!this.original_edit_instance) {
        return;
      }
      if (this.original_edit_instance.type != "polygon") {
        return;
      }
      if (this.original_edit_instance_index == undefined) {
        return;
      }

      const command = new UpdateInstanceCommand(
        this.instance_list[this.original_edit_instance_index],
        this.original_edit_instance_index,
        this.original_edit_instance,
        this
      );
      this.annotation_ui_context.command_manager.executeCommand(command);

      if (
        this.instance_hover_index != undefined &&
        typeof this.instance_list[this.instance_hover_index]["points"][
          this.polygon_point_hover_index
          ] != "undefined"
      ) {
        this.instance_list[this.instance_hover_index]["points"][
          this.polygon_point_hover_index
          ].selected = false;
      }
      this.original_edit_instance = undefined;
      this.original_edit_instance_index = undefined;
    },
    line_mouse_up_edit: function () {
      if (!this.original_edit_instance) {
        return;
      }
      if (this.original_edit_instance.type != "line") {
        return;
      }
      if (this.original_edit_instance_index == undefined) {
        return;
      }
      const command = new UpdateInstanceCommand(
        this.instance_list[this.original_edit_instance_index],
        this.instance_hover_index,
        this.original_edit_instance,
        this
      );
      this.annotation_ui_context.command_manager.executeCommand(command);
      if (
        this.instance_hover_index != undefined &&
        typeof this.instance_list[this.instance_hover_index]["points"][
          this.polygon_point_hover_index
          ] != "undefined"
      ) {
        this.instance_list[this.instance_hover_index]["points"][
          this.polygon_point_hover_index
          ].selected = false;
      }
      this.original_edit_instance = undefined;
      this.original_edit_instance_index = undefined;
    },
    point_mouse_up_edit: function () {
      if (!this.original_edit_instance) {
        return;
      }
      if (this.original_edit_instance.type != "point") {
        return;
      }
      if (this.original_edit_instance_index == undefined) {
        return;
      }
      const command = new UpdateInstanceCommand(
        this.instance_list[this.original_edit_instance_index],
        this.instance_hover_index,
        this.original_edit_instance,
        this
      );
      this.annotation_ui_context.command_manager.executeCommand(command);
      if (
        this.instance_hover_index != undefined &&
        typeof this.instance_list[this.instance_hover_index]["points"][
          this.polygon_point_hover_index
          ] != "undefined"
      ) {
        this.instance_list[this.instance_hover_index]["points"][
          this.polygon_point_hover_index
          ].selected = false;
      }
      this.original_edit_instance = undefined;
      this.original_edit_instance_index = undefined;
    },
    cuboid_mouse_up_edit: function () {
      if (!this.original_edit_instance) {
        return;
      }
      if (this.original_edit_instance.type != "cuboid") {
        return;
      }
      if (this.original_edit_instance_index == undefined) {
        return;
      }
      const command = new UpdateInstanceCommand(
        this.instance_list[this.original_edit_instance_index],
        this.original_edit_instance_index,
        this.original_edit_instance,
        this
      );
      this.annotation_ui_context.command_manager.executeCommand(command);
      this.is_moving_cuboid_corner = false;
      this.original_edit_instance = undefined;
      this.original_edit_instance_index = undefined;
    },
    curve_mouse_up_edit: function () {
      if (!this.original_edit_instance) {
        return;
      }
      if (this.original_edit_instance.type != "curve") {
        return;
      }
      if (this.original_edit_instance_index == undefined) {
        return;
      }
      const command = new UpdateInstanceCommand(
        this.instance_list[this.original_edit_instance_index],
        this.original_edit_instance_index,
        this.original_edit_instance,
        this
      );
      this.annotation_ui_context.command_manager.executeCommand(command);
      this.original_edit_instance = undefined;
      this.original_edit_instance_index = undefined;
    },
    keypoint_mouse_up_edit: function () {
      if (!this.original_edit_instance) {
        return;
      }
      if (this.original_edit_instance.type != "keypoints") {
        return;
      }
      if (this.original_edit_instance_index == undefined) {
        return;
      }

      const command = new UpdateInstanceCommand(
        this.instance_list[this.original_edit_instance_index],
        this.original_edit_instance_index,
        this.original_edit_instance,
        this
      );
      this.annotation_ui_context.command_manager.executeCommand(command);
      this.original_edit_instance = undefined;
      this.original_edit_instance_index = undefined;
    },
    polygon_delete_point_click_callback: function (polygon_point_index) {
      if (!this.selected_instance) {
        return
      }
      if (!this.selected_instance) {
        return;
      }
      if (this.selected_instance.type !== "polygon") {
        return;
      }
      let i = 0;
      if (polygon_point_index != undefined) {
        this.selected_instance.points.splice(polygon_point_index, 1);
      } else {
        for (const point of this.selected_instance.points) {
          if (
            this.point_is_intersecting_circle(this.mouse_position, point, 8)
          ) {
            this.selected_instance.points.splice(i, 1);
            break;
          }
          i += 1;
        }
      }
      let ann_ctx = this.build_ann_event_ctx()
      let ann_tool_event: InteractionEvent = genImageAnnotationEvent(null, ann_ctx)
      const coordinator = this.generate_interaction_coordinator(ann_tool_event) as PolygonInstanceCoordinator;

      let result = {} as CoordinatorProcessResult
      coordinator.polygon_delete_point(result, polygon_point_index)

    },

    get_node_hover_index: function () {
      if (!this.instance_hover_index) {
        return;
      }
      let instance = this.instance_list[this.instance_hover_index];
      if (!instance.node_hover_index) {
        return;
      }
      return instance.node_hover_index;
    },

    double_click_keypoint_special_action: function () {
      let node_hover_index = this.get_node_hover_index();
      if (node_hover_index == undefined) {
        return;
      }
      let update = {
        index: this.instance_hover_index,
        node_hover_index: node_hover_index,
        mode: "on_click_update_point_attribute",
      };
      this.instance_update(update);
    },

    double_click: function (event) {
      if(!this.is_active){
        return
      }
      this.mouse_position = this.mouse_transform(event, this.mouse_position);
      let ann_ctx = this.build_ann_event_ctx()
      let ann_tool_event: InteractionEvent = genImageAnnotationEvent(event, ann_ctx)
      if (!this.current_interaction) {
        this.current_interaction = new Interaction()
      }
      // this.current_interaction.add_event(ann_tool_event)
      const coordinator = this.generate_interaction_coordinator(ann_tool_event);
      if (coordinator) {
        let result: CoordinatorProcessResult = coordinator.perform_action_from_event(ann_tool_event);
        if (result.instance_moved === true) {
          this.$emit('set_has_changed', true);
        }
        if (result.instance_moved && this.show_snackbar_occlude_direction) {
          this.show_snackbar_occlude_direction = false;
        }
      }
      this.double_click_keypoint_special_action();
    },

    mouse_up: function (event) {
      if(!this.is_active){
        return
      }
      // start LIMITS, returns immediately
      this.canvas_mouse_tools.mouse_is_down = false

      let locked_frame_number = this.image_annotation_ctx.current_frame;
      if (this.view_only_mode == true) {
        return;
      }
      if (this.seeking == true) {
        return;
      }

      if (this.mouse_down_limits_result == false) {
        return;
      }

      if (this.draw_mode == false) {
        if (this.is_actively_resizing == true) {
          this.is_actively_resizing = false;
        }
      }

      if (event.which === 2) {
        this.mouse_wheel_button = false;
        return
      }
      this.$store.commit("mouse_state_up");

      if (this.draw_mode == false) {
        //console.debug('mouse upp edit', this.instance_hover_index, this.instance_hover_type);
        if (this.instance_list != undefined) {
          this.point_mouse_up_edit();
          this.line_mouse_up_edit();
          if (this.ellipse_hovered_instance) {
            this.stop_ellipse_resize();
          }
          // this.polygon_mouse_up_edit();
          this.cuboid_mouse_up_edit();
          this.curve_mouse_up_edit();
          this.keypoint_mouse_up_edit();
        }
      }

      // TODO clarify difference between mode, and action, ie drawing.
      if (this.draw_mode == true) {
        if (this.instance_type == "cuboid") {
          this.cuboid_mouse_up(locked_frame_number);
        }
        if (this.instance_type == "ellipse") {
          this.ellipse_mouse_up();
        }
        if (this.instance_template_selected) {
          this.instance_template_mouse_up(locked_frame_number);
        }
        if (["line", "curve"].includes(this.instance_type)) {

          this.is_actively_drawing = true;
          this.instance_insert_point(locked_frame_number);
        }

        if (
          this.instance_type == "line" &&
          this.current_polygon_point_list.length == 2
        ) {

          const command = new CreateInstanceCommand(
            this.current_instance,
            this,
            locked_frame_number
          );
          this.annotation_ui_context.command_manager.executeCommand(command);
          this.is_actively_drawing = false;
          this.current_polygon_point_list = [];
        }

        if (this.instance_type == "point") {
          this.instance_insert_point(locked_frame_number);
          const command = new CreateInstanceCommand(
            this.current_instance,
            this,
            locked_frame_number
          );
          this.annotation_ui_context.command_manager.executeCommand(command);
          this.current_polygon_point_list = [];
        }

        if (this.instance_type == "curve") {
          this.curve_mouse_up(locked_frame_number);
        }


      }
      // For new Refactored instance types
      this.mouse_up_v2_handler(event)
    },
    stop_ellipse_resize: function () {
      this.ellipse_hovered_instance = undefined;
      this.ellipse_hovered_instance_index = undefined;
      this.ellipse_hovered_corner = undefined;
      this.ellipse_hovered_corner_key = undefined;

      if (!this.original_edit_instance) {
        return;
      }
      if (this.original_edit_instance.type != "ellipse") {
        return;
      }
      if (this.original_edit_instance_index == undefined) {
        return;
      }
      const command = new UpdateInstanceCommand(
        this.instance_list[this.original_edit_instance_index],
        this.original_edit_instance_index,
        this.original_edit_instance,
        this
      );
      this.annotation_ui_context.command_manager.executeCommand(command);
    },
    ellipse_mouse_up: function () {
      if (!this.ellipse_current_drawing_face && this.draw_mode) {
        this.$store.commit("init_draw");
        this.is_actively_drawing = true;
        this.ellipse_current_drawing_face = true;
      } else {
        this.$store.commit("finish_draw");
        this.is_actively_drawing = false;
        this.ellipse_current_drawing_face = false;
      }
    },
    cuboid_mouse_up: function (frame_number = undefined) {
      if (!this.cuboid_current_drawing_face) {
        this.is_actively_drawing = true;
        this.cuboid_current_drawing_face = "first";
      } else if (this.cuboid_current_drawing_face === "first") {
        this.is_actively_drawing = true;
        this.cuboid_current_drawing_face = "second";
      } else {
        const create_box_command = new CreateInstanceCommand(
          this.current_instance,
          this,
          frame_number
        );
        this.annotation_ui_context.command_manager.executeCommand(create_box_command);
        this.cuboid_current_rear_face = undefined;
        this.cuboid_current_drawing_face = undefined;
        this.is_actively_drawing = false;
      }
    },
    lock_cuboid_rear_face: function () {
      var x_min = parseInt(this.mouse_down_position.x);
      var y_min = parseInt(this.mouse_down_position.y);
      var x_max = parseInt(this.mouse_position.x);
      var y_max = parseInt(this.mouse_position.y);

      // Handle inverting origin point
      if (x_max < x_min) {
        x_max = parseInt(this.mouse_down_position.x);
        x_min = parseInt(this.mouse_position.x);
      }

      if (y_max < y_min) {
        y_max = parseInt(this.mouse_down_position.y);
        y_min = parseInt(this.mouse_position.y);
      }

      if (x_min < 0) {
        x_min = 0;
      }
      if (y_min < 0) {
        y_min = 0;
      }

      // testing
      //x_max = 99999
      //y_max = 99999

      // 480 is from 0 to 479.
      if (this.original_media_width) {
        if (x_max >= this.original_media_width) {
          x_max = this.original_media_width - 1;
        }

        if (y_max >= this.original_media_height) {
          y_max = this.original_media_height - 1;
        }
      }

      var width = x_max - x_min;
      var height = y_max - y_min;

      this.cuboid_current_rear_face = {
        width: width,
        height: height,
        top_left: {
          x: x_min,
          y: y_min,
        },
        top_right: {
          x: x_min + width,
          y: y_min,
        },
        bot_left: {
          x: x_min,
          y: y_min + height,
        },
        bot_right: {
          x: x_max,
          y: y_max,
        },
      };
    },
    ellipse_mouse_down: function (frame_number = undefined) {
      if (this.ellipse_current_drawing_face && this.draw_mode) {
        const create_box_command = new CreateInstanceCommand(
          this.current_instance,
          this,
          frame_number
        );
        this.annotation_ui_context.command_manager.executeCommand(create_box_command);
      }
    },
    cuboid_mouse_down: function () {
      // WIP

      if (this.is_actively_drawing != true) {
        return;
      }
      if (this.cuboid_current_drawing_face === "first") {
        this.lock_cuboid_rear_face();
      }
      if (
        this.current_instance.x_max - this.current_instance.x_min <= 5 &&
        this.current_instance.y_max - this.current_instance.y_min <= 5
      ) {
        // TODO raise error

        console.debug("Instance too small");
        return;
      }
    },

    mouse_down_limits: function (event) {
      /* not a fan of having a value
       * and a flag... but also have to deal with both
       * mouse up and down firing, but not wanting to rerun this stuff twice
       * If there was a way to control the relation of mouse up/down
       * firing but that feels very unclear
       *
       * Also not sure if we don't return will it wait for the function
       * to complete as expected...
       *
       * So the default here is that it's true,
       * and we expect that if it's true mouse_up will also allow it to continue
       * It gets reset each time.
       *
       * In comparison to running this at save,
       * it means for current video boxes it will run twice
       * But the benefit is that then it prevents it from getting into broken state
       * in first place
       */

      // default
      this.mouse_down_limits_result = true;

      // 1: left, 2: middle, 3: right, could be null
      // https://stackoverflow.com/questions/1206203/how-to-distinguish-between-left-and-right-mouse-click-with-jquery

      if (event.which == 3) {
        this.mouse_down_limits_result = false;
        return false;
      }

      if (this.annotation_ui_context.show_context_menu == true) {
        this.mouse_down_limits_result = false;
        return false;
      }

      // this feels a bit funny
      if (this.draw_mode == false) {
        return true;
      }

      if (this.space_bar == true || this.ctrl_key) {
        // note pattern of needing both... for now this
        // is so the mouse up respects this too
        this.mouse_down_limits_result = false;
        return false;
      }

      // TODO clarify if we could just do this first check
      if (!this.annotation_ui_context.current_label_file || !this.annotation_ui_context.current_label_file.id) {
        this.snackbar_warning = true;
        this.snackbar_warning_text = "Please select a label first";
        this.mouse_down_limits_result = false;
        return false;
      }

      if (this.image_annotation_ctx.video_mode == true) {
        if (this.validate_sequences() == false) {
          this.mouse_down_limits_result = false;
          return false;
        }
      }

      return true;
    },

    refresh_instance_list_sidebar: function (
      instance_index = this.instance_list.length - 1
    ) {

      this.event_create_instance = {...this.current_instance};
      this.image_annotation_ctx.request_change_current_instance = instance_index;
      this.image_annotation_ctx.trigger_refresh_current_instance = Date.now();
      this.update_canvas()
    },

    unset_instance_list_sidebar: function () {
      this.event_create_instance = null;
      this.image_annotation_ctx.request_change_current_instance = null;
      this.image_annotation_ctx.trigger_refresh_current_instance = Date.now();
    },
    polygon_mid_point_mouse_down: function () {
      if (!this.selected_instance) {
        return;
      }
      if (!this.is_actively_resizing) {
        return;
      }

      const instance = {...this.selected_instance};

      if (!instance) {
        return;
      }
      if (instance.type !== "polygon") {
        return;
      }
      if (instance.midpoint_hover == undefined) {
        return;
      }

      let points = instance.points.map((p) => ({...p}));

      let rest_of_points = [];
      if (this.hovered_figure_id) {
        points = instance.points.filter(
          (p) => p.figure_id === this.hovered_figure_id
        );
        rest_of_points = instance.points.filter(
          (p) => p.figure_id !== this.hovered_figure_id
        );
      }
      let midpoints_polygon = instance.midpoints_polygon;
      if (this.hovered_figure_id) {
        midpoints_polygon = instance.midpoints_polygon[this.hovered_figure_id];
      }

      let new_point_to_add = midpoints_polygon[instance.midpoint_hover];
      if (new_point_to_add == undefined) {
        return;
      }
      points.splice(instance.midpoint_hover + 1, 0, {
        ...new_point_to_add,
        figure_id: this.hovered_figure_id,
      });
      this.polygon_point_hover_index = instance.midpoint_hover + 1;
      this.polygon_point_click_index = instance.midpoint_hover + 1;
      this.polygon_click_index = this.selected_instance_index;

      let hovered_point = points[this.polygon_point_hover_index];
      if (!hovered_point) {
        return;
      }
      hovered_point.selected = true;
      this.lock_point_hover_change = true;
      instance.midpoint_hover = undefined;
      instance.selected = true;
      if (this.hovered_figure_id) {
        instance.points = points.concat(rest_of_points);
      } else {
        instance.points = points;
      }
      this.instance_list.splice(this.selected_instance_index, 1, instance);
    },
    get_polygon_figures: function (polygon_instance) {
      let figure_list = [];
      if (!polygon_instance || polygon_instance.type !== "polygon") {
        return [];
      }
      for (const p of polygon_instance.points) {
        if (!p.figure_id) {
          continue;
        }
        if (!figure_list.includes(p.figure_id)) {
          figure_list.push(p.figure_id);
        }
      }
      return figure_list;
    },
    find_auto_border_point: function (polygon, points, instance_index) {
      let found_point = false;
      let point_index = 0;
      for (const point of points) {
        if (point.hovered_while_drawing) {
          if (!this.auto_border_context.auto_border_polygon_p1) {
            this.auto_border_context.auto_border_polygon_p1 = point;
            this.auto_border_context.auto_border_polygon_p1_index = point_index;
            this.auto_border_context.auto_border_polygon_p1_figure = point.figure_id;
            this.auto_border_context.auto_border_polygon_p1_instance_index = instance_index;
            point.point_set_as_auto_border = true;
            found_point = true;
            this.show_snackbar_auto_border = true;
            break;
          } else if (
            !this.auto_border_context.auto_border_polygon_p2 &&
            point != this.auto_border_context.auto_border_polygon_p1 &&
            instance_index === this.auto_border_context.auto_border_polygon_p1_instance_index
          ) {
            this.auto_border_context.auto_border_polygon_p2 = point;
            this.auto_border_context.auto_border_polygon_p2_index = point_index;
            this.auto_border_context.auto_border_polygon_p2_figure = point.figure_id;
            point.point_set_as_auto_border = true;
            this.auto_border_context.auto_border_polygon_p2_instance_index = instance_index;
            this.show_snackbar_auto_border = false;
            found_point = true;
            break;
          }
        }
        point_index += 1;
      }
      return found_point;
    },
    polygon_auto_border_mouse_down: function () {
      if (!this.draw_mode) {
        return;
      }
      if (!this.is_actively_drawing) {
        return;
      }
      if (!this.auto_border_context.auto_border_polygon_p1 && this.auto_border_context.auto_border_polygon_p2) {
        return;
      }
      let found_point = false;
      for (let instance_index = 0; instance_index < this.instance_list.length; instance_index++) {
        const polygon = this.instance_list[instance_index];
        if (polygon.type !== "polygon" || polygon.soft_delete) {
          continue;
        }

        let points = polygon.points;
        let figure_list = this.get_polygon_figures(polygon);

        if (figure_list.length === 0) {
          let autoborder_point_exists = this.find_auto_border_point(
            polygon,
            points,
            instance_index
          );
          if (autoborder_point_exists) {
            found_point = true;
          }
        } else {
          for (const figure_id of figure_list) {
            points = polygon.points.filter((p) => p.figure_id === figure_id);
            let autoborder_point_exists = this.find_auto_border_point(
              polygon,
              points,
              instance_index
            );
            if (autoborder_point_exists) {
              found_point = true;
            }
          }
        }
        if (found_point) {
          break;
        }
      }
    },
    instance_template_mouse_down: function () {
    },
    add_label_file_to_instance(instance) {
      instance.label_file = this.annotation_ui_context.current_label_file;
      instance.label_file_id = this.annotation_ui_context.current_label_file.id;
      return instance;
    },
    add_instance_template_to_instance_list(frame_number) {
      this.actively_drawing_instance_template.instance_list.forEach((instance) => {
        let new_instance = duplicate_instance(instance, this);
        if (this.image_annotation_ctx.video_mode == true) {
          new_instance.number =
            this.current_sequence_from_sequence_component.number;
          new_instance.sequence_id =
            this.current_sequence_from_sequence_component.id;
        }
        this.add_label_file_to_instance(new_instance);
        if (new_instance.type === "keypoints") {
          new_instance.set_new_xy_to_scaled_values();
        } else if (new_instance.type === "box") {
          new_instance.x_min = parseInt(this.mouse_position.x, 10);
          new_instance.y_min = parseInt(this.mouse_position.y, 10);
          new_instance.x_max = parseInt(
            this.mouse_position.x + new_instance.width,
            10
          );
          new_instance.y_max = parseInt(
            this.mouse_position.y + new_instance.height,
            10
          );
        } else if (new_instance.type === "polygon") {
          let x_diff = this.mouse_position.x - new_instance.points[0].x;
          let y_diff = this.mouse_position.y - new_instance.points[0].y;
          new_instance.points.forEach((point) => {
            point.x += x_diff;
            point.y += y_diff;
          });
        }
        this.add_instance_to_file(
          new_instance,
          frame_number
        );
        //const command = new CreateInstanceCommand(new_instance, this);
        //this.annotation_ui_context.command_manager.executeCommand(command);
      });
    },
    instance_template_has_keypoints_type: function (instance_template) {
      if (!instance_template || !instance_template.instance_list) {
        return
      }
      for (let instance of instance_template.instance_list) {
        if (instance.type === 'keypoints') {
          return true
        }
      }
      return false;
    },
    add_node_guided_mode: function (frame_number) {
      if (!this.actively_drawing_keypoints_instance) {
        return
      }
      if (this.guided_nodes_ordinal === 1) {
        this.actively_drawing_keypoints_instance.reset_guided_nodes();
      }
      let occlude = false;
      if (this.n_key) {
        occlude = true;
      }
      this.actively_drawing_keypoints_instance.add_guided_mode_node(this.guided_nodes_ordinal, occlude);
      this.guided_nodes_ordinal += 1;
      this.show_snackbar_guided_keypoints_drawing(this.guided_nodes_ordinal)
      if (this.guided_nodes_ordinal - 1 === this.actively_drawing_keypoints_instance.nodes.length) {
        this.actively_drawing_keypoints_instance.finish_guided_nodes_drawing();
        this.actively_drawing_keypoints_instance.select()
        this.actively_drawing_keypoints_instance.guided_mode_active = false
        this.add_instance_template_to_instance_list(frame_number);
        this.instance_template_draw_started = undefined;
        this.is_actively_drawing = undefined;
        this.instance_template_start_point = undefined;
        this.edit_mode_toggle(false);
      }
    },
    start_keypoints_drawing: function (frame_number) {
      this.actively_drawing_instance_template = duplicate_instance_template(this.current_instance_template, this);
      this.instance_template_start_point = {
        x: this.mouse_position.x,
        y: this.mouse_position.y,
      };
      if (this.current_instance_template.mode === '1_click') {
        this.actively_drawing_instance_template.instance_list[0].save_original_nodes();
        this.actively_drawing_instance_template.instance_list[0].set_nodes_coords_based_on_size(30, 30, this.instance_template_start_point);
        this.actively_drawing_instance_template.instance_list[0].width = 1;
        this.actively_drawing_instance_template.instance_list[0].height = 1;
      } else if (this.current_instance_template.mode === 'guided') {
        this.actively_drawing_keypoints_instance.guided_mode_active = true;
        this.add_node_guided_mode(frame_number);
      }
      this.instance_template_draw_started = true;
      this.is_actively_drawing = true;
    },
    instance_template_mouse_up: async function (frame_number = undefined) {
      if (this.instance_template_draw_started) {
        if (this.actively_drawing_instance_template.mode === 'guided') {
          this.add_node_guided_mode(frame_number);
        } else {
          this.add_instance_template_to_instance_list(frame_number);
          if (this.actively_drawing_keypoints_instance) {
            let instance = this.actively_drawing_keypoints_instance;
            let index = this.instance_list.length - 1;
            for (let i = 0; i < this.instance_list.length; i++) {
              if (this.instance_list[i].creation_ref_id === instance.creation_ref_id) {
                index = i;
                break;
              }
            }
            this.edit_mode_toggle(false)
            instance.select()
            instance.status = "updated";
            Vue.set(
              this.instance_list,
              this.instance_hover_index,
              instance
            );
          }
          this.instance_template_draw_started = undefined;
          this.is_actively_drawing = undefined;
          this.instance_template_start_point = undefined;
        }

      } else {
        // TODO: Might need to change this logic when we support more than one instance per instance template.
        if (this.instance_template_has_keypoints_type(this.current_instance_template)) {
          this.start_keypoints_drawing(frame_number);
        } else {
          this.add_instance_template_to_instance_list(frame_number);
          this.instance_template_draw_started = undefined;
          this.is_actively_drawing = undefined;
          this.instance_template_start_point = undefined;
        }
      }
    },
    create_canvas_mouse_ctx: function(){
      let canvas_mouse_ctx: CanvasMouseCtx = {
        mouse_position: this.mouse_position,
        canvas_element_ctx: this.canvas_element_ctx,
        instance_context: this.instance_context,
        trigger_instance_changed: this.trigger_instance_changed,
        instance_selected: () => this.instance_selected,
        instance_deselected: () => this.instance_deselected,
        new_global_instance: () => {
          return new GlobalInstance()
        },
        mouse_down_delta_event: this.mouse_down_delta_event,
        mouse_down_position: this.mouse_down_position,
        label_settings: this.label_settings,
        canvas_transform: this.canvas_transform
      }
      return canvas_mouse_ctx
    },
    create_coordinator_router: function (event: ImageInteractionEvent): ImageAnnotationCoordinatorRouter {
      let canvas_mouse_ctx: CanvasMouseCtx = this.create_canvas_mouse_ctx()
      const interaction_generator = new ImageAnnotationCoordinatorRouter(
        event,
        this.instance_hover_index,
        this.instance_list,
        this.draw_mode,
        this.instance_type,
        canvas_mouse_ctx,
        this.annotation_ui_context.command_manager
      );
      return interaction_generator

    },
    generate_interaction_coordinator: function (event: ImageInteractionEvent): ImageAnnotationCoordinator {

      let coord_router: ImageAnnotationCoordinatorRouter = this.create_coordinator_router(event)
      return coord_router.generate_coordinator();

    },
    key_points_mouse_down: function () {
      if (this.instance_hover_index == undefined) {
        return;
      }
      let instance = this.instance_list[this.instance_hover_index];
      if (!instance.is_node_hovered && !instance.is_bounding_box_hovered) {
        return;
      }
      instance.start_movement();
    },
    set_mouse_wheel: function () {
      this.mouse_wheel_button = true;
    },
    build_ann_event_ctx: function (): ImageAnnotationEventCtx {
      let ann_ctx: ImageAnnotationEventCtx = {
        polygon_point_hover_index: this.polygon_point_hover_index,
        label_file: this.annotation_ui_context.current_label_file as LabelFile,
        instance_type: this.instance_type,
        instance_list: this.instance_list as Instance[],
        draw_mode: this.draw_mode,
        shift_key: this.shift_key,
        polygon_point_click_index: this.polygon_point_click_index,
        instance_hover_index: this.instance_hover_index,
        auto_border_context: this.auto_border_context,
        is_actively_drawing: this.is_actively_drawing,
        hovered_instance: this.hovered_instance,
        current_drawing_instance: this.current_instance,
        label_file_colour_map: this.label_file_colour_map as LabelColourMap,
        mouse_position: this.mouse_position as MousePosition,
        mouse_down_position: this.mouse_down_position as MousePosition,
        mouse_down_delta_event: this.mouse_down_delta_event as MousePosition,
        canvas_mouse_tools: this.canvas_mouse_tools,
        canvas_transform: this.canvas_transform,
        canvas_element: this.canvas_element,
        view_issue_mode: this.view_issue_mode,
        frame_number: this.image_annotation_ctx.current_frame,
        ann_core_ctx: this,
        instance_select_for_issue: this.instance_select_for_issue,
        view_only_mode: this.view_only_mode,
        image_label_settings: this.label_settings,
        original_edit_instance: this.original_edit_instance,
        locked_editing_instance: this.locked_editing_instance,
        lock_point_hover_change: this.lock_point_hover_change,
        polygon_merge_tool: this.polygon_merge_tool,
        video_mode: this.image_annotation_ctx.video_mode,
        current_sequence_from_sequence_component: this.current_sequence_from_sequence_component
      }
      return ann_ctx
    },
    mouse_move_v2_handler: function (event) {
      let ann_ctx = this.build_ann_event_ctx()
      let ann_tool_event: InteractionEvent = genImageAnnotationEvent(event, ann_ctx)
      const coordinator = this.generate_interaction_coordinator(ann_tool_event);
      if (coordinator) {
        let result: CoordinatorProcessResult = coordinator.perform_action_from_event(ann_tool_event);
        if (result.instance_moved) {
          this.$emit('set_has_changed', true);
        }
        this.polygon_point_hover_index = result.polygon_point_hover_index
        if (result.auto_border_context) {
          this.auto_border_context = result.auto_border_context
        }

        this.original_edit_instance = result.original_edit_instance
        this.locked_editing_instance = result.locked_editing_instance
      }
    },
    new_instance_refresh: function (new_instance_index: number) {
      this.refresh_instance_list_sidebar()
      this.reset_current_instances()
      let instance = this.instance_list[new_instance_index]
      instance.on('hover_in', this.instance_hovered)
      instance.on('hover_out', this.instance_unhovered)
      this.update_canvas()
      this.$emit('set_has_changed', true);
    },
    mouse_down_v2_handler: function (event) {

      let ann_ctx = this.build_ann_event_ctx()
      let ann_tool_event: InteractionEvent = genImageAnnotationEvent(event, ann_ctx)
      if (!this.current_interaction) {
        this.current_interaction = new Interaction()
      }

      // this.current_interaction.add_event(ann_tool_event)
      const coordinator = this.generate_interaction_coordinator(ann_tool_event);
      if (coordinator) {
        let result = coordinator.perform_action_from_event(ann_tool_event);
        if (result) {
          this.is_actively_drawing = result.is_actively_drawing
        }
        if (result.new_instance_index != undefined) {
          post_init_instance(this.instance_list[result.new_instance_index],
            this.label_file_map,
            this.canvas_element,
            this.label_settings,
            this.canvas_transform,
            this.instance_hovered,
            this.instance_unhovered,
            this.canvas_mouse_tools
          )
          this.new_instance_refresh(result.new_instance_index)
        }
        this.original_edit_instance = result.original_edit_instance
        if (result.auto_border_context) {
          this.auto_border_context = result.auto_border_context
        }

        this.locked_editing_instance = result.locked_editing_instance
        this.lock_point_hover_change = result.lock_point_hover_change
        this.polygon_point_click_index = result.polygon_point_click_index
      }
    },
    reset_current_instances: function () {
      this.current_drawing_box_instance = new BoxInstance()
      this.current_drawing_polygon_instance = new PolygonInstance()
    },
    mouse_up_v2_handler: function (event) {
      let ann_ctx = this.build_ann_event_ctx()
      let ann_tool_event: InteractionEvent = genImageAnnotationEvent(event, ann_ctx)
      if (!this.current_interaction) {
        this.current_interaction = new Interaction()
      }
      // this.current_interaction.add_event(ann_tool_event)
      const coordinator = this.generate_interaction_coordinator(ann_tool_event);
      if (coordinator) {
        let result: CoordinatorProcessResult = coordinator.perform_action_from_event(ann_tool_event);
        if (result.instance_moved === true) {
          this.$emit('set_has_changed', true);
        }
        if (result.new_instance_index != undefined) {
          post_init_instance(this.instance_list[result.new_instance_index],
            this.label_file_map,
            this.canvas_element,
            this.label_settings,
            this.canvas_transform,
            this.instance_hovered,
            this.instance_unhovered,
            this.canvas_mouse_tools
          )
          this.new_instance_refresh(result.new_instance_index)
          this.is_actively_drawing = result.is_actively_drawing
        }
        if (result.instance_moved && this.show_snackbar_occlude_direction) {
          this.show_snackbar_occlude_direction = false;
        }
        this.original_edit_instance = result.original_edit_instance
        this.locked_editing_instance = result.locked_editing_instance
        this.lock_point_hover_change = result.lock_point_hover_change
      }
    },
    mouse_down: function (event) {
      if(!this.is_active){
        return
      }
      let locked_frame_number = this.image_annotation_ctx.current_frame;
      this.mouse_position = this.mouse_transform(event, this.mouse_position);

      if (this.view_only_mode == true) {
        return;
      }

      if (this.mouse_down_limits(event) == false) {
        return;
      }
      if (event.which === 2) {
        this.set_mouse_wheel(event);
        return
      }

      this.ghost_may_promote_instance_to_actual();

      // For new refactored instance types (eventually all should be here)
      this.mouse_down_v2_handler(event)

      if (this.seeking == false) {
        this.canvas_mouse_tools.mouse_is_down = true
        this.$store.commit("mouse_state_down");

        this.select_something();
        this.select_issue();

        if (this.instance_type == "cuboid") {
          this.cuboid_mouse_down();
        }

        if (this.instance_type == "ellipse") {
          this.ellipse_mouse_down(locked_frame_number);
        }
        if (this.instance_type == "keypoints") {
          this.key_points_mouse_down();
        }
        if (this.instance_template_selected) {
          this.instance_template_mouse_down();
        }
      }

      if (this.draw_mode == false) {
        if (this.is_actively_resizing == false) {
          this.is_actively_resizing = true;
        }
      }

      // this.polygon_auto_border_mouse_down()
      this.mouse_down_position = this.mouse_transform(event, this.mouse_down_position)
      this.mouse_down_position.request_time = Date.now()
      // this.lock_polygon_corner();
      // this.polygon_mid_point_mouse_down()


    },
    lock_polygon_corner: function () {
      this.polygon_point_click_index = this.polygon_point_hover_index
      this.polygon_click_index = this.instance_hover_index

    },
    get_instances_core: function (response) {

      this.show_annotations = true
      this.global_instance = null // reset

      if (response.data['file_serialized']) {
        let new_instance_list = this.create_instance_list_with_class_types(
          response.data['file_serialized']['instance_list']
        );
        this.instance_list = new_instance_list
      }

      this.image_annotation_ctx.loading = false

      this.trigger_refresh_with_delay();

    },

    trigger_refresh_with_delay: function () {
      setTimeout(() => (this.refresh = Date.now()), 80);
    },
    get_instance_list_for_image: async function () {
      let url = undefined;
      let file = this.working_file;

      if (this.task_instances) {
        this.get_instances_core({data: this.task_instances})
        return
      }

      if (this.$store.getters.is_on_public_project) {
        url = `/api/project/${this.project_string_id}/file/${String(this.working_file.id)}/annotation/list`;

        const response = await axios.post(url, {
          directory_id:
          this.$store.state.project.current_directory.directory_id,
          job_id: this.job_id,
          attached_to_job: file.attached_to_job,
        });
        this.get_instances_core(response);
        this.image_annotation_ctx.annotations_loading = false;
      }
      else if (this.$store.state.builder_or_trainer.mode == "builder") {
        if (this.task && this.task.id) {
          if (this.task.id === '-1' || this.task.id === -1) {
            return
          }
          // If a task is present, prefer this route to handle permissions
          url = "/api/v1/task/" + this.task.id + "/annotation/list";
          file = this.working_file;
        } else {
          url = `/api/project/${this.project_string_id}/file/${String(
            this.working_file.id
          )}/annotation/list`;
        }
        try {
          const response = await axios.post(url, {
            directory_id:
            this.$store.state.project.current_directory.directory_id,
            job_id: this.job_id,
            task_child_file_id: this.working_file.id,
            attached_to_job: file.attached_to_job,
          });
          this.get_instances_core(response);
          this.image_annotation_ctx.annotations_loading = false;
        } catch (error) {
          console.debug(error);
          this.image_annotation_ctx.loading = false;
        }
        return;
      } else if (this.$store.state.builder_or_trainer.mode == "trainer") {
        if (this.task.id === '-1' || this.task.id === -1) {
          return
        }
        url = "/api/v1/task/" + this.task.id + "/annotation/list";
        try {
          const response = await axios.get(url, {});
          this.get_instances_core(response);
          this.image_annotation_ctx.annotations_loading = false;
        } catch (error) {
          console.debug(error);
          this.image_annotation_ctx.loading = false;
        }
      }
    },
    add_override_colors_for_model_runs: function () {
      if (!this.model_run_list) {
        return;
      }
      for (const instance of this.instance_list) {
        if (instance.model_run_id) {
          let model_run = this.model_run_list.filter(
            (m) => m.id === instance.model_run_id
          );
          if (model_run.length > 0) {
            model_run = model_run[0];
            instance.override_color = model_run.color;
          }
        }
      }
    },
    set_global_instance_on_parent_instance_list: function () {
      this.get_and_set_global_instance(this.image_annotation_ctx.video_parent_file_instance_list)
    },
    get_instances: async function (play_after_success = false) {
      if (this.image_annotation_ctx.annotations_loading) {
        return;
      }
      this.image_annotation_ctx.annotations_loading = true;
      this.show_annotations = false;
      // Fetch Instance list for either video or image.
      if (this.image_annotation_ctx.video_mode == true) {
        /*  Caution, if this is firing twice
         *    Look at vidue.vue   get_video_single_image()
         *    It's spawning a 'video_file_update' event this is waiting for.
         */
        /*
         * Key observation here is that, if the frame exists in the dict,
         * then we don't need to get a new buffer list,
         * otherwise we do. And we can trigger  this.get_video_instance_buffer()
         * seperetly for special event handling
         *
         */

        await this.update_instance_list_from_buffer_or_get_new_buffer(
          play_after_success
        );

        this.set_global_instance_on_parent_instance_list();
      } else {
        // Context of Images Only
        await this.get_instance_list_for_image();
        this.get_and_set_global_instance(this.instance_list)
      }
      this.add_override_colors_for_model_runs();

      this.image_annotation_ctx.annotations_loading = false;
      this.update_canvas();

    },

    async update_instance_list_from_buffer_or_get_new_buffer(
      play_after_success
    ) {
      if (this.image_annotation_ctx.current_frame in this.instance_buffer_dict) {
        // Initialize instances to class objects before assigning pointer.
        this.initialize_instance_buffer_dict_frame(this.image_annotation_ctx.current_frame);
        // Instance list is always a pointer to the actual instance_buffer dict.
        // IMPORTANT  This is a POINTER not a new object. This is a critical assumption.
        // See https://docs.google.com/document/d/1KkpccWaCoiVWkiit8W_F5xlH0Ap_9j4hWduZteU4nxE/edit

        this.instance_list = this.instance_buffer_dict[this.image_annotation_ctx.current_frame];
        this.add_override_colors_for_model_runs();
        this.show_annotations = true;
        this.image_annotation_ctx.loading = false;
        this.image_annotation_ctx.annotations_loading = false;
        if (
          this.image_annotation_ctx.instance_buffer_metadata[this.image_annotation_ctx.current_frame] &&
          this.image_annotation_ctx.instance_buffer_metadata[this.image_annotation_ctx.current_frame].pending_save
        ) {
          this.$emit('set_has_changed', true);
        }
      } else {
        // Save Any pending frames before refreshing buffer (This line might be removed when we stop
        // resetting the frame buffer on each fetch)
        await this.$emit('save');
        await this.get_video_instance_buffer(play_after_success);
      }
    },
    async get_instance_buffer_parallel(url_base, frame_start, frames_end) {
      const step_size = 5; // We will fetch 5 frames per call
      const limit = pLimit(15); // 10 Max concurrent request.
      const total_frames = frames_end - frame_start;
      try {
        // Build frames start/end
        const frames_tuples = [];
        for (let i = frame_start; i < frames_end; i += step_size + 1) {
          frames_tuples.push([i, i + step_size]);
        }
        const promises = frames_tuples.map((frame_tuple) => {
          return limit(() => {
            let new_url = `${url_base}/instance/buffer/start/${frame_tuple[0]}/end/${frame_tuple[1]}/list`;
            return axios.post(new_url, {
              directory_id:
              this.$store.state.project.current_directory.directory_id,
            });
          });
        });

        let all_responses = await Promise.all(promises);
        let new_instance_buffer_dict = {};
        for (const response of all_responses) {
          new_instance_buffer_dict = {
            ...new_instance_buffer_dict,
            ...response.data.instance_buffer_dict,
          };
        }
        return new_instance_buffer_dict;
      } catch (e) {
        console.error(e)
        this.error = this.$route_api_errors(e)
        return undefined;
      }


    },
    async get_video_instance_buffer(play_after_success) {
      /*
       * Directly triggers getting buffer
       * Caution, this should rarely be called directly
       * normally it's called in conjunction with something
       * that checks if we already have a local copy like
       *
       * Using project id from store for case of single file
       * permissions ie file/:file_id
       *
       */
      this.show_annotations = false;
      this.image_annotation_ctx.loading = true;

      this.image_annotation_ctx.annotations_loading = true;

      this.instance_buffer_error = {};

      this.instance_frame_start = this.image_annotation_ctx.current_frame;

      let url = this.url_instance_buffer;

      try {
        // Get the buffer from the Server. Note that at this point it is not initialized.
        // We'll initialize class instances as per frame and not all at once for performance reasons.
        let new_instance_buffer_dict = await this.get_instance_buffer_parallel(
          url,
          this.image_annotation_ctx.current_frame,
          this.image_annotation_ctx.current_frame + this.label_settings.instance_buffer_size
        );
        if (!new_instance_buffer_dict) {
          return
        }
        this.instance_buffer_dict = new_instance_buffer_dict;
        // Now set the current list from buffer
        if (this.instance_buffer_dict) {
          // We want to do the equals because that creates the reference on the instance list to buffer dict
          this.initialize_instance_buffer_dict_frame(this.image_annotation_ctx.current_frame);
          this.instance_list = this.instance_buffer_dict[this.image_annotation_ctx.current_frame];
        } else {
          // handle if buffer list doesn't load all the way?
          this.instance_list = [];
        }

        this.show_annotations = true;
        this.image_annotation_ctx.loading = false;
        this.image_annotation_ctx.annotations_loading = false;
        this.trigger_refresh_with_delay();
        this.update_canvas();

        if (play_after_success == true) {
          this.video_play = Date.now();
        }
      } catch (error) {
        this.instance_buffer_error = this.$route_api_errors(error);
        console.debug(error);
        this.image_annotation_ctx.loading = false;
      }
    },

    sleep: function (ms) {
      return new Promise((resolve) => setTimeout(resolve, ms));
      // bottom of https://www.sitepoint.com/delay-sleep-pause-wait/
      // use aysnc in front of function
    },

    next_issue_task: async function (task) {
      if (this.image_annotation_ctx.loading == true || this.image_annotation_ctx.annotations_loading == true) {
        return;
      }

      if (this.has_changed) {
        this.$emit('save');
        await this.sleep(1000);
      }

      this.reset_for_file_change_context();

      this.image_annotation_ctx.loading = true;

      try {
        const response = await axios.post(
          `/api/v1/task/${task.id}/next-task-with-issues`,
          {
            task_id: task.id,
          }
        );
        if (response.data) {
          if (response.data.task_id && response.data.task_id !== task.id) {
            this.$router.push(`/task/${response.data.task_id}`);
          }
        }
      } catch (error) {
        console.debug(error);
      } finally {
        this.image_annotation_ctx.loading = false;
      }
    },
    reset_for_file_change_context: function () {
      this.current_sequence_annotation_core_prop = {
        id: null,
        number: null
      }
      this.image_annotation_ctx.video_mode = false   // if we don't have this can be issues switching to say an image
      this.degrees = 0
      this.instance_buffer_dict = {}
      this.image_annotation_ctx.instance_buffer_metadata = {}
      this.instance_list = []
      if (this.image_annotation_ctx.video_mode) {
        this.$refs.video_controllers.reset_cache();
      }
      if (this.$refs.qa_carrousel) {
        this.$refs.qa_carrousel.annotation_show_previous_instance = 0
        this.$refs.qa_carrousel.annotation_show_progress = 0
        this.annotation_show_current_instance = 0
      }

    },
    annotation_show_activate(show_type) {

      console.log("Showing annotation show")
      this.annotation_show_on = !this.annotation_show_on
      this.annotation_show_type = show_type
      if (this.$refs.qa_carrousel && this.annotation_show_on) {
        let instance = this.instance_list[this.$refs.qa_carrousel.annotation_show_current_instance]
        this.snap_to_instance(instance)
        this.$refs.qa_carrousel.play()
      }

      if (!this.annotation_show_on && this.$refs.instance_detail_list) {
        this.$refs.qa_carrousel.annotation_show_progress = 0;
        this.$refs.qa_carrousel.annotation_show_current_instance = 0;
        this.$refs.qa_carrousel.annotation_show_previous_instance = 0;
        this.$refs.instance_detail_list.show_all();
      }
    },
    async annotation_show_change_item(direction = "next") {
      let do_change_item

      const file = this.working_file;
      if (file.type == "video") {
        if (this.$refs.video_controllers.at_end_of_video == true) {
          do_change_item = true;
        } else {
          if (direction === 'next') {
            await this.$refs.video_controllers.move_frame(1);
            await this.$nextTick()
            this.$refs.qa_carrousel.annotation_show_current_instance = 0;
            this.$refs.qa_carrousel.annotation_show_previous_instance = this.instance_list.length;
            this.$refs.qa_carrousel.annotation_show_progress = 0
            this.focus_instance({index: this.$refs.qa_carrousel.annotation_show_current_instance})
          } else if (direction === 'previous') {
            await this.$refs.video_controllers.move_frame(-1);
            await this.$nextTick()
            this.$refs.qa_carrousel.annotation_show_current_instance = this.instance_list.length;
            this.$refs.qa_carrousel.annotation_show_previous_instance = 0
            this.$refs.qa_carrousel.annotation_show_progress = 100
            this.focus_instance({index: this.$refs.qa_carrousel.annotation_show_current_instance})
          }

        }
      }
      if (file.type == "image") {
        do_change_item = true;
      }

      if (do_change_item == true) {
        if (this.annotation_show_type === "task") {
          return this.$emit('trigger_task_change', direction, this.task, false);
        }
        this.change_file(direction);
      }
    },
    set_annotation_show_duration(duration) {
      this.annotation_show_duration_per_instance = (duration + 1) * 1000;
    },
    change_file(direction, file) {
      if (direction == "next" || direction == "previous") {
        this.$emit("request_file_change", direction, file);
      }
    },
    on_change_current_task: async function () {
      if (!this.task) {
        return;
      }
      if (!this.task.id) {
        return;
      }

      if (
        this.image_annotation_ctx.loading == true ||
        this.image_annotation_ctx.annotations_loading == true ||
        this.full_file_loading
      ) {
        return;
      }
      this.show_default_navigation = false;

      this.full_file_loading = true;
      if (this.has_changed) {
        await this.$emit('save');
      }
      this.reset_for_file_change_context();
      await this.refresh_attributes_from_current_file(this.working_file);

      await this.current_file_updates(this.working_file);
      await this.prepare_canvas_for_new_file(this.working_file);

      this.full_file_loading = false;
      this.annotation_show_progress = 0;
      this.ghost_clear_for_file_change_context();
      this.on_canvas_scale_global_changed(
        this.label_settings.canvas_scale_global_setting
      );
      this.canvas_mouse_tools.reset_transform_with_global_scale();
      this.$emit('set_ui_schema');

      if (this.task_image) {
        this.html_image = this.task_image
      }
    },
    on_change_current_file: async function () {
      if (!this.working_file) {
        return;
      }
      if (!this.working_file.id) {
        return;
      }

      if (
        this.image_annotation_ctx.loading == true ||
        this.image_annotation_ctx.annotations_loading == true ||
        this.full_file_loading
      ) {
        // Don't change file while loading
        // The button based method catches this but keyboard short cut doesn't
        return;
      }
      this.full_file_loading = true;

      if (this.has_changed) {
        await this.$emit('save');
      }
      this.reset_for_file_change_context();

      await this.refresh_attributes_from_current_file(this.working_file);

      this.current_file_updates(this.working_file);
      await this.prepare_canvas_for_new_file(this.working_file);

      this.full_file_loading = false;
      this.ghost_clear_for_file_change_context();
      this.on_canvas_scale_global_changed(
        this.label_settings.canvas_scale_global_setting
      );
      this.canvas_mouse_tools.reset_transform_with_global_scale();
      this.$emit('set_ui_schema');
    },

    refresh_attributes_from_current_file: async function (file) {
      if (!file) {
        throw new Error("Provide file.");
      }
      // Change mode  ?
      if (file.type == "image") {
        // TODO a better way... this is so the watch on current video changes
        this.current_video_file_id = null;
        this.image_annotation_ctx.video_mode = false;
        this.current_video = {
          frame_count: 0,
          current_frame: 0,
        };
        this.working_file_cant_be_accessed = null
        this.working_file_cant_be_accessed_error = null
        // maybe this.current_file should store width/height? ...
        try {
          const new_image = await this.addImageProcess(file.image.url_signed);
          if (!file.image.width || !file.image.height) {
            file.image.width = new_image.width
            file.image.height = new_image.height
          }
          this.html_image = new_image;
          this.refresh = Date.now();
          this.original_media_width = file.image.width;
          this.original_media_height = file.image.height;
          this.canvas_mouse_tools.set_canvas_width_height(this.original_media_width, this.original_media_height)
          this.update_canvas();


        } catch (error) {
          this.working_file_cant_be_accessed = true
          this.working_file_cant_be_accessed_error = this.$route_api_errors(error)
          this.working_file_cant_be_accessed_error['Blob Storage error'] = 'You may not have permissions. If you are an Admin, check storage config and signed URL settings.'
        }
      }
      if (file.type === "video") {
        this.image_annotation_ctx.video_mode = true; // order matters here, downstream things need this to pull right stuff
        // may be a good opportunity to think about a computed property here

        this.current_video_file_id = file.id;
        this.current_video = file.video;
        // Trigger update of child props before fetching frames an sequences.
        await this.$nextTick();

        // We need to update sequence lists synchronously to know when to remove the placeholder.
        this.$refs.sequence_list.clear_sequence_list_cache();
        await this.$refs.sequence_list.get_sequence_list();
        // Update the frame data.
        await this.$refs.video_controllers.current_video_update();
        const new_sequence_list = this.$refs.sequence_list.sequence_list;
        this.$refs.sequence_list.change_current_sequence(new_sequence_list[0]);
      }
    },

    toggle_instance_transparency: function () {
      if (this.default_instance_opacity === 1) {
        this.default_instance_opacity = 0.25;
      } else {
        this.default_instance_opacity = 1;
      }
    },


    toggle_file_change_left() {
      if (!this.task) {
        this.change_file("previous");
      } else {
        this.$emit("change_task", "previous", this.task, false)
      }
    },

    toggle_shift_frame_left() {
      if (this.annotation_show_on) {
        return
      }
      this.shift_frame_via_store(-1);
    },

    trigger_instance_focus: function () {
      if (this.instance_hover_index != undefined) {
        this.focus_instance({index: this.instance_hover_index})
      } else {
        this.focus_instance_show_all()
      }
    },

    toggle_shift_frame_right() {
      if (this.annotation_show_on) {
        return
      }
      this.shift_frame_via_store(1);
    },

    toggle_file_change_right() {
      if (!this.task) {
        this.change_file("next");
      } else {
        this.$emit("change_task", "next", this.task, false)
      }
    },

    toggle_show_hide_occlusion: function () {
      this.label_settings.show_occluded_keypoints =
        !this.label_settings.show_occluded_keypoints;
      this.refresh = new Date();
    },

    toggle_escape_key: function () {
      if (this.view_only_mode == true) {
        return;
      }
      if (this.instance_select_for_issue || this.view_issue_mode) {
        return;
      }
      if (this.instance_select_for_merge) {
        return;
      }

      this.edit_mode_toggle(this.draw_mode);
      this.is_actively_drawing = false;
    },

    jump_to_next_instance_frame() {
      this.$refs.video_controllers.next_instance();
    },

    complete_and_move() {
      if (
        this.working_file &&
        this.working_file.ann_is_complete == true ||
        this.view_only_mode == true
      ) {
        return;
      }
      this.$emit('save', true); // and_complete == true
    },

    reset_drawing: function () {
      if (this.view_only_mode == true) {
        return;
      }
      this.lock_point_hover_change = false; // reset
      this.ellipse_current_drawing_face = false; // reset
      const auto_border_tool = new PolygonAutoBorderTool(this.auto_border_context)
      auto_border_tool.reset_instance_points(this.instance_list)
      auto_border_tool.reset_auto_border_context()
      this.hide_context_menu();
      this.$store.commit('finish_draw')
      this.current_polygon_point_list = []
      this.instance_template_draw_started = false;
      this.is_actively_drawing = false;
      this.instance_template_start_point = undefined;
      this.actively_drawing_instance_template = undefined;
      this.reset_current_instances()
    },
    show_loading_paste: function () {
      this.show_snackbar_paste = true;
      this.snackbar_paste_message = 'Pasting Instances Please Wait....';
    },
    show_success_paste: function () {
      this.show_snackbar_paste = true;
      this.snackbar_paste_message = 'Instance Pasted on Frames ahead.';
    },
    initialize_instance: function (instance): Instance {
      return initialize_instance_object(instance, this)
    },

    move_instance: function (instance_clipboard) {
      /*
      * Mostly used for pasting instances on same image/frame, so that they don't
      * get pasted on the exact same position.
      * */
      if (instance_clipboard.type === "point") {
        instance_clipboard.points[0].x += 50;
        instance_clipboard.points[0].y += 50;
      } else if (instance_clipboard.type === "box") {
        instance_clipboard.x_min += 50;
        instance_clipboard.x_max += 50;
        instance_clipboard.y_min += 50;
        instance_clipboard.y_max += 50;
      } else if (instance_clipboard.type === "line" || instance_clipboard.type === "polygon") {
        for (const point of instance_clipboard.points) {
          point.x += 50;
          point.y += 50;
        }
      } else if (instance_clipboard.type === "keypoints") {
        for (const node of instance_clipboard.nodes) {
          node.x += 50;
          node.y += 50;
        }
      } else if (instance_clipboard.type === "cuboid") {
        for (let key in instance_clipboard.front_face) {
          if (["width", "height"].includes(key)) {
            continue;
          }
          instance_clipboard.front_face[key].x += 85;
          instance_clipboard.front_face[key].y += 85;
          instance_clipboard.rear_face[key].x += 85;
          instance_clipboard.rear_face[key].y += 85;
        }
      } else if (instance_clipboard.type === "ellipse") {
        instance_clipboard.center_y += 50;
        instance_clipboard.center_x += 50;
      } else if (instance_clipboard.type === "curve") {
        instance_clipboard.p1.x += 50;
        instance_clipboard.p1.y += 50;
        instance_clipboard.p2.x += 50;
        instance_clipboard.p2.y += 50;
      }
      return instance_clipboard
    },
    add_pasted_instance_to_instance_list: async function (
      instance_clipboard,
      next_frames,
      original_file_id,
      frame_number = undefined
    ) {
      let on_new_frame_or_file = false;
      if (
        instance_clipboard.original_frame_number != this.image_annotation_ctx.current_frame ||
        next_frames != undefined
      ) {
        on_new_frame_or_file = true;
      }
      if (this.working_file && this.working_file.id != original_file_id) {
        on_new_frame_or_file = true;
      }
      if (this.task && this.working_file.id != original_file_id) {
        on_new_frame_or_file = true;
      }
      if (!on_new_frame_or_file) {
        instance_clipboard = this.move_instance(instance_clipboard)
      }

      // Deselect instances.
      for (const instance of this.instance_list) {
        this.deselect_instance(instance)
      }
      let pasted_instance = initialize_instance_object(instance_clipboard, this);
      pasted_instance = post_init_instance(pasted_instance,
        this.label_file_map,
        this.canvas_element,
        this.label_settings,
        this.canvas_transform,
        this.instance_hovered,
        this.instance_unhovered,
        this.canvas_mouse_tools
      )
      if (next_frames != undefined) {
        let next_frames_to_add = parseInt(next_frames, 10);
        const frames_to_save = [];
        // Fetch Instance List for empty frame buffers
        let missing_frames = []
        for (let i = this.image_annotation_ctx.current_frame + 1; i <= this.image_annotation_ctx.current_frame + next_frames_to_add; i++) {
          if (!this.instance_buffer_dict[i]) {
            missing_frames.push(i)
          }
        }

        let min_frame = Math.min(...missing_frames);
        let max_frame = Math.max(...missing_frames);
        let url = this.url_instance_buffer;
        let new_instance_buffer = await this.get_instance_buffer_parallel(url, min_frame, max_frame)
        if (!new_instance_buffer) {
          return
        }
        this.instance_buffer_dict = {
          ...this.instance_buffer_dict,
          ...new_instance_buffer
        };
        for (let i = this.image_annotation_ctx.current_frame + 1; i <= this.image_annotation_ctx.current_frame + next_frames_to_add; i++) {
          // Here we need to create a new COPY of the instance. Otherwise, if we moved one instance
          // It will move on all the other frames.
          let new_frame_instance = duplicate_instance(pasted_instance, this);
          new_frame_instance = initialize_instance_object(new_frame_instance, this);
          // Set the last argument to true, to prevent to push to the instance_list here.
          this.add_instance_to_file(new_frame_instance, i);
          frames_to_save.push(i);
        }
        this.refresh_instance_list_sidebar();
        this.show_loading_paste();
        this.$emit('save_multiple_frames', frames_to_save)
        this.show_success_paste();
      } else {
        this.add_instance_to_file(
          pasted_instance,
          frame_number
        );
        // Auto select on label view detail for inmediate attribute edition.
        this.refresh_instance_list_sidebar();
      }
    },
    paste_instance: async function (
      next_frames = undefined,
      instance_hover_index = undefined,
      frame_number = undefined
    ) {
      const clipboard = this.clipboard;
      if (this.any_frame_saving || this.any_loading) {
        return
      }
      if (this.image_annotation_ctx.go_to_keyframe_loading) {
        return
      }
      if (!clipboard && instance_hover_index == undefined) {
        return;
      }
      if (instance_hover_index != undefined) {
        this.copy_instance(false, instance_hover_index);
      }
      // We need to duplicate on each paste to avoid double ID's on the instance list.
      const new_clipboard_instance_list = [];

      for (const instance_clipboard of this.clipboard.instance_list) {
        let instance_clipboard_dup =
          duplicate_instance(instance_clipboard, this);
        await this.add_pasted_instance_to_instance_list(
          instance_clipboard_dup,
          next_frames,
          this.clipboard.file_id,
          frame_number
        );
        new_clipboard_instance_list.push(instance_clipboard_dup);
      }


      this.set_clipboard(new_clipboard_instance_list);
    },
    set_clipboard: function (instance_list) {
      let file_id = this.working_file.id;
      this.$store.commit("set_clipboard", {
        instance_list: instance_list,
        file_id: file_id,
      });
    },
    on_context_menu_copy_instance: function (instance_index) {
      this.copy_instance(false, instance_index);
    },
    copy_instance: function (
      hotkey_triggered = false,
      instance_index = undefined
    ) {
      if (this.draw_mode) {
        return;
      }
      if (!this.label_settings.allow_multiple_instance_select) {
        if (!this.selected_instance && instance_index == undefined) {
          return;
        }
        if (this.hotkey_triggered && !this.selected_instance) {
          return;
        }
        const instance_to_copy = this.selected_instance
          ? this.selected_instance
          : this.instance_list[instance_index];
        this.instance_clipboard = duplicate_instance(instance_to_copy, this);
        this.instance_clipboard.selected = true;
        this.instance_clipboard.original_frame_number = this.image_annotation_ctx.current_frame;

        this.set_clipboard([this.instance_clipboard]);
      } else {
        alert("Copy paste not implemented for multiple instnaces.");
        // TODO implement flag limit conditions for multi selects.
        if (!this.selected_instance && instance_index == undefined) {
          return;
        }
      }
    },
    update_draw_mode_on_instances: function (draw_mode) {
      this.instance_context.draw_mode = draw_mode;
    },
    edit_mode_toggle: function (draw_mode) {
      this.reset_drawing();
      this.$emit('draw_mode_change')
      this.update_draw_mode_on_instances(draw_mode);
      this.is_actively_drawing = false; // QUESTION do we want this as a toggle or just set to false to clear
      if (this.draw_mode && this.is_keypoint_template && this.current_instance_template.mode === 'guided') {
        this.guided_nodes_ordinal = 1;
        this.show_snackbar_guided_keypoints_drawing(this.guided_nodes_ordinal)
      } else {
        this.show_custom_snackbar = false;
      }
    },
    update_sequence_data: function (instance_list, frame_number, response) {
      /*
      * Updates ID's and color data from server response
      * */

      SequenceUpdateHelpers.populate_empty_sequence_ids(
        instance_list,
        response.data.new_sequence_list
      )

      // Update any new created sequences
      if (response.data.new_sequence_list) {
        for (let new_seq of response.data.new_sequence_list) {
          this.$refs.sequence_list.add_or_update_existing_sequence(new_seq);
        }
      }

      // Add new Keyframe Numbers to Sequence from the created instances.
      for (var instance of response.data.added_instances) {
        this.add_keyframe_to_sequence(instance, frame_number)
        if (instance.type == "deleted") {
          this.$refs.sequence_list.remove_frame_number_from_sequence(
            instance.sequence_id,
            frame_number
          )
        }
      }
    },
    add_keyframe_to_sequence(instance, frame_number) {
      if (instance.type == "created" ||
        instance.type == "new_instance" ||
        instance.type == "undeleted")      // not 'edited'
      {
        this.$refs.sequence_list.add_frame_number_to_sequence(
          instance.sequence_id,
          frame_number
        );
      }
    },
    request_next_instance: function (label_file_id) {
      this.$refs.video_controllers.next_instance(label_file_id);
    },
  },
});
</script>

<style>
#canvas_wrapper,
#annotation_core {
  outline: none;
  -webkit-tap-highlight-color: rgba(255, 255, 255, 0); /* mobile webkit */
}
</style>
