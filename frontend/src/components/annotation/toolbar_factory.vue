<template>
  <div v-if="interface_type === 'audio' || interface_type === 'image' || interface_type === 'video' || interface_type === 'text'">
    <main_menu
      :height="`${show_default_navigation ? '100px' : '50px'}`"
      :show_default_navigation="show_default_navigation"
    >
      <template slot="second_row">
        <div>
          <image_and_video_toolbar
            ref="toolbar"
            v-if="interface_type === 'image' || interface_type === 'video'"
            :height="50"
            :instance_type_list="filtered_instance_type_list"
            v-bind="$props"
            v-on="$listeners"
          />
          <text_toolbar
            ref="toolbar"
            v-if="interface_type === 'text'"
            :height="50"
            :instance_type_list="filtered_instance_type_list"
            v-bind="$props"
            v-on="$listeners"
          />
          <audio_toolbar
            ref="toolbar"
            v-if="interface_type === 'audio'"
            :height="50"
            :instance_type_list="filtered_instance_type_list"
            v-bind="$props"
            v-on="$listeners"
          />
        </div>
      </template>
    </main_menu>
  </div>
</template>

<script lang="ts">
import Vue from "vue";
import image_and_video_toolbar from "./image_and_video_annotation/toolbar.vue"
import text_toolbar from "./text_annotation/text_toolbar.vue"
import audio_toolbar from './audio_annotation/audio_toolbar'
import CustomButtonsSection from "../ui_schema/custom_buttons_section.vue";

export default Vue.extend({
  name: "toolbar_factory",
  components:{
    CustomButtonsSection,
    image_and_video_toolbar,
    text_toolbar,
    audio_toolbar
  },
  props: {
    platform: {
      default: 'win',
    },
    project_string_id: { type: String, required: true },
    working_file: { type: Object, required: true },
    command_manager: { type: Object, required: true },
    history: { type: Object, default: null },
    interface_type: { type: String, default: null },
    save_loading: { type: Boolean, default: false },
    annotations_loading: { type: Boolean, default: true },
    label_schema: { type: Object, required: true },
    loading: { type: Boolean, default: false },
    view_only_mode: { type: Boolean, default: false },
    video_mode: { type: Boolean, default: false },
    label_settings: { type: Object, default: null },
    task: { type: Object, default: null },
    file: { type: Object, default: null },
    canvas_scale_local: { type: Number, default: 1 },
    has_changed: { type: Boolean, default: false },
    label_list: { type: Array, default: [] },
    draw_mode: { type: Boolean, default: true },
    label_file_colour_map: { type: Object, default: {} },
    full_file_loading: { type: Boolean, default: false },
    instance_template_selected: { type: Boolean, default: false },
    loading_instance_templates: { type: Boolean, default: false },
    view_issue_mode: { type: Boolean, default: false },
    is_keypoint_template: { type: Boolean, default: false },
    enabled_edit_schema: { type: Boolean, default: false },
    annotation_show_on: { type: Boolean, default: false },
    filtered_instance_type_list_function: { type: Function, default: () => {} },
    instance_type_list: { type: Array, default: [] },
    instance_type: { type: String, default: "box" },
    annotation_ui_context: { type: Object, required: true },
    bulk_mode: { type: Boolean, default: false },
    search_mode: { type: Boolean, default: false },
    show_ui_schema_context_menu: { type: Boolean, default: false }
  },
  mounted() {
    if (window.Cypress) {
      window.AnnotationCoreToolbar = this;
    }
  },
  computed: {
    show_default_navigation: function(): Boolean {
      if (!this.task) return true

      return false
    },
    filtered_instance_type_list: function () {
      const filtered_instance_type_list = this.filtered_instance_type_list_function(this.instance_type_list)
      return filtered_instance_type_list
    },
  }
})
</script>
