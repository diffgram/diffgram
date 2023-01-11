<template>
  <div>
    <div v-if="!interface_type || !interface_type && !initializing">
      <empty_file_editor_placeholder v-bind="$props" />
    </div>
    <div v-else-if="!credentials_granted && !initializing">
      <empty_file_editor_placeholder
        icon="mdi-account-cancel"
        :loading="false"
        :project_string_id="project_string_id"
        :title="`Invalid credentials`"
        :message="`You need more credentials to work on this task.`"
        :show_upload="false"
      />
    </div>
    <div v-else-if="interface_type === 'image' || interface_type === 'video'">
      <v_annotation_core
        class="pt-1 pl-1"
        v-if="!changing_file && !changing_task"
        v-bind="$props"
        v-on="$listeners"
        ref="annotation_core" 
      />
    </div>
      <div v-else-if="interface_type === 'sensor_fusion'">
        <sensor_fusion_editor
          ref="sensor_fusion_editor"
          v-bind="$props"
          v-on="$listeners"
        />
      </div>
      <div v-else-if="interface_type === 'text'">
        <text_annotation_core
          v-bind="$props"
          v-on="$listeners"
        />
      </div>
      <div v-else-if="interface_type === 'geospatial'">
        <geo_annotation_core
          v-bind="$props"
          v-on="$listeners"
        />
      </div>
      <div v-else-if="interface_type === 'audio'">
        <audio_annotation_core
          v-bind="$props"
          v-on="$listeners"
        />
      </div>
  </div>
</template>

<script lang="ts">
import Vue from "vue"
import image_and_audio_annotation_core from "./image_and_video_annotation/annotation_core.vue"
import text_annotation_core from "./text_annotation/text_annotation_core.vue"
import geo_annotation_core from "./geo_annotation/geo_annotation_core.vue"
import audio_annotation_core from "./audio_annotation/audio_annotation_core.vue"
import sensor_fusion_annotation_core from './3d_annotation/sensor_fusion_editor.vue' 
import empty_file_editor_placeholder from "./image_and_video_annotation/empty_file_editor_placeholder.vue";

export default Vue.extend({
  name: "annotation_interface",
  components: {
    image_and_audio_annotation_core,
    text_annotation_core,
    geo_annotation_core,
    audio_annotation_core,
    sensor_fusion_annotation_core,
    empty_file_editor_placeholder
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
    userscript_select_disabled: {},
    url_instance_buffer: {},
    save_loading_image: {},
    submitted_to_review: {},
    annotations_loading: {},
    loading: {},
    filtered_instance_type_list_function: {},
    get_userscript: {},
    save_loading_frames_list: {},
    video_mode: {},
    go_to_keyframe_loading: {},
    has_changed: {},
    instance_buffer_metadata: {},
    create_instance_template_url: {},
    video_parent_file_instance_list: {},
    has_pending_frames: {},
    instance_store: {},
    label_schema: {},
    model_run_id_list: {},
    model_run_color_list: {},
    task: {},
    file: {},
    task_id_prop: {},
    request_save: {},
    accesskey: {},
    job_id: {},
    view_only_mode: {},
    label_list: {},
    label_file_colour_map: {},
    enabled_edit_schema: {},
    finish_annotation_show: {},
    global_attribute_groups_list: {},
    per_instance_attribute_groups_list: {},
    task_image: {},
    task_instances: {},
    task_loading: {},
    credentials_granted: {},
    initializing: {},
    changing_file: {},
    changing_task: {},
  },
  computed: {
    interface_type: function() {
      if (!this.working_file || !this.working_file.type) return null
      
      return this.working_file.type
    }
  }
})
</script>
