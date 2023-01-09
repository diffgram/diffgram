<template>
  <v-navigation-drawer
    permanent
    left
    style="border-right: 1px solid #e0e0e0;border-top: 1px solid #e0e0e0; height: 100%"
    v-if="!annotation_interface === 'image_or_video'"
    :width="label_settings.left_nav_width"
  >


    <instance_detail_list_view ref="instance_detail_list"
                               v-if=""
                               :instance_list="instance_list"
                               :instance_store="instance_store"
                               :model_run_list="model_run_list"
                               :label_file_colour_map="label_file_colour_map"
                               :refresh="refresh"
                               :per_instance_attribute_groups_list="per_instance_attribute_groups_list"
                               @toggle_instance_focus="$emit('toggle_instance_focus', $event)"
                               @show_all="$emit('focus_instance_show_all', $event)"
                               @update_canvas="$emit('update_canvas', $event)"
                               @instance_update="$emit('instance_update', $event)"
                               :video_mode="video_mode"
                               :task="task"
                               :view_only_mode="view_only_mode"
                               :label_settings="label_settings"
                               :label_list="label_list"
                               :project_string_id="project_string_id"
                               :global_attribute_groups_list="global_attribute_groups_list"
                               :schema_id="label_schema.id"
                               :current_global_instance="current_global_instance"
                               :draw_mode="draw_mode"
                               :current_frame="current_frame"
                               :current_video_file_id="working_file.id"
                               :current_label_file_id="current_label_file ? current_label_file.id : undefined"
                               :video_playing="video_playing"
                               :external_requested_index="request_change_current_instance"
                               :trigger_refresh_current_instance="trigger_refresh_current_instance"
                               :current_file="task ? task : working_file"
    >
    </instance_detail_list_view>

    <instance_history_sidepanel
      v-show="selected_instance_for_history != undefined"
      :project_string_id="project_string_id"
      @close_instance_history_panel="$emit('close_instance_history_panel')"
      :instance="selected_instance_for_history"
    >
    </instance_history_sidepanel>

    <v-divider></v-divider>

    <v-expansion-panels
      :accordion="true"
      :inset="false"
      :multiple="false"
      :focusable="true"
      :disabled="false"
      :flat="true"
      :hover="false"
      :tile="true"
    >
      <v-expansion-panel>

        <v-expansion-panel-header
          data-cy="show_userscript_panel_button"
          class="d-flex justify-start pa-0 pr-1 align-center"
          style="border-top: 1px solid #e0e0e0;border-bottom: 1px solid #e0e0e0">

          <v-icon left class="ml-4 flex-grow-0" color="primary" size="18">
            mdi-language-javascript
          </v-icon>

          <h4>Scripts</h4>

          <v-spacer></v-spacer>

        </v-expansion-panel-header>

        <v-expansion-panel-content>

          <userscript
            :project_string_id_prop="project_string_id"
            :create_instance="event_create_instance"
            :current_userscript_prop="() => get_userscript($refs.userscript)"
            :userscript_select_disabled="userscript_select_disabled"
            :show_code_editor="!task || !task.id"
            :show_external_scripts="!task || !task.id"
            :show_save="!task || !task.id"
            :show_other_controls="!task || !task.id"
            ref="userscript"
          >
          </userscript>

        </v-expansion-panel-content>

      </v-expansion-panel>
    </v-expansion-panels>

    <v-expansion-panels
      v-model="issues_expansion_panel"
      :accordion="true"
      :inset="false"
      :multiple="false"
      :focusable="true"
      :disabled="false"
      :flat="true"
      :hover="false"
      :tile="true"
    >
      <v-expansion-panel>

        <v-expansion-panel-header
          data-cy="show_issues_panel_button"
          class="d-flex justify-start pa-0 sidebar-accordeon-header align-center">

          <v-icon left class="ml-5 flex-grow-0" color="primary" size="18">
            mdi-comment-multiple
          </v-icon>

          <h4>Issues</h4>

          <v-spacer></v-spacer>

          <v-chip x-small class="d-flex justify-center flex-grow-0">
            {{ issues_list.length }}
          </v-chip>

        </v-expansion-panel-header>

        <v-expansion-panel-content>

          <standard_button
            v-if="show_modify_an_issue != true"
            tooltip_message="New Issue"
            datacy="new_issue_in_side_panel"
            @click="show_modify_an_issue=true"
            icon="add"
            :icon_style="true"
            color="primary"
          >
          </standard_button>

          <create_issue_panel
            v-show="show_modify_an_issue == true && !current_issue"
            :project_string_id="project_string_id ? project_string_id : this.$store.state.project.current.project_string_id"
            :instance_list="instance_list"
            :task="task"
            :file="working_file"
            :frame_number="this.video_mode ? this.current_frame : undefined"
            :mouse_position="issue_mouse_position"
            @new_issue_created="refresh_issues_sidepanel"
            @open_side_panel="open_issue_panel"
            @close_issue_panel="close_issue_panel"
          />

          <view_edit_issue_panel
            v-if="!loading"
            v-show="show_modify_an_issue == true && current_issue"
            :project_string_id="project_string_id ? project_string_id : this.$store.state.project.current.project_string_id"
            :task="task"
            :instance_list="instance_list"
            :current_issue_id="current_issue ? current_issue.id : undefined"
            :file="working_file"
            @close_view_edit_panel="close_view_edit_issue_panel"
            @start_attach_instance_edition="start_attach_instance_edition"
            @update_issues_list="update_issues_list"
            @stop_attach_instance_edition="stop_attach_instance_edition"
            @update_canvas="update_canvas"
            ref="view_edit_issue_panel"
          />

          <!-- List -->
          <issues_sidepanel
            :project_string_id="project_string_id ? project_string_id : this.$store.state.project.current.project_string_id"
            :task="task"
            :file="working_file"
            @view_issue_detail="open_view_edit_panel"
            @issues_fetched="issues_fetched"
            ref="issues_sidepanel"
          />


        </v-expansion-panel-content>

      </v-expansion-panel>
    </v-expansion-panels>

  </v-navigation-drawer>
</template>

<script lang="ts">
import instance_detail_list_view from "./instance_detail_list_view";
import {File} from '../../types/files'
import {ImageLabelSettings} from "../../types/image_label_settings";
import {types} from "sass";
import String = types.String;
import InstanceStore from "../../helpers/InstanceStore";
import {LabelFile} from "../../types/label";

export default {
  name: "sidebar_image_annotation",
  comments: {
    instance_detail_list_view: instance_detail_list_view
  },
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
    draw_mode: {type: Boolean, required: true},
    current_frame: {type: Number, required: true},
    current_label_file: {type: Object as LabelFile, required: true},
    video_playing: {type: Boolean, required: false},
    request_change_current_instance: {type: Number, required: true},
    trigger_refresh_current_instance: {type: Date, required: false},
    selected_instance_for_history: {type: Date, required: true},
    event_create_instance: {type: Object, required: true},
  },
  computed: {
    instance_list: function () {
      return this.instance_store.get_instance_list(this.working_file.id)
    }
  },
  data: function () {
    return {}
  },
  methods: {},
}
</script>

<style scoped>

</style>
