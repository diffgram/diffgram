<template>
<div>
  <div style="position: relative">
    <main_menu
      :height="`${!task ? '100px' : '50px'}`"
      :show_default_navigation="!task"
    >
      <template slot="second_row">
        <audio_toolbar
          :undo_disabled="undo_disabled"
          :redo_disabled="redo_disabled"
          :has_changed="has_changed"
          :save_loading="save_loading"
          :loading="loading"
          :label_schema="label_schema"
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
          @undo="undo()"
          @redo="redo()"
        />
      </template>
    </main_menu>

    <div class="d-flex" style="width: 100%; height: 100%">
      <audio_sidebar
        :current_instance="current_instance"
        :label_file_colour_map="label_file_colour_map"
        :schema_id="label_schema.id"
        :label_list="label_list"
        :toolbar_height="`${!task ? '100px' : '50px'}`"
        :instance_list="instance_list ? instance_list.get().filter(instance => !instance.soft_delete) : []"
        :attribute_group_list_prop="label_list"
        :per_instance_attribute_groups_list="per_instance_attribute_groups_list"
        @on_select_instance="on_select_instance"
        @change_instance_label="change_instance_label"
      />
      <waveform_selector 
        v-if="current_label" 
        :current_label="current_label" 
        :audio_file="file" 
        @instance_create="instance_create"
      />
    </div>

  </div>
</div>
</template>

<script>
import audio_toolbar from './audio_toolbar'
import audio_sidebar from './audio_sidebar.vue'
import waveform_selector from './render_elements/waveform_selector.vue'
import CommandManager from "../../helpers/command/command_manager"
import InstanceList from "../../helpers/instance_list"
import History from "../../helpers/history"
import {
  CreateInstanceCommand,
  DeleteInstanceCommand,
  UpdateInstanceLabelCommand,
  UpdateInstanceAttributeCommand
} from "../../helpers/command/available_commands"
import { AudioAnnotationInstance } from "../vue_canvas/instances/AudioInstance"

export default {
  name: "audio_annotation_core",
  components:{
    audio_toolbar,
    audio_sidebar,
    waveform_selector
  },
    props: {
    file: {
      type: Object,
      default: undefined
    },
    task: {
      type: Object,
      default: undefined
    },
    job_id: {
      type: Number,
      default: undefined
    },
    label_file_colour_map: {
      type: Object,
      required: true
    },
    label_list: {
      type: Array,
      required: true
    },
    project_string_id: {
      type: String,
      required: true
    },
    global_attribute_groups_list: {
      type: Array,
      required: true
    },
    per_instance_attribute_groups_list: {
      type: Array,
      required: true
    },
    label_schema: {
      type: Object,
      default: {}
    }
  },
  data: function(){
    return{
      has_changed: false,
      view_only_mode: false,
      draw_mode: false,
      current_global_instance: null,
      request_change_current_instance: null,
      global_attribute_groups_list: [],
      instance_list: [],
      label_file_colour_map: {},
      current_label: null,
      current_instance: null,
      label_settings: {
        left_nav_width: 450
      },
      loading: false,
      save_loading: false,
      trigger_refresh_current_instance: Date.now(),
      refresh: Date.now(),
      // Command
      instance_list: undefined,
      command_manager: undefined,
      history: undefined,
    }
  },
  computed: {
    undo_disabled: function () {
      return !this.history || !this.history.undo_posible
    },
    redo_disabled: function () {
      return !this.history || !this.history.redo_posible
    }
  },
  mounted() {
      this.history = new History()
      this.command_manager = new CommandManager(this.history)
      this.instance_list = new InstanceList()
  },
  methods: {
    instance_create: function(audiosurfer_id, start_time, end_time) {
      const created_instance = new AudioAnnotationInstance()
      created_instance.create_frontend_instance(audiosurfer_id, start_time, end_time, {... this.current_label}, {})
      this.instance_list.push([created_instance])
      const command = new CreateInstanceCommand([created_instance], this.instance_list)
      this.command_manager.executeCommand(command)
      this.has_changed = true
    },
    instance_update_region: function() {},
    insatnce_update_label: function() {},
    insatnce_update_attribute: function() {},
    insatance_delete: function() {},

    focus_instance_show_all: function(){

    },
    defer_task: function(){

    },
    change_label_file: function(label_file){
      this.current_label = label_file;
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

    },
    change_instance_label: async function (event) {
      const { instance, label } = event
      const command = new UpdateInstanceLabelCommand([instance], this.instance_list)
      command.set_new_label(label)
      this.command_manager.executeCommand(command)
      this.has_changed = true
    },
    on_select_instance: function(instance) {
      this.current_instance = instance
    },
    undo: function () {
      if (!this.history.undo_posible) return;

      let undone = this.command_manager.undo();
      this.current_instance = null

      if (undone) this.has_changed = true;
    },
    redo: function () {
      if (!this.history.redo_posible) return;

      let redone = this.command_manager.redo();
      this.current_instance = null

      if (redone) this.has_changed = true;
    },
  }
}
</script>

<style scoped>

</style>
