<template>
  <v-toolbar
    v-if="show_toolbar"
    dense
    width="100%"
    elevation="0"
    fixed
    :height="height"
    style="overflow: hidden; padding:0; border-bottom: 1px solid #e0e0e0"
  >
    <v-toolbar-items class="pl-0 ml-0" style="border: 1px solid #e0e0e0; width: 100%">

      <v-chip v-if="file && file.state === 'removed'" color="error" small class="mt-3">
        <v-icon small>mdi-archive</v-icon>
        Archived
      </v-chip>
      <div v-show="task && task.id">
        <v-layout>
          <ahref_seo_optimal :href="'/home/dashboard'">
            <div class="pt-2 pr-3 clickable">

              <img src="https://storage.googleapis.com/diffgram-002/public/logo/diffgram_logo_word_only.png"
                   height="30px"/>

            </div>
          </ahref_seo_optimal>

          <tooltip_button
            color="primary"
            :icon_style="true"
            icon="mdi-home"
            tooltip_message="Home"
            @click="$router.push('/job/' + task.job_id)"
            :bottom="true">
          </tooltip_button>


        </v-layout>
      </div>
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




    <div style="width: 310px" class=" pt-4">
      <label_select_annotation
        data-cy="toolbar_label_selector"
        :project_string_id="project_string_id"
        :label_file_list="label_list"
        default_hot_keys="l"
        :label_file_colour_map="label_file_colour_map"
        @change="$emit('change_label_file', $event)"
        :loading="loading"
        :request_refresh_from_project="true"
        :show_visibility_toggle="true"
        @update_label_file_visible="$emit('update_label_file_visibility', $event)"
      >
      </label_select_annotation>
    </div>


      <v-flex xs2>
        <div class="pl-3 pr-3 pt-4">

          <!-- instance_selector -->
          <diffgram_select
            v-if="view_only_mode != true"
            :item_list="instance_type_list"
            data_cy="instance-type-select"
            v-model="instance_type"
            label="New Instance Type"
            :disabled="loading || loading_instance_templates"
            @change="$emit('change_instance_type', instance_type)"
          >
          </diffgram_select>

        </div>
      </v-flex>

      <tooltip_button
        v-if="instance_type == 'tag'"
        @click="$emit('new_tag_instance')"
        color="primary"
        :icon_style="true"
        icon="mdi-tag-plus-outline"
        tooltip_message="Manual New Tag (Automatic on Label Change)"
        :bottom="true">
      </tooltip_button>

      <v-divider
        vertical
      ></v-divider>


      <div class="pl-3 pt-3 pr-2">
        <v-switch v-if="view_only_mode != true"
                  :label_file="mode_text"
                  data-cy="edit_toggle"
                  :disabled="view_issue_mode"
                  v-model="draw_mode_local"
                  @change="$emit('edit_mode_toggle', draw_mode_local)"
                  :label="mode_text">
        </v-switch>
      </div>


      <v-divider
        vertical
        v-if="!view_only_mode"
      ></v-divider>


      <div>
        <tooltip_button
          @click="$emit('save')"
          datacy="save_button"
          :loading="save_loading"
          :disabled="!has_changed || save_loading || view_only_mode || (file == undefined && task == undefined)"
          color="primary"
          icon="save"
          tooltip_message="Save Image / Frame"
          :icon_style="true"
          :bottom="true">
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


      <div>
        <tooltip_button
          data-cy="previous_file_button"
          tooltip_message="Previous File"
          v-if="!task && file && file.id"
          @click="$emit('change_file', 'previous')"
          :disabled="loading || annotations_loading || full_file_loading || !file"
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
          data-cy="next_file_button"
          tooltip_message="Next File"
          v-if="!task && file && file.id"
          @click="$emit('change_file', 'next')"
          :disabled="loading || annotations_loading ||  full_file_loading || !file"
          color="primary"
          icon="mdi-chevron-right-circle"
          :icon_style="true"
          :bottom="true"
        >
        </tooltip_button>
      </div>
      <div>
        <tooltip_button
          tooltip_message="Previous Task"
          v-if="task"
          @click="$emit('change_task', 'previous')"
          :disabled="loading || annotations_loading ||  full_file_loading || !task"
          color="primary"
          icon="mdi-chevron-left-circle"
          :icon_style="true"
          :bottom="true"
        >
        </tooltip_button>
      </div>
      <div>
        <tooltip_button
          tooltip_message="Next Task"
          v-if="task"
          @click="$emit('change_task', 'next')"
          :disabled="loading || annotations_loading || full_file_loading || !task"
          color="primary"
          icon="mdi-chevron-right-circle"
          :icon_style="true"
          :bottom="true"
        >
        </tooltip_button>

      </div>


      <v-divider
        vertical
      ></v-divider>


      <tooltip_button
        data-cy="refresh_instances"
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

      <button_with_menu
        datacy="display_hotkeys_button"
        tooltip_message="Hotkeys"
        v-if="view_only_mode != true"
        color="primary"
        icon="mdi-keyboard-settings"
        :close_by_button="true"
      >

        <template slot="content">
          <hotkeys_sensor_fusion></hotkeys_sensor_fusion>
        </template>

      </button_with_menu>

      <v-divider
        vertical
      ></v-divider>


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
              color="primary">

              <template slot="content">

                <task_meta_data_card v-if="task"
                                     :file="task.file"
                                     :video="task.file"
                                     :task="task"
                                     :project_string_id="project_string_id ? project_string_id : this.$store.state.project.current.project_string_id"
                                     :elevation="0">

                </task_meta_data_card>
              </template>

            </button_with_menu>

            <!-- show_file_information -->
            <button_with_menu
              v-if="file && !task"
              datacy="show_file_information"
              tooltip_message="View File Information"
              icon="mdi-information"
              color="primary">

              <template slot="content">

                <file_meta_data_card v-if="file && !task"
                                     :video="file"
                                     :elevation="0"
                                     :file="file"
                                     :project_string_id="project_string_id ? project_string_id : this.$store.state.project.current.project_string_id"
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
              color="primary">

              <template slot="content">

                <file_relations_card v-if="file"
                                     :file="file"
                                     :project_string_id="project_string_id ? project_string_id : this.$store.state.project.current.project_string_id"
                                     :elevation="0">

                </file_relations_card>
              </template>

            </button_with_menu>


            <!-- show_linked_relations_task -->
            <button_with_menu
              v-if="task"
              datacy="show_linked_relations_task"
              tooltip_message="View Task Relations"
              icon="mdi-link-box-variant"
              color="primary">

              <template slot="content">

                <task_relations_card
                  v-if="task"
                  :file="task.file"
                  :task="task"
                  :project_string_id="project_string_id ? project_string_id : this.$store.state.project.current.project_string_id"
                  :elevation="0">

                </task_relations_card>
              </template>

            </button_with_menu>


            <button_with_menu
              tooltip_message="Resize Panels"
              icon="mdi-resize"
              color="primary">

              <template slot="content">
                <v-layout column>

                  <v-card-title>
                    Panel Sizes
                  </v-card-title>

                  <v-checkbox
                    label="Auto Size Canvas"
                    v-model="label_settings_local.canvas_scale_global_is_automatic"
                  >
                  </v-checkbox>

                  <v-slider
                    label="Canvas"
                    min=.2
                    max=2
                    step=.05
                    thumb-label="always"
                    ticks
                    @change="label_settings_local.canvas_scale_global_is_automatic = false"
                    v-model="label_settings_local.canvas_scale_global_setting">
                  </v-slider>

                  <v-slider
                    label="Left"
                    min=200
                    step=50
                    max=750
                    thumb-label="always"
                    ticks
                    @input="
                    $store.commit('set_user_setting',
                          ['studio_left_nav_width', label_settings_local.left_nav_width])"
                    v-model="label_settings_local.left_nav_width">
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
              :small="true">
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

                  <v-card-title>
                    Settings
                  </v-card-title>

                  <v-checkbox label="Show Any Text"
                              data-cy="show_any_text_checkbox"
                              v-model="label_settings_local.show_text">
                  </v-checkbox>

                  <v-checkbox label="Show Label Text"
                              data-cy="show_label_text_checkbox"
                              v-model="label_settings_local.show_label_text">
                  </v-checkbox>

                  <v-checkbox label="Show Attribute Text"
                              data-cy="show_attribute_text_checkbox"
                              v-model="label_settings_local.show_attribute_text">
                  </v-checkbox>

                  <v-checkbox label="Show Removed"
                              data-cy="show_removed_text_checkbox"
                              v-model="label_settings_local.show_removed_instances">
                  </v-checkbox>

                  <v-slider label="Panning Speed"
                            min=1
                            max=20
                            thumb-label
                            ticks
                            v-model="label_settings_local.pan_speed">
                  </v-slider>

                  <v-slider label="Zoom Speed"
                            min=1
                            max=20
                            thumb-label
                            ticks
                            v-model="label_settings_local.zoom_speed">
                  </v-slider>

                  <v-slider label="Text Font Size"
                            min=10
                            max=30
                            thumb-label
                            ticks
                            v-model="label_settings_local.font_size">
                  </v-slider>

                  <v-slider label="Target Reticle Size"
                            min=5
                            max=40
                            thumb-label
                            ticks
                            v-model="label_settings_local.target_reticle_size">
                  </v-slider>

                  <v-slider label="Vertex Size"
                            min=0
                            max=40
                            thumb-label
                            ticks
                            v-model="label_settings_local.vertex_size">
                  </v-slider>

                  <v-slider label="Spatial Line Size"
                            min=0
                            max=4
                            thumb-label
                            ticks
                            v-model="label_settings_local.spatial_line_size">
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


          <v-card-title v-if="task && task.id">
            Task Specific
          </v-card-title>

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
          </v-layout>
        </template>
      </button_with_menu>
      <v-spacer class="flex-grow-1"></v-spacer>


    </v-toolbar-items>
    <v-chip
      v-if="view_only_mode == true"
      small
      color="primary"
      class="d-flex pa-2 justify-center align-center">
      <span style="font-size: 12px" class="mr-2"><strong> <v-icon class="mr-2">mdi-eye</v-icon>View only</strong></span>
    </v-chip>
  </v-toolbar>

