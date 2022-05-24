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
        @delete_instance="delete_instance"
        @on_update_attribute="update_attribute"
      />
      <waveform_selector 
        v-if="current_label && instance_list" 
        :force_watch_trigger="force_watch_trigger"
        :instance_list="instance_list.get()"
        :current_label="current_label" 
        :audio_file="file" 
        @instance_create_update="instance_create_update"
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
  UpdateInstanceAttributeCommand,
  UpdateInstanceAudioCoordinatesCommand
} from "../../helpers/command/available_commands"
import { AudioAnnotationInstance } from "../vue_canvas/instances/AudioInstance"
import { deferTask, finishTaskAnnotation } from "../../services/tasksServices"
import { getInstanceList, postInstanceList } from "../../services/instanceList";

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
      force_watch_trigger: 0,
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

    this.initialize_interface_data()
    this.start_autosave()
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
    instance_create_update: function(audiosurfer_id, start_time, end_time) {
      let instance;
      let command;

      const instance_already_exists = this.instance_list.get().find(inst => inst.audiosurfer_id === audiosurfer_id && !inst.soft_delete)

      if (!instance_already_exists) {
        instance = new AudioAnnotationInstance()
        instance.create_frontend_instance(audiosurfer_id, start_time, end_time, {... this.current_label}, {})
        this.instance_list.push([instance])
        command = new CreateInstanceCommand([instance], this.instance_list)
      } else {
        command = new UpdateInstanceAudioCoordinatesCommand([instance_already_exists], this.instance_list)
        command.set_new_geo_coords(start_time, end_time)
      }
      this.command_manager.executeCommand(command)
      this.has_changed = true
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
    },
    change_file(direction, file) {
      if (direction == "next" || direction == "previous") {
        this.$emit("request_file_change", direction, file);
      }
    },
    save: async function(){
      this.has_changed = false
      this.save_loading = true
      let url;
      if (this.task && this.task.id) {
        url = `/api/v1/task/${this.task.id}/annotation/update`;
      } else {
        url = `/api/project/${this.project_string_id}/file/${this.file.id}/annotation/update`
      }

      const res = await postInstanceList(url, this.instance_list.get_all())
      const { added_instances } = res
      this.instance_list.get_all().map(instance => {
        const instance_uuid = instance.creation_ref_id
        const updated_instance = added_instances.find(added_instance => added_instance.creation_ref_id === instance_uuid)
        if (updated_instance) {
            instance.id = updated_instance.id
        }
      })
      this.save_loading = false
      console.log("Saved")
    },
    trigger_task_change: async function (direction, assign_to_user = false) {
      if (this.has_changed) {
        await this.save();
        await this.save();
      }
      this.$emit("request_new_task", direction, this.task, assign_to_user);
    },
    on_task_annotation_complete_and_save: async function () {
      await this.save();
      await this.save();
      const response = await finishTaskAnnotation(this.task.id);
      const new_status = response.data.task.status;
      this.task.status = new_status;
      if (new_status !== "complete") {
        this.submitted_to_review = true;
      }
      if (this.$props.task && this.$props.task.id) {
        this.save_loading_image = false;
        this.trigger_task_change("next", this.$props.task, true);
      }
    },
    update_attribute: function(attribute) {
      const command = new UpdateInstanceAttributeCommand([this.instance_list.get().find(inst => inst.creation_ref_id === this.current_instance.creation_ref_id)], this.instance_list)
      command.set_new_attribute(attribute[0].id, {...attribute[1]})
      this.command_manager.executeCommand(command)
      this.has_changed = true
      this.update_trigger()
    },
    delete_instance: async function (instance) {
      const delete_command = new DeleteInstanceCommand([instance], this.instance_list)
      this.command_manager.executeCommand(delete_command)
      this.has_changed = true
      this.update_trigger()
    },
    change_instance_label: async function (event) {
      const { instance, label } = event
      const command = new UpdateInstanceLabelCommand([instance], this.instance_list)
      command.set_new_label(label)
      this.command_manager.executeCommand(command)
      this.has_changed = true
      this.update_trigger()
    },
    on_select_instance: function(instance) {
      this.current_instance = instance
    },
    undo: function () {
      if (!this.history.undo_posible) return;

      let undone = this.command_manager.undo();
      this.update_trigger()
      this.current_instance = null

      if (undone) this.has_changed = true;
    },
    redo: function () {
      if (!this.history.redo_posible) return;

      let redone = this.command_manager.redo();
      this.update_trigger()
      this.current_instance = null

      if (redone) this.has_changed = true;
    },
    start_autosave: function () {
      this.interval_autosave = setInterval(
        this.detect_is_ok_to_save,
          15 * 1000
        );
    },
    detect_is_ok_to_save: async function () {
      if (this.has_changed) {
        await this.save();
      }
    },
  }
}
</script>

<style scoped>

</style>
