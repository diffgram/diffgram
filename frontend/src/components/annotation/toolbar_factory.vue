<template>
  <div v-if="interface_type === 'image' || interface_type === 'video'">
    <main_menu
      :height="`${show_default_navigation ? '100px' : '50px'}`"
      :show_default_navigation="show_default_navigation"
    >
      <template slot="second_row">
        <image_and_video_toolbar
          ref="toolbar"
          :height="50"
          v-bind="$props"
          v-on="$listeners"
        />
      </template>
    </main_menu>
  </div>
</template>

<script lang="ts">
import Vue from "vue";
import image_and_video_toolbar from "./image_and_video_annotation/toolbar.vue"

export default Vue.extend({
  name: "toolbar_factory",
  components:{
    image_and_video_toolbar
  },
  props: {
    project_string_id: {
      type: String,
      required: true
    },
    working_file: {
      type: Object,
      required: true
    },
    command_manager: {
      type: Object
    },
    save_loading: {
      type: Boolean,
      default: false
    },
    annotations_loading: {
      type: Boolean,
      default: true
    },
    label_schema: {
      type: Object,
      required: true
    },
    loading: {
      type: Boolean,
      default: false
    },
    view_only_mode: {
      type: Boolean,
      default: false
    },
    video_mode: {
      type: Boolean,
      default: false
    },
    label_settings: {
      type: Object,
      default: null
    },
    task: {
      type: Object,
      default: null
    },
    file: {
      type: Object,
      default: null
    },
    canvas_scale_local: {
      type: Number,
      default: 1
    },
    has_changed: {
      type: Boolean,
      default: false
    },
    label_list: {
      type: Array,
      default: []
    },
    draw_mode: {
      type: Boolean,
      default: true
    },
    label_file_colour_map: {
      type: Object,
      default: {}
    },
    full_file_loading: {
      type: Boolean,
      default: false
    },
    instance_template_selected: {
      type: Boolean,
      default: false
    },
    loading_instance_templates: {
      type: Boolean,
      default: false
    },
    instance_type_list: {
      type: Array,
      default: []
    },
    

            :instance_type_list="filtered_instance_type_list"
            :view_issue_mode="view_issue_mode"
            :is_keypoint_template="is_keypoint_template"
            :enabled_edit_schema="enabled_edit_schema"
            :annotation_show_on="annotation_show_on"
  },
  computed: {
    interface_type: function(): string | null {
      if (!this.working_file || !this.working_file.type) return null
      
      return this.working_file.type
    }
  }
})
</script>
