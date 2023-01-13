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
          :instance_type_list="filtered_instance_type_list"
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
      type: Object,
      required: true
    },
    interface_type: {
      type: String,
      default: null
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
    view_issue_mode: {
      type: Boolean,
      default: false
    },
    is_keypoint_template: {
      type: Boolean,
      default: false
    },
    enabled_edit_schema: {
      type: Boolean,
      default: false
    },
    annotation_show_on: {
      type: Boolean,
      default: false
    },
    filtered_instance_type_list_function: {
      type: Function,
      default: () => {}
    }
  },
  data() {
    return {
      instance_type_list: [
        {name: "box", display_name: "Box", icon: "mdi-checkbox-blank"},
        {name: "polygon", display_name: "Polygon", icon: "mdi-vector-polygon"},
        {name: "tag", display_name: "Tag", icon: "mdi-tag"},
        {name: "point", display_name: "Point", icon: "mdi-circle-slice-8"},
        {name: "line", display_name: "Fixed Line", icon: "mdi-minus"},
        {name: "cuboid", display_name: "Cuboid 2D", icon: "mdi-cube-outline"},
        {name: "ellipse", display_name: "Ellipse & Circle", icon: "mdi-ellipse-outline"},
        {name: "curve", display_name: "Curve Quadratic", icon: "mdi-chart-bell-curve-cumulative"},
      ],
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
