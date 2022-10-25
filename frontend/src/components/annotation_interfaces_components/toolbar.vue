<template>
  <div class="toolbar-container">
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

    <v-divider vertical class="toolbar-divider" />
    <label_schema_selector
      ref="label_scehma_selector"
      :project_string_id="project_string_id"
      :initial_schema="label_schema"
      @on_focus="set_typing_state(true)"
      @on_blue="set_typing_state(false)"
      @change="change_label_schema"
    />
    <div class="toolbar_space" />
    <label_select_annotation
      :project_string_id="project_string_id"
      :label_file_list="label_list"
      :schema_id="label_schema.id"
      :request_refresh_from_project="true"
      :show_visibility_toggle="true"
      :is_typing_or_menu_open="$store.state.user.is_typing_or_menu_open"
      @on_focus="set_typing_state(true)"
      @on_blue="set_typing_state(false)"
      @change="change_label_file"
      @update_label_file_visible="update_label_file_visibility"
    />
    <div class="toolbar_space" />
    <diffgram_select
      v-model="instance_type"
      v-if="instance_type_list"
      data_cy="instance-type-select"
      label="New Instance Type"
      class="select-width"
      :item_list="instance_type_list"
      :disabled="loading || loading_instance_templates || view_only_mode"
      @change="change_instance_type"
    />
    <v-divider vertical class="toolbar-divider" />

    <v-switch :label="mode_text" />

    <v-divider vertical class="toolbar-divider" />

    <standard_button
      text_style
      icon="mdi-content-save"
      button_message="save"
    />

    <v-divider vertical class="toolbar-divider" />
    <standard_button
      icon_style
      icon="mdi-arrow-left-circle"
      tooltip_message="Prevous file"
    />
    <standard_button
      icon_style
      icon="mdi-arrow-right-circle"
      tooltip_message="Next file"
    />
    <v-divider vertical class="toolbar-divider" />

    <standard_button
      icon_style
      icon="mdi-keyboard-settings"
      tooltip_message="Hotkeys"
    />
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
import instance_type_list, { InstanceType } from "./instance_types"

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
  },
  props: {
    project_string_id: {
      type: String,
      required: true
    },
    label_schema: {
      type: Object,
      required: true
    },
    label_settings: {
      type: Object,
      default: null,
    },
    task: {
      type: Object,
      default: null
    },
    file: {
      type: Object,
      default: null
    },
    label_list: {
      type: Array,
      default: []
    },
    show_toolbar: {
      default: true,
      type: Boolean,
    },
    loading: {
      type: Boolean,
      default: false,
    },
    view_only_mode: {
      type: Boolean,
      default: false,
    },
    draw_mode: {
      type: Boolean,
      default: true
    },
    loading_instance_templates: {
      type: Boolean,
      default: false
    },
    annotation_show_on: {
      type: Boolean,
      default:  false
    },
  },
  data() {
    return {
      label_settings_local: {
        canvas_scale_global_is_automatic: true,
      } as Object,
      draw_mode_local: true as Boolean,
      loading_instance_type: true as Boolean,
      instance_type: "box" as String,
      instance_type_list: null as Array<InstanceType>,
      numberValue: 1 as Number,
      duration_labels: [
        "1", 
        "2", 
        "3", 
        "4", 
        "5"
      ] as Array<String>,
    };
  },
  created() {
    this.instance_type_list = instance_type_list.image_video
  },
  watch: {
    label_settings_local: {
      deep: true,
      handler: function (new_value) {
        this.$emit("label_settings_change", new_value);
      },
    },
    label_settings(new_nalue) {
      this.label_settings_local = new_nalue;
    },
    draw_mode(new_nalue) {
      this.draw_mode_local = new_nalue;
    },
  },
  async mounted() {
    this.label_settings_local = this.$props.label_settings;
    this.draw_mode_local = this.$props.draw_mode;


    this.loading_instance_type = false;
  },

  computed: {
    mode_text: function (): string {
      if (this.draw_mode_local == true) {
        return "Drawing";
      } else {
        return "Editing";
      }
    }
  },
  methods: {
    // REFACTORED
    set_typing_state: function(state: boolean): void {
      this.$store.commit('set_user_is_typing_or_menu_open', state)
    },
    change_label_schema: function(label_schema: Object): void {
      this.$emit('change_label_schema', label_schema)
    },
    change_label_file: function(label_file: Object): void {
      this.$emit('change_label_file', label_file)
    },
    update_label_file_visibility: function(label_file: Object): void {
      this.$emit('update_label_file_visibility', label_file)
    },
    change_instance_type: function(instance_type: string): void {
      this.$emit('change_instance_type', instance_type)
    }
    ///
  },
});
</script>

<style scoped>
.toolbar-container {
  display: flex; 
  flex-direction: row;
  align-items: center;
  border-bottom: 1px solid rgba(0,0,0,.12);
}

.toolbar-divider {
  margin-right: 10px;
  margin-left: 10px
}

.toolbar_space {
  width: 10px;
}

.select-width {
  max-width: 200px;
}
</style>
