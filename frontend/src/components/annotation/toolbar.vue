<template>
  <v-toolbar
    v-if="show_toolbar"
    dense
    width="100%"
    elevation="0"
    fixed
    :height="height"
    style="overflow: hidden; padding: 0; border-bottom: 1px solid #e0e0e0"
  >
    <v-toolbar-items>
      <v-chip
        v-if="file && file.state === 'removed'"
        color="error"
        small
        class="mt-3"
        ><v-icon small>mdi-archive</v-icon>Archived</v-chip
      >
      <div v-show="task && task.id">
        <v-layout>
          <ui_schema name="logo">
            <ahref_seo_optimal
              v-if="$store.getters.get_ui_schema('logo', 'visible')"
              :href="'/me'"
            >
              <div class="pt-2 pr-3 clickable">
                <img
                  src="https://storage.googleapis.com/diffgram-002/public/logo/diffgram_logo_word_only.png"
                  height="30px"
                />
              </div>
            </ahref_seo_optimal>
          </ui_schema>

          <tooltip_button
            ui_schema_name="home"
            color="primary"
            datacy="toolbar_home_button"
            :icon_style="true"
            icon="mdi-home"
            tooltip_message="Home"
            @click="$router.push('/me')"
            :bottom="true"
          >
          </tooltip_button>

          <tooltip_button
            ui_schema_name="task_list"
            color="primary"
            :icon_style="true"
            icon="mdi-playlist-play"
            tooltip_message="Task List"
            @click="$router.push('/job/' + task.job_id)"
            :bottom="true"
          >
          </tooltip_button>

          <v-divider vertical></v-divider>
        </v-layout>
      </div>

      <!-- Undo Redo -->

      <div v-if="show_undo_redo == true && command_manager">
        <tooltip_button
          :disabled="
            save_loading ||
            view_only_mode ||
            command_manager.command_history.length == 0 ||
            command_manager.command_index == undefined
          "
          color="primary"
          :icon_style="true"
          icon="mdi-undo"
          tooltip_message="Undo (ctrl+z)"
          @click="$emit('undo')"
          :bottom="true"
          ui_schema_name="undo"
        >
        </tooltip_button>

        <tooltip_button
          :disabled="
            save_loading ||
            view_only_mode ||
            command_manager.command_history.length == 0 ||
            command_manager.command_index ==
              command_manager.command_history.length - 1
          "
          color="primary"
          :icon_style="true"
          icon="mdi-redo"
          tooltip_message="Redo (ctrl+y)"
          @click="$emit('redo')"
          :bottom="true"
          ui_schema_name="redo"
        >
        </tooltip_button>
      </div>

      <v-divider v-if="task" vertical></v-divider>

      <v_is_complete
        v-if="task"
        :project_string_id="project_string_id"
        :current_file="file ? file : task.file"
        :task="task"
        @complete_task="$emit('complete_task')"
        @replace_file="$emit('replace_file', $event)"
        :save_and_complete="true"
        :loading="save_loading"
        :disabled="save_loading || view_only_mode || (!file && !task)"
        :view_only_mode="view_only_mode"
        :task_id="task ? task.id : undefined"
      >
      </v_is_complete>

      <!-- Defer, In Task Context Only -->
      <div>
        <tooltip_button
          v-if="task && task.id && task.status == 'available'"
          ui_schema_name="defer"
          @click="$emit('task_update_toggle_deferred')"
          :loading="save_loading"
          :disabled="
            save_loading ||
            view_only_mode ||
            (file == undefined && task == undefined)
          "
          color="primary"
          :icon_style="true"
          icon="mdi-debug-step-over"
          tooltip_message="Defer"
          :bottom="true"
        >
        </tooltip_button>
      </div>

      <v-divider vertical></v-divider>

      <ui_schema name="zoom" data-cy="toolbar_zoom_info">
        <div class="pt-3 pl-2 pr-2">
          <v-tooltip bottom color="info">
            <template v-slot:activator="{ on }">
              <v-chip v-on="on" color="white" small text-color="primary">
                <h3>{{ Math.round(canvas_scale_local * 100) }}%</h3>
              </v-chip>
            </template>

            <v-alert type="info">
              While over image <kbd>Scroll</kbd> to Zoom.
            </v-alert>
          </v-tooltip>
        </div>
      </ui_schema>

      <v-divider vertical></v-divider>

      <ui_schema name="label_selector">
        <div style="width: 310px">
          <div class="pl-2 pr-3 pt-4">
            <label_select_annotation
              :project_string_id="project_string_id"
              :label_file_list="label_list"
              :label_file_colour_map="label_file_colour_map"
              @change="$emit('change_label_file', $event)"
              :loading="loading"
              :request_refresh_from_project="true"
              :show_visibility_toggle="true"
              @update_label_file_visible="
                $emit('update_label_file_visibility', $event)
              "
            >
            </label_select_annotation>
          </div>
        </div>
      </ui_schema>

      <!-- TODO @get_next_instance="request_next_instance" -->

      <!-- TODO in task mode, this can be force set by Schema
          and optionally hidden-->

      <ui_schema name="instance_selector">
        <div class="pl-3 pr-3 pt-4" style="max-width: 200px">
          <!-- instance_selector -->
          <diffgram_select
            :item_list="instance_type_list"
            data_cy="instance-type-select"
            v-model="instance_type"
            label="New Instance Type"
            :disabled="loading || loading_instance_templates || view_only_mode"
            @change="$emit('change_instance_type', instance_type)"
          >
          </diffgram_select>
        </div>
      </ui_schema>

      <tooltip_button
        v-if="instance_type == 'tag'"
        @click="$emit('new_tag_instance')"
        color="primary"
        :icon_style="true"
        icon="mdi-tag-plus-outline"
        tooltip_message="Manual New Tag (Automatic on Label Change)"
        :bottom="true"
      >
      </tooltip_button>

      <ui_schema name="edit_instance_template">
        <tooltip_button
          tooltip_message="Edit Instance Template"
          v-if="instance_template_selected && is_keypoint_template"
          @click="$emit('open_instance_template_dialog')"
          color="primary"
          icon="mdi-vector-polyline-edit"
          :icon_style="true"
          :bottom="true"
        >
        </tooltip_button>
      </ui_schema>

      <v-divider vertical></v-divider>

      <ui_schema name="draw_edit">
        <div class="pl-3 pt-3 pr-2">
          <v-switch
            v-if="view_only_mode != true"
            :label_file="mode_text"
            data-cy="edit_toggle"
            :disabled="view_issue_mode"
            v-model="draw_mode_local"
            @change="$emit('edit_mode_toggle', draw_mode_local)"
            :label="mode_text"
          >
          </v-switch>
        </div>
      </ui_schema>

      <v-divider vertical v-if="!view_only_mode"></v-divider>

      <div>
        <tooltip_button
          ui_schema_name="save"
          @click="$emit('save')"
          datacy="save_button"
          :loading="save_loading"
          :disabled="
            !has_changed ||
            save_loading ||
            view_only_mode ||
            (file == undefined && task == undefined)
          "
          color="primary"
          icon="save"
          tooltip_message="Save Image / Frame"
          :icon_style="true"
          :bottom="true"
        >
        </tooltip_button>
      </div>
      <div class="has-changed">
        <div style="width: 100px">
          <span v-if="save_loading"> Saving. </span>
          <span v-else>
            <span v-if="has_changed">Changes Detected...</span>
            <span v-else>Saved.</span>
          </span>
        </div>
      </div>

      <v-divider v-if="!view_only_mode" vertical></v-divider>

      <!-- Curious about displaying the "current size" somewhere but
          haven't found a great position to do it

      Would prefer this to be maybe a drag operation but this seems reasonable for now
      If we include this on the actual panel then it moves funny

      Because the right panel overflows on top of menu bar
      this is far left so at least a a person can get back / undo it...
        -->

      <!-- QA in progress
        https://stackoverflow.com/questions/58809023/vuetify-same-slot-content-for-multiple-template-slots-->

      <!-- Caution, the item-text here seems to define the return type to
            v-model, which we use for important things.-->

      <!--  without this div the order of the two buttons randomly swaps
    -->
      <div>
        <tooltip_button
          tooltip_message="Previous File"
          v-if="!task && file && file.id"
          @click="$emit('change_file', 'previous')"
          :disabled="
            loading || annotations_loading || full_file_loading || !file
          "
          color="primary"
          icon="mdi-chevron-left-circle"
          :icon_style="true"
          :bottom="true"
        >
        </tooltip_button>
        <!-- TODO Move some of disabled logic into functions don't like having
            so much of it here as it gets more complext -->
      </div>
      <div>
        <tooltip_button
          tooltip_message="Next File"
          v-if="!task && file && file.id"
          @click="$emit('change_file', 'next')"
          :disabled="
            loading || annotations_loading || full_file_loading || !file
          "
          color="primary"
          icon="mdi-chevron-right-circle"
          :icon_style="true"
          :bottom="true"
        >
        </tooltip_button>
      </div>
      <v-divider vertical />
      <div>
        <button_with_menu
          datacy="open-annotation-show-menu"
          v-if="annotation_show_on !== true"
          tooltip_message="Annotation show"
          color="primary"
          :icon="anootations_show_icon"
          :close_by_button="true"
          :disabled="loading || annotations_loading || full_file_loading"
        >
          <template slot="content">
            <v-btn
              data-cy="start-annotation-show"
              @click="
                $emit(
                  'annotation_show',
                  !task && file && file.id ? 'file' : 'task'
                )
              "
            >
              <span> Start </span>
            </v-btn>
            <v-slider
              v-model="numberValue"
              :tick-labels="duration_labels"
              :max="4"
              step="1"
              ticks="always"
              tick-size="4"
              hint="Duration in seconds"
              persistent-hint
              @change="$emit('show_duration_change', $event)"
            />
          </template>
        </button_with_menu>
        <tooltip_button
          v-else
          data-cy="pause-annotation-show"
          tooltip_message="Pause"
          ui_schema_name="stop_shideshow"
          @click="
            $emit('annotation_show', !task && file && file.id ? 'file' : 'task')
          "
          color="primary"
          icon="pause"
          :icon_style="true"
          :bottom="true"
        />
      </div>
      <v-divider vertical />
      <div>
        <tooltip_button
          tooltip_message="Previous Task"
          v-if="task"
          ui_schema_name="previous_task"
          datacy="previous_task"
          @click="$emit('change_task', 'previous')"
          :disabled="
            loading || annotations_loading || full_file_loading || !task
          "
          color="primary"
          icon="mdi-chevron-left-circle"
          :icon_style="true"
          :bottom="true"
        >
        </tooltip_button>

        <!-- This is a WIP example of injecting a tombstone button to help positionally
        make it easier for user.-->
        <!-- 
      <tooltip_button
        tooltip_message="Add Button"
        ui_schema_name="add_button"
        v-if="!$store.getters.get_ui_schema('previous_task', 'visible')"
        @click="$emit('add_ui_schema')"
        color="primary"
        icon="add"
        :icon_style="true"
        :bottom="true"
      >
      </tooltip_button>
      --></div>
      <div>
        <tooltip_button
          tooltip_message="Next Task"
          v-if="task"
          ui_schema_name="next_task"
          datacy="next_task"
          @click="$emit('change_task', 'next')"
          :disabled="
            loading || annotations_loading || full_file_loading || !task
          "
          color="primary"
          icon="mdi-chevron-right-circle"
          :icon_style="true"
          :bottom="true"
        >
        </tooltip_button>
      </div>

      <v-divider vertical></v-divider>

      <tooltip_button
        tooltip_message="Refresh Instances"
        v-if="$store.state.user.current.is_super_admin == true"
        @click="$emit('refresh_all_instances')"
        :loading="loading || annotations_loading"
        color="primary"
        icon="mdi-refresh"
        :icon_style="true"
        :bottom="true"
      >
      </tooltip_button>

      <!--  Moving away from default of multi select here, so hide for now -->
      <!--
  <tooltip_button
      @click="delete_instance"
      :disabled="draw_mode"
      color="primary"
      icon="delete"
      :icon_style="true"
      tooltip_message="Delete instances selected."
      :bottom="true">
  </tooltip_button>
  -->

      <ui_schema name="brightness_contrast_filters">
        <button_with_menu
          tooltip_message="Brightness, Contrast, Filters"
          color="primary"
          icon="exposure"
        >
          <template slot="content">
            <v-layout column>
              <v-slider
                v-model="label_settings_local.filter_brightness"
                prepend-icon="brightness_4"
                min="50"
                max="200"
              >
              </v-slider>

              <v-slider
                v-model="label_settings_local.filter_contrast"
                prepend-icon="exposure"
                min="50"
                max="200"
              ></v-slider>

              <v-slider
                v-model="label_settings_local.filter_grayscale"
                prepend-icon="gradient"
                min="0"
                max="100"
              ></v-slider>

              <v-btn icon @click="filter_reset()">
                <v-icon color="primary"> autorenew </v-icon>
              </v-btn>
            </v-layout>
          </template>
        </button_with_menu>
      </ui_schema>

      <button_with_menu
        tooltip_message="Hotkeys"
        v-if="view_only_mode != true"
        color="primary"
        icon="mdi-keyboard-settings"
        :close_by_button="true"
      >
        <template slot="content">
          <hotkeys></hotkeys>
        </template>
      </button_with_menu>

      <!-- WIP -->
      <!--
  <button_with_menu
    tooltip_message="Go To File"
    icon="mdi-arrow-up"
    color="primary"
    :commit_menu_status="true"
    :disabled="any_loading"
    :close_by_button="true"
        >

    <template slot="content">

        <v-text-field label="Go to File"
                      type="number"
                      v-model.number="user_requested_file_id">
        </v-text-field>

        <v-btn :disabled="loading"
                color="primary"
                @click="go_to_file">
          Go
        </v-btn>

      </template>
    </button_with_menu>
  -->

      <v_annotation_trainer_menu
        v-if="task && task.id"
        :job_id="task.job_id"
        :task="task"
      >
      </v_annotation_trainer_menu>

      <v-divider vertical></v-divider>

      <!-- MORE -->
      <button_with_menu
        tooltip_message="More"
        datacy="more_button"
        icon="mdi-dots-vertical"
        color="primary"
        :commit_menu_status="true"
        :disabled="loading"
        :close_by_button="true"
      >
        <template slot="content">
          <v-layout class="pb-4">
            <!-- View Task Information -->
            <button_with_menu
              v-if="task && task.id"
              tooltip_message="View Task Information"
              icon="mdi-information"
              color="primary"
            >
              <template slot="content">
                <task_meta_data_card
                  v-if="task"
                  :file="task.file"
                  :video="task.file"
                  :task="task"
                  :project_string_id="
                    project_string_id
                      ? project_string_id
                      : this.$store.state.project.current.project_string_id
                  "
                  :elevation="0"
                >
                </task_meta_data_card>
              </template>
            </button_with_menu>

            <!-- show_file_information -->
            <button_with_menu
              v-if="file && !task"
              datacy="show_file_information"
              tooltip_message="View File Information"
              icon="mdi-information"
              color="primary"
            >
              <template slot="content">
                <file_meta_data_card
                  v-if="file && !task"
                  :video="file"
                  :elevation="0"
                  :file="file"
                  :project_string_id="
                    project_string_id
                      ? project_string_id
                      : this.$store.state.project.current.project_string_id
                  "
                >
                </file_meta_data_card>
              </template>
            </button_with_menu>

            <!-- show_linked_relations_file -->
            <button_with_menu
              v-if="file && !task"
              datacy="show_linked_relations_file"
              tooltip_message="View Task Relations"
              icon="mdi-link-box-variant"
              color="primary"
            >
              <template slot="content">
                <file_relations_card
                  v-if="file"
                  :file="file"
                  :project_string_id="
                    project_string_id
                      ? project_string_id
                      : this.$store.state.project.current.project_string_id
                  "
                  :elevation="0"
                >
                </file_relations_card>
              </template>
            </button_with_menu>

            <!-- show_linked_relations_task -->
            <button_with_menu
              v-if="task"
              datacy="show_linked_relations_task"
              tooltip_message="View Task Relations"
              icon="mdi-link-box-variant"
              color="primary"
            >
              <template slot="content">
                <task_relations_card
                  v-if="task"
                  :file="task.file"
                  :task="task"
                  :project_string_id="
                    project_string_id
                      ? project_string_id
                      : this.$store.state.project.current.project_string_id
                  "
                  :elevation="0"
                >
                </task_relations_card>
              </template>
            </button_with_menu>

            <button_with_menu
              tooltip_message="Resize Panels"
              icon="mdi-resize"
              color="primary"
            >
              <template slot="content">
                <v-layout column>
                  <v-card-title> Panel Sizes </v-card-title>

                  <v-checkbox
                    label="Auto Size Canvas"
                    v-model="
                      label_settings_local.canvas_scale_global_is_automatic
                    "
                  >
                  </v-checkbox>

                  <v-slider
                    label="Canvas"
                    min=".2"
                    max="2"
                    step=".05"
                    thumb-label="always"
                    ticks
                    @change="on_change_canvas_scale_global"
                    @click="on_change_canvas_scale_global"
                    v-model="label_settings_local.canvas_scale_global_setting"
                  >
                  </v-slider>

                  <v-slider
                    label="Left"
                    min="200"
                    step="50"
                    max="750"
                    thumb-label="always"
                    ticks
                    @input="
                      $store.commit('set_user_setting', [
                        'studio_left_nav_width',
                        label_settings_local.left_nav_width,
                      ])
                    "
                    v-model="label_settings_local.left_nav_width"
                  >
                  </v-slider>
                </v-layout>
              </template>
            </button_with_menu>

            <!-- Clear unsaved -->
            <tooltip_button
              @click="$emit('clear__new_and_no_ids')"
              tooltip_message="Clear Unsaved"
              icon="mdi-close-circle-multiple"
              :icon_style="true"
              color="primary"
              tooltip_direction="bottom"
              :small="true"
            >
            </tooltip_button>

            <!-- Settings -->
            <button_with_menu
              tooltip_message="Annotation Settings"
              color="primary"
              datacy="advanced_setting"
              icon="settings"
              tooltip_direction="bottom"
            >
              <template slot="content">
                <v-layout column data-cy="annotation_setting_menu">
                  <v-card-title> Settings </v-card-title>

                  <v-checkbox
                    label="Show Any Text"
                    data-cy="show_any_text_checkbox"
                    v-model="label_settings_local.show_text"
                  >
                  </v-checkbox>

                  <v-checkbox
                    label="Show Label Text"
                    data-cy="show_label_text_checkbox"
                    v-model="label_settings_local.show_label_text"
                  >
                  </v-checkbox>

                  <v-checkbox
                    label="Show Attribute Text"
                    data-cy="show_attribute_text_checkbox"
                    v-model="label_settings_local.show_attribute_text"
                  >
                  </v-checkbox>

                  <v-checkbox
                    label="Show Removed"
                    data-cy="show_removed_text_checkbox"
                    v-model="label_settings_local.show_removed_instances"
                  >
                  </v-checkbox>

                  <v-checkbox
                    label="Allow Multiple Instance Select"
                    data-cy="show_allow_multiple_select_checkbox"
                    v-model="
                      label_settings_local.allow_multiple_instance_select
                    "
                  >
                  </v-checkbox>

                  <v-checkbox
                    label="Show Occluded Keypoints"
                    data-cy="show_occluded_keypoints"
                    v-model="label_settings_local.show_occluded_keypoints"
                  >
                  </v-checkbox>

                  <v-checkbox
                    label="Show Left Right Icons Keypoints"
                    data-cy="show_left_right_arrows"
                    v-model="label_settings_local.show_left_right_arrows"
                  >
                  </v-checkbox>

                  <v-checkbox
                    label="Enable Snap to Instance"
                    data-cy="enable_snap_to_instance"
                    v-model="label_settings_local.enable_snap_to_instance"
                  >
                  </v-checkbox>

                  <v-slider
                    label="Text Font Size"
                    min="10"
                    max="30"
                    thumb-label
                    ticks
                    v-model="label_settings_local.font_size"
                    prepend-icon="mdi-format-size"
                  >
                  </v-slider>

                  <v-slider
                    label="Text Background Opacity"
                    v-model="label_settings_local.font_background_opacity"
                    prepend-icon="brightness_4"
                    thumb-label
                    ticks
                    min="0.0"
                    step=".05"
                    max="1.0"
                  >
                  </v-slider>

                  <v-slider
                    label="Target Reticle Size"
                    min="5"
                    max="40"
                    thumb-label
                    ticks
                    v-model="label_settings_local.target_reticle_size"
                  >
                  </v-slider>

                  <v-slider
                    label="Vertex Size"
                    min="0"
                    max="40"
                    thumb-label
                    ticks
                    v-model="label_settings_local.vertex_size"
                  >
                  </v-slider>

                  <v-slider
                    label="Spatial Line Size"
                    min="0"
                    max="4"
                    thumb-label
                    ticks
                    v-model="label_settings_local.spatial_line_size"
                  >
                  </v-slider>

                  <v-checkbox
                    label="Show Ghost Instances"
                    data-cy="show_ghost_instances"
                    v-model="label_settings_local.show_ghost_instances"
                  >
                  </v-checkbox>

                  <v-checkbox
                    label="On Instance Creation: Advance Sequence Number"
                    data-cy="on_instance_creation_advance_sequence"
                    v-model="
                      label_settings_local.on_instance_creation_advance_sequence
                    "
                  >
                  </v-checkbox>

                  <!-- Note backend enforces hard
                limit on this (ie max 1000) , so need to update
                there too if required-->
                  <v-slider
                    label="Video Instance Buffer"
                    min="15"
                    max="300"
                    thumb-label
                    ticks
                    v-model="label_settings_local.instance_buffer_size"
                  >
                  </v-slider>

                  <tooltip_button
                    tooltip_message="Restore All User Settings & Prompts"
                    @click="$store.commit('restore_default_user_settings')"
                    color="primary"
                    icon="mdi-refresh"
                    :icon_style="true"
                    :bottom="true"
                  >
                  </tooltip_button>
                </v-layout>
              </template>
            </button_with_menu>
          </v-layout>

          <v-card-title v-if="task && task.id"> Task Specific </v-card-title>

          <v-layout v-if="task && task.id">
            <tooltip_button
              tooltip_message="Jump to Next Task With Issues."
              @click="$emit('next_issue_task')"
              :disabled="loading || annotations_loading"
              color="primary"
              icon="mdi-reload-alert"
              :icon_style="true"
              :bottom="true"
            >
            </tooltip_button>

            <tooltip_button
              v-if="$store.state.builder_or_trainer.mode == 'builder'"
              tooltip_message="Export This Task"
              @click="
                $router.push(
                  '/project/' +
                    $store.state.project.current.project_string_id +
                    '/export?task_id=' +
                    task.id
                )
              "
              icon="mdi-export"
              :icon_style="true"
              :bottom="true"
              color="primary"
            >
            </tooltip_button>
          </v-layout>

          <v-layout>
            <tooltip_button
              tooltip_message="Copy All Instances"
              @click="$emit('copy_all_instances')"
              :disabled="loading || annotations_loading"
              color="primary"
              icon="mdi-content-duplicate"
              :icon_style="true"
              :bottom="true"
            >
            </tooltip_button>
          </v-layout>
        </template>
      </button_with_menu>
      <v-spacer class="flex-grow-1"></v-spacer>
    </v-toolbar-items>
    <v-chip
      v-if="view_only_mode == true"
      small
      color="primary"
      class="d-flex pa-2 justify-center align-center"
    >
      <span style="font-size: 12px" class="mr-2"
        ><strong> <v-icon class="mr-2">mdi-eye</v-icon>View only</strong></span
      >
    </v-chip>
  </v-toolbar>
