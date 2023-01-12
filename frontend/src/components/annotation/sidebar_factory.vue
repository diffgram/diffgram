<template>
  <sidebar_image_annotation
    v-if="annotation_interface === 'image_or_video'"
    :annotation_ui_context="annotation_ui_context"
    :label_file_colour_map="label_file_colour_map"
    :project_string_id="project_string_id"
    :label_list="label_list"
    :current_global_instance="current_global_instance"
    :instance_list="instance_list"
    @toggle_instance_focus="$emit('toggle_instance_focus', $event)"
    @focus_instance_show_all="$emit('focus_instance_show_all', $event)"
    @update_canvas="$emit('update_canvas', $event)"
    @instance_update="$emit('instance_update', $event)"
    @open_view_edit_panel="$emit('open_view_edit_panel', $event)"
    @clear_selected_instances_image="$emit('clear_selected_instances_image', $event)"
  ></sidebar_image_annotation>
</template>

<script lang="ts">
import Vue from "vue";
import {BaseAnnotationUIContext} from "../../types/AnnotationUIContext";
import {LabelColourMap} from "../../types/label_colour_map";
import {LabelFile} from "../../types/label";
import sidebar_image_annotation from './image_and_video_annotation/sidebar_image_annotation.vue'
import {Instance} from "../vue_canvas/instances/Instance";
export default Vue.extend({
  name: "sidebar_factory",
  components:{
    sidebar_image_annotation
  },
  props: {
    annotation_interface: {type: String, required: true},
    annotation_ui_context: {type: Object as BaseAnnotationUIContext, required: true},
    label_file_colour_map: {type: Object as LabelColourMap, required: true},
    label_list: {type: Array as LabelFile[], required: true},
    project_string_id: {type: String, required: true},
    current_global_instance: {type: Object, required: false},
    instance_list: {type: Array as Instance[], required: false},
  },
  data: function () {
    return {}
  },
  methods: {},
})
</script>

<style scoped>

</style>
