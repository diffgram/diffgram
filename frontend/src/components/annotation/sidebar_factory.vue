<template>
  <sidebar_image_annotation
    v-if="annotation_interface === 'image_or_video'"
    :working_file="working_file"
    :instance_type="instance_type"
    :annotation_interface="annotation_interface"
    :instance_store="instance_store"
    :per_instance_attribute_groups_list="per_instance_attribute_groups_list"

    @toggle_instance_focus="$emit('toggle_instance_focus', $event)"
    @focus_instance_show_all="$emit('focus_instance_show_all', $event)"
    @update_canvas="$emit('update_canvas', $event)"
    @instance_update="$emit('instance_update', $event)"
  ></sidebar_image_annotation>
</template>

<script lang="ts">
import {File} from '../../types/files'
import {ImageLabelSettings} from "../../types/image_label_settings";
import InstanceStore from "../../helpers/InstanceStore";
import TaskPrefetcher from "../../helpers/task/TaskPrefetcher";
import {LabelFile} from "../../types/label";
import IssuesAnnotationUIManager from "./issues/IssuesAnnotationUIManager";

export default {
  name: "sidebar_factory",
  props: {
    annotation_interface: {type: String, default: undefined},
    working_file: {type: Object as File, default: undefined},
    label_settings: {type: Object as ImageLabelSettings, default: undefined},
    instance_type: {type: String, default: 'box'},
    instance_store: {type: Object as InstanceStore, default: undefined},
    model_run_list: {type: Array, default: undefined},
    label_file_colour_map: {type: Object, default: undefined},
    refresh: {type: Date, default: undefined},
    per_instance_attribute_groups_list: {type: Array, required: true},
    video_mode: {type: Boolean, required: true},
    task: {type: Object, required: true},
    view_only_mode: {type: Boolean, required: true},
    label_list: {type: Array, required: true},
    project_string_id: {type: String, required: true},
    global_attribute_groups_list: {type: Array, required: true},
    label_schema: {type: Object, required: true},
    current_global_instance: {type: Object, required: true},
    draw_mode: {type: Boolean, required: false},
    current_frame: {type: Number, required: false},
    current_label_file: {type: Object as LabelFile, required: true},
    video_playing: {type: Boolean, required: false},
    request_change_current_instance: {type: Number, required: false},
    trigger_refresh_current_instance: {type: Date, required: false},
    selected_instance_for_history: {type: Number, required: false},
    event_create_instance: {type: Number, required: false},
    get_userscript: {type: Function, required: true},
    userscript_select_disabled: {type: Boolean, required: true},
    issues_ui_manager: {type: Object as IssuesAnnotationUIManager, required: true},
  },
  data: function () {
    return {}
  },
  methods: {},
}
</script>

<style scoped>

</style>
