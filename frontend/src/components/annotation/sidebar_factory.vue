<template>
<div>
  <sidebar_image_annotation
    v-if="(interface_type === 'image' || interface_type === 'video')"
    :annotation_ui_context="annotation_ui_context"
    :label_file_colour_map="label_file_colour_map"
    :project_string_id="project_string_id"
    :label_list="label_list"
    :current_global_instance="current_global_instance"
    :compound_global_instance="compound_global_instance"
    :video_parent_file_instance_list="video_parent_file_instance_list"
    :instance_list="instance_list"
    @toggle_instance_focus="$emit('toggle_instance_focus', $event)"
    @focus_instance_show_all="$emit('focus_instance_show_all', $event)"
    @update_canvas="$emit('update_canvas', $event)"
    @instance_update="$emit('instance_update', $event)"
    @open_view_edit_panel="$emit('open_view_edit_panel', $event)"
    @clear_selected_instances_image="$emit('clear_selected_instances_image', $event)"
    @global_compound_attribute_change="$emit('global_compound_attribute_change', $event)"
    ref="sidebar_image"
  />
  <text_sidebar
    v-if="interface_type === 'text'"
    :project_string_id="project_string_id"
    :annotation_ui_context="annotation_ui_context"
    :label_list="label_list"
    :current_global_instance="current_global_instance"
    :compound_global_instance="compound_global_instance"
    :instance_list="instance_list"

    :loading="rendering"
    :label_file_colour_map="label_file_colour_map"
    :toolbar_height="`${!task ? '100px' : '50px'}`"
    :schema_id="label_schema.id"
    :current_instance="current_instance"
    :attribute_group_list_prop="label_list"
    :per_instance_attribute_groups_list="per_instance_attribute_groups_list"
    :global_attribute_groups_list="global_attribute_groups_list"
    @on_select_instance="on_select_instance"
    @delete_instance="delete_instance"
    @on_instance_hover="on_instance_hover"
    @on_instance_stop_hover="on_instance_stop_hover"
    @on_update_attribute="on_update_attribute"
    @change_instance_label="change_instance_label"
    ref="sidebar_text"
  />
</div>
</template>

<script lang="ts">
import Vue from "vue";
import {BaseAnnotationUIContext} from "../../types/AnnotationUIContext";
import {LabelColourMap} from "../../types/label_colour_map";
import {LabelFile} from "../../types/label";
import sidebar_image_annotation from './image_and_video_annotation/sidebar_image_annotation.vue'
import text_sidebar from './text_annotation/text_sidebar.vue'
import {Instance} from "../vue_canvas/instances/Instance";

export default Vue.extend({
  name: "sidebar_factory",
  components:{
    sidebar_image_annotation,
    text_sidebar
  },
  props: {
    interface_type: {
      type: String, 
      required: true
    },
    annotation_ui_context: {
      type: Object as BaseAnnotationUIContext, 
      required: true
    },
    label_file_colour_map: {
      type: Object as LabelColourMap, 
      required: true
    },
    label_list: {
      type: Array as LabelFile[], 
      required: true
    },
    project_string_id: {
      type: String, 
      required: true
    },
    current_global_instance: {
      type: Object, 
      required: false
    },
    compound_global_instance: {
      type: Object, 
      required: false
    },
    instance_list: {
      type: Array as Instance[], 
      required: false
    },
    video_parent_file_instance_list: {
      type: Array as Instance[], 
      required: false
    },
  },
  data: function () {
    return {}
  },
  methods: {
    get_current_sidebar_ref: function(){
      if(this.interface_type === 'image' || this.interface_type === 'video'){
        return this.$refs.sidebar_image
      }
      else if(this.interface_type === 'text') {
        return this.$refs.sidebar_image
      }
      // TODO: ADD OTHER INTERFACE TYPES HERE.
    }
  },
})
</script>

<style scoped>

</style>
