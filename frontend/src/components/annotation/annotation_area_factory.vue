<template>
  <div>
    <v_error_multiple :error="error" />
    <div v-if="!interface_type || !interface_type && !initializing">
      <empty_file_editor_placeholder
        :message="`File ID: ${annotation_ui_context.working_file ? annotation_ui_context.working_file.id : 'N/A'}. File Type: ${annotation_ui_context.working_file ? annotation_ui_context.working_file.type : 'N/A'}`"
        :title="'Invalid File loaded'"
      />
    </div>
    <div v-else-if="interface_type === 'compound' && annotation_ui_context.working_file_list.length === 0 && !initializing" >
      <empty_file_editor_placeholder
        :message="'Try adding child files to this compound file.'"
        :title="'This compound file has no child files.'" />
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
    <div v-if="interface_type === 'image' || interface_type === 'video'">
      <v_annotation_core
        class="pt-1 pl-1"
        v-if="!changing_file && !changing_task && annotation_ui_context.image_annotation_ctx != undefined"
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
import empty_file_editor_placeholder from "./image_and_video_annotation/empty_file_editor_placeholder.vue"


export default Vue.extend({
  name: "annotation_area_factory",
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
    interface_type: {
      type: String,
      required: true
    },
    working_file: {
      type: Object,
      required: true
    },
    credentials_granted: {
      type: Boolean,
      required: true
    },
    annotation_ui_context: {
      type: Object,
      required: true
    },
    userscript_select_disabled: {
      type: Boolean,
      default: false
    },
    url_instance_buffer: {
      type: String || undefined || null,
      default: null
    },
    save_loading_image: {
      type: Boolean,
      default: false
    },
    submitted_to_review: {
      type: Boolean,
      default: false
    },
    annotations_loading: {
      type: Boolean,
      default: false
    },
    loading: {
      type: Boolean,
      default: false
    },
    filtered_instance_type_list_function: {
      type: Function,
      default: () => {}
    },
    get_userscript: {
      type: Function,
      default: () => {}
    },
    save_loading_frames_list: {
      type: Array,
      default: []
    },
    video_mode: {
      type: Boolean,
      default: false
    },
    go_to_keyframe_loading: {
      type: Boolean,
      default: false
    },
    has_changed: {
      type: Boolean,
      default: false
    },
    instance_buffer_metadata: {
      type: Object,
      default: {}
    },
    create_instance_template_url: {
      type: String,
      default: ''
    },
    video_parent_file_instance_list: {
      type: Array,
      default: []
    },
    has_pending_frames: {
      type: Boolean,
      default: false
    },
    instance_store: {
      type: Object,
      default: {}
    },
    label_schema: {
      type: Object || null,
      default: null
    },
    model_run_id_list: {
      type: Array,
      default: []
    },
    model_run_color_list: {
      type: Array,
      default: []
    },
    task: {
      type: Object || null,
      default: null
    },
    file: {
      type: Object,
      default: null
    },
    task_id_prop: {
      type: Number,
      default: null
    },
    request_save: {
      type: Boolean,
      default: false
    },
    accesskey: {
      type: String,
      default: 'full'
    },
    job_id: {
      type: Number,
      default: null
    },
    view_only_mode: {
      type: Boolean,
      default: false
    },
    label_list: {
      type: Array,
      default: []
    },
    label_file_colour_map: {
      type: Object,
      default: {}
    },
    enabled_edit_schema: {
      type: Boolean,
      default: false
    },
    finish_annotation_show: {
      type: Boolean,
      default: false
    },
    global_attribute_groups_list: {
      type: Array,
      default: []
    },
    per_instance_attribute_groups_list: {
      type: Array,
      default: []
    },
    task_image: {
      type: Node || null,
      default: null
    },
    task_instances: {
      type: Object,
      default: null
    },
    task_loading: {
      type: Boolean,
      default: false
    },
    initializing: {
      type: Boolean,
      default: false
    },
    changing_file: {
      type: Boolean,
      default: false
    },
    changing_task: {
      type: Boolean,
      default: false
    },
    issues_ui_manager: {
      type: Object,
      default: {}
    },
    task_error: {
      type: Object,
      default: null
    },
    error: {
      type: Object,
      default: null
    },
    draw_mode: {
      type: Boolean,
      default: true
    }
  },
  computed: {

    current_interface_ref: function () {
      if (this.interface_type === 'image' || this.interface_type === 'video') {
        return this.$refs.annotation_core
      } else if (this.interface_type === 'sensor_fusion') {
        return this.$refs.sensor_fusion_editor
      } else if (this.interface_type === 'text') {
        return this.$refs.text_annotation_core
      } else if (this.interface_type === 'geo') {
        return this.$refs.geo_annotation_core
      } else if (this.interface_type === 'audio') {
        return this.$refs.audio_annotation_core
      } else if (this.interface_type === 'compound') {
        // Not implemented yet. Will need to deduct current interface from mouse hover maybe
        return null
      }
    },
  }
})
</script>