</template>

<script lang="ts">
import Vue from "vue";
import label_select_annotation from "../label/label_select_annotation.vue";
import file_meta_data_card from "./file_meta_data_card";
import task_relations_card from "./task_relations_card";
import file_relations_card from "./file_relations_card";
import task_meta_data_card from "./task_meta_data_card";
import hotkeys from "./hotkeys";

export default Vue.extend({
  name: "toolbar",
  components: {
    label_select_annotation,
    file_meta_data_card,
    file_relations_card,
    task_meta_data_card,
    task_relations_card,
    hotkeys,
  },
  props: {
    project_string_id: {},
    label_settings: {
      default: null,
    },
    task: {},
    file: {},
    canvas_scale_local: {},
    label_list: {},
    label_file_colour_map: {},
    show_toolbar: {
      default: true,
      type: Boolean,
    },
    height: {
      default: null,
    },
    command_manager: {
      default: null,
    },
    save_loading: {
      default: false,
    },
    loading: {
      default: false,
    },
    view_only_mode: {
      default: false,
    },
    show_undo_redo: {
      default: true,
      type: Boolean,
    },
    has_changed: {
      default: false,
    },
    draw_mode: {
      default: true,
    },
    full_file_loading: {},
    annotations_loading: {},
    instance_template_selected: {},
    instance_type: {},
    loading_instance_templates: {},
    instance_type_list: {},
    view_issue_mode: {},
    is_keypoint_template: {},
    enabled_edit_schema: {
      default: false,
      type: Boolean,
    },
    annotation_show_on: {
      type: Boolean,
    },
  },
  data() {
    return {
      label_settings_local: {
        canvas_scale_global_is_automatic: true,
      },
      draw_mode_local: true,
      numberValue: 1,
      duration_labels: ["1", "2", "3", "4", "5"],
    };
  },
  watch: {
    label_settings_local: {
      deep: true,
      handler: function (event) {
        this.$emit("label_settings_change", event);
      },
    },
    label_settings(event) {
      this.label_settings_local = event;
    },
    draw_mode(event) {
      this.draw_mode_local = event;
    },
  },
  mounted() {
    this.label_settings_local = this.$props.label_settings;
    this.draw_mode_local = this.$props.draw_mode;
  },
  computed: {
    mode_text: function () {
      if (this.draw_mode_local == true) {
        return "Drawing";
      } else {
        return "Editing";
      }
    },
    anootations_show_icon: function () {
      if (this.annotation_show_on) return "pause";
      return "play_circle";
    },
  },
  methods: {
    on_change_canvas_scale_global: function () {
      this.label_settings_local.canvas_scale_global_is_automatic = false;
      this.$emit(
        "canvas_scale_global_changed",
        this.label_settings_local.canvas_scale_global_setting
      );
    },
    filter_reset: function () {
      this.label_settings_local.filter_brightness = 100;
      this.label_settings_local.filter_contrast = 100;
      this.label_settings_local.filter_grayscale = 0;
    },
  },
});
</script>
