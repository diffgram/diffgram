<template>
<div>
  <div style="position: relative">
    <main_menu
      :height="`${!task ? '100px' : '50px'}`"
      :show_default_navigation="!task"
    >
      <template slot="second_row">
        <audio_toolbar
          :has_changed="has_changed"
          :save_loading="save_loading"
          :loading="loading"
          :project_string_id="project_string_id"
          :label_list="label_list"
          :label_file_colour_map="label_file_colour_map"
          :task="task"
          :file="file"
          @on_task_annotation_complete_and_save="on_task_annotation_complete_and_save"
          @task_update_toggle_deferred="defer_task"
          @change_label_file="change_label_file"
          @change_label_visibility="change_label_visibility"
          @change_file="change_file"
          @save="save"
          @change_task="trigger_task_change"
        />
      </template>
    </main_menu>

    <div class="d-flex" style="width: 100%; height: 100%">
      <div style="border-right: 2px solid #e0e0e0">
        <instance_detail_list_view
          :style="`width: ${label_settings.left_nav_width}px; ` "
          ref="instance_detail_list"
          :instance_list="instance_list"
          :model_run_list="[]"
          :label_file_colour_map="label_file_colour_map"
          :refresh="refresh"
          @toggle_instance_focus="focus_instance($event)"
          @show_all="focus_instance_show_all()"
          @instance_update="instance_update($event)"
          :task="task"
          :view_only_mode="view_only_mode"
          :label_settings = "label_settings"
          :label_list = "label_list"
          :global_attribute_groups_list="global_attribute_groups_list"
          :current_global_instance="current_global_instance"
          :draw_mode = "draw_mode"
          :external_requested_index="request_change_current_instance"
          :trigger_refresh_current_instance="trigger_refresh_current_instance"
          :current_file="file ? file : task"
        >
        </instance_detail_list_view>
      </div>
      <waveform_selector :audio_file="file"></waveform_selector>

    </div>

  </div>
</div>
</template>

<script>
import audio_toolbar from './audio_toolbar'
import waveform_selector from './waveform_selector'
import instance_detail_list_view from '../instance_detail_list_view'
export default {
  name: "audio_annotation_core",
  components:{
    instance_detail_list_view,
    audio_toolbar,
    waveform_selector
  },
  props: {
    project_string_id:{
      default: null
    },
    task: {
      default: null
    },
    file: {
      default: null
    },
  },
  data: function(){
    return{
      has_changed: false,
      view_only_mode: false,
      draw_mode: false,
      current_global_instance: null,
      request_change_current_instance: null,
      global_attribute_groups_list: [],
      label_list: [],
      instance_list: [],
      label_file_colour_map: {},
      label_settings: {
        left_nav_width: 450
      },
      loading: false,
      save_loading: false,
      trigger_refresh_current_instance: Date.now(),
      refresh: Date.now(),
    }
  },
  methods: {
    instance_update: function(){

    },
    focus_instance_show_all: function(){

    },
    focus_instance: function(){

    },
    defer_task: function(){

    },
    change_label_file: function(){

    },
    change_label_visibility: function(){

    },
    change_file: function(){

    },
    save: function(){

    },
    trigger_task_change: function(){

    },
    on_task_annotation_complete_and_save: function(){

    }
  }
}
</script>

<style scoped>

</style>
