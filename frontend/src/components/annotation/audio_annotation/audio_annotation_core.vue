<template>
<div>
  <div style="position: relative; width: 100%; height: 100%">
    <div class="d-flex" style="width: 100%; height: 100%">
      <waveform_selector
        v-if="instance_list"
        :force_watch_trigger="force_watch_trigger"
        :instance_list="instance_list.get()"
        :current_label="current_label"
        :audio_file="working_file"
        :invisible_labels="invisible_labels"
        @asign_wavesurfer_id="asign_wavesurfer_id"
        @instance_create="instance_create"
        @instance_update="instance_update"
      />
    </div>

  </div>
</div>
</template>

<script>
import audio_toolbar from './audio_toolbar'
import audio_sidebar from './audio_sidebar.vue'
import waveform_selector from './render_elements/waveform_selector.vue'
import InstanceList from "../../../helpers/instance_list"
import History from "../../../helpers/history"
import {
  CreateInstanceCommand,
  DeleteInstanceCommand,
  UpdateInstanceLabelCommand,
  UpdateInstanceAttributeCommand,
  UpdateInstanceAudioCoordinatesCommand
} from "../../../helpers/command/available_commands"
import { AudioAnnotationInstance } from "../../vue_canvas/instances/AudioInstance"
import { deferTask, finishTaskAnnotation } from "../../../services/tasksServices"
import { getInstanceList, postInstanceList } from "../../../services/instanceList";
import { BaseAnnotationUIContext } from "../../../types/AnnotationUIContext";

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
    },
    instance_store: {
      type: Object,
      required: true
    },
    working_file: {
      type: Object,
      default: undefined
    },
    annotation_ui_context: {
      type: Object,
      required: true
    },
  },
  data: function(){
    return{
      has_changed: false,
      view_only_mode: false,
      draw_mode: false,
      current_global_instance: null,
      request_change_current_instance: null,
      instance_list: [],
      current_label: null,
      current_instance: null,
      label_settings: {
        left_nav_width: 450
      },
      loading: false,
      save_loading: false,
      trigger_refresh_current_instance: Date.now(),
      refresh: Date.now(),
      force_watch_trigger: 0,
      invisible_labels: [],
      // Command
      instance_list: undefined,
    }
  },
  watch: {
    instance_list: function (newVal) {
      if (this.working_file.type === "audio" && newVal) {
        this.instance_store.set_instance_list(this.working_file.id, newVal)
        this.instance_store.set_file_type(this.working_file.id, this.working_file.type)
        this.$emit('instance_list_updated', newVal, this.working_file.id, this.working_file.type)
      }
    },
    'annotation_ui_context.current_label_file': function (label) {
      this.current_label = label
    },
  },
  mounted() {
    this.instance_list = new InstanceList()

    if (this.annotation_ui_context) {
      this.current_label = this.annotation_ui_context.current_label_file
    }

    this.initialize_interface_data()
    this.start_autosave()
    this.hot_key_listeners()
  },
  beforeDestroy() {
    this.remove_listeners()
  },
  methods: {
    initialize_interface_data: async function() {
            let url;
            let payload;
            if (this.task && this.task.id) {
                url = `/api/v1/task/${this.task.id}/annotation/list`;
                payload = {
                    directory_id: this.$store.state.project.current_directory.directory_id,
                    job_id: this.job_id,
                    attached_to_job: this.task.file.attached_to_job,
                    task_child_file_id: this.working_file.id,
                }
            } else {
                url = `/api/project/${this.$props.project_string_id}/file/${this.$props.file.id}/annotation/list`;
                payload = {}
            }
            const raw_instance_list = await getInstanceList(url, payload)

            // Get instances from teh backend and render them
            const initial_instances = raw_instance_list.map(instance_object => {
              const { id, start_time, end_time, label_file, attribute_groups } = instance_object
              const instance = new AudioAnnotationInstance();
              instance.create_instance(id, start_time, end_time, label_file, attribute_groups)

              return instance
            })

            this.instance_list.push(initial_instances)
            this.update_trigger()
        },
    update_trigger: function() {
      this.force_watch_trigger += 1
    },
    asign_wavesurfer_id: function(instance_id, audiosurfer_id) {
      this.instance_list.get_all().map(instance => {
        if (instance.id === instance_id) {
            instance.audiosurfer_id = audiosurfer_id
        }
      })
    },
    instance_create(audiosurfer_id, start_time, end_time) {
      let instance;
      let command;

      const existing_instance = this.instance_list.get().find(inst => inst.audiosurfer_id === audiosurfer_id && !inst.soft_delete)

      if (existing_instance) {
        return
      }

      instance = new AudioAnnotationInstance()
      instance.create_frontend_instance(audiosurfer_id, start_time, end_time, {... this.current_label}, {})
      this.instance_list.push([instance])
      command = new CreateInstanceCommand([instance], this.instance_list)

      this.annotation_ui_context.command_manager.executeCommand(command)
      this.$emit('set_has_changed', true)
      this.update_trigger()
    },
    instance_update(audiosurfer_id, start_time, end_time) {

      let instance;
      let command;

      const existing_instance = this.instance_list.get().find(inst => inst.audiosurfer_id === audiosurfer_id && !inst.soft_delete)

      if (!existing_instance) {
        return
      }

      command = new UpdateInstanceAudioCoordinatesCommand([existing_instance], this.instance_list)
      command.set_new_geo_coords(start_time, end_time)

      this.annotation_ui_context.command_manager.executeCommand(command)
      this.$emit('set_has_changed', true)
      this.update_trigger()
    },
    defer_task: async function () {
      await deferTask({
        task_id: this.task.id,
        mode: "toggle_deferred"
      })
      this.trigger_task_change('next')
      this.update_trigger()
    },
    change_label_file: function(label_file){
      this.current_label = label_file;
    },
    change_label_visibility: async function (label) {
      if (label.is_visible) {
        this.invisible_labels = this.invisible_labels.filter(label_id => label_id !== label.id)
      } else {
        this.invisible_labels.push(label.id)
      }
      this.update_trigger()
    },
    change_file(direction, file) {
      if (direction == "next" || direction == "previous") {
        this.$emit("request_file_change", direction, file);
      }
    },
    update_attribute: function(attribute) {
      const command = new UpdateInstanceAttributeCommand([this.instance_list.get().find(inst => inst.creation_ref_id === this.current_instance.creation_ref_id)], this.instance_list)
      command.set_new_attribute(attribute[0].id, {...attribute[1]})
      this.annotation_ui_context.command_manager.executeCommand(command)
      this.has_changed = true
      this.update_trigger()
    },
    delete_instance: async function (instance) {
      const delete_command = new DeleteInstanceCommand([instance], this.instance_list)
      this.annotation_ui_context.command_manager.executeCommand(delete_command)
      this.has_changed = true
      this.$emit('set_has_changed', true)
      this.update_trigger()
    },
    change_instance_label: async function (event) {
      const { instance, label } = event
      const command = new UpdateInstanceLabelCommand([instance], this.instance_list)
      command.set_new_label(label)
      this.annotation_ui_context.command_manager.executeCommand(command)
      this.has_changed = true
      this.update_trigger()
    },
    on_select_instance: function(instance) {
      this.current_instance = instance
    },
    start_autosave: function () {
      this.interval_autosave = setInterval(
        this.detect_is_ok_to_save,
          15 * 1000
        );
    },
    detect_is_ok_to_save: async function () {
      if (this.has_changed) {
        this.$emit('save');
      }
    },
    hot_key_listeners: function() {
      window.removeEventListener("keydown", this.keydown_event_listeners)
      window.addEventListener("keydown", this.keydown_event_listeners)
    },
    remove_listeners: function() {
      window.removeEventListener("keydown", this.keydown_event_listeners)
    },
    keydown_event_listeners: async function(e) {
      if (e.keyCode === 83) {
        this.$emit('save')
      }
    },
    on_change_label_schema: function(schema){
      this.$emit('change_label_schema', schema)
    },
  }
}
</script>

<style scoped>

</style>