</template>

<script lang="ts">

  import Vue from "vue";
  import label_select_annotation from '../label/label_select_annotation.vue';
  import file_meta_data_card from '../annotation/file_meta_data_card'
  import task_relations_card from '../annotation/task_relations_card'
  import file_relations_card from '../annotation/file_relations_card'
  import task_meta_data_card from '../annotation/task_meta_data_card'
  import hotkeys_sensor_fusion from './hotkeys_sensor_fusion'

  export default Vue.extend({
      name: 'toolbar_3d',
      components: {
        label_select_annotation,
        file_meta_data_card,
        file_relations_card,
        task_meta_data_card,
        task_relations_card,
        hotkeys_sensor_fusion
      },
      props: {
        'project_string_id': {},
        'label_settings': {
          default: null
        },
        'task': {},
        'file': {},
        'canvas_scale_local': {},
        'label_list': {},
        'label_file_colour_map': {},
        'show_toolbar': {
          default: true,
          type: Boolean
        },
        'height': {
          default: null
        },
        'command_manager': {
          default: null
        },
        'save_loading': {
          default: false
        },
        'loading': {
          default: false
        },
        'view_only_mode': {
          default: false
        },
        'show_undo_redo': {
          default: true,
          type: Boolean
        },
        'has_changed': {
          default: false
        },
        'draw_mode': {
          default: true
        },
        'full_file_loading': {},
        'annotations_loading': {},
        'instance_template_selected': {},
        'instance_type': {},
        'loading_instance_templates': {},
        'instance_type_list': {},
        'view_issue_mode': {}
      },
      data() {
        return {
          label_settings_local: {
            canvas_scale_global_is_automatic: true
          },
          draw_mode_local: true,
        }
      },
      watch: {
        label_settings_local(event) {
          this.$emit('label_settings_change', event)
        },
        label_settings(event) {
          this.label_settings_local = event
        },
        draw_mode(event) {
          this.draw_mode_local = event
        }
      },
      mounted() {
        this.label_settings_local = this.$props.label_settings
        this.draw_mode_local = this.$props.draw_mode
      },
      computed: {
        mode_text: function () {
          if (this.draw_mode_local == true) {
            return "Drawing"
          } else {
            return "Editing"
          }
        },
      },
      methods: {

        filter_reset: function () {
          this.label_settings_local.filter_brightness = 100
          this.label_settings_local.filter_contrast = 100
          this.label_settings_local.filter_grayscale = 0
        },

      }
    }
  ) </script>

<style>
  .v-toolbar__content{
    padding: 0;
  }
</style>
