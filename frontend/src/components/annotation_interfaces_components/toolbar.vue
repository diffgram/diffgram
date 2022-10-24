<template>
  <div style="display: flex; flex-direction: row">
    <standard_button
      icon_style
      icon="mdi-undo"
      tooltip_message="undo"
    />
    <standard_button
      icon_style
      icon="mdi-redo"
      tooltip_message="redo"
    />
    <v-divider vertical />
  </div>
</template>

<script lang="ts">
import Vue from "vue";
import label_select_annotation from "../label/label_select_annotation.vue";
import label_schema_selector from "../label/label_schema_selector.vue";
import file_meta_data_card from "../annotation/file_meta_data_card.vue";
import time_tracker from "../task/time_track/time_tracker.vue";
import task_relations_card from "../annotation/task_relations_card.vue";
import file_relations_card from "../annotation/file_relations_card.vue";
import task_meta_data_card from "../annotation/task_meta_data_card.vue";
import hotkeys from "../annotation/hotkeys.vue";
import task_status from "../annotation/task_status.vue"
import Guided_1_click_mode_selector from "../instance_templates/guided_1_click_mode_selector.vue";
import Standard_button from "../base/standard_button.vue";

export default Vue.extend({
  name: "toolbar",
  components: {
    Guided_1_click_mode_selector,
    label_select_annotation,
    label_schema_selector,
    file_meta_data_card,
    time_tracker,
    file_relations_card,
    task_meta_data_card,
    task_relations_card,
    hotkeys,
    task_status,
    Standard_button
  },
  props: {
    project_string_id: {},
    label_schema: {
      required: true
    },
    label_settings: {
      default: null,
    },
    task: {},
    file: {},
    canvas_scale_local: {},
    label_list: {},
    label_file_colour_map: {},
    show_toolbar: {
      default: true,
      type: Boolean,
    },
    height: {
      default: null,
    },
    command_manager: {
      default: null,
    },
    save_loading: {
      default: false,
    },
    loading: {
      default: false,
    },
    view_only_mode: {
      default: false,
    },
    show_undo_redo: {
      default: true,
      type: Boolean,
    },
    has_changed: {
      default: false,
    },
    draw_mode: {
      default: true,
    },
    full_file_loading: {},
    annotations_loading: {},
    instance_template_selected: {},

    loading_instance_templates: {},
    instance_type_list: {},
    view_issue_mode: {},
    is_keypoint_template: {},
    enabled_edit_schema: {
      default: false,
      type: Boolean,
    },
    annotation_show_on: {
      type: Boolean,
    },
  },
  data() {
    return {
      label_settings_local: {
        canvas_scale_global_is_automatic: true,
      },
      draw_mode_local: true,
      loading_instance_type: true,
      instance_type: "box",
      numberValue: 1,
      duration_labels: ["1", "2", "3", "4", "5"],
    };
  },
  watch: {
    label_settings_local: {
      deep: true,
      handler: function (event) {
        this.$emit("label_settings_change", event);
      },
    },
    label_settings(event) {
      this.label_settings_local = event;
    },
    draw_mode(event) {
      this.draw_mode_local = event;
    },
  },
  async mounted() {
    this.label_settings_local = this.$props.label_settings;
    this.draw_mode_local = this.$props.draw_mode;


    this.loading_instance_type = false;
  },

  computed: {
    mode_text: function () {
      if (this.draw_mode_local == true) {
        return "Drawing";
      } else {
        return "Editing";
      }
    },
    anootations_show_icon: function () {
      if (this.annotation_show_on) return "pause";
      return "play_circle";
    },
  },
  methods: {
    set_instance_type: function(inst_type){
      this.instance_type = inst_type
    },
    on_mode_set: function(mode){
      this.$emit('keypoints_mode_set', mode)
    },
    set_mode: function(mode){
      if(!this.$refs.keypoints_mode_selector){
        return
      }
      if(mode === '1_click'){
        this.$refs.keypoints_mode_selector.set_active(0)
      }
      else if(mode === 'guided'){
        this.$refs.keypoints_mode_selector.set_active(1)
      }
    },
    go_to_job: function(){
      if(this.task.job.type === 'examination'){
        this.$router.push(`/${this.project_string_id}/examination/${this.task.job_id}`)
      }
      else{
        this.$router.push(`/job/${this.task.job_id}`)
      }

    },
    on_change_canvas_scale_global: function () {
      this.label_settings_local.canvas_scale_global_is_automatic = false;
      this.$emit(
        "canvas_scale_global_changed",
        this.label_settings_local.canvas_scale_global_setting
      );
    },
    trigger_smooth_canvas_events: function () {
      this.$emit('smooth_canvas_changed', this.label_settings_local.smooth_canvas),
      this.$store.commit('set_user_setting', [
        'smooth_canvas',
        this.label_settings_local.smooth_canvas,
      ])
    },
    filter_reset: function () {
      this.label_settings_local.filter_brightness = 100;
      this.label_settings_local.filter_contrast = 100;
      this.label_settings_local.filter_grayscale = 0;

      this.label_settings_local.smooth_canvas = true
      this.trigger_smooth_canvas_events()
    },
  },
});
</script>
