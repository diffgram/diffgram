<template>
  <v-navigation-drawer
    permanent
    left
    :style="`border-right: 1px solid #e0e0e0;border-top: 1px solid #e0e0e0; height: ${height}px`"
    :width="annotation_ui_context.current_image_annotation_ctx.label_settings.left_nav_width"
  >


    <instance_detail_list_view ref="instance_detail_list"
                               v-show="!annotation_ui_context.issues_ui_manager.show_modify_an_issue"
                               :instance_list="instance_list"
                               :video_parent_file_instance_list="video_parent_file_instance_list"
                               :instance_store="annotation_ui_context.instance_store"
                               :model_run_list="annotation_ui_context.model_run_list"
                               :label_file_colour_map="label_file_colour_map"
                               :refresh="annotation_ui_context.refresh"
                               :root_file="root_file"
                               :per_instance_attribute_groups_list="annotation_ui_context.per_instance_attribute_groups_list"
                               @toggle_instance_focus="$emit('toggle_instance_focus', $event)"
                               @show_all="$emit('focus_instance_show_all', $event)"
                               @update_canvas="$emit('update_canvas', $event)"
                               @instance_update="$emit('instance_update', $event)"
                               @global_compound_attribute_change="$emit('global_compound_attribute_change', $event)"
                               :video_mode="annotation_ui_context.current_image_annotation_ctx.video_mode"
                               :task="annotation_ui_context.task"
                               :view_only_mode="annotation_ui_context.view_only_mode"
                               :label_settings="annotation_ui_context.current_image_annotation_ctx.label_settings"
                               :label_list="label_list"
                               :project_string_id="project_string_id"
                               :global_attribute_groups_list="annotation_ui_context.global_attribute_groups_list"
                               :global_attribute_groups_list_compound="annotation_ui_context.global_attribute_groups_list_compound"
                               :schema_id="annotation_ui_context.label_schema.id"
                               :current_global_instance="current_global_instance"
                               :compound_global_instance="compound_global_instance"
                               :draw_mode="annotation_ui_context.current_image_annotation_ctx.draw_mode"
                               :current_frame="annotation_ui_context.current_image_annotation_ctx.current_frame"
                               :current_video_file_id="annotation_ui_context.working_file.id"
                               :current_label_file_id="annotation_ui_context.current_label_file ? annotation_ui_context.current_label_file.id : undefined"
                               :video_playing="annotation_ui_context.current_image_annotation_ctx.video_playing"
                               :external_requested_index="annotation_ui_context.current_image_annotation_ctx.request_change_current_instance"
                               :trigger_refresh_current_instance="annotation_ui_context.current_image_annotation_ctx.trigger_refresh_current_instance"
                               :current_file="annotation_ui_context.task ? annotation_ui_context.task : annotation_ui_context.working_file"
    >
    </instance_detail_list_view>

    <instance_history_sidepanel
      v-show="annotation_ui_context.selected_instance_for_history != undefined"
      :project_string_id="project_string_id"
      @close_instance_history_panel="$emit('close_instance_history_panel')"
      :instance="annotation_ui_context.selected_instance_for_history"
    >
    </instance_history_sidepanel>

    <v-divider></v-divider>

    <!-- <v-expansion-panels
      :accordion="true"
      :inset="false"
      :multiple="false"
      :focusable="true"
      :disabled="false"
      :flat="true"
      :hover="true"
      :tile="true"
      v-show="!annotation_ui_context.issues_ui_manager.show_modify_an_issue"
    >
      <v-expansion-panel>

        <v-expansion-panel-header
          data-cy="show_userscript_panel_button"
          class="d-flex justify-start pa-0 pr-1 align-center sidebar-accordeon-header"
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
            :create_instance="annotation_ui_context.current_image_annotation_ctx.event_create_instance"
            :current_userscript_prop="() => annotation_ui_context.current_image_annotation_ctx.get_userscript($refs.userscript)"
            :userscript_select_disabled="annotation_ui_context.current_image_annotation_ctx.userscript_select_disabled"
            :show_code_editor="!annotation_ui_context.task || !annotation_ui_context.task.id"
            :show_external_scripts="!annotation_ui_context.task || !annotation_ui_context.task.id"
            :show_save="!annotation_ui_context.task || !annotation_ui_context.task.id"
            :show_other_controls="!annotation_ui_context.task || !annotation_ui_context.task.id"
            ref="userscript"
          >
          </userscript>

        </v-expansion-panel-content>

      </v-expansion-panel>
    </v-expansion-panels> -->

    <v-expansion-panels
      v-model="annotation_ui_context.issues_ui_manager.issues_expansion_panel"
      :accordion="true"
      :inset="false"
      :multiple="false"
      :focusable="true"
      :disabled="false"
      :flat="true"
      :hover="true"
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
            {{ annotation_ui_context.issues_ui_manager.issues_list.length }}
          </v-chip>

        </v-expansion-panel-header>

        <v-expansion-panel-content>

          <standard_button
            v-if="!annotation_ui_context.issues_ui_manager.show_modify_an_issue"
            tooltip_message="New Issue"
            datacy="new_issue_in_side_panel"
            @click="annotation_ui_context.issues_ui_manager.show_modify_an_issue=true"
            icon="add"
            :icon_style="true"
            color="primary"
          >
          </standard_button>

          <create_issue_panel
            v-show="annotation_ui_context.issues_ui_manager.show_modify_an_issue && !annotation_ui_context.issues_ui_manager.current_issue"
            :project_string_id="project_string_id ? project_string_id : this.$store.state.project.current.project_string_id"
            :instance_list="instance_list"
            :task="annotation_ui_context.task"
            :file="annotation_ui_context.working_file"
            :frame_number="annotation_ui_context.current_image_annotation_ctx.video_mode ? annotation_ui_context.current_image_annotation_ctx.current_frame : undefined"
            :mouse_position="annotation_ui_context.issues_ui_manager.issue_mouse_position"
            @new_issue_created="refresh_issues_sidepanel"
            @open_side_panel="open_issue_panel"
            @close_issue_panel="close_issue_panel"
          />

          <view_edit_issue_panel
            v-if="!annotation_ui_context.current_image_annotation_ctx.loading && annotation_ui_context.issues_ui_manager.show_modify_an_issue && annotation_ui_context.issues_ui_manager.current_issue"
            :project_string_id="project_string_id ? project_string_id : this.$store.state.project.current.project_string_id"
            :task="annotation_ui_context.task"
            :instance_list="instance_list"
            :current_issue_id="annotation_ui_context.issues_ui_manager.current_issue ? annotation_ui_context.issues_ui_manager.current_issue.id : undefined"
            :file="annotation_ui_context.working_file"
            @close_view_edit_panel="close_view_edit_issue_panel"
            @start_attach_instance_edition="start_attach_instance_edition"
            @update_issues_list="update_issues_list"
            @stop_attach_instance_edition="stop_attach_instance_edition"
            @update_canvas="$emit('update_canvas')"
            ref="view_edit_issue_panel"
          />

          <!-- List -->
          <issues_sidepanel
            v-show="!annotation_ui_context.issues_ui_manager.show_modify_an_issue"
            :project_string_id="project_string_id ? project_string_id : this.$store.state.project.current.project_string_id"
            :task="annotation_ui_context.task"
            :issues_ui_manager="annotation_ui_context.issues_ui_manager"
            :file="annotation_ui_context.working_file"
            @view_issue_detail="$emit('open_view_edit_panel', $event)"
            @issues_fetched="issues_fetched"
            ref="issues_sidepanel"
          />


        </v-expansion-panel-content>

      </v-expansion-panel>
    </v-expansion-panels>

  </v-navigation-drawer>
