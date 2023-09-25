<template>
<div :style="`height: ${sidebar_height}px `">
  <sidebar_image_annotation
    v-if="(interface_type === 'image' || interface_type === 'video')"
    :height="sidebar_height"
    :annotation_ui_context="annotation_ui_context"
    :label_file_colour_map="label_file_colour_map"
    :project_string_id="project_string_id"
    :label_list="label_list"
    :current_global_instance="current_global_instance"
    :compound_global_instance="compound_global_instance"
    :video_parent_file_instance_list="video_parent_file_instance_list"
    :instance_list="Array.isArray(instance_list) ? instance_list : []"
    :root_file="root_file"
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
    :sidebar_height="sidebar_height"
    :annotation_ui_context="annotation_ui_context"
    :label_list="label_list"
    :current_global_instance="current_global_instance"
    :compound_global_instance="compound_global_instance"
    :instance_list="instance_list && instance_list.instance_list ? instance_list.instance_list.filter(inst => !inst.soft_delete) : []"
    :label_file_colour_map="label_file_colour_map"
    :attribute_group_list_prop="label_list"
    :per_instance_attribute_groups_list="annotation_ui_context.per_instance_attribute_groups_list"
    :global_attribute_groups_list="annotation_ui_context.global_attribute_groups_list"
    :schema_id="annotation_ui_context.label_schema.id"
    :loading="annotation_ui_context.get_current_ann_ctx() ? annotation_ui_context.get_current_ann_ctx().rendering :  true"
    :current_instance="annotation_ui_context.get_current_ann_ctx() && annotation_ui_context.get_current_ann_ctx().current_instance"
    @on_select_instance="(e) => $emit('on_select_instance', e)"
    @delete_instance="(e) => $emit('on_delete_instance', e)"
    @on_instance_hover="(e) => $emit('hover_text_instance', e)"
    @on_instance_stop_hover="$emit('stop_hover_text_instance')"
    @on_update_attribute="(e, is_global) => $emit('on_update_attribute', e, is_global)"
    @change_instance_label="(e) => $emit('on_change_instance_label', e)"
    @global_compound_attribute_change="$emit('global_compound_attribute_change', $event)"
    ref="sidebar_text"
  />
  <audio_sidebar
    v-if="interface_type === 'audio'"
    :current_instance="annotation_ui_context.get_current_ann_ctx() && annotation_ui_context.get_current_ann_ctx().current_instance"
    :label_file_colour_map="label_file_colour_map"
    :schema_id="annotation_ui_context.label_schema.id"
    :label_list="label_list"
    :toolbar_height="`${!this.annotation_ui_context.task ? '100px' : '50px'}`"
    :instance_list="instance_list && instance_list.instance_list ? instance_list.instance_list.filter(inst => !inst.soft_delete) : []"
    :attribute_group_list_prop="label_list"
    :per_instance_attribute_groups_list="annotation_ui_context.per_instance_attribute_groups_list"
    :loading="false"
    :project_string_id="project_string_id"
    @on_select_instance="(e) => $emit('on_select_instance', e)"
    @change_instance_label="(e) => $emit('on_change_instance_label', e)"
    @delete_instance="(e) => $emit('on_delete_instance', e)"
    @on_update_attribute="(e, is_global) => $emit('on_update_attribute', e, is_global)"
    ref="sidebar_audio"
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
import audio_sidebar from './audio_annotation/audio_sidebar.vue'

import {Instance} from "../vue_canvas/instances/Instance";

export default Vue.extend({
  name: "sidebar_factory",
  components:{
    sidebar_image_annotation,
    text_sidebar,
    audio_sidebar
  },
  props: {
    interface_type: {type: String, required: true},
    annotation_ui_context: {type: Object as BaseAnnotationUIContext, required: true},
    label_file_colour_map: {type: Object as LabelColourMap, required: true},
    label_list: {type: Array as LabelFile[], required: true},
    project_string_id: {type: String, required: true},
    current_global_instance: {type: Object, required: false},
    compound_global_instance: {type: Object, required: false},
    instance_list: {required: false},
    video_parent_file_instance_list: {type: Array as Instance[], required: false},
    root_file: {type: Object, required: true},
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
        return this.$refs.sidebar_text
      }
      else if(this.interface_type==='text') {
        return this.$refs.sidebar_audio
      }
      // TODO: ADD OTHER INTERFACE TYPES HERE.
    },

  },
  computed: {
    sidebar_height: function(){
      if(this.annotation_ui_context.task){
        return window.innerHeight - 50;
      }
      return window.innerHeight - 100;
    }
  }
})
</script>

<style>
.v-navigation-drawer__content {
  display: flex;
  flex-direction: column;
  overflow-y: auto;
}
</style>