</template>

<script lang="ts">
import Vue from "vue";
import instance_detail_list_view from "./instance_detail_list_view.vue";
import view_edit_issue_panel from "../../discussions/view_edit_issue_panel.vue";
import issues_sidepanel from "../../discussions/issues_sidepanel.vue";
import userscript from "./userscript/userscript.vue";
import {types} from "sass";
import String = types.String;
import {LabelFile} from "../../../types/label";
import {BaseAnnotationUIContext} from "../../../types/AnnotationUIContext";
import {LabelColourMap} from "../../../types/label_colour_map";
import instance_history_sidepanel from "./instance_history_sidepanel.vue";
import {Instance} from "../../vue_canvas/instances/Instance";
import create_issue_panel from "../../discussions/create_issue_panel.vue";
export default Vue.extend({
  name: "sidebar_image_annotation",
  components: {
    instance_detail_list_view,
    view_edit_issue_panel,
    issues_sidepanel,
    userscript,
    create_issue_panel,
    instance_history_sidepanel
  },
  props: {
    annotation_ui_context: {type: BaseAnnotationUIContext, required: true},
    label_file_colour_map: {type: Object as LabelColourMap, required: true},
    label_list: {type: Array as LabelFile[], required: true},
    project_string_id: {type: String, required: true},
    current_global_instance: {type: Object},
    compound_global_instance: {type: Object},
    height: {type: Number},
    root_file: {type: Object},
    instance_list: {type: Array as Instance[], required: false, default: ()=>{return[]}},
    video_parent_file_instance_list: {type: Array as Instance[], required: true, default: ()=>{return[]}},
  },
  computed: {
    userscript_select_disabled: function () {
      return this.annotation_ui_context.task && this.annotation_ui_context.task.id
    },
    my_instance_list_test: function(){
      return this.annotation_ui_context.instance_store.get_instance_list(this.annotation_ui_context.working_file.id)
    }
  },
  data: function () {
    return {

    }
  },
  mounted() {
    if (this.$refs.issues_sidepanel) {
      this.$refs.issues_sidepanel.get_issues_list()
    }
  },
  methods: {

    open_issue_panel(mouse_position) {
      // This boolean controls if issues create/edit panel is shown or hidden.
      this.annotation_ui_context.issues_ui_manager.show_modify_an_issue = true
      this.annotation_ui_context.issues_ui_manager.issue_mouse_position = mouse_position;
      this.annotation_ui_context.issues_ui_manager.issues_expansion_panel = 0;

      // Close context menu and set select instance mode
      this.annotation_ui_context.current_image_annotation_ctx.show_context_menu = false;
      this.$store.commit("set_instance_select_for_issue", true);
      // const issues_ui_mngr = this.annotation_ui_context.issues_ui_manager;
      // this.annotation_ui_context.image_annotation_ctx.issues_ui_manager = Object.create(issues_ui_mngr)
    },
    close_issue_panel() {
      this.annotation_ui_context.issues_ui_manager.show_modify_an_issue = false;
      this.$store.commit("set_instance_select_for_issue", false);
      this.annotation_ui_context.issues_ui_manager.snackbar_issues = false;
      this.annotation_ui_context.issues_ui_manager.issue_mouse_position = undefined;
      // this.clear_selected();
      this.$emit('clear_selected_instances_image')
    },
    close_view_edit_issue_panel() {
      this.annotation_ui_context.issues_ui_manager.current_issue = undefined;
      this.annotation_ui_context.issues_ui_manager.show_modify_an_issue = false;
      this.annotation_ui_context.issues_ui_manager.issue_mouse_position = undefined;
      this.annotation_ui_context.current_image_annotation_ctx.label_settings.allow_multiple_instance_select = false;
      this.$store.commit("set_view_issue_mode", false);
      this.$store.commit("set_instance_select_for_issue", false);
    },
    start_attach_instance_edition() {
      this.$store.commit("set_instance_select_for_issue", true);
      this.annotation_ui_context.issues_ui_manager.snackbar_issues = true;
    },
    update_issues_list(issue) {
      this.annotation_ui_context.issues_ui_manager.update_issue(issue);
    },
    refresh_issues_sidepanel(issue) {
      this.annotation_ui_context.issues_ui_manager.add_issue_to_list(issue);
    },
    stop_attach_instance_edition() {
      this.$store.commit("set_instance_select_for_issue", false);
      this.annotation_ui_context.issues_ui_manager.snackbar_issues = false;
    },
    issues_fetched: function (issues_list) {
      this.annotation_ui_context.issues_ui_manager.issues_list = issues_list;
    },

  },
})
</script>

<style scoped>

</style>
