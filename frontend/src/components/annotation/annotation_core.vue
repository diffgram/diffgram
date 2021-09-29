<template>
  <div id="annotation_core">


    <div style="position: relative">


      <main_menu :height="`${show_default_navigation ? '100px' : '50px'}`"

                 :show_default_navigation="show_default_navigation">

        <template slot="second_row" >

          <toolbar :height="50"
                   :command_manager="command_manager"
                   :save_loading="this.video_mode ? this.save_loading_frame[this.current_frame] : this.save_loading_image"
                   :annotations_loading="annotations_loading"
                   :loading="loading"
                   :view_only_mode="view_only_mode"
                   :label_settings="label_settings"
                   :project_string_id="project_string_id"
                   :task="task"
                   :file="file"
                   :canvas_scale_local="canvas_scale_local"
                   :has_changed="has_changed"
                   :label_list="label_list"
                   :draw_mode="draw_mode"
                   :label_file_colour_map="label_file_colour_map"
                   :full_file_loading="full_file_loading"
                   :instance_template_selected="instance_template_selected"
                   :instance_type="instance_type"
                   :loading_instance_templates="loading_instance_templates"
                   :instance_type_list="instance_type_list"
                   :view_issue_mode="view_issue_mode"
                   :is_keypoint_template="is_keypoint_template"
                   @label_settings_change="label_settings = $event, refresh = Date.now()"
                   @change_label_file="change_current_label_file_template($event)"
                   @update_label_file_visibility="update_label_file_visible($event)"
                   @change_instance_type="change_instance_type($event)"
                   @edit_mode_toggle="edit_mode_toggle($event)"
                   @undo="undo()"
                   @redo="redo(), refresh = Date.now()"
                   @save="save()"
                   @change_file="change_file($event)"
                   @change_task="trigger_task_change($event, task)"
                   @next_issue_task="next_issue_task(task)"
                   @refresh_all_instances="refresh_all_instances"
                   @task_update_toggle_deferred="task_update('toggle_deferred')"
                   @complete_task="complete_task()"
                   @clear__new_and_no_ids="clear__new_and_no_ids()"
                   @new_tag_instance="insert_tag_type()"
                   @replace_file="$emit('replace_file', $event)"
                   @open_instance_template_dialog="open_instance_template_dialog()"
                   @copy_all_instances="copy_all_instances"

          >
          </toolbar>



        </template>

      </main_menu>

      <!-- Errors / info -->
      <v-alert v-if="task_error.task_request"
               type="info">
        {{task_error.task_request}}
      </v-alert>

      <v_error_multiple :error="save_error">
      </v_error_multiple>
      <v_error_multiple :error="save_multiple_frames_error">
      </v_error_multiple>
      <v_error_multiple :error="save_warning" type="warning" data-cy="save_warning">
      </v_error_multiple>
      <div fluid v-if="display_refresh_cache_button">
        <v-btn small color="warning" @click="regenerate_file_cache" :loading="regenerate_file_cache_loading">
          <v-icon>mdi-refresh</v-icon>
          Refresh File Data
        </v-btn>
      </div>
      <v_error_multiple :error="error">
      </v_error_multiple>


      <v_error_multiple :error="instance_buffer_error">
      </v_error_multiple>


    </div>
    <v-snackbar
      v-if="snackbar_merge_polygon"
      v-model="snackbar_merge_polygon"
      :multi-line="true"
      :timeout="-1"
    >
      Please select the Polygons to merge with.

      <template v-slot:action="{ attrs }">
        <v-btn
          color="red"
          text
          v-bind="attrs"
          @click="cancel_merge"
        >
         Cancel
        </v-btn>
        <v-btn
          :disabled="instances_to_merge.length === 0"
          color="success"
          text
          v-bind="attrs"
          @click="merge_polygons"
        >
          Merge Polygons
        </v-btn>
      </template>
    </v-snackbar>
    <v-snackbar
      v-if="snackbar_issues"
      v-model="snackbar_issues"
      :multi-line="true"
      :timeout="-1"
    >
      Please select the instances to attach to the issue.

      <template v-slot:action="{ attrs }">
        <v-btn
          color="red"
          text
          v-bind="attrs"
          @click="done_selecting_instaces_issues"
        >
          Ok.
        </v-btn>
      </template>
    </v-snackbar>

    <v-snackbar
      v-if="show_custom_snackbar"
      v-model="show_custom_snackbar"
      :multi-line="true"
      :timeout="-1"
    >
      {{snackbar_message}}

      <template v-slot:action="{ attrs }">
        <v-btn
          color="red"
          text
          v-bind="attrs"
          @click="show_custom_snackbar = false"
        >
          Ok.
        </v-btn>
      </template>
    </v-snackbar>


    <v-snackbar
      v-if="show_snackbar_auto_border"
      v-model="show_snackbar_auto_border"
      :multi-line="true"
      :timeout="-1"
    >
      Select the second point of the same polygon for autobordering (or press "x" key to cancel)

      <template v-slot:action="{ attrs }">
        <v-btn
          color="red"
          text
          v-bind="attrs"
          @click="show_snackbar_auto_border = false"
        >
          Ok.
        </v-btn>
      </template>
    </v-snackbar>
    <v-snackbar
      v-if="show_snackbar_paste"
      v-model="show_snackbar_paste"
      :multi-line="true"
    >
      {{snackbar_paste_message}}

      <template v-slot:action="{ attrs }">
        <v-btn
          color="red"
          text
          v-bind="attrs"
          @click="show_snackbar_paste = false"
        >
          Ok.
        </v-btn>
      </template>
    </v-snackbar>

    <v-sheet style="outline: none" >

      <v-layout style="outline: none">




        <!-- Left nav -->
        <v-navigation-drawer permanent
                             left
                             v-if="!error_no_permissions.data"
                             :width="label_settings.left_nav_width"
        >

          <v-alert v-if="$store.state.user.settings.studio_box_info == true &&
                    file != undefined"
                   dismissible
                   @input="$store.commit('set_user_setting', ['studio_box_info', false])"
                   type="info"
                   :value="instance_type == 'box'">
            Two click mode: Click and release first point, draw, click second point.
          </v-alert>

          <!-- This could use a lot of improvement -->
          <div v-if="instance_type == 'polygon'">
            <v-alert dismissible type="info" v-model="alert_info_drawing">
              To complete polygon click first point again,
              or <kbd>Enter</kbd> key,
              or hover in turbo mode.
            </v-alert>
          </div>

          <instance_detail_list_view  class="pl-4 pr-4"
                                      ref="instance_detail_list"
                                      v-if="!task_error.task_request"
                                      :instance_list="instance_list"
                                      :model_run_list="model_run_list"
                                      :label_file_colour_map="label_file_colour_map"
                                      :refresh="refresh"
                                      @toggle_instance_focus="focus_instance($event)"
                                      @show_all="focus_instance_show_all()"
                                      @update_canvas="update_canvas"
                                      @instance_update="instance_update($event)"
                                      :video_mode="video_mode"
                                      :task="task"
                                      :view_only_mode="view_only_mode"
                                      :label_settings = "label_settings"
                                      :label_list = "label_list"
                                      :draw_mode = "draw_mode"
                                      :current_frame = "current_frame"
                                      :current_video_file_id = "current_video_file_id"
                                      :current_label_file_id = "current_label_file_id"
                                      :video_playing="video_playing"
                                      :external_requested_index="request_change_current_instance"
                                      :trigger_refresh_current_instance="trigger_refresh_current_instance"
                                      :current_file="file ? file : task"
          >
          </instance_detail_list_view>


          <instance_history_sidepanel v-show="show_instance_history"
                                      :project_string_id="project_string_id"
                                      @close_instance_history_panel="close_instance_history_panel"
                                      :instance="selected_instance_for_history">

          </instance_history_sidepanel>
          <create_issue_panel :project_string_id="project_string_id ? project_string_id : this.$store.state.project.current.project_string_id"
                              v-show="show_issue_panel == true && !current_issue"
                              :instance_list="instance_list"
                              :task="task"
                              :file="file"
                              :frame_number="this.video_mode ? this.current_frame : undefined"
                              :mouse_position="issue_mouse_position"
                              @new_issue_created="refresh_issues_sidepanel"
                              @open_side_panel="open_issue_panel"
                              @close_issue_panel="close_issue_panel"
          ></create_issue_panel>
          <view_edit_issue_panel
            v-if="!loading"
            v-show="show_issue_panel == true && current_issue"
            :project_string_id="project_string_id ? project_string_id : this.$store.state.project.current.project_string_id"
            :task="task"
            :instance_list="instance_list"
            :current_issue_id="current_issue ? current_issue.id : undefined"
            :file="file"
            @close_view_edit_panel="close_view_edit_issue_panel"
            @start_attach_instance_edition="start_attach_instance_edition"
            @update_issues_list="update_issues_list"
            @stop_attach_instance_edition="stop_attach_instance_edition"
            @update_canvas="update_canvas"
            ref="view_edit_issue_panel"
          ></view_edit_issue_panel>


          <v-card-title >
            <v-icon left
                    color="primary"
                    size="28">mdi-language-javascript</v-icon>
            UserScripts
            <v-spacer></v-spacer>
            <v-btn data-cy="show_userscript_panel_button"
                   @click="userscript_minimized=!userscript_minimized"
                   v-if="userscript_minimized" icon>
              <v-icon>mdi-chevron-down</v-icon>
            </v-btn>
            <v-btn @click="userscript_minimized=!userscript_minimized"
                   v-if="!userscript_minimized" icon>
              <v-icon>mdi-chevron-up</v-icon>
            </v-btn>
          </v-card-title>

          <userscript
            v-show="!userscript_minimized"
            :project_string_id_prop="project_string_id"
            :create_instance="event_create_instance"
            :current_userscript_prop="get_userscript()"
            :userscript_select_disabled="userscript_select_disabled()"
            :show_code_editor="!task || !task.id"
            :show_external_scripts="!task || !task.id"
            :show_save="!task || !task.id"
            :show_other_controls="!task || !task.id"
            ref="userscript"
          >
          </userscript>

          <issues_sidepanel
            :minimized="minimize_issues_sidepanel"
            :project_string_id="project_string_id ? project_string_id : this.$store.state.project.current.project_string_id"
            :task="task"
            :file="file"
            @view_issue_detail="open_view_edit_panel"
            @issues_fetched="issues_fetched"
            @minimize_issues_panel="minimize_issues_sidepanel = true"
            @maximize_issues_panel="minimize_issues_sidepanel = false"
            ref="issues_sidepanel"
          ></issues_sidepanel>

        </v-navigation-drawer>


        <!-- TODO would want to think a bit about how to block scrolling
          / keep other things locked at top...

        We have the class for padding here so that it doesn't add the extra scroll bar

       TODO think about detecting max height from remaining space between menu and bottom.


	      * There's not really a super obvious good way to do that, since if we have the scroll on the other thing that could be full too...
		  * Could detect if scrolled out all the way, and then scroll the page instead...

       The problem if we have
       ' style="overflow-y:auto; max-height: 900px" ' on here
       is that the video sequence gets gobbled up in this

       -->
        <v-container v-if="error_no_permissions.data">
          <v_error_multiple  class="ma-auto" :error="error_no_permissions"></v_error_multiple>
          <v-container class="d-flex">
            <v-btn @click="go_to_login" v-if="!this.$store.state.user.logged_in" type="primary" color="primary" class="mr-4"> <v-icon>mdi-login-variant</v-icon>Login</v-btn>
            <v-btn  v-if="this.$store.state.user.logged_in" @click="go_to_projects" type="primary" color="primary"> <v-icon>mdi-folder-move</v-icon>Change Project</v-btn>

          </v-container>
        </v-container>
        <div id="annotation" tabindex="0"
             v-if="!error_no_permissions.data">

          <!-- Must wrap canvas to detect events in this context
      Careful, the slider needs to be in this context too
      in order for the canvas render to detect it

      -->

          <div  contenteditable="true"  id="canvas_wrapper" style="position: relative;"

                @mousemove="mouse_move"
                @mousedown="mouse_down"
                @dblclick="double_click"
                @mouseup="mouse_up"
                @contextmenu="contextmenu"
                :style="canvas_style">

            <!-- Diffgram loading loading your data -->
            <v-fade-transition :hide-on-leave="true">
              <v-container  v-show="show_place_holder" style="width: 100%">
                <v-img
                  src="https://storage.googleapis.com/diffgram_public/app/Empty_state_card.svg" alt="" style="max-width: 100%; width:100%"></v-img>
                <!-- https://storage.googleapis.com/diffgram_public/app/Copy-of-Loading-Placeholder.png -->
              </v-container>
            </v-fade-transition>
            <autoborder_avaiable_alert
              :x_position="canvas_alert_x"
              :y_position="canvas_alert_y"
              ref="autoborder_alert"
            >

            </autoborder_avaiable_alert>

            <ghost_canvas_available_alert
              :x_position="canvas_alert_x"
              :y_position="canvas_alert_y"
              ref="ghost_canvas_available_alert"
            >

            </ghost_canvas_available_alert>

            <canvas
              data-cy="canvas"
              ref="canvas"
              v-show="!show_place_holder"
              id="my_canvas"
              v-canvas:cb="onRendered"
              :height="canvas_height_scaled"
              :width="canvas_width_scaled"
              :canvas_transform="canvas_transform">


              <v_bg :image="html_image"
                    :current_file="file"
                    :refresh="refresh"
                    @update_canvas="update_canvas"
                    :canvas_filters="canvas_filters"
                    :ord="1"
                    :annotations_loading="any_loading"
              >
              </v_bg>

              <!-- Important, needs at least 1 non dictionary var to trigger
          reactive changes. ie :x = mouse_position.x -->

              <target_reticle   :ord="2"
                                :x="mouse_position.x"
                                :y="mouse_position.y"
                                :mouse_position="mouse_position"
                                :height="canvas_height"
                                :width="canvas_width"
                                :show="show_target_reticle"
                                :target_colour="current_label_file ? current_label_file.colour : undefined"
                                :text_color="this.$get_sequence_color(this.current_instance.sequence_id)"
                                :target_text="this.current_instance.number"
                                :target_type="target_reticle_type"
                                :canvas_transform="canvas_transform"
                                :reticle_size="label_settings.target_reticle_size"
              >
              </target_reticle>

              <!-- Current file -->
              <canvas_instance_list :ord="3"
                                    :instance_list="instance_list"
                                    :default_instance_opacity="default_instance_opacity"
                                    :vertex_size="label_settings.vertex_size"
                                    :cuboid_corner_move_point="cuboid_corner_move_point"
                                    :video_mode="video_mode"
                                    :auto_border_polygon_p1="auto_border_polygon_p1"
                                    :auto_border_polygon_p2="auto_border_polygon_p2"
                                    :issues_list="issues_list"
                                    :current_frame="current_frame"
                                    :label_settings="label_settings"
                                    :current_instance="current_instance"
                                    :is_actively_drawing="is_actively_drawing"
                                    :refresh="refresh"
                                    :draw_mode="draw_mode"
                                    :mouse_position="mouse_position"
                                    @instance_hover_update="instance_hover_update($event[0], $event[1], $event[2], $event[3])"
                                    @cuboid_face_hover_update="cuboid_face_hover_update"
                                    @issue_hover_update="issue_hover_update"
                                    :canvas_transform="canvas_transform"
                                    :show_annotations="show_annotations"
                                    :annotations_loading="annotations_loading"
                                    :label_file_colour_map="label_file_colour_map"
                                    :instance_focused_index="instance_focused_index"
                                    :hidden_label_id_list="hidden_label_id_list"
                                    :is_actively_resizing="is_actively_resizing"
                                    :emit_instance_hover="!draw_mode || emit_instance_hover"
              >
              </canvas_instance_list>


              <ghost_instance_list_canvas
                :ord="4"
                :show="label_settings.show_ghost_instances"
                :instance_list="ghost_instance_list"
                :vertex_size="label_settings.vertex_size"
                :video_mode="video_mode"
                :current_frame="current_frame"
                :label_settings="label_settings"
                :is_actively_drawing="is_actively_drawing"
                :refresh="refresh"
                :draw_mode="draw_mode"
                :mouse_position="mouse_position"
                :canvas_transform="canvas_transform"
                :show_annotations="show_annotations"
                :annotations_loading="annotations_loading"
                :label_file_colour_map="label_file_colour_map"
                :hidden_label_id_list="hidden_label_id_list"
                :is_actively_resizing="is_actively_resizing"
                :emit_instance_hover="true"
                @instance_hover_update="ghost_instance_hover_update($event[0], $event[1], $event[2])"
              >
              </ghost_instance_list_canvas>




              <!-- Careful, must have this object exist
                  prior to loading instance list otherwise it won't update
                  If there are no instance sit doesn't render anything so that's ok...-->
              <canvas_instance_list v-if="gold_standard_file"
                                    :ord="4"
                                    :vertex_size="label_settings.vertex_size"
                                    :default_instance_opacity="default_instance_opacity"
                                    :cuboid_corner_move_point="cuboid_corner_move_point"
                                    :mode="'gold_standard'"
                                    :instance_list="gold_standard_file.instance_list"
                                    :auto_border_polygon_p1="auto_border_polygon_p1"
                                    :auto_border_polygon_p2="auto_border_polygon_p2"
                                    :video_mode="video_mode"
                                    :is_actively_drawing="is_actively_drawing"
                                    :current_frame="current_frame"
                                    :issues_list="issues_list"
                                    :label_settings="label_settings"
                                    :current_instance="current_instance"
                                    :refresh="refresh"
                                    :draw_mode="draw_mode"
                                    :mouse_position="mouse_position"
                                    :canvas_transform="canvas_transform"
                                    :show_annotations="show_annotations"
                                    :annotations_loading="annotations_loading"
                                    :label_file_colour_map="label_file_colour_map"
                                    :is_actively_resizing="is_actively_resizing"
                                    :hidden_label_id_list="hidden_label_id_list"
              >
              </canvas_instance_list>

              <canvas_current_instance  :ord="5"
                                        :current_instance="current_instance"
                                        :mouse_position="mouse_position"
                                        :canvas_transform="canvas_transform"
                                        :draw_mode="draw_mode"
                                        :is_actively_drawing="is_actively_drawing"
                                        :label_file_colour_map="label_file_colour_map">

              </canvas_current_instance>
              <current_instance_template
                :ord="6"
                :current_instance_template="current_instance_template"
                :vertex_size="label_settings.vertex_size"
                :instance_template_start_point="instance_template_start_point"
                :instance_template_draw_started="instance_template_draw_started"
                :mouse_position="mouse_position"
                :canvas_transform="canvas_transform"
                :draw_mode="draw_mode"
                :is_actively_drawing="is_actively_drawing"
                :label_file_colour_map="label_file_colour_map">

              </current_instance_template>

            </canvas>
            <polygon_borders_context_menu
              :show_context_menu="show_polygon_border_context_menu"
              :mouse_position="mouse_position"
              :project_string_id="project_string_id"
              @start_auto_bordering="perform_auto_bordering"
              @close_context_menu="show_polygon_border_context_menu = false"
            ></polygon_borders_context_menu>
            <context_menu :mouse_position="mouse_position"
                          :show_context_menu="show_context_menu"
                          :instance_clipboard="instance_clipboard"
                          :draw_mode="draw_mode"
                          :selected_instance_index="selected_instance_index"
                          :project_string_id="project_string_id"
                          :polygon_point_hover_index="polygon_point_hover_index"
                          :task="task"
                          :instance_hover_index="instance_hover_index"
                          :hovered_figure_id="hovered_figure_id"
                          :instance_list="instance_list"
                          :sequence_list="sequence_list_local_copy"
                          :video_mode="video_mode"
                          @instance_update="instance_update($event)"
                          @share_dialog_open="open_share_dialog"
                          @open_issue_panel="open_issue_panel"
                          @on_click_polygon_unmerge="polygon_unmerge"
                          @on_click_polygon_merge="start_polygon_select_for_merge"
                          @delete_polygon_point="polygon_delete_point"
                          @copy_instance="on_context_menu_copy_instance"
                          @paste_instance="paste_instance"
                          @paste_instance_on_next_frames="paste_instance"
                          @create_instance_template="create_instance_template"
                          @open_instance_history_panel="show_instance_history_panel"
                          @close_instance_history_panel="show_instance_history_panel"
                          ref="context_menu"
                          @share_dialog_close="close_share_dialog"
                          @close_context_menu="show_context_menu = false"
                          @hide_context_menu="hide_context_menu" />
          </div>

          <v_video  v-if="video_mode"
                    :style="style_max_width"
                    v-show="!show_place_holder"
                    class="pb-0"
                    :current_video="current_video"
                    :video_mode="video_mode"
                    :player_height="'80px'"
                    :parent_save="this.detect_is_ok_to_save"
                    :video_primary_id="'video_primary'"
                    @playing="video_playing = true"
                    @pause="video_playing = false"
                    @seeking_update="seeking_update($event)"
                    :project_string_id="project_string_id"
                    @change_frame_from_video_event="change_frame_from_video_event($event)"
                    @video_animation_unit_of_work="video_animation_unit_of_work($event)"
                    @video_current_frame_guess="current_frame = parseInt($event)"
                    @slide_start="detect_is_ok_to_save()"
                    @request_save="detect_is_ok_to_save()"
                    @go_to_keyframe="go_to_key_frame_handler()"
                    @set_canvas_dimensions="set_canvas_dimensions()"
                    @update_canvas="update_canvas"
                    :current_video_file_id="current_video_file_id"
                    :video_pause_request="video_pause"
                    :video_play_request="video_play"
                    :task="task"
                    :loading="any_loading"
                    :view_only_mode="view_only_mode"
                    :has_changed="has_changed"
                    :canvas_width_scaled="canvas_width_scaled"
                    ref="video_controllers"
          >
          </v_video>


          <v_sequence_list
            v-show="!show_place_holder"
            :video_mode="video_mode"
            class="pl-4"
            :project_string_id="project_string_id ? project_string_id : this.$props.project_string_id"
            :view_only_mode="view_only_mode"
            :current_video_file_id="current_video_file_id"
            :current_frame="current_frame"
            :label_file_id="current_label_file_id"
            :current_sequence_annotation_core_prop="current_sequence_annotation_core_prop"
            @highest_sequence_number="highest_sequence_number = $event"
            @current_sequence_changed="current_sequence_from_sequence_component = $event"
            @loading_sequences="set_loading_sequences"
            @sequence_list="sequence_list_local_copy = $event"
            :task="task"
            :current_label_file="current_label_file"
            :video_playing="video_playing"
            :force_new_sequence_request="force_new_sequence_request"
            :label_file_list="label_list"
            :request_clear_sequence_list_cache="request_clear_sequence_list_cache"
            :label_settings="label_settings"
            ref="sequence_list"
          >
          </v_sequence_list>


        </div>
      </v-layout>
    </v-sheet>

    <!-- Right Side navigation -->
    <!--
    <v-navigation-drawer right
                          absolute
                          permanent
                          v-if="!error_no_permissions.data"
                          :width="right_nav_width"
                          >

        <v-alert type="info" v-if="render_mode == 'home'" dismissible>
          All Labels are shown here for viewing existing instances
          on files. Only the labels chosen at the Start will
          be available to annotators.
        </v-alert>

        <v_labels_view
                         v-if="label_settings.show_list == true &&
                                !task_error.task_request && !error_no_permissions.data"
                         :project_string_id="project_string_id"
                         @change_label_file_function="change_current_label_file_template($event)"
                         :loading="loading"
                         @request_boxes_refresh="request_boxes_refresh"
                         @update_label_file_visible="update_label_file_visible($event)"
                         :video_mode="video_mode"
                         :view_only_mode="view_only_mode"
                         :instance_type="instance_type"
                         :push_label_file_colour_map="label_file_colour_map"
                         :with_next_instance_buttons="video_mode"
                         :push_label_list="label_list"
                         :task="task"
                         :video_playing="video_playing"
                         :show_visibility_toggle="true"
                         @get_next_instance="request_next_instance"
        >
        </v_labels_view>


  </v-navigation-drawer>
  -->

    <!-- I would like to have a second sheet here for video stuff
     but wondering if we should just attach the video thing to the image
     This may need lot of fiddling to get it to load right under other sheet
     -->
    <!--
  <v-bottom-sheet :value="true">

    <h2 class="text-center"> BOTTOM </h2>

  </v-bottom-sheet>
  -->


    <!-- Media core -->

    <!--
    CAUTION: We still need this to render behind the scences
      to get data for other stuff even if we don't show it.

      no-click-animation:
          Disables the bounce effect when clicking outside of a
          v-dialog's content when using the persistent prop.

      persistent:
          Clicking outside of the element will not deactivate it.

    This can't be in the "absolute components"

    https://vuetifyjs.com/en/components/bottom-sheets

      TODO explore 'fullscreen' flag
      may be useful if more files...

      https://github.com/vuetifyjs/vuetify/issues/8640
      needs :retain-focus="false" (but shouldn't)

    -->




    <instance_template_creation_dialog
      :project_string_id="project_string_id"
      :instance_template="current_instance_template"
      ref="instance_template_creation_dialog"
    ></instance_template_creation_dialog>
    <v-snackbar v-model="snackbar_warning"
                v-if="snackbar_warning"
                top
                :timeout="5000"
                color="warning">
      {{ snackbar_warning_text }}
      <v-btn color="primary"
             text
             @click="snackbar_warning = false">
        Close
      </v-btn>
    </v-snackbar>

    <v-snackbar v-model="snackbar_success"
                v-if="snackbar_success"
                top
                :timeout="2000"
                color="success">
      {{ snackbar_success_text }}
    </v-snackbar>

    <v-alert type='info'
             v-if="file && file.type =='text'">
      Text Preview Coming Soon - Export or See 3rd Party Link In Task Template
    </v-alert>

  </div>
</template>

<script lang="ts">
  // @ts-nocheck
  import moment from 'moment'
  import axios from 'axios';
  import Vue from 'vue';
  import instance_detail_list_view from './instance_detail_list_view'
  import autoborder_avaiable_alert from './autoborder_avaiable_alert'
  import ghost_canvas_available_alert from './ghost_canvas_available_alert'
  import canvas_current_instance from '../vue_canvas/current_instance'
  import canvas_instance_list from '../vue_canvas/instance_list'
  import ghost_instance_list_canvas from '../vue_canvas/ghost_instance_list'
  import instance_history_sidepanel from '../annotation/instance_history_sidepanel'
  import v_bg from '../vue_canvas/v_bg'
  import v_text from '../vue_canvas/v_text'
  import target_reticle from '../vue_canvas/target_reticle'
  import task_status_icons from '../regular_concrete/task_status_icons'
  import context_menu from '../context_menu/context_menu.vue';
  import polygon_borders_context_menu from '../context_menu/polygon_borders_context_menu.vue';
  import issues_sidepanel from '../discussions/issues_sidepanel.vue';
  import current_instance_template from '../vue_canvas/current_instance_template.vue';
  import instance_template_creation_dialog from '../instance_templates/instance_template_creation_dialog';
  import create_issue_panel from '../discussions/create_issue_panel.vue';
  import view_edit_issue_panel from '../discussions/view_edit_issue_panel.vue';
  import { ellipse } from '../vue_canvas/ellipse.js';
  import {CommandManagerAnnotationCore} from './annotation_core_command_manager.js'
  import {CreateInstanceCommand} from './commands/create_instance_command.js'
  import {UpdateInstanceCommand} from './commands/update_instance_command.js'
  import {AnnotationCoreInteractionGenerator} from '../vue_canvas/interactions/AnnotationCoreInteractionGenerator'
  import { polygon } from '../vue_canvas/polygon.js';
  import { v4 as uuidv4 } from 'uuid';
  import { cloneDeep } from 'lodash';
  import { KeypointInstance } from '../vue_canvas/instances/KeypointInstance';
  import userscript from './userscript/userscript.vue';
  import toolbar from './toolbar.vue'
  import { sha256 } from 'js-sha256';
  import stringify  from 'json-stable-stringify';
  import PropType from 'vue'
  import {InstanceContext} from "../vue_canvas/instances/InstanceContext";
  import {CanvasMouseTools} from "../vue_canvas/CanvasMouseTools";
  import pLimit from 'p-limit';
  Vue.prototype.$ellipse = new ellipse();
  Vue.prototype.$polygon = new polygon();


  /**
   * @vue-prop {string} project_string_id - Project id
   * @vue-prop {number} job_id - Job id
   * @vue-prop {object} job - An instance of a job
   * @vue-data {number} context_menu_hover_index - Instance index of hovered object in context_menu
   * @vue-data {boolean} show_context_menu - Flag to show or hide context_menu
   * @vue-event {boolean} hide_context_menu - Hides the visible context menu
   * @vue-event {boolean} context_menu_hover - Sets context_menu_hover_index when mousing over an instance object in canvas
   */

  export default Vue.extend( {
      name: 'annotation_core',
      components: {
        create_issue_panel,
        instance_detail_list_view,
        autoborder_avaiable_alert,
        instance_template_creation_dialog,
        instance_history_sidepanel,
        polygon_borders_context_menu,
        view_edit_issue_panel,
        issues_sidepanel,
        canvas_current_instance,
        current_instance_template,
        canvas_instance_list,
        ghost_instance_list_canvas,
        v_bg,
        v_text,
        target_reticle,
        task_status_icons,
        context_menu,
        userscript,
        toolbar,
        ghost_canvas_available_alert
      },
      props: {
        'project_string_id': {
          default: null,
          type: String
        },
        // TODO review this being a prop...
        'job_id': {
          default: null
        },
        'job': {
          default: null
        },
        'task': {
          default: null
        },
        'label_file_colour_map': {},
        'label_list': {},
        'task_mode_prop': {
          default: null
        },
        'request_save': {},
        'annotator_email': {},
        'file': {
          default: {
            image: {
            }
          }
        },
        'model_run_id_list': {
          default: null
        },
        'model_run_color_list':{
          default: null
        },
        'current_version_prop': {},

        'view_only_mode': {
          default: false
        }
      },
      watch: {
        file: {
          handler(newVal, oldVal){
            if(newVal != oldVal){
              this.on_change_current_file();
            }
          },
        },
        task: {
          handler(newVal, oldVal){
            if(newVal != oldVal){
              this.on_change_current_task();
            }
          }
        },
        model_run_id_list(newVal, oldVal){
          if(newVal && newVal.length > 0){
            this.fetch_model_run_list();
          }
          else{
            this.model_run_list = [];
          }

        },
        mouse_computed(newval, oldval){
          // We don't want to create a new object here since the reference is used on all instance types.
          // If we create a new object we'll lose the reference on our class InstanceTypes
          this.mouse_down_delta_event.x = parseInt(newval.delta_x - oldval.delta_x)
          this.mouse_down_delta_event.y = parseInt(newval.delta_y - oldval.delta_y)
        },

        // This is in part when annotation_core is used by say verison viewer
        // should we be watching current_file_prop?
        instance_select_for_issue(newval, oldval) {
          if(newval){
            this.update_canvas();
            this.snackbar_issues = true;
            this.draw_mode = false;
            this.label_settings.allow_multiple_instance_select = true;
          }
          else{
            this.snackbar_issues = false;
          }
        },
        instance_select_for_merge(newval, oldval) {
          if(newval){
            this.update_canvas();
            this.snackbar_merge_polygon = true;
            this.draw_mode = false;
            this.instances_to_merge = [];
            this.label_settings.allow_multiple_instance_select = true;
          }
          else{
            this.snackbar_merge_polygon = false;
            this.label_settings.allow_multiple_instance_select = false;
            this.instances_to_merge = [];
            this.clear_selected();

          }
        },
        current_version_prop() {
          this.current_version = this.current_version_prop
          this.get_media()
        },
        request_save: function (bool) {
          if (bool == true) {
            this.save()
          }

        },
        '$route': 'page_refresh',
        draw_mode: function () {

          this.polygon_point_hover_index = null

          this.clear_selected()

        },
        show_issue_panel: function () {
          if (this.show_issue_panel == true) {
            this.label_settings.show_ghost_instances = false
            this.label_settings.ghost_instances_closed_by_open_view_edit_panel = true
          } else {
            if (this.label_settings.ghost_instances_closed_by_open_view_edit_panel == true) {
              this.label_settings.show_ghost_instances = true
              this.label_settings.ghost_instances_closed_by_open_view_edit_panel = false
            }
          }
        }
      },

      // data()   comment is here for searching
      data() {
        return {

          instance_rotate_control_mouse_hover: null,

          snackbar_paste_message: '',
          ghost_instance_hover_index: null,
          default_instance_opacity: 0.25,
          model_run_list: null,
          ghost_instance_hover_type: null,
          ghost_instance_list: [],

          show_default_navigation: true,
          snackbar_merge_polygon: false,

          parent_merge_instance: null,
          hovered_figure_id: null,
          parent_merge_instance_index: null,
          instances_to_merge: [],

          userscript_minimized: true,

          event_create_instance: undefined,

          selected_instance_for_history: undefined,
          show_instance_history: false,
          regenerate_file_cache_loading: false,
          display_refresh_cache_button: false,
          get_instances_loading: false,
          canvas_mouse_tools: false,
          show_custom_snackbar: false,
          snackbar_message: undefined,
          selected_instance_template: undefined,
          instance_template_start_point: undefined,
          is_moving_cuboid_corner: false,
          instance_context: new InstanceContext(),
          instance_template_draw_started: false,
          mouse_down_delta_event: { x : 0, y : 0},
          issues_list: undefined,
          canvas_alert_x: undefined,
          canvas_alert_y: undefined,
          original_edit_instance: undefined,
          original_edit_instance_index: undefined,
          loading_sequences: false,
          ctrl_key: false,
          command_manager: undefined,
          show_snackbar_auto_border: false,
          show_snackbar_paste: false,

          sequence_list_local_copy: null,

          request_change_current_instance: null,
          current_issue: undefined,
          share_dialog_open: false,
          show_issue_panel: false,
          snackbar_issues: false, // Controls the display of snackbar with info message when selecting instance on issues.
          trigger_refresh_current_instance: null,
          ellipse_hovered_corner: undefined,
          ellipse_hovered_corner_key: undefined,
          ellipse_hovered_instance: undefined,
          ellipse_hovered_instance_index: undefined,

          drawing_curve: false,
          curve_hovered_point: undefined,

          request_clear_sequence_list_cache: null,

          user_requested_file_id: null,

          instance_clipboard: undefined,
          show_context_menu: false,
          media_core_height: 300,   // assumes admin mode, minimize "jerk" by defaulting
          // it takes time for media_core to pass real value, so we want this to be close to real value
          emit_instance_hover: true,   // ie can set to true to get hover updates

          // Sequence design doc https://docs.google.com/document/d/1EVvPke7Ms25KsmDKpwrQcqB1k6pgB5SNs5WDbwGmLCo/edit#heading=h.oo1xxxn8bkpp

          // sending data from this component to sequence component
          current_sequence_annotation_core_prop: {
            id: null,
            number: null
          },

          // canonical source, we always use this ie to see current sequence
          current_sequence_from_sequence_component: {
            id: null,
            number: null
          },

          force_new_sequence_request: null,
          issue_mouse_position: undefined,


          lock_point_hover_change: false,
          save_warning: {},

          magic_nav_spacer: 40,


          hidden_label_id_list: [],
          space_bar: false,

          mouse_down_limits_result: true,

          highest_sequence_number: 0,

          instance_buffer_dict: {},
          instance_buffer_metadata: {},


          // Order here is important for corner moving. First one keeps y coord fixed and second one keeps x coord fixed.
          lateral_edges : {
            'bot_right': ['top_right', 'bot_left'],
            'bot_left': ['top_left', 'bot_right'],

            'top_left': ['bot_left', 'top_right'],
            'top_right': ['bot_right', 'top_left'],
          },
          opposite_edges_map : {
            'bot_left': 'top_right',
            'bot_right': 'top_left',
            'top_left': 'bot_right',
            'top_right': 'bot_left'
          },

          cuboid_force_move_face: false,
          cuboid_current_drawing_face: undefined,
          ellipse_current_drawing_face: undefined,

          is_actively_drawing: false,
          is_actively_resizing: false,

          save_count: 0,

          save_error: {},
          save_multiple_frames_error: {},
          error: {},
          instance_buffer_error: {},

          task_error: {
            'task_request': null
          },

          current_version: null,

          loading: false,

          label_settings: {
            show_ghost_instances: true,
            show_text: true,
            show_label_text: true,
            show_attribute_text: true,
            show_list: true,
            show_occluded_keypoints: true,
            allow_multiple_instance_select: false,
            font_size: 20,
            spatial_line_size: 2,
            vertex_size: 3,
            show_removed_instances: false,
            target_reticle_size: 20,
            filter_brightness: 100, // Percentage. Applies a linear multiplier to the drawing, making it appear more or less bright.
            filter_contrast: 100, // Percentage. A value of 0% will create a drawing that is completely black. A value of 100% leaves the drawing unchanged.
            filter_grayscale: 0, //  A value of 100% is completely gray-scale. A value of 0% leaves the drawing unchanged.
            instance_buffer_size: 60,
            canvas_scale_global_is_automatic: true,
            canvas_scale_global_setting: 0.5,
            left_nav_width: 450,
            on_instance_creation_advance_sequence: true,
            ghost_instances_closed_by_open_view_edit_panel: false
          },

          annotations_loading: false,
          save_loading_image: false,
          save_loading_frame: {},
          minimize_issues_sidepanel: false,

          source_control_menu: false,

          show_annotations: true,

          snackbar_warning: false,
          snackbar_warning_text: null, // "text" or "message" better name?

          snackbar_success: false,
          snackbar_success_text: null,
          gold_standard_file: {
            instance_list: [],     // careful, need this to not be null for vue canvas to work as expected
            id: null
          },

          // We could also use this dictionary for other parts
          // that rely on type to specifcy an icon
          instance_type_list: [
            {'name': 'polygon',
              'display_name': 'Polygon',
              'icon': 'mdi-vector-polygon'
            },
            {'name': 'box',
              'display_name': 'Box',
              'icon': 'mdi-checkbox-blank'
            },
            {'name': 'tag',
              'display_name': 'Tag',
              'icon': 'mdi-tag'
            },
            {'name': 'point',
              'display_name': 'Point',
              'icon': 'mdi-circle-slice-8'
            },
            {'name': 'line',
              'display_name': 'Fixed Line',
              'icon': 'mdi-minus'
            },
            {'name': 'cuboid',
              'display_name': 'Cuboid 2D',
              'icon': 'mdi-cube-outline'
            },
            {'name': 'ellipse',
              'display_name': 'Ellipse & Circle',   // feel free to change if circle is it's own thing with update
              'icon': 'mdi-ellipse-outline'
            },
            {'name': 'curve',
              'display_name': 'Curve Quadratic',
              'icon': 'mdi-chart-bell-curve-cumulative'
            }
          ],

          instance_type: 'box', //"box" or "polygon" or... "text"... or "cuboid"

          polygon_type_list: ['closed'],

          instance_sub_type: 'closed',

          // this gets set from image or video
          // additionall used as a nuetral reference when it applies to both types
          canvas_width: 1,
          canvas_height: 1,

          seeking: false,

          video_playing: false, // bool of if playing or paused
          video_play: null,  // work around for requests being sent to video.vue
          video_pause: null,

          current_video: {
            frame_count: 0,
            current_frame: 0
          },

          cuboid_current_rear_face: undefined,
          video_mode: false,
          draw_mode: true,
          cuboid_face_hover: undefined,
          alert_info_drawing: true,

          brightness_menu: false,

          // Contains the index position in the array this.instance_list, corresponding to the instance that
          // the mouse is hovering at any given time.
          instance_hover_index: null,
          issue_hover_index: null,

          // Contains the instance type that's being hovered at any given time.
          // Can be any of ['polygon', 'box', 'line', 'point', 'cuboid']
          instance_hover_type: null,

          // some instances types still need second level hover concept
          box_edit_point_hover: null,
          cuboid_corner_move_point: null,
          polygon_point_hover_index: null,

          polygon_point_click_index: null,
          polygon_click_index: null,

          current_frame: 0,

          message: "",
          refresh: null,
          canvas_element: null,

          current_label_file: {
            id: null,
            label: {
            }
          },

          Annotation_assignments : [],

          html_image: new Image(),  // our canvas expects an image at init

          save_on_change: true,
          complete_on_change: true,
          mouse_position: {
            raw: {
              x: 0,
              y: 0
            },
            x: 150,
            y: 150
          },

          instance_list: [],
          show_text_file_place_holder: false,
          instance_list_cache: [],

          current_polygon_point_list: [],

          current_video_file_id: null,

          zoom_settings: {
            ratio: 2,
            size: 50,
            location: "target_reticle",
            on: false
          },

          mouse_request_time: null,

          mouse_down_position: {
            request_time: null,
            x: 0,
            y: 0,
            raw: {
              x: 0,
              y: 0
            }
          },

          instance_frame_start: 0,
          canvas_rectangle: null,
          loading_instance_templates: false,
          instance_template_list: [],
          auto_border_polygon_p1: undefined,
          auto_border_polygon_p1_index: undefined,
          auto_border_polygon_p1_figure: undefined,
          auto_border_polygon_p1_instance_index: undefined,
          auto_border_polygon_p2: undefined,
          auto_border_polygon_p2_index: undefined,
          auto_border_polygon_p2_figure: undefined,
          auto_border_polygon_p2_instance_index: undefined,
          show_polygon_border_context_menu: false,
          has_changed: false,
          interval_autosave: null,
          full_file_loading: false, // For controlling the loading of the entire file + instances when changing a file.

          canvas_scale_local: 1,  // for actually scaling dimensions within canvas

          canvas_translate: {
            x: 0,
            y: 0
          },
          error_no_permissions: {},
          snap_to_edges: 5,
          shift_key: false,
          ctrl_key: false,

          metadata: {
            length: null
          },

          instance_focused_index: null,

          window_width_from_listener: 1280,
          window_height_from_listener: 650
        }
      },
      computed: {
        clipboard: function() {
          return this.$store.getters.get_clipboard
        },
        instance_template_dict: function(){
          let result = {};
          for(let i = 0; i < this.instance_template_list.length; i++){
            const curr = this.instance_template_list[i];
            result[curr.id] = {
              ...curr
            }
          }
          return result;
        },
        current_instance_template: function(){
          return this.instance_template_dict[this.instance_type];
        },
        is_keypoint_template: function(){
          if(!this.current_instance_template){return false}

          if(this.current_instance_template.instance_list.filter(i => i.type === 'keypoints').length > 0){
            return true
          }

          return false;
        },
        instance_template_selected: function(){
          let result = false;
          this.instance_template_list.forEach(inst => {
            if(inst.id === this.instance_type){
              result = true;
            }
          })
          return result
        },
        target_reticle_type: function(){
          if(['box', 'cuboid'].includes(this.instance_type)){
            return 'canvas_cross'
          }
          else if (['polygon', 'point', 'line', 'ellipse', 'curve'].includes(this.instance_type)){
            return 'small_cross'
          }
          else{
            return 'canvas_cross'
          }
        },
        show_target_reticle: function(){
          if (this.$props.view_only_mode == true || this.space_bar == true || this.any_loading == true) {
            return false
          }

          if(this.seeking){
            return false
          }

          if(!this.draw_mode){
            return false
          }
          if(this.show_context_menu){
            return false
          }
          if (this.instance_type == "tag") {
            return false
          }

          return true;

        },
        mouse_computed: function () {
          if (this.$store.state.annotation_state.mouse_down == false) {
            // Becuase we only want this to update when the mouse is down, otherwise for example starting point for event is misaligned.
            return {
              delta_x : 0,
              delta_y : 0
            }
          }
          let delta_x = this.mouse_position.x - this.mouse_down_position.x
          let delta_y = this.mouse_position.y - this.mouse_down_position.y
          delta_x = parseInt(delta_x)
          delta_y = parseInt(delta_y)

          return {
            delta_x : delta_x,
            delta_y : delta_y
          }
        },

        instance_select_for_issue: function(){
          return this.$store.getters.get_instance_select_for_issue;
        },
        instance_select_for_merge: function(){
          return this.$store.getters.get_instance_select_for_merge;
        },
        hovered_instance: function(){
          if(!this.instance_list){ return }
          if(this.instance_hover_index != undefined){ return }
        },
        selected_instance: function(){
          if(!this.instance_list){return}
          for(let i=0; i < this.instance_list.length; i ++){
            if(this.instance_list[i].selected){
              return this.instance_list[i]
            }
          }
        },
        selected_instance_index: function(){
          if(!this.instance_list){return}
          for(let i=0; i < this.instance_list.length; i ++){
            if(this.instance_list[i].selected){
              return i
            }
          }
        },
        view_issue_mode: function(){
          return this.$store.getters.get_view_issue_mode;
        },

        show_place_holder() {
          return this.full_file_loading;
        },
        any_loading() {
          /* Does not include save_loading because we currently
       * pass this to v_bg which flashes screen when showing loading
       * Something to review.
       */
          return this.full_file_loading || this.annotations_loading || this.loading || this.loading_sequences || this.get_instances_loading
        },

        canvas_scale_global() {

          /* The window size is defined as
       * window_size = image_size * global_scale
       * a = b * c
       * which is equal to
       * a/b = (b * c)/b
       * a/b = c   (simplified)
       * So window_width / image_size = global scale
       *
       * Then the question becomes how to set it relative to other elements.
       * (That's what the extra little number is for)
       *
       * For user set, could have a "zoom" slider too. But I think people also sometimes
       * like setting a number?
       *
       * Note that "_setting" is the automatic or user set number,
       * where as withoout that suffix it's the "internal" system used value.
       *
       * Still needs more work in relation to auto components but strong step in direction
       *
       * At the moment the user setting thing doesn't really make sense (if auto is working well)
       * but perhaps in future as we allow more control over how other components
       * are positioned it will.
       * Context here is that it's not a "zoom".
       */
          // Manual override
          if (this.label_settings.canvas_scale_global_is_automatic == false) {
            return this.label_settings.canvas_scale_global_setting
          }

          if (this.$props.file && this.$props.file.type == 'text') {
            // Temp until more text functions. eg so canvas doesn't 'explode' to large size.
            return 100
          }

          let image_size_width = 1920 // default
          let image_size_height = 1280

          if (this.canvas_width) {

            //  TODO rename 'canvas' thing here as it's more like original media width
            // the 'canvas_scaled' is what's being used for actual canvas stuff?
            image_size_width = this.canvas_width
            image_size_height = this.canvas_height
          }
          // basically the math above does work but it needs right image size

          /*
       * magic_nav_spacer is
       * rough space between actual pane size and padding on either side of image.
       * meant as a reminder to review that concept a bit more closely doesn't quite feel
       * right yet
       *
       * the goal of calculation is to make it relative to left and right panel
       */
          let middle_pane_width = this.window_width_from_listener - this.label_settings.left_nav_width - this.magic_nav_spacer

          let toolbar_height = 80

          // get media core height
          if (document.getElementById("media_core")){
            this.media_core_height = document.getElementById("media_core").__vue__.height
          }

          let middle_pane_height = this.window_height_from_listener - toolbar_height
            - this.media_core_height - this.magic_nav_spacer

          if (this.video_mode == true) {
            // TEMP this is solving wrong problem
            // In preview mode it def makes more sense for sequences to be to the right of video
            let video_offset = 80
            if (this.media_core_height) {
              video_offset = 200
            } else {
              video_offset = 80
            }
            middle_pane_height = middle_pane_height - video_offset
          }

          // careful height comparison relative to height, width to width
          let height_scaled = middle_pane_height / image_size_height
          let width_scaled = middle_pane_width / image_size_width

          // careful to do the scale first, so we do the min of scaled values
          let lowest_size = Math.min(height_scaled, width_scaled)

          let new_size = Math.round(lowest_size * 100) / 100

          this.label_settings.canvas_scale_global_setting = new_size


          return new_size


        },


        canvas_width_scaled: function () {
          return this.canvas_width * this.canvas_scale_global
        },

        canvas_height_scaled: function () {
          return this.canvas_height * this.canvas_scale_global
        },

        canvas_scale_combined: function () {
          return this.canvas_scale_local * this.canvas_scale_global
        },

        canvas_transform: function () {
          return {
            'canvas_scale_global': this.canvas_scale_global,
            'canvas_scale_local': this.canvas_scale_local,
            'canvas_scale_combined' : this.canvas_scale_local * this.canvas_scale_global,
            'translate': this.canvas_translate
          }
        },

        canvas_filters: function () {

          return {
            'brightness': this.label_settings.filter_brightness,
            'contrast': this.label_settings.filter_contrast,
            'grayscale': this.label_settings.filter_grayscale
          }

        },

        current_polygon_point: function () {
          var x = parseInt(this.mouse_down_position.x)
          var y = parseInt(this.mouse_down_position.y)

          return {
            x: x,
            y: y,
            selected: false
          }

        },
        current_instance: function () {

          // QUESTIONs
          // how do we want to name space this better as we get more instance types
          // some shared stuff though...

          // we use computed function here since label referecnes this.current_label_file
          // and this won't work in data dictionary

          // Do we actually need to cast this as Int here if db handles it?
          var x_min = parseInt(this.mouse_down_position.x)
          var y_min = parseInt(this.mouse_down_position.y)
          var x_max = parseInt(this.mouse_position.x)
          var y_max = parseInt(this.mouse_position.y)

          // Handle inverting origin point
          if (x_max < x_min) {
            x_max = parseInt(this.mouse_down_position.x)
            x_min = parseInt(this.mouse_position.x)
          }

          if (y_max < y_min) {
            y_max = parseInt(this.mouse_down_position.y)
            y_min = parseInt(this.mouse_position.y)
          }

          if (x_min < 0) {x_min = 0}
          if (y_min < 0) {y_min = 0}

          // testing
          //x_max = 99999
          //y_max = 99999

          // 480 is from 0 to 479.
          if (this.canvas_width) {
            if (x_max >= this.canvas_width) {
              x_max = this.canvas_width - 1}

            if (y_max >= this.canvas_height) {
              y_max = this.canvas_height - 1}
          }

          var width = x_max - x_min
          var height = y_max - y_min

          // Maybe if != cuboid this is null?

          if (this.instance_type == "cuboid") {
            let front_face_width = width;
            let front_face_height = height;
            if(this.cuboid_current_drawing_face === 'second' && this.cuboid_current_rear_face){
              front_face_width = this.cuboid_current_rear_face.width
              front_face_height = this.cuboid_current_rear_face.height;
            }
            var front_face = {
              'width': front_face_width,
              'height': front_face_height,
              'top_left' : {
                x: parseInt(this.mouse_position.x) - front_face_width,
                y:  parseInt(this.mouse_position.y) - front_face_height
              },
              'top_right' : {
                x: parseInt(this.mouse_position.x),
                y:  parseInt(this.mouse_position.y) - front_face_height
              },
              'bot_left' : {
                x: parseInt(this.mouse_position.x) - front_face_width,
                y: parseInt(this.mouse_position.y)
              },
              'bot_right' : {
                x: parseInt(this.mouse_position.x),
                y: parseInt(this.mouse_position.y)
              }
            }

            // default rear face to front face?
            // or "hide it"?
            // setting = to front face directly links in way we don't want
            // Lock rear face after first face has been drawn.
            if(this.cuboid_current_drawing_face === 'second' && this.cuboid_current_rear_face){
              var rear_face = this.cuboid_current_rear_face

            }
            else{
              var rear_face = {
                'width': width,
                'height': height,
                'top_left' : {
                  x: x_min,
                  y: y_min
                },
                'top_right' : {
                  x: x_min + width,
                  y: y_min
                },
                'bot_left' : {
                  x: x_min,
                  y: y_min + height
                },
                'bot_right' : {
                  x: x_max,
                  y: y_max
                }
              }
            }
          }
          else {
            var front_face = null
            var rear_face = null
          }

          let number = null
          let sequence_id = null
          if (this.video_mode == true) {
            number = this.current_sequence_from_sequence_component.number
            sequence_id = this.current_sequence_from_sequence_component.id
          }
          let p1,cp,p2;
          if(this.instance_type === 'curve' && this.current_polygon_point_list.length > 0){
            p1 = {x: this.current_polygon_point_list[0].x, y: this.current_polygon_point_list[0].y}
            if(this.current_polygon_point_list.length >= 2){
              cp = {
                x: (this.current_polygon_point_list[0].x + this.current_polygon_point_list[1].x) / 2,
                y: (this.current_polygon_point_list[0].y + this.current_polygon_point_list[1].y) / 2
              }
              p2 ={
                x: this.current_polygon_point_list[1].x,
                y: this.current_polygon_point_list[1].y
              }
            }

          }
          let instance_data = {
            x_min: x_min,
            y_min: y_min,
            center_x: this.instance_type === 'ellipse' ? x_min : undefined,
            center_y: this.instance_type === 'ellipse' ? y_min : undefined,
            x_max: x_max,
            y_max: y_max,
            p1: p1,
            cp: cp,
            p2: p2,
            edges: [],
            nodes: [],
            auto_border_polygon_p1: this.auto_border_polygon_p1,
            auto_border_polygon_p2: this.auto_border_polygon_p2,
            cuboid_current_drawing_face: this.cuboid_current_drawing_face,
            front_face: front_face,
            angle: 0,
            rear_face: rear_face,
            width: width,
            height: height,
            label_file: this.current_label_file,
            label_file_id: this.current_label_file_id,
            selected: 'false',
            number: number,
            machine_made: false,
            type: this.instance_type,
            points: this.current_polygon_point_list,
            sequence_id: sequence_id,
            soft_delete: false    // default for new instances
          }
          this.calculate_min_max_points(instance_data)
          return instance_data;
        },

        current_label_file_id: function () {
          /*
        * Jan 4, we sometimes need the "id" ie for change detection
          BUT it creates awkward thing that if current_label_file becomes
          undefined, it crashes interface

          Using this as a workaround into shared computed property
        */

          if (this.current_label_file) {
            return this.current_label_file.id
          } else {
            return null
          }
        },

        save_text() {
          if (this.save_on_change == true) {
            return "Saving automatically"
          } else {
            return "Saving manually"
          }
        },

        canvas_style: function () {
          return "width:" + this.canvas_width_scaled + "px"
        },

        style_max_width: function () {
          return "max-width:" + this.canvas_width_scaled + "px"
        }


      },

      created() {
        this.created()
        // put all created stuff in here, workaround so we can call created internal refresh concept
      },

      beforeDestroy() {
        /* https://vuejs.org/v2/api/#beforeDestroy
     * https://forum.vuejs.org/t/where-to-call-removeeventlistener/63123/2
     *
     */

        clearInterval(this.interval_autosave);
        this.detect_is_ok_to_save();
        this.remove_event_listeners()

        // watcher removal
        this.get_instances_watcher()
        this.save_watcher()
        this.save_and_complete_watcher()
        this.refresh_video_buffer_watcher()
        //console.debug("Destroyed")
      },
      destroyed() {

      },

      mounted() {
        if (window.Cypress) {
          window.AnnotationCore = this;
        }
        this.mounted()
      },

      methods: {
        cancel_merge: function(){
          this.$store.commit('set_instance_select_for_merge', false);
        },
        delete_instances_and_add_to_merged_instance: function(parent_instance, instances_to_merge){
          // For instance to merge, delete it and add al points to parent instance with a new figure ID.
          for(const instance of instances_to_merge){
            let figure_id = uuidv4();
            let new_points = parent_instance.points.map(p => p);
            for(const point of instance.points){
              let new_figure_id = figure_id;
              if(point.figure_id){
                new_figure_id = point.figure_id;
              }
              new_points.push({
                ...point,
                figure_id: new_figure_id
              })
            }

            let instance_index = this.instance_list.indexOf(instance);
            if(instance_index > -1){
              this.delete_single_instance(instance_index);
            }
            parent_instance.points = new_points;

          }
        },
        merge_polygons: function(){
          let parent_instance = this.parent_merge_instance;
          let instances_to_merge = this.instances_to_merge;
          let has_multiple_figures = parent_instance.points.filter(p => p.figure_id != undefined).length > 0;
          if(has_multiple_figures){
            // For each instance to merge, delete it and add al points to parent instance with a new figure ID.
            this.delete_instances_and_add_to_merged_instance(parent_instance, instances_to_merge);
          }
          else{
            // Add a figure ID for parent instance points
            let figure_id = uuidv4();
            parent_instance.points = parent_instance.points.map(p => {
              return {
                ...p,
                figure_id:  figure_id
              }
            })
            // For each instance to merge, delete it and add al points to parent instance with a new figure ID.
            this.delete_instances_and_add_to_merged_instance(parent_instance, instances_to_merge);
          }
          this.$store.commit('set_instance_select_for_merge', false);
        },

        get_save_loading: function(frame_number){
          if(this.video_mode){
            if(!this.save_loading_frame[frame_number]){
              return false
            }
            else{
              return true;
            }
          }
          else{
            return this.save_loading_image;
          }
        },
        set_save_loading(value, frame){
          if(this.video_mode){
            this.save_loading_frame[frame] = value;
          }
          else{
            this.save_loading_image = value;
          }
          this.$forceUpdate();
        },
        // userscript (to be placed in class once context figured)
        set_instance_human_edited: function(instance){
          if(!instance){
            return
          }
          instance.change_source = 'ui_diffgram_frontend'
          instance.machine_made = false;
        },
        get_roi_canvas_from_instance: function (instance, ghost_canvas) {
          // https://developer.mozilla.org/en-US/docs/Web/API/CanvasRenderingContext2D/getImageData


          let ghost_canvas_context = ghost_canvas.getContext('2d')

          let region_of_interest_image_data = ghost_canvas_context.getImageData(
            instance.x_min, instance.y_min,
            instance.width, instance.height)

          var roi_canvas = document.createElement('canvas');
          var roi_canvas_ctx = roi_canvas.getContext('2d');
          roi_canvas.width =  instance.width;
          roi_canvas.height = instance.height;

          roi_canvas_ctx.putImageData(region_of_interest_image_data, 0, 0);

          return roi_canvas
        },
        regenerate_file_cache: async function(){
          this.regenerate_file_cache_loading = true;
          let frame_number = this.current_frame;
          let file_id = undefined;
          if(this.$props.task){
            file_id = this.$props.task.file.id;
          }
          else{
            file_id = this.$props.file.id;
          }
          let project_string = this.$props.project_string_id;
          if(!project_string){
            project_string = this.$store.state.project.current.project_string_id;
          }
          const response = await axios.post(`/api/v1/project/${project_string}/file/${file_id}/regenerate-cache`,
            {
              frame_number: frame_number
            }
          );
          if(response.status === 200){
            this.has_changed = false;
            location.reload();
          }
        },
        get_new_canvas: function () {
          this.html_image.crossOrigin = "Anonymous";

          let ghostcanvas = document.createElement('canvas');
          let metadata = this.get_metadata()

          ghostcanvas.height = metadata.height
          ghostcanvas.width = metadata.width
          let context = ghostcanvas.getContext('2d');

          context.drawImage(this.html_image,0,0)
          return ghostcanvas
        },

        get_metadata: function() {
          let metadata
          if (this.$props.file.type == 'video'){
            metadata = {...this.$props.file.video}
          } else {
            metadata = {...this.$props.file.image}
          }
          return metadata
        },

        get_userscript: function() {
          if (this.job && this.job.default_userscript) {
            return this.job.default_userscript
          }
          if (this.task && this.task.default_userscript) {
            return this.task.default_userscript
          }
          if (this.$refs.userscript &&
            this.$refs.userscript.userscript_literal) {
            return this.$refs.userscript.userscript_literal
          }
          return undefined
        },
        userscript_select_disabled: function () {
          if (this.task && this.task.id) { return true}
        },
        go_to_key_frame_handler: function(){
          this.close_instance_history_panel();
          this.detect_is_ok_to_save();

        },
        show_instance_history_panel: function(instance_index){
          this.show_instance_history = true;
          this.selected_instance_for_history = this.instance_list[instance_index];

        },
        close_instance_history_panel: function(e){
          this.show_instance_history = false;
          this.selected_instance_for_history = undefined;
        },
        warn_user_unload: function(e){
          let pending_changes_frames = false;
          for(let key of Object.keys(this.instance_buffer_metadata)){
            if(this.instance_buffer_metadata[key].pending_save){
              pending_changes_frames = true
              break;
            }
          }
          if(this.has_changed || pending_changes_frames){
            // Cancel the event
            e.preventDefault()
            // Chrome requires returnValue to be set
            e.returnValue = ''

          }


        },
        check_if_pending_created_instance: function(){
          // Sets the pending changes flag if there are any instances that have not been saved yet.
          for(let i = 0; i < this.instance_list.length; i++){
            let instance = this.instance_list[i];
            if(!instance.id){
              this.has_changed = true;
            }
          }
        },
        instance_template_has_keypoints_type: function(instance_template){
          return instance_template.instance_list.filter(instance => instance.type === 'keypoints').length > 0;
        },
        get_create_instance_template_url: function(){
          if(this.$props.project_string_id){
            return `/api/v1/project/${this.$props.project_string_id}/instance-template/new`
          }
          else{
            return `/api/v1/task/${this.$props.task.id}/instance-template/new`
          }
        },


        clear__new_and_no_ids: function () {

          // careful we start from top since we splice as we go
          for(var i = this.instance_list.length -1; i >= 0 ; i--){
            let current_instance = this.instance_list[i];
            if (current_instance.id == undefined){
              this.instance_list.splice(i, 1)
            }
          }

        },

        get_userscript_id_string: function (userscript_id) {

          if (!userscript_id) {
            this.userscript = this.get_userscript()
            if (this.userscript.id) {
              userscript_id = this.userscript.id.toString()
            }
          }
          return userscript_id

        },

        create_box: function(x_min, y_min, x_max, y_max, userscript_id=undefined){

          if (x_min == undefined
            || y_min == undefined
            || x_max == undefined
            || y_max == undefined) {
            throw new Error("Must have x_min, y_min, x_max, y_max")
          }

          // current_instance is computed
          // TODO use function in create instance command
          let new_instance = {...this.current_instance}

          new_instance.x_min = parseInt(x_min)
          new_instance.x_max = parseInt(x_max)
          new_instance.y_min = parseInt(y_min)
          new_instance.y_max = parseInt(y_max)

          new_instance.width = parseInt(x_max - x_min)
          new_instance.height = parseInt(y_max - y_min)

          new_instance.change_source = "userscript_" + this.get_userscript_id_string(userscript_id)

          let reasonable = this.check_reasonableness(new_instance)
          if (reasonable != true) {
            console.warn("Instance not reasonable: ", reasonable, "Instance was ignored.")
            return
          }

          const command = new CreateInstanceCommand(new_instance, this)
          this.command_manager.executeCommand(command);

          this.event_create_instance = new_instance

          //this.$emit('created_instance', new_instance)

        },

        check_reasonableness: function (instance) {
          // returns true if reasonable otherwise string reason
          // a lot of ways we could expand this in the future to be more descriptive

          let reasonable = 7
          let values_to_check = [
            instance.x_min,
            instance.x_max,
            instance.y_min,
            instance.y_max]
          for (let value of values_to_check){
            if (value < 0) {
              return "min/max value < 0"
            }
          }
          if (instance.width < reasonable) {
            return "instance.width < reasonable"
          }
          if (instance.height < reasonable) {
            return "instance.height < reasonable"
          }
          if (instance.points){
            for (let point of instance.points) {
              if (point.x < 0) {
                return "point.x < 0"
              }
              if (point.y < 0) {
                return "point.y < 0"
              }
            }
          }
          if (instance.type == 'polygon') {
            if (!instance.points) {
              return "no polygon points key"
            }
            if (instance.points.length < 2) {
              return "not enough points for polygon"
            }
          }
          return true
        },

        slice_of_canvas: function (x_min, y_min, x_max, y_max) {
          // idea of taking a slice of canvas from instance
          // then running algorithm that wants more "full" resolution
          // eg to improve performance
          // maybe something like this https://stackoverflow.com/questions/45234492/copy-a-part-of-canvas-to-image
          // but translation back and forth I'm not sure
        },

        create_instance_from_keypoints: function(x, y){
          let new_instance = {
            ...this.current_instance,
            points: [...this.current_instance.points.map(p => ({...p}))]
          };
          new_instance.type = "point"
          new_instance.points = [{'x' : x, 'y' : y}]
          const command = new CreateInstanceCommand(new_instance, this)
          this.command_manager.executeCommand(command);
        },

        update_polygon_width_height: function (instance) {
          // assumes instance passed by reference

          if (!instance.points) { return }

          instance.x_min = 99999
          instance.x_max = 0
          instance.y_min = 99999
          instance.y_max = 0
          const x = 'x'
          const y = 'y'

          for (let i =0; i < instance.points.length; i++) {

            let point = instance.points[i]

            if (point[x] <= instance.x_min) { instance.x_min = parseInt(point[x]) }
            if (point[x] >= instance.x_max) { instance.x_max = parseInt(point[x]) }
            if (point[y] <= instance.y_min) { instance.y_min = parseInt(point[y]) }
            if (point[y] >= instance.y_max) { instance.y_max = parseInt(point[y]) }
          }

          instance.width = parseInt(instance.x_max - instance.x_min)
          instance.height = parseInt(instance.y_max - instance.y_min)

        },

        create_polygon: function(points_list, userscript_id=undefined){
          let new_instance = {
            ...this.current_instance,
            points: [...this.current_instance.points.map(p => ({...p}))]
          };
          new_instance.type = "polygon"
          new_instance.points = points_list
          new_instance.change_source = "userscript_" + this.get_userscript_id_string(userscript_id)

          this.update_polygon_width_height(new_instance)
          //console.debug(new_instance.width, new_instance.height)

          let reasonable = this.check_reasonableness(new_instance)
          if (reasonable != true) {
            console.warn("Instance not reasonable: ", reasonable)
            return
          }

          const command = new CreateInstanceCommand(new_instance, this)
          this.command_manager.executeCommand(command);
        },

        __bodypix_points_to_instances: function (keypoints_list) {

          // TODO also need to set instance type

          for (let keypoint of keypoints_list){
            this.current_instance.points = [keypoint.position]
            const command = new CreateInstanceCommand(this.current_instance, this)
            this.command_manager.executeCommand(command);
          }

        },


        create_instance_template: async function(instance_index, name){
          try {
            this.error = {}
            const instance = this.instance_list[instance_index];
            if (!instance) {
              return
            }
            if (!name) {
              this.error = {'name': 'Please provide a name for the instance template.'}
              return
            }
            const url = this.get_create_instance_template_url();
            const response = await axios.post(url,
              {
                name: name,
                reference_height: this.canvas_height,
                reference_width: this.canvas_width,
                instance_list: [instance]
              });

            if(response.status === 200){
              this.instance_template_list.push(
                response.data.instance_template
              )
              this.instance_type_list.push({
                icon: 'mdi-shape',
                display_name: response.data.instance_template.name,
                name: response.data.instance_template.id
              });
              this.show_snackbar('Instance template created successfully.');
            }
          }
          catch(error){
            console.error(error)
            this.error = this.$route_api_errors(error)
          }
          finally{
            this.loading = false
          }
        },
        show_snackbar: function(message){
          this.snackbar_message = message;
          this.show_custom_snackbar = true
        },

        open_instance_template_dialog: function(){
          this.$refs.instance_template_creation_dialog.open();
        },

        trigger_instance_changed(){
          // Callback for when an instance is changed
          // This is a WIP that will be used for all the class Instance Types
          // For now we only have Kepoints instance using this.
          this.has_changed = true
        },
        instance_selected: function(instance){
          // Callback for when an instance is selected
          // This is a WIP that will be used for all the class Instance Types
          // For now we only have Kepoints instance using this.
        },
        instance_deselected: function(){
          //TODO: implement
        },
        instance_hovered: function(instance){
          // Callback for when an instance is selected
          // This is a WIP that will be used for all the class Instance Types
          // For now we only have Kepoints instance using this.

          if(!this.instance_list){ return }
          for(let i = 0; i < this.instance_list.length; i++){
            if(instance.creation_ref_id === this.instance_list[i].creation_ref_id){
              this.instance_hover_index = i;
            }
          }
        },
        instance_unhovered: function(instance){

          if(this.instance_hover_index == undefined){return}

          if(this.instance_list[this.instance_hover_index].creation_ref_id === instance.creation_ref_id){
            this.instance_hover_index = null;
          }

        },

        test_instance_list_and_list_in_buffer_by_ref: function (){
          for(let i = 0; i < this.instance_list.length; i++){
            let is_valid_by_ref = this.instance_list[i] == this.instance_buffer_dict[this.current_frame][i]
            if(!is_valid_by_ref){
              return false
            }
          }
          return true
        },

        create_instance_list_with_class_types: function(instance_list){
          const result = []
          if (!instance_list) { return result }
          for(let i = 0; i < instance_list.length; i++){
            let current_instance = instance_list[i];

            // Note that this variable may now be one of any of the classes on vue_canvas/instances folder.
            // Or (for now) it could also be a vanilla JS object (for those types) that haven't been refactored.
            let initialized_instance = this.initialize_instance(current_instance)
            result.push(initialized_instance);
          }
          return result;
        },
        initialize_instance_buffer_dict_frame: function(frame_number){
          /**
           * This function initializes the instances of a frame's instance list.
           * We just do this once per frame, so this function should only be executed
           * one time per frame number. To control this we have the instance_buffer_metadata
           * to know which ones have been initialized.
           * */

          if(frame_number == undefined){ return }
          // We don't initialize again if we already initialized the frame.
          if(!this.instance_buffer_dict[frame_number]){ return }

          if(this.instance_buffer_metadata[frame_number] &&
            this.instance_buffer_metadata[frame_number].initialized){
            return
          }

          // Perform the instance_buffer_dict initialization.
          for(let i = 0; i < this.instance_buffer_dict[frame_number].length; i++){
            let current_instance = this.instance_buffer_dict[frame_number][i]
            current_instance = this.initialize_instance(current_instance);
            this.instance_buffer_dict[frame_number][i] = current_instance
          }

          // Set the metadata to prevent initializing again in the future
          if(this.instance_buffer_metadata[frame_number]){
            this.instance_buffer_metadata[frame_number].initialized = true;
          }
          else{
            this.instance_buffer_metadata[frame_number] = {initialized: true};
          }
        },
        populate_canvas_element: function(){
          if(!this.canvas_element){
            this.canvas_element = document.getElementById("my_canvas")
          }
        },
        fetch_instance_template: async function(){
          try {
            this.loading_instance_templates = true;
            this.canvas_element = document.getElementById("my_canvas")
            this.canvas_element_ctx = this.canvas_element.getContext('2d');
            const response = await axios.post(`/api/v1/project/${this.$props.project_string_id}/instance-template/list`, {});
            if (response.data.instance_template_list) {
              this.instance_template_list = response.data.instance_template_list.map(instance_template => {

                instance_template.instance_list = instance_template.instance_list.map(instance =>{
                  instance.reference_width = instance_template.reference_width;
                  instance.reference_height = instance_template.reference_height;
                  return instance
                });
                // Note that here we are creating a new object for the instance list, all references are lost.
                instance_template.instance_list = this.create_instance_list_with_class_types(
                  instance_template.instance_list
                );

                return instance_template

              })
              this.instance_template_list.forEach(inst =>{
                let icon = 'mdi-shape'
                if (inst.instance_list && inst.instance_list[0].type == 'keypoints') {
                  icon = 'mdi-vector-polyline-edit'
                }
                this.instance_type_list.push({
                  name: inst.id,
                  display_name: inst.name,
                  icon: icon
                })
              })
            }

          } catch (error) {

          }
          finally {
            this.loading_instance_templates = false;
          }

        },
        redo: function(){
          if(!this.command_manager ){return}
          let redone = this.command_manager.redo();
          if(redone){
            this.has_changed = true
          }
          this.update_canvas();
        },
        undo: function(){
          if(!this.command_manager ){return}
          let undone = this.command_manager.undo();
          if(undone){
            this.has_changed = true
          }
          this.update_canvas();
        },
        set_loading_sequences: function(loading_sequences){
          this.loading_sequences = loading_sequences
        },
        set_canvas_dimensions: function(){
          let file = null;
          if(this.$props.file){
            file = this.$props.file;
          }
          else if(this.$props.task){
            file = this.$props.task.file;
          }
          else{
            throw new Error('Must provide task or file in props.')
          }
          this.canvas_width = file.video.width;
          this.canvas_height = file.video.height;
        },
        issues_fetched: function(issues_list){
          this.issues_list = issues_list;
        },
        open_view_edit_panel(issue){
          // This boolean controls if issues create/edit panel is shown or hidden.
          this.show_issue_panel = true;

          // Case for edit/view mode.
          this.current_issue = issue;
          this.draw_mode = false;
          this.label_settings.allow_multiple_instance_select = true;
          this.$store.commit('set_view_issue_mode', true);
          if(this.video_mode){
            if(this.current_frame !== issue.marker_frame_number){
              this.$refs.video_controllers.go_to_keyframe(issue.marker_frame_number);
            }

          }
        },
        polygon_unmerge(unmerge_instance_index, figure_id){
          let instance = this.instance_list[unmerge_instance_index];
          // Remove All points from the polygon with the give figure id
          let figure_points = instance.points.filter(p => p.figure_id == figure_id).map(p => ({...p, figure_id: undefined}))
          instance.points = instance.points.filter(p => p.figure_id != figure_id)

          // Check if only 1 figure remains, and delete figure id.
          let figure_list = this.get_polygon_figures(instance)
          if(figure_list.length === 1){
            instance.points = instance.points.map(p => ({...p, figure_id: undefined}))
          }

          // Create the previously merged figure as a new instance.
          let instance_to_unmerge = this.duplicate_instance(instance);
          // Remove point and just leave the points in the figure
          instance_to_unmerge.points = figure_points;
          this.push_instance_to_instance_list_and_buffer(instance_to_unmerge, this.current_frame);
          // Auto select on label view detail for inmediate attribute edition.
          this.create_instance_events()
        },
        start_polygon_select_for_merge(merge_instance_index){
          // Close context menu and set select instance mode
          if(merge_instance_index == undefined){
            return
          }
          this.parent_merge_instance = this.instance_list[merge_instance_index];
          this.parent_merge_instance_index = merge_instance_index;
          this.show_context_menu = false;
          this.$store.commit('set_instance_select_for_merge', true);
        },
        open_issue_panel(mouse_position){
          // This boolean controls if issues create/edit panel is shown or hidden.
          this.show_issue_panel = true;
          // Close context menu and set select instance mode
          this.show_context_menu = false;
          this.issue_mouse_position = mouse_position;
          this.$store.commit('set_instance_select_for_issue', true);
        },
        refresh_issues_sidepanel(issue){
          this.$refs.issues_sidepanel.add_issue_to_list(issue);
        },
        update_issues_list(issue){
          if(this.$refs['issues_sidepanel']){
            this.$refs['issues_sidepanel'].update_issue(issue)
          }
        },
        start_attach_instance_edition(){
          this.$store.commit('set_instance_select_for_issue', true);
          this.snackbar_issues = true;
        },
        stop_attach_instance_edition(){
          this.$store.commit('set_instance_select_for_issue', false);
          this.snackbar_issues = false;
        },
        close_view_edit_issue_panel(){
          this.current_issue = undefined;
          this.show_issue_panel = false;
          this.label_settings.allow_multiple_instance_select = false;
          this.$store.commit('set_view_issue_mode', false);
          this.$store.commit('set_instance_select_for_issue', false);

        },
        close_issue_panel(){
          this.show_issue_panel = false;
          this.$store.commit('set_instance_select_for_issue', false);
          this.snackbar_issues = false;
          this.issue_mouse_position = undefined;
          this.clear_selected();
        },
        done_selecting_instaces_issues(){
          this.snackbar_issues = false;
        },
        open_share_dialog: function(){
          this.share_dialog_open = true;
        },
        close_share_dialog: function(){
          this.share_dialog_open = false;
        },
        clear_selected: function () {
          for (let i in this.instance_list) {
            this.instance_list[i].selected = false
          }
        },

        shift_frame_via_store: function(direction) {
          // direction is an int where: -1 to go back, 1 go forward
          if(this.current_frame === 0 && direction === -1){
            return
          }

          if(this.current_frame >= (this.current_video.frame_count - 1) && direction === 1){
            return
          }

          let new_frame = direction + this.current_frame
          this.$store.commit('go_to_keyframe_via_store', new_frame)

        },

        hide_context_menu: function(){    // search tags: close close_context
          this.show_context_menu = false;
          // this.emit_instance_hover = false;   // computation optimzation
          // there's a timing issue with doing this though so leave off for now.
        },

        open_context_menu: function(){

          //this.emit_instance_hover = true;
          this.show_context_menu = true;

        },

        detect_clicks_outside_context_menu: function (e) {

          // skip clicks on the actual context menu
          if (e.target.matches('.context-menu, .context-menu *')){
            return;
          }
          // assume if not on context menu, then it's outside and we want to hide it
          this.hide_context_menu()
        },

        mouse_events_global_down: function(e) {

          this.detect_clicks_outside_context_menu(e)

        },

        contextmenu: function(e) {
          /* contextmenu is built in event
       * We assume a click here will open it
       */
          e.preventDefault();
          this.open_context_menu();
        },

        start_autosave: function() {
          this.interval_autosave = setInterval(this.detect_is_ok_to_save, 15*1000);
        },

        detect_is_ok_to_save: async function() {
          if (this.has_changed) {
            await this.save();
          }
        },

        focus_instance: function (focus) {
          // Do we want to support focusing more than one at a time?
          // If we only want one can just pass that singluar instance as the "focus" one
          // this.instance_list[index].focused = True

          // careful can't use id, since newly created instances won't have an ID!
          this.instance_focused_index = focus.index
        },

        focus_instance_show_all() {
          this.instance_focused_index = null
        },

        instance_update: function (update) {
          /*
         * update, an object like:
         *
         *  index, number
         *  mode, string, ie one of [delete, delete_undo, toggle_missing, ... etc.]
         *  list_type, instance_list type, string  [gold_standard, default]  defaults to default
         *  payload, object, relative to mode
         *
         * ie
         *  index: 1
         *  mode: "delete"
         *
         */
          // Main communication point for actions taken on instance list
          // propagating to main
          // Once the list is updated here it filters back to instance_list component

          if (this.$props.view_only_mode == true) { return }

          let index = update.index
          if (index == undefined) { return }  // careful 0 is ok.

          // since sharing list type component need to determine which list to update
          // could also use render mode but may be different contexts
          if (!update.list_type || update.list_type == "default") {
            var instance = this.instance_list[index]
          }
          if (update.list_type == "gold_standard") {
            var instance = this.gold_standard_file.instance_list[index]
          }

          if (!instance) {
            console.debug("Invalid index")
            return
          }

          if (update.mode == 'pause_object'){
            instance.pause_object = true
          }

          if (update.mode == 'on_click_update_point_attribute'){
            if (instance.nodes[update.node_hover_index].occluded == true) {
              instance.nodes[update.node_hover_index].occluded = false
            } else {
              instance.nodes[update.node_hover_index].occluded = true
            }
          }

          // instance update
          if (update.mode == "update_label") {
            // not 100% sure if we need both here
            instance.label_file = update.payload
            instance.label_file_id = update.payload.id
          }

          if (update.mode == "change_sequence"){

            instance.sequence_id = update.sequence.id
            instance.number = update.sequence.number

          }

          if (update.mode == "rating_update") {
            instance.rating = update.payload
          }

          if (update.mode == "delete") {
            instance.soft_delete = true
          }

          if (update.mode == "delete_undo") {
            instance.soft_delete = false
          }

          if (update.mode == "delete" ||
            update.mode == "delete_undo") {

            // sequence related, design https://docs.google.com/document/d/1HVY_Y3NsVQgHyQAH-NfsKnVL4XZyBssLz2fgssZWFYc/edit#heading=h.121li5q14mt2
            if (instance.label_file_id != this.current_lable_file_id) {
              // this.save()
              this.has_changed = true;
              this.request_clear_sequence_list_cache = Date.now()
            }
          }

          if (update.mode == "toggle_missing") {
            if (instance.missing) {
              instance.missing = !instance.missing
            } else {
              instance.missing = true
            }
          }

          if (update.mode == "attribute_change") {
            /*
         *   We expect the event to supply a group_id
         *   which we use as the key to set this.
         *   The value should be a dictionary of the form
         *   ie similar to
         *      136: {archived: false, display_order: null, group_id: 136, id: 173, kind: "select", name: "select",…
         *    which is stored under attribute groups ie
         *    attribute_groups: { 136, 190, 253 …}
         *
         *    For the event to propogate this we must set a key
         *    ie :key="attribute_template.id"
         */
            if (!instance.attribute_groups) {instance.attribute_groups = {}
            }

            /* key on group id to avoid having to iterate through stuff
         * assume allow only one per group...
         * otherwise could be a list
         *
         * In the past we recevied a single attribute here
         * However now that a group can have many attributes as the value
         * (ie for multiple select)
         * we pass the "value" concept here...
         */

            let group = update.payload[0]
            let value = update.payload[1]

            // we assume this represents a group
            instance.attribute_groups[group.id] = value
            //console.debug(group, value)
          }

          // end instance update

          let insert_instance_result = this.insert_instance(index, instance, update)

          this.has_changed = true;
          this.trigger_refresh_with_delay()


        },

        clone_instance(instance) {
          // WIP
          let new_instance = cloneDeep(instance)
          new_instance.id = null
          return new_instance
        },

        insert_instance(index, instance, update) {
          // Use index = ` -1 ` if New instnace

          // use splice to update, directly updating propery doesn't detect change vue js stuff
          //  question, this extra update step is only needed for the attribute stuff right?

          if (!update.list_type || update.list_type == "default") {
            if (index === -1){
              this.instance_list.push(instance)
            } else {
              this.instance_list.splice(index, 1, instance)
            }
            // update instance buffer
            if (this.video_mode == true)  {
              if (this.current_frame in this.instance_buffer_dict){
                // Updating existing reference
                if (index === -1){
                  this.instance_buffer_dict[this.current_frame].push(instance)
                } else {
                  this.instance_buffer_dict[this.current_frame].splice(index, 1, instance)
                }
              }
              else{
                // This is ok ONLY becuase we already checked that the reference to instance_list
                // did not exist
                this.instance_buffer_dict[this.current_frame] = [instance]
              }
            }

          }
          if (update.list_type == "gold_standard") {
            this.gold_standard_file.instance_list.splice(index, 1, instance)
          }

          return true

        },
        created: function () {

          this.update_user_settings_from_store();
          this.command_manager = new CommandManagerAnnotationCore();
          // Initial File Set
          if(this.$props.file){
            this.on_change_current_file();
          }
          else if(this.$props.task){
            this.on_change_current_task();
          }
        },

        update_user_settings_from_store() {
          if (this.$store.state.user.settings.studio_left_nav_width) {
            this.label_settings.left_nav_width = this.$store.state.user.settings.studio_left_nav_width
          }
        },

        update_window_size_from_listener() {
          // function so we can destroy it after
          this.window_width_from_listener = window.innerWidth
          this.window_height_from_listener = window.innerHeight
        },

        restore_event_listeners: function( ) {
          this.remove_event_listeners()
          this.add_event_listeners()
        },

        remove_event_listeners() {
          /*
       * Careful needs to match ie up and up || down and down
       *
       */

          // global
          window.removeEventListener('beforeunload', this.warn_user_unload)
          document.removeEventListener('mousedown', this.mouse_events_global_down)
          window.removeEventListener('keydown', this.keyboard_events_global_down)

          window.removeEventListener('keyup', this.keyboard_events_global_up)
          window.removeEventListener('resize', this.update_window_size_from_listener)

          // local
          this.annotation_area.removeEventListener('keydown', this.keyboard_events_local_down)
          this.annotation_area.removeEventListener('keyup', this.keyboard_events_local_up)
          this.canvas_wrapper.removeEventListener('wheel', this.wheel)
        },

        add_event_listeners() {

          /* Can call getEventListeners(window)
       * to get list of them
       *
       */

          this.canvas_wrapper = document.getElementById("canvas_wrapper")
          // rather have canvas_wrapper inside this functionsss in case it needs to "refresh" it

          this.annotation_area = document.getElementById("annotation")
          window.addEventListener('beforeunload', this.warn_user_unload)
          this.annotation_area.addEventListener('keyup', this.keyboard_events_local_up);
          this.annotation_area.addEventListener('keydown', this.keyboard_events_local_down);
          window.addEventListener('keydown', this.keyboard_events_global_down);
          document.addEventListener('mousedown', this.mouse_events_global_down);
          window.addEventListener('keyup', this.keyboard_events_global_up);
          window.addEventListener('resize', this.update_window_size_from_listener)

          this.update_window_size_from_listener()      // Initial size (resize doesn't fire on first load)

          this.canvas_wrapper.addEventListener('wheel', this.wheel);


        },

        async mounted() {
          this.canvas_mouse_tools = new CanvasMouseTools(
            this.mouse_position,
            this.canvas_translate,
          )
          //console.debug("mounted")
          // Reset issue mode
          this.$store.commit('set_instance_select_for_issue', false);
          this.$store.commit('set_instance_select_for_merge', false);
          this.$store.commit('set_view_issue_mode', false);
          this.$store.commit('set_user_is_typing_or_menu_open', false)
          this.add_event_listeners()
          this.fetch_model_run_list();
          this.fetch_instance_template();

          this.update_canvas()

          // assumes canvas wrapper available
          this.canvas_wrapper.style.display = ""

          var self = this
          this.get_instances_watcher = this.$store.watch((state) => {
              return this.$store.state.annotation_state.get_instances
            },
            (new_val, old_val) => {
              self.get_instances()
            },
          )

          this.refresh_video_buffer_watcher = this.$store.watch((state) => {
              return this.$store.state.annotation_state.refresh_video_buffer
            },(new_val, old_val) => {
              self.get_video_instance_buffer()
            },
          )

          this.save_watcher = this.$store.watch((state) => {
              return this.$store.state.annotation_state.save
            },
            (new_val, old_val) => {
              self.save()
            },
          )
          this.save_and_complete_watcher = this.$store.watch((state) => {
              return this.$store.state.annotation_state.save_and_complete
            },
            (new_val, old_val) => {
              self.save(true)
            },
          )


          if (this.$props.task || this.job_id) {
            this.task_mode_mounted()
          }

          this.start_autosave();    // created() gets called again when the task ID changes eg "go to next"


        },
        fetch_model_run_list: async function(){
          if(!this.$props.model_run_id_list){
            return
          }
          if(this.$props.model_run_id_list.length === 0){
            return
          }

          this.loading = true
          try{
            const response = await axios.post(
              `/api/v1/project/${this.$props.project_string_id}/model-runs/list`,
              {
                id_list: this.$props.model_run_id_list.map(x => parseInt(x, 10))
              }
            );
            if (response.data['model_run_list'] != undefined) {
              this.model_run_list = response.data.model_run_list;
              for(let i = 0; i < this.model_run_list.length; i++){
                this.model_run_list[i].color = this.model_run_color_list[i];
              }
            }
          }
          catch (error) {
            console.error(error);
          }
          finally {
            this.loading = false;
          }
        },
        task_mode_mounted: function () {


          // Default because can be timing issues with how it loads new value
          // from media_core

          this.media_core_height = 0
          this.show_default_navigation = false


        },
        go_to_login: function () {
          this.$router.push('/user/login')
        },

        go_to_projects: function () {
          this.$router.push('/projects')
        },

        // WIP doesn't quite refresh as expected
        go_to_file: function () {
          this.$router.push('/file/' + this.user_requested_file_id)
          this.get_media()  //

        },

        page_refresh: function () {
          this.created()
          this.mounted()
          this.$store.commit('init_label_refresh')

        },

        async refresh_all_instances(){
          await this.get_instances();
          this.update_canvas();
          this.$forceUpdate();

        },
        update_canvas: async function () {
          this.refresh = new Date();
          this.canvas_element = document.getElementById("my_canvas")
          this.canvas_element_ctx = this.canvas_element.getContext('2d');

          this.$forceUpdate();
        },

        change_instance_type: function ($event) {
          this.instance_type = $event
          this.current_polygon_point_list = []
          this.cuboid_face_hover = undefined;
          this.$store.commit('finish_draw')
        },

        validate_sequences: function() {

          /* Constraints
       *    Check if the sequence already exists in the instance list
       *
       * In prior contexts we had this runnning "after the fact"
       * so it was trying to detect 2
       * now we are running it "on demand" so a single one is wrong.
       * TODO consider optimizing this by returning the moment count == 1
       * I don't want to jump to this yet in case there's a need for the prior
       * setup.
       *
       *  strange we did not seem
       * to be checking the single file flag ones
       */

          if (this.current_label_file.label.default_sequences_to_single_frame) {
            return true
          }

          let count = 0

          for (let i in this.instance_list) {
            if (this.instance_list[i].soft_delete == true) {
              continue
            }
            // careful need to check on label id too
            if (this.instance_list[i].number == this.current_sequence_from_sequence_component.number &&
              this.instance_list[i].label_file_id == this.current_label_file.id) {

              count += 1
            }
          }

          // We allow 2,
          // But if we run check proactively then only can be one.
          if (count != 0) {
            this.snackbar_warning = true
            this.snackbar_warning_text = "Edit existing Instance, or go to a new frame, or create a new Sequence."
            return false
          }
          else {
            return true
          }
        },

        /*  We accept it's possible
       *  to have a sequence selected that's "wrong"
       *  and we validate this at save instead of trying
       *  to prevent it. Because,
       *  trying to prevent it creates the ill posed problem
       *  of guessing what sequence a user wants,
       *  where as this makes it simple for the user, they
       *  are on whatever sequence they select.
       */

        video_animation_unit_of_work: function (image) {
          /*
       *  From animation in the context of getting
       *  passed an image from a video
       *  And NOT for pulling a single frame
       *
       *
       *  Refresh workaround note:
       *    As of Jan 16, 2020 it appears to not be
       *    since perhaps instance_list is changing?
       *
       *    Question, is "refresh" a heavy operation?
       *    the date thing shouldn't be, but not clear if the
       *    settimeout and/or it's relation to animation from does
       *    anthing?
       *
       */

          this.html_image = image
          //this.trigger_refresh_with_delay()
          // todo getting buffer should be in Video component
          // also this could be a lot smarter ie getting instances
          // while still some buffer left etc.
          if (this.current_frame in this.instance_buffer_dict) {
            // We want to initialize the buffer dict before assinging the pointer on instance_list.
            this.initialize_instance_buffer_dict_frame(this.current_frame)
            // IMPORTANT  This is a POINTER not a new object. This is a critical assumption.
            // See https://docs.google.com/document/d/1KkpccWaCoiVWkiit8W_F5xlH0Ap_9j4hWduZteU4nxE/edit
            this.instance_list = this.instance_buffer_dict[this.current_frame];
          } else {
            this.video_pause = Date.now()

            this.get_instances(true)
          }
          this.add_override_colors_for_model_runs();
        },

        toggle_pause_play: function () {
          if (this.video_playing) {
            this.video_pause = Date.now()
          } else {
            this.video_play = Date.now()
          }
        },

        seeking_update: function (seeking) {
          this.seeking = seeking
        },

        ghost_refresh_instances: function () {
          this.ghost_instance_list = []
          if (!this.sequence_list_local_copy) { return }

          let keyframes_to_sequences = this.build_keyframes_to_sequences_dict()

          this.populate_ghost_list_with_most_recent_instances_from_keyframes(keyframes_to_sequences)

          this.may_fire_user_ghost_canvas_available_alert()

        },

        may_fire_user_ghost_canvas_available_alert: function () {
          if (this.$store.state.user.settings.hide_ghost_canvas_available_alert == true) {
            return
          }
          if (this.ghost_instance_list.length >= 1) {
            this.canvas_alert_x = this.mouse_position.x
            this.canvas_alert_y = this.mouse_position.y
            this.$refs.ghost_canvas_available_alert.show_alert();
          }
        },
        build_keyframes_to_sequences_dict: function () {
          /*
       * build dict of keyframes with sequences
       * context that searching each instance_list might as well do all at once.
       * returns example like
       * frame: [list of sequence ids]
       * 351: [3619]
         355: [3620, 3621]
       *
       */
          let keyframes_to_sequences = {}

          for (let sequence of this.sequence_list_local_copy){
            if (!sequence.keyframe_list) { return }
            if (!sequence.keyframe_list.frame_number_list) { return }

            let frame_number_list = sequence.keyframe_list.frame_number_list
            let last_keyframe = frame_number_list[frame_number_list.length - 1]
            if (last_keyframe == undefined) {continue}  // careful, 0th frame is ok

            if(!keyframes_to_sequences[last_keyframe]) {
              keyframes_to_sequences[last_keyframe] = [sequence.number];
            } else {
              keyframes_to_sequences[last_keyframe].push(sequence.number);
            }
          }
          return keyframes_to_sequences
        },

        ghost_determine_if_no_conflicts_with_existing: function (ghost_instance) {
          for (let existing_instance of this.instance_list){
            if (existing_instance.sequence_id == ghost_instance.sequence_id) {
              return false
            }
            if (existing_instance.label_file_id == ghost_instance.label_file_id &&
              existing_instance.number == ghost_instance.number) {
              return false
            }
          }
          return true
        },

        populate_ghost_list_with_most_recent_instances_from_keyframes: function(keyframes_to_sequences){
          if(!keyframes_to_sequences){
            return
          }
          for (const [keyframe, sequence_numbers] of Object.entries(keyframes_to_sequences)){

            let instance_list = this.instance_buffer_dict[keyframe];
            if (!instance_list) { continue }

            for (let instance of instance_list) {
              if (sequence_numbers.includes(instance.number)) {

                // if it's the last object then we don't show ghost
                if (instance.pause_object == true) { continue }

                if (this.ghost_determine_if_no_conflicts_with_existing(instance) == false) {
                  continue
                }

                this.duplicate_instance_into_ghost_list(instance)
              }
            }
          }
        },

        duplicate_instance_into_ghost_list: function (instance){
          if (!instance) { return }
          let instance_clipboard = this.duplicate_instance(instance);
          instance_clipboard.id = null
          instance_clipboard.created_time = null  //
          instance_clipboard.creation_ref_id = null // we expect this will be set once user accepts it
          this.ghost_instance_list.push(instance_clipboard)
        },


        change_frame_from_video_event: function (url) {
          /* Careful to call get_instances() since this handles
       * if we are on a keyframe and  don't need to call instance buffer
       * this method supercedes the old video_file_update()
       */
          this.get_instances()
          this.ghost_refresh_instances()
          if (url) {
            this.add_image_process(url)
          }
        },

        add_image_process: function (url) {
          /*
       * Question, is it correct this is ONLY for
       * pulling the frame? ie this will NOT be called during video play?
       *
       */

          var self = this
          self.addImageProcess(url).then(image => {

            // this gets instances if it needs to
            //  (ie the instance buffer)
            self.html_image = image

            self.canvas_wrapper.style.display = ""
            self.loading = false

            // Jan 15, 2020 Did we not have this prior??
            self.trigger_refresh_with_delay()
          })
        },

        current_file_updates: async function (file) {
          if(!file){
            throw new Error('Provide file.')
          }
          if (file.type == "image") {
            this.video_mode = false

            this.canvas_width = file.image.width
            this.canvas_height = file.image.height

            var self = this
            this.addImageProcess(file.image.url_signed).then(new_image => {
              self.html_image = new_image
              self.loading = false
              self.refresh = Date.now()

            })
          }

          if (file.type == "video") {
            this.video_mode = true
            this.current_video = file.video
            this.current_video_file_id = file.id

            this.canvas_width = file.video.width
            this.canvas_height = file.video.height

            this.$refs.video_controllers.reset_cache();
            await this.$refs.video_controllers.get_video_single_image();
          }
        },
        // todo why not make this part of rest of event stuff
        wheel: function (event) {

          if (this.show_context_menu == true) { return } // becasue could have own menus that scroll

          this.zoom_wheel_scroll_canvas_transform_update(event)

        },

        clamp_values: function (val, min, max) {
          //https://stackoverflow.com/questions/11409895/whats-the-most-elegant-way-to-cap-a-number-to-a-segment
          return Math.min(Math.max(val, min), max)
        },

        zoom_wheel_scroll_canvas_transform_update: function (event) {

          this.hide_context_menu()    // context of position updating looks funny if it stays

          this.canvas_scale_local = this.canvas_mouse_tools.zoom_wheel_scroll_canvas_transform_update(
            event, this.canvas_scale_local)

          this.canvas_translate = this.canvas_mouse_tools.zoom_wheel_canvas_translate(
            event, this.canvas_scale_local)
        },

        update_label_file_visible: function (label_file) {

          if (label_file.is_visible == true){
            let index = this.hidden_label_id_list.indexOf(label_file.id)
            this.hidden_label_id_list.splice(index, 1)
          }
          else {
            this.hidden_label_id_list.push(label_file.id)
          }
        },

        issue_hover_update: function (index: Number) {
          if(index != null){
            this.issue_hover_index = parseInt(index)
          }
          else{
            this.issue_hover_index = null;
          }

        },
        cuboid_face_hover_update: function(cuboid_face){
          this.cuboid_face_hover = cuboid_face;
        },

        ghost_instance_hover_update: function (index: Number, type : String, figure_id: String) {
          //if (this.lock_point_hover_change == true) {return}
          if (index != null) {
            this.ghost_instance_hover_index = parseInt(index)
            this.ghost_instance_hover_type = type   // ie polygon, box, etc.
          }
          else{
            this.ghost_instance_hover_index = null;
            this.ghost_instance_hover_type = null;
          }

        },

        instance_hover_update: function (
            index: Number,
            type : String,
            figure_id: String,
            instance_rotate_control_mouse_hover: Boolean
            ) {

          if (this.lock_point_hover_change == true) {return}
          // important, we don't change the value if it's locked
          // otherwise it's easy for user to get "off" of the point they want

          if (index != null) {
            this.instance_hover_index = parseInt(index)
            this.hovered_figure_id = figure_id;
            this.instance_hover_type = type   // ie polygon, box, etc.
            this.instance_rotate_control_mouse_hover = instance_rotate_control_mouse_hover
          }
          else{
            this.instance_hover_index = null;
            this.hovered_figure_id = null;
            this.instance_hover_type = null;
            this.instance_rotate_control_mouse_hover = null
          }
        },

        remove_file_request(file) {

          if (file.type == "image" || file.type == "video") {

            for (var i in this.File_list) {
              if (this.File_list[i].id == file.id) {
                this.File_list.splice(i, 1)


                if (this.File_list.length > 0) {
                  if (this.File_list[i].id == this.$props.file.id) {
                    this.$props.file = this.File_list[0]
                    this.change_file("none", this.File_list[0])
                  }
                }

              }
            }
          }
        },
        delete_single_instance: function (index: Number) {

          /* Given an index of instance in instance_list delete it
       *
       * Shorthand wrapper around instance_update
       *
       * ie try with selecting annotation_core
       * go to edit mode and:
       * $vm0.delete_single_instance($vm0.instance_hover_index)
       */

          this.instance_update({
            index: index,
            mode: "delete"
          })

        },

        delete_instance: function () {

          if (this.$props.view_only_mode == true) { return }

          for (var i in this.instance_list) {
            if (this.instance_list[i].selected == true) {
              this.delete_single_instance(i);
            }
          }
        },

        request_boxes_refresh() {
          this.get_instances()

        },

        change_current_label_file_template: function (label_file) {

          this.current_label_file = label_file
          if (this.instance_type == "tag") {
            this.insert_tag_type()
          }

        },

        insert_tag_type: function() {
          this.push_instance_to_instance_list_and_buffer(this.current_instance, this.current_frame)
        },

        add_instance_to_frame_buffer: function(instance, frame_number){
          if(!this.video_mode){return}
          if (frame_number == undefined) {
            throw "frame number undefined in video mode (push_instance_to_instance_list_and_buffer)"
          }
          if (instance == undefined) {
            throw "instance is undefined in add_instance_to_frame_buffer()"
          }
          instance.creation_ref_id = uuidv4();
          instance.client_created_time = new Date().toISOString();
          if(this.instance_buffer_dict[frame_number]){
            this.instance_buffer_dict[frame_number].push(instance)
          }
          else{
            this.instance_buffer_dict[frame_number] = [instance]
          }

          // Set Metadata to manage saving frames
          if(this.instance_buffer_metadata[frame_number]){
            this.instance_buffer_metadata[frame_number].pending_save = true
          }
          else{
            this.instance_buffer_metadata[frame_number] = {pending_save: true}
          }

        },

        // TODO rename? / refactor? in contect of more awareness of ref/by value for buffer

        push_instance_to_instance_list_and_buffer: async function(
          instance = undefined,
          frame_number = undefined) {

          if (this.video_mode == true && frame_number == undefined) {
            throw "frame number undefined in video mode (push_instance_to_instance_list)"
          }
          let instance_to_push = this.current_instance;

          if(instance != undefined){
            instance_to_push = instance
          }
          instance_to_push.creation_ref_id = uuidv4();
          instance_to_push.client_created_time = new Date().toISOString();

          if (!instance_to_push.change_source) {
            instance_to_push.change_source = 'ui_diffgram_frontend';
          }

          this.instance_list.push(instance_to_push)

          this.has_changed = true;

          if (this.video_mode == true) {
            let was_saved = await this.save();
            if(!was_saved){
              // If instance was not saved, because of concurrent saves. We still set it to pending
              this.has_changed = true;
            }
          }
          // polygon point thing applies to a few different types
          // so for now just run it

          this.current_polygon_point_list = [] // reset list

          // Caution, this feeds into current instance, so it can look like it's dramatically not working
          // if this is set incorrectly.
          this.is_actively_drawing = false


        },

        point_is_intersecting_circle: function (mouse, point, radius = 8) {
          // Careful this is effected by scale
          // bool, true if point if intersecting circle
          let radius_scaled = radius / this.canvas_transform['canvas_scale_combined']
          const result = Math.sqrt((point.x - mouse.x) ** 2 + (mouse.y - point.y) ** 2) < radius_scaled;  // < number == circle.radius
          return result
        },
        detect_hover_on_curve: function(){
          if(!this.instance_list){ return }
          if(this.lock_point_hover_change){return}
          if(this.draw_mode){return}

          let instance_index = this.instance_hover_index;
          let instance = this.instance_list[instance_index];
          if(instance && instance.type === 'curve'){
            this.canvas_element.style.cursor = 'all-scroll'
          }
        },
        detect_hover_on_curve_control_points: function(){
          if(!this.instance_list){ return }
          if(this.lock_point_hover_change){return}
          //caution this needs to be before we change the hover point

          let instance_index = this.instance_hover_index;
          let instance = this.instance_list[instance_index];

          if (!instance || instance.type !== 'curve'){
            this.curve_hovered_point = undefined;
            return
          }

          if(this.point_is_intersecting_circle(this.mouse_position, instance.p1, 10)){
            this.curve_hovered_point = 'p1'
            this.canvas_element.style.cursor = 'all-scroll'
          }
          if(this.point_is_intersecting_circle(this.mouse_position, instance.cp, 10)){
            this.curve_hovered_point = 'cp'
            this.canvas_element.style.cursor = 'all-scroll'
          }
          if(this.point_is_intersecting_circle(this.mouse_position, instance.p2, 10)){
            this.curve_hovered_point = 'p2'
            this.canvas_element.style.cursor = 'all-scroll'
          }
        },
        detect_hover_on_ellipse_corners: function () {
          // not happy with this name, maybe something more along the lines of
          // determine which point in the cuboid we are near?
          // or something...
          if(this.is_actively_resizing){
            return
          }
          if(this.instance_select_for_issue){return}
          if(this.instance_select_for_merge){return}
          if(!this.instance_list){return}
          // avoid having a check for every point?
          let instance_index = this.instance_hover_index;
          let instance = this.instance_list[instance_index]
          // If theres no hovered instance instance try to get the selected instance.
          if(!instance || instance.type !== 'ellipse'){
            instance = this.selected_instance;
            instance_index = this.selected_instance_index;
          }


          // Fallback case when we are currently resizing on an instance.
          if (!instance || instance.type !== 'ellipse'){
            instance = this.ellipse_hovered_instance;
            instance_index = this.ellipse_hovered_instance_index;
            if(instance){
              instance.selected = true;
            }
            return
          }

          if (!instance || instance.type !== 'ellipse'){
            this.ellipse_hovered_corner = undefined;
            return
          }
          let result = undefined;
          let result_key = undefined;
          for(let key in instance.corners){
            if(this.point_is_intersecting_circle(this.mouse_position, instance.corners[key], 16)){
              result = instance.corners[key]
              result_key = key;
            }
          }

          this.ellipse_hovered_corner_key = result_key;


          this.ellipse_hovered_instance = instance;
          this.ellipse_hovered_instance_index = instance_index;

          // Set Mouse Style and hover data key.
          if(result && (result_key === 'right' || result_key === 'left')){
            this.ellipse_hovered_corner = result;
            this.canvas_element.style.cursor = 'col-resize'
          }

          if(result && result_key === 'top_right'){
            this.ellipse_hovered_corner = result;
            this.canvas_element.style.cursor = 'ne-resize'
          }
          if(result && result_key === 'bot_right'){
            this.ellipse_hovered_corner = result;
            this.canvas_element.style.cursor = 'se-resize'
          }
          if(result && result_key === 'top_left'){
            this.ellipse_hovered_corner = result;
            this.canvas_element.style.cursor = 'nw-resize'
          }
          if(result && result_key === 'bot_left'){
            this.ellipse_hovered_corner = result;
            this.canvas_element.style.cursor = 'sw-resize'
          }

          if(result && (result_key === 'bot' || result_key === 'top')){
            this.ellipse_hovered_corner = result;
            this.canvas_element.style.cursor = 'row-resize'
          }
          if(result && (result_key === 'rotate')){
            this.ellipse_hovered_corner = result;
            this.canvas_element.style.cursor = 'help'
          }
          if(!result){
            this.ellipse_hovered_corner = undefined;
          }

          return result;
        },

        detect_hover_on_cuboid_corners: function () {
          if(!this.selected_instance){ return}
          if(this.selected_instance.type != 'cuboid'){ return}
          // not happy with this name, maybe something more along the lines of
          // determine which point in the cuboid we are near?
          // or something...

          // avoid having a check for every point?
          let instance = this.selected_instance

          let face_result = null
          face_result = this.is_on_cuboid_corner(instance.front_face, 'front_face')


          // false means none found, if is found we skip to save computation
          // null means force rear was trigged
          // this setup feels a bit awkward
          if (face_result == false || face_result == null) {

            face_result = this.is_on_cuboid_corner(instance.rear_face, 'rear_face')
          }

        },

        build_middle_point: function (a_point, b_point) {

          return {
            'x' : (a_point.x + b_point.x) / 2,
            'y': (a_point.y + b_point.y) / 2
          }

        },

        is_on_cuboid_corner: function (face, name) {
          if(this.is_moving_cuboid_corner){return}
          // again not happy with name
          // trying to get accross it takes a face with multiple points
          // and then sees if any are intersecting
          // then does current expected stuff
          // returns true if found to allow early exit
          for (let key in face) {
            if(key ==='width' || key === 'height'){
              continue
            }
            // corners
            if (this.point_is_intersecting_circle(this.mouse_position, face[key], 12)) {
              this.canvas_element.style.cursor = 'all-scroll'
              let cuboid_corner_move_point = {}
              cuboid_corner_move_point['point'] = key
              cuboid_corner_move_point['face'] = name
              cuboid_corner_move_point['type'] = 'corner'
              this.cuboid_corner_move_point = cuboid_corner_move_point
              return true

            }
          }
          this.cuboid_corner_move_point = {};
          return false

        },

        determine_movement_point_for_box: function (instance: Object) {
          /*
       * Keep in mind these concepts can be realtive too right
       * like "max" from which side etc. can flip if I recall right
       *
       * See move_box_literal_points for where this gets used
       *
       * Not sure if we need to invert the resize things
       * or if we should use different ones.
       */

          if (instance.type != "box" ||
            this.lock_point_hover_change == true) {
            return false
          }

          // where x == 0th index y == 1st index, string name of point 2nd index
          let point_list = [
            [instance.x_min, instance.y_min, "x_min_y_min", "nwse-resize"], //north east south west
            [instance.x_max, instance.y_min, "x_max_y_min", "nesw-resize"], // see https://www.w3schools.com/cssref/pr_class_cursor.asp
            [instance.x_min, instance.y_max, "x_min_y_max", "nesw-resize"],
            [instance.x_max, instance.y_max, "x_max_y_max", "nwse-resize"],
          ]

          for (let point of point_list) {

            let intersection = this.point_is_intersecting_circle(
              this.mouse_position, { 'x': point[0], 'y': point[1] })

            if (intersection == true) {
              this.box_edit_point_hover = point[2]
              if(this.view_issue_mode){
                // When viewing an issue we will not allow moving/resizing of instances
                this.canvas_element.style.cursor = 'not-allowed'
              }
              else{
                this.canvas_element.style.cursor = point[3]
              }

              return true
            }
          }

          /*
       * Inside the box but not on a corner detection,
       * we assume we are in the context of a box,
       * ie because we have a instance_hover_index SO
       * if we are in a box, and NOT intersecting a "special"
       * point like a corner, default is inside the whole box right???
       *
       */
          this.box_edit_point_hover = "not_intersecting_special_points"

          this.canvas_element.style.cursor = 'pointer'



          // no intersection found
          // not clear what this would be used for....
          return false

        },
        find_midpoint_index: function(instance, midpoints_polygon){
          let midpoint_hover = undefined;
          let count = 0;

          for(const point of midpoints_polygon){
            // TODO use user set param here
            let result = this.point_is_intersecting_circle(
              this.mouse_position,
              point,
              parseInt(this.label_settings.vertex_size * 4)
            )

            if(result){
              midpoint_hover = count;
              this.canvas_element.style.cursor = 'all-scroll'
            }
            count += 1;
          }
          if(midpoint_hover != undefined){
            instance.midpoint_hover = midpoint_hover

            this.instance_list.splice(this.selected_instance_index, 1, instance);
          }
          else{
            instance.midpoint_hover = undefined;
          }
          return midpoint_hover
        },
        detect_hover_polygon_midpoints: function(){
          // https://diffgram.teamwork.com/#/tasks/23511334

          if(!this.selected_instance){return}
          const instance = this.selected_instance
          if(!instance.selected){return}
          if (!instance.midpoints_polygon ) {return }

          // Check for hover on any middle point
          let midpoints_polygon = instance.midpoints_polygon;
          if(!Array.isArray(midpoints_polygon)){
            for(let figure_id of Object.keys(midpoints_polygon)){
              let figure_midpoints = midpoints_polygon[figure_id]
              let midpoint_hovered_point = this.find_midpoint_index(instance, figure_midpoints)
              if(midpoint_hovered_point != undefined){
                break
              }
            }
          }
          else{
            this.find_midpoint_index(instance, midpoints_polygon)
          }


        },
        detect_other_polygon_points: function(){
          if(!this.is_actively_drawing){return}
          if(!this.instance_type == 'polygon'){return}
          const polygons_list = this.instance_list.filter(x => x.type == 'polygon');

          for(const polygon of polygons_list){
            for (const point of polygon.points){
              if(this.point_is_intersecting_circle(this.mouse_position, point, 8)){
                point.hovered_while_drawing = true;
              }
              else{
                point.hovered_while_drawing = false;
              }

            }
          }
        },
        // TODO clarify this does more than update styling
        update_mouse_style: function () {

          if (this.$props.view_only_mode == true) { return }


          if (this.draw_mode == false) {

            if (this.lock_point_hover_change == false) {
              this.canvas_element.style.cursor = 'default'
            }
            // TODO handle if visible



            this.detect_hover_on_cuboid_corners()

            this.detect_hover_on_ellipse_corners()

            this.detect_hover_on_curve();
            this.detect_hover_on_curve_control_points();

            this.detect_if_movement_string_update_needed_for_box()

            this.detect_nearest_polygon_point();
            this.detect_hover_polygon_midpoints();

            this.detect_issue_hover();

            this.style_mouse_if_rotation()


          } else {
            this.canvas_element.style.cursor = 'default'
          }
        },

        style_mouse_if_rotation: function () {
          if(this.instance_rotate_control_mouse_hover == true) {
            this.canvas_element.style.cursor = 'help'
          }
        },
        detect_issue_hover: function(){
          if (this.issue_hover_index != undefined && !isNaN(this.issue_hover_index)) {
            this.canvas_element.style.cursor = 'pointer'
          }
        },
        detect_if_movement_string_update_needed_for_box: function () {

          if (this.instance_hover_index != undefined && this.instance_hover_type == 'box') {

            let instance = this.instance_list[this.instance_hover_index]

            // CAREFUL here we want to compare the transformed mouse point
            // to the actual boxes

            if (instance != null) {
              if (!this.hidden_label_id_list.includes(instance.label_file_id)) {
                this.determine_movement_point_for_box(instance)
              }
            }
          }

        },
        check_polygon_intersection_on_points: function(instance, points){
          for (var j in points) {
            let result = this.point_is_intersecting_circle(this.mouse_position, instance['points'][j])

            if (result == true) {
              this.canvas_element.style.cursor = 'all-scroll'
              this.polygon_point_hover_index = parseInt(j)
              return true
            }
          }
          return false
        },
        detect_nearest_polygon_point: function () {
          /*
         * Caution updates mouse cursor as side effect.
         */

          // TODO find nearest point
          // ie if it's interesting "point" type instances or lines?
          // could just naively loop over it but feels like there has to to be another way
          // maybe when we are rendering each thing, if the mouse is over it then
          // could do that? or something more generic here

          /* So what's interesting is that at the moment this runs twice
         * for a singular point - but it's "generic"
         * in the sense that it still works
         * This could probably be similar for lines too?
         */

          // TODO get a flag from polygon multiple to detect if
          // Should change to pointer here
          this.polygon_point_hover_index = null

          if (this.instance_hover_index != undefined && ['polygon', 'line', 'point'].includes(this.instance_hover_type)) {

            var instance = this.instance_list[this.instance_hover_index]
          }


          if (instance != undefined) {
            let has_figures = instance.points.filter(p => p.figure_id != undefined).length > 0;
            if (!this.hidden_label_id_list.includes(instance.label_file_id)) {

              // Polygon might have multiple figures.
              if(!has_figures){
                this.check_polygon_intersection_on_points(instance, instance.points)
              }
              else{
                let figures_list = [];
                for(const p of instance.points){
                  if(!figures_list.includes(p.figure_id)){
                    figures_list.push(p.figure_id)
                  }
                }
                for(const figure_id of figures_list){
                  let points = instance.points.filter(p => p.figure_id === figure_id)
                  let intersects = this.check_polygon_intersection_on_points(instance, points);
                  if (intersects){
                    break
                  }
                }
              }

            }
          }
        },
        select_issue: function(){
          if (this.$props.view_only_mode == true) { return }
          if (this.issue_hover_index == undefined || isNaN(this.issue_hover_index)) { return }    // careful 0 index is ok
          if (!this.issues_list[this.issue_hover_index]) { return }
          if( this.draw_mode ){ return }
          if( this.view_issue_mode && this.instance_select_for_issue ){ return }
          if( this.view_issue_mode && this.instance_select_for_merge ){ return }
          const issue = this.issues_list[this.issue_hover_index];
          this.open_view_edit_panel(issue);
        },

        update_instances_to_merge: function(instance_to_select){
          if(instance_to_select.selected){
            this.instances_to_merge.push(instance_to_select)
          }
          else{
            let index = this.instances_to_merge.indexOf(instance_to_select)
            if (index > -1) {
              this.instances_to_merge.splice(index, 1)
            }

          }

        },
        is_allowed_instance_to_merge: function(instance_to_select){
          if(this.parent_merge_instance.id === instance_to_select.id){
            return false
          }
          if(this.parent_merge_instance.label_file_id !== instance_to_select.label_file_id){
            return false
          }

          if(this.parent_merge_instance.type !== instance_to_select.type){
            return false
          }
          return true
        },

        select_something: function () {

          if (this.view_only_mode == true) { return }
          if (this.ellipse_hovered_corner_key) { return }
          if (this.selected_instance && this.selected_instance.midpoint_hover != undefined) { return }
          if (this.instance_hover_index === undefined && this.issue_hover_index === undefined) { return }    // careful 0 index is ok
          if( this.draw_mode ){ return }
          if( this.view_issue_mode && !this.instance_select_for_issue ){ return }

          this.request_change_current_instance = this.instance_hover_index
          this.trigger_refresh_current_instance = Date.now()    // decouple, for case of file changing but instance list being the same index

          if (this.label_settings.allow_multiple_instance_select == false) {
            this.clear_selected()
          }
          const instance_to_select =  this.instance_list[this.instance_hover_index];
          if(this.instance_select_for_merge){
            // Allow only selection of polygon with the same label file ID.
            if(!this.is_allowed_instance_to_merge(instance_to_select)){
              return
            }
          }

          if(instance_to_select){
            instance_to_select.selected = !instance_to_select.selected;
            instance_to_select.status = 'updated';
            Vue.set(this.instance_list, this.instance_hover_index, instance_to_select);
            if (this.box_edit_point_hover != null) {
              // Logic for selecting box data.
              instance_to_select.box_edit_point_hover = this.box_edit_point_hover;
            }
          }
          if(this.instance_select_for_merge){
            // Allow only selection of polygon with the same label file ID.
            this.update_instances_to_merge(instance_to_select)
          }


        },
        box_update_position: function (instance, i) {
          instance.width = instance.x_max - instance.x_min
          instance.height = instance.y_max - instance.y_min

          // Handle inverting origin point
          if (instance.x_max < instance.x_min) {
            let x_max_temp = instance.x_max
            instance.x_max = instance.x_min
            instance.x_min = x_max_temp
          }

          if (instance.y_max < instance.y_min) {
            let y_max_temp = instance.y_max
            instance.y_max = instance.y_min
            instance.y_min = y_max_temp
          }

          instance.status = 'updated'

          this.instance_list.splice(i, 1, instance)

        },

        move_curve: function(event){
          if (this.is_actively_resizing == false) {return}
          if(this.instance_hover_index == undefined){return}
          const instance = this.instance_list[this.instance_hover_index];
          if(instance.type !== 'curve'){ return }
          if(this.curve_hovered_point){
            let x_new = parseInt(this.mouse_position.x)
            let y_new = parseInt(this.mouse_position.y)
            const instance = this.instance_list[this.instance_hover_index];
            if(!this.original_edit_instance){
              this.original_edit_instance = {
                ...instance,
                p1: {...instance.p1},
                p2: {...instance.p2},
                cp: {...instance.cp}
              };
              this.original_edit_instance_index = this.instance_hover_index;
            }
            instance[this.curve_hovered_point].x = x_new
            instance[this.curve_hovered_point].y = y_new
          }
          else{
            // Move Entire curve
            let x_move = this.mouse_down_delta_event.x
            let y_move = this.mouse_down_delta_event.y
            instance.p1.x += x_move
            instance.p1.y += y_move

            instance.p2.x += x_move
            instance.p2.y += y_move

            instance.cp.x += x_move
            instance.cp.y += y_move
          }

          return true;
        },
        move_ellipse: function(event){
          if (this.is_actively_resizing == false) {
            return
          }
          if(!this.ellipse_hovered_corner_key && this.instance_hover_index == undefined){
            return
          }
          let x_move = this.mouse_down_delta_event.x
          let y_move = this.mouse_down_delta_event.y

          let instance = this.ellipse_hovered_instance;
          let instance_index = this.ellipse_hovered_instance_index;
          if(!instance){
            return
          }
          if(!this.original_edit_instance){
            this.original_edit_instance = {
              ...this.instance_list[instance_index],
              points: [...this.instance_list[instance_index].points.map(p => ({...p}))]
            };
            this.original_edit_instance_index = instance_index;
          }


          if(['right'].includes(this.ellipse_hovered_corner_key)){
            instance.width += x_move
          }
          if(['left'].includes(this.ellipse_hovered_corner_key)){
            instance.width -= x_move
          }
          if(['top'].includes(this.ellipse_hovered_corner_key)){
            instance.height -= y_move
          }
          if(['bot'].includes(this.ellipse_hovered_corner_key)){
            instance.height += y_move
          }
          if(['top_right'].includes(this.ellipse_hovered_corner_key)){
            instance.height -= y_move
            instance.width += x_move
          }
          if(['top_left'].includes(this.ellipse_hovered_corner_key)){
            instance.height -= y_move;
            instance.width -= x_move;
          }
          if(['bot_right'].includes(this.ellipse_hovered_corner_key)){
            instance.height += y_move;
            instance.width += x_move;
          }
          if(['bot_left'].includes(this.ellipse_hovered_corner_key)){
            instance.height += y_move;
            instance.width -= x_move;
          }

          if(['rotate'].includes(this.ellipse_hovered_corner_key)){
            instance.angle = this.get_angle_of_rotated_ellipse(instance);
          }

          // Translation

          if(this.instance_hover_index != undefined && !this.ellipse_hovered_corner_key){
            instance.center_x +=  x_move;
            instance.center_y +=  y_move;
            instance.center_x = parseInt(instance.center_x)
            instance.center_y = parseInt(instance.center_y)
          }

          instance.width = parseInt(instance.width)
          instance.height = parseInt(instance.height)
          instance.status = 'updated'
          this.instance_list.splice(instance_index, 1, instance);
          return true
        },

        get_angle_of_rotated_ellipse: function (instance) {
          // Read: https://math.stackexchange.com/questions/361412/finding-the-angle-between-three-points
          let a = instance.width;
          let b = instance.height;
          let t = Math.atan(-(b) *  Math.tan(0))/ (a);
          let centered_x = this.$ellipse.get_x_of_rotated_ellipse(t, instance, 0)
          let centered_y = this.$ellipse.get_y_of_rotated_ellipse(t, instance, 0)
          let A = {x: centered_x, y: centered_y}
          let B = {x: instance.center_x, y: instance.center_y}
          let C = {x: this.mouse_position.x, y: this.mouse_position.y}
          let BA = {x: A.x - B.x, y: A.y - B.y}
          let BC = {x: C.x - B.x, y: C.y - B.y}
          let BA_len = Math.sqrt((BA.x ** 2) + (BA.y ** 2))
          let BC_len = Math.sqrt((BC.x ** 2) + (BC.y ** 2))
          let BA_dot_BC = (BA.x * BC.x) + (BA.y * BC.y)
          let theta = Math.acos(BA_dot_BC / (BA_len * BC_len))
          let angle = 0;
          if(this.mouse_position.y < B.y){
            angle = (Math.PI /2)  - theta
          }
          else{
            if(theta <= (Math.PI/2) && theta > 0){
              // First cuadrant.
              angle = (Math.PI /2)  + theta
            }
            else if(theta > (Math.PI/2) && theta > 0){
              // Second Cuadrant
              angle = (Math.PI /2)  + theta
            }
          }
          return angle;
        },

        move_cuboid: function (event) {

          // Would prefer this to be part of general "move" something thing.
          if (this.is_actively_resizing == false) {
            return
          }
          let cuboid_did_move = false;
          let instance = this.instance_list[this.instance_hover_index]
          if(!instance){
            return
          }

          // Feel like this is duplicated with mouse style thing
          let force_move_face = false

          if (instance.cuboid_force_move_face == true || this.cuboid_force_move_face == true) {
            force_move_face = true
          }
          let x_move = this.mouse_down_delta_event.x
          let y_move = this.mouse_down_delta_event.y
          let type = this.cuboid_corner_move_point ? this.cuboid_corner_move_point.type : undefined
          let face_key = this.cuboid_corner_move_point ? this.cuboid_corner_move_point.face : undefined
          let point = this.cuboid_corner_move_point ? this.cuboid_corner_move_point.point : undefined
          let face;
          if (face_key) {
            face = instance[face_key]

          }
          if (this.cuboid_face_hover && type != 'corner') {
            cuboid_did_move = this.move_cuboid_face(this.cuboid_face_hover, x_move, y_move);

          }
          if (force_move_face == false) {

            if (type == 'corner' || this.is_moving_cuboid_corner) {
              if(face){

              }
              this.is_moving_cuboid_corner = true;
              cuboid_did_move = this.move_cuboid_edge(face, point, x_move, y_move);

            }
          }
          return cuboid_did_move
        },

        move_cuboid_face: function (hovered_face, x_move, y_move) {
          if(!['right', 'left', 'top', 'bottom', 'rear', 'front'].includes(hovered_face)){
            return false
          }

          const instance = this.instance_list[this.instance_hover_index];
          if(!this.original_edit_instance){
            this.original_edit_instance = {
              ...this.instance_list[this.polygon_click_index],
              points: [...this.instance_list[this.polygon_click_index].points.map(p => ({...p}))]
            };
            this.original_edit_instance.rear_face = {
              ...instance.rear_face,
              top_right: {...instance.rear_face.top_right},
              top_left: {...instance.rear_face.top_left},
              bot_left: {...instance.rear_face.bot_left},
              bot_right: {...instance.rear_face.bot_right},
            }
            this.original_edit_instance.front_face = {
              ...instance.front_face,
              top_right: {...instance.front_face.top_right},
              top_left: {...instance.front_face.top_left},
              bot_left: {...instance.front_face.bot_left},
              bot_right: {...instance.front_face.bot_right},
            }
            this.original_edit_instance_index = this.polygon_click_index;
          }
          let is_updated = true;
          if(hovered_face === 'rear'){
            const instance = this.instance_list[this.instance_hover_index]
            const face = instance['rear_face']
            for (let key in face) {
              if(key === 'height' || key === 'width'){
                continue;
              }
              let point = face[key]
              point.x += x_move
              point.y += y_move
              face[key] = point
            }
          }
          else if(hovered_face === 'right'){

            instance.front_face.top_right.x += x_move;
            instance.front_face.bot_right.x += x_move;
            instance.rear_face.bot_right.x += x_move;
            instance.rear_face.top_right.x += x_move;
            instance.rear_face.width = Math.abs(instance.rear_face.top_right.x - instance.rear_face.top_left.x);
            instance.front_face.width = Math.abs(instance.front_face.top_right.x - instance.front_face.top_left.x);
          }
          else if(hovered_face === 'left'){
            instance.front_face.top_left.x += x_move;
            instance.front_face.bot_left.x += x_move;
            instance.rear_face.bot_left.x += x_move;
            instance.rear_face.top_left.x += x_move;
            instance.rear_face.width = Math.abs(instance.rear_face.top_right.x - instance.rear_face.top_left.x);
            instance.front_face.width = Math.abs(instance.front_face.top_right.x - instance.front_face.top_left.x);
          }
          else if(hovered_face === 'bottom'){
            instance.front_face.bot_right.y += y_move;
            instance.front_face.bot_left.y += y_move;
            instance.rear_face.bot_right.y += y_move;
            instance.rear_face.bot_left.y += y_move;
            instance.rear_face.height = Math.abs(instance.rear_face.top_right.y - instance.rear_face.bot_right.y);
            instance.front_face.height = Math.abs(instance.front_face.top_right.y - instance.front_face.bot_right.y);
          }
          else if(hovered_face === 'top'){
            instance.front_face.top_right.y += y_move;
            instance.front_face.top_left.y += y_move;
            instance.rear_face.top_right.y += y_move;
            instance.rear_face.top_left.y += y_move;
            instance.rear_face.height = Math.abs(instance.rear_face.top_right.y - instance.rear_face.bot_right.y);
            instance.front_face.height = Math.abs(instance.front_face.top_right.y - instance.front_face.bot_right.y);
          }
          else{
            is_updated = false;
          }
          if(is_updated){
            instance.status = 'updated'
          }
          this.instance_list.splice(this.instance_hover_index, 1, instance)
          return is_updated;
        },

        move_cuboid_edge: function (face, edge_name, x_move, y_move) {
          /* Define which points are mapped to which edge
       * Given an edge, adjust all points in maping appropirately
       */
          const opposite_edge = this.opposite_edges_map[edge_name];
          const lateral_edges = this.lateral_edges[edge_name];
          const instance = this.instance_list[this.instance_hover_index];
          if(!this.original_edit_instance){
            this.original_edit_instance = {
              ...this.instance_list[this.polygon_click_index],
              points: [...this.instance_list[this.polygon_click_index].points.map(p => ({...p}))]
            };
            this.original_edit_instance.rear_face = {
              ...instance.rear_face,
              top_right: {...instance.rear_face.top_right},
              top_left: {...instance.rear_face.top_left},
              bot_left: {...instance.rear_face.bot_left},
              bot_right: {...instance.rear_face.bot_right},
            }
            this.original_edit_instance.front_face = {
              ...instance.front_face,
              top_right: {...instance.front_face.top_right},
              top_left: {...instance.front_face.top_left},
              bot_left: {...instance.front_face.bot_left},
              bot_right: {...instance.front_face.bot_right},
            }
            this.original_edit_instance_index = this.polygon_click_index;
          }
          // First Move select Point
          let selected_point = face[edge_name];
          selected_point.x += x_move;
          selected_point.y += y_move;
          selected_point.x = parseInt(selected_point.x, 10)
          selected_point.y = parseInt(selected_point.y, 10)
          face[edge_name] = selected_point;
          // Now move lateral edges.

          for(let i=0; i< lateral_edges.length; i++){
            const key = lateral_edges[i];
            let point = face[key]
            if(i === 0){
              point.x += x_move;
              point.x = parseInt(point.x, 10)
            }
            else{
              point.y += y_move;
              point.y = parseInt(point.y, 10)
            }
            face[key] = point;
          }

          instance.status = 'updated'
          this.instance_list.splice(this.instance_hover_index, 1, instance)
          return true

        },
        drag_polygon: function(event){
          if (this.is_actively_resizing == false) {return}
          if(this.polygon_point_click_index){return}
          if(this.instance_hover_index == undefined){return}
          if(this.instance_hover_type !== 'polygon'){return}
          const instance = this.instance_list[this.instance_hover_index]
          if(!instance.selected){return}
          if(!this.original_edit_instance){
            this.original_edit_instance = {
              ...this.instance_list[this.polygon_click_index],
              points: [...this.instance_list[this.polygon_click_index].points.map(p => ({...p}))]
            };
            this.original_edit_instance_index = this.polygon_click_index;
          }
          let points = instance.points;
          if(this.hovered_figure_id){
            points = instance.points.filter(p => p.figure_id === this.hovered_figure_id)
          }
          let x_move = this.mouse_down_delta_event.x
          let y_move = this.mouse_down_delta_event.y
          for(const point of points){
            point.x += x_move
            point.y += y_move
          }
          if(!this.hovered_figure_id){
            this.instance_list.splice(this.instance_hover_index, 1, instance);
          }
          else{
            let rest_of_points = instance.points.filter(p => p.figure_id !== this.hovered_figure_id);
            instance.points = points.concat(rest_of_points);
            this.instance_list.splice(this.instance_hover_index, 1, instance);
          }

          return true
        },

        ghost_clear_for_file_change_context: function()  {
          this.ghost_clear_hover_index()
          this.ghost_clear_list()
        },

        ghost_clear_hover_index: function () {
          this.ghost_instance_hover_index = null
          this.ghost_instance_hover_type = null
        },

        ghost_clear_list: function () {
          this.ghost_instance_list = []
        },

        ghost_promote_instance_to_actual: function (ghost_index) {
          this.has_changed = true  // otherwise user click event won't trigger change detection

          let instance = this.ghost_instance_list[ghost_index]
          this.add_instance_to_frame_buffer(instance, this.current_frame)    // this handles the creation_ref_id stuff too
          this.ghost_instance_list.splice(ghost_index, 1)   // remove from ghost list
        },

        ghost_may_promote_instance_to_actual: function () {
          if (this.label_settings.show_ghost_instances == false) { return }
          if (this.ghost_instance_hover_index != undefined) { // may be 0!
            this.instance_hover_index = this.ghost_instance_hover_index
            this.instance_hover_type = this.ghost_instance_hover_type
            this.ghost_promote_instance_to_actual(this.ghost_instance_hover_index)
            this.ghost_clear_hover_index()
          }
        },
        calculate_min_max_points: function(instance){
          if(!instance){
            return
          }
          if(['polygon', 'point'].includes(instance.type)){
            instance.x_min = Math.min(...instance.points.map(p => p.x))
            instance.y_min = Math.min(...instance.points.map(p => p.y))
            instance.x_max = Math.max(...instance.points.map(p => p.x))
            instance.y_max = Math.max(...instance.points.map(p => p.y))
          }
          else if(['cuboid'].includes(instance.type)){
            instance.x_min = Math.min(
              instance.front_face['top_right']['x'],
              instance.front_face['bot_right']['x'],
              instance.front_face['top_left']['x'],
              instance.front_face['bot_right']['x'],
              instance.rear_face['top_right']['x'],
              instance.rear_face['bot_right']['x'],
              instance.rear_face['top_left']['x'],
              instance.rear_face['bot_right']['x'],
            )
            instance.x_max = Math.max(
              instance.front_face['top_right']['x'],
              instance.front_face['bot_right']['x'],
              instance.front_face['top_left']['x'],
              instance.front_face['bot_right']['x'],
              instance.rear_face['top_right']['x'],
              instance.rear_face['bot_right']['x'],
              instance.rear_face['top_left']['x'],
              instance.rear_face['bot_right']['x'],
            )
            instance.y_min = Math.min(
              instance.front_face['top_right']['y'],
              instance.front_face['bot_right']['y'],
              instance.front_face['top_left']['y'],
              instance.front_face['bot_right']['y'],
              instance.rear_face['top_right']['y'],
              instance.rear_face['bot_right']['y'],
              instance.rear_face['top_left']['y'],
              instance.rear_face['bot_right']['y'],
            )
            instance.y_max = Math.max(
              instance.front_face['top_right']['y'],
              instance.front_face['bot_right']['y'],
              instance.front_face['top_left']['y'],
              instance.front_face['bot_right']['y'],
              instance.rear_face['top_right']['y'],
              instance.rear_face['bot_right']['y'],
              instance.rear_face['top_left']['y'],
              instance.rear_face['bot_right']['y'],
            )
          }
          else if(['ellipse'].includes(instance.type)){
            instance.x_min = instance.center_x - instance.width;
            instance.y_min = instance.center_y - instance.height;
            instance.x_max = instance.center_x + instance.width
            instance.y_max = instance.center_y + instance.height
          }
          else if(['curve'].includes(instance.type)){
            instance.x_min = Math.min(instance.p1.x, instance.p2.x)
            instance.x_max = Math.max(instance.p1.x, instance.p2.x)
            instance.y_min = Math.min(instance.p1.y, instance.p2.y)
            instance.y_max = Math.max(instance.p1.y, instance.p2.y)
          }
          else if(['keypoints'].includes(instance.type)){
            instance.calculate_min_max_points()
          }

          instance.x_min = parseInt(instance.x_min)
          instance.y_min = parseInt(instance.y_min)
          instance.x_max = parseInt(instance.x_max)
          instance.y_max = parseInt(instance.y_max)

        },
        move_keypoints: function(){
          let key_points_did_move = false;
          let instance = this.instance_list[this.instance_hover_index];
          if(instance && this.is_actively_resizing){
            if(!this.original_edit_instance){
              this.original_edit_instance = instance.duplicate_for_undo();
              this.original_edit_instance_index = this.instance_hover_index;
            }
            key_points_did_move = instance.move();
          }
          return key_points_did_move
        },
        move_something: function (event) {

          /*
       * Limits (ie in edit mode) are assumed to be here.
       * ie move_box() doesn't check in edit mode.
       */

          if (this.draw_mode == true ) { return }
          if (this.$props.view_only_mode == true) { return }
          if (this.instance_select_for_issue == true) { return }
          if (this.instance_select_for_merge == true) { return }
          if (this.view_issue_mode) { return }
          let cuboid_did_move = false;
          let ellipse_did_move = false;
          let curve_did_move = false;
          let key_points_did_move = false;

          if ((this.instance_hover_index != undefined && this.instance_hover_type == 'cuboid') || this.selected_instance && this.selected_instance.type === 'cuboid') {
            cuboid_did_move = this.move_cuboid(event)
          }
          if (this.ellipse_hovered_corner || (this.instance_hover_index != undefined && this.instance_hover_type === 'ellipse')) {
            ellipse_did_move = this.move_ellipse(event)
          }
          if (this.instance_hover_index != undefined && this.instance_hover_type === 'curve') {
            curve_did_move = this.move_curve(event)
          }

          if (this.instance_hover_index != undefined && this.instance_hover_type === 'keypoints') {
            key_points_did_move = this.move_keypoints(event)
          }
          // want this seperate from other conditinos for now
          // this is similar to that "activel drawing" concept
          // not 100% sure how to explain difference between it
          if (this.$store.state.annotation_state.mouse_down == true) {
            this.lock_point_hover_change = true
          }
          else {
            // release lock
            this.lock_point_hover_change = false
          }

          //console.debug("at move_something()", this.lock_point_hover_change, this.instance_hover_index, this.box_edit_point_hover)


          let box_did_move = this.move_box(event)
          let polygon_did_move = this.move_polygon_line_or_point(event)
          let polygon_dragged = false;
          if(!polygon_did_move){
            polygon_dragged = this.drag_polygon(event);
          }

          if (box_did_move || polygon_did_move || cuboid_did_move || ellipse_did_move || curve_did_move || polygon_dragged || key_points_did_move) {
            this.calculate_min_max_points(this.instance_list[this.instance_hover_index]);
            this.set_instance_human_edited(this.instance_list[this.instance_hover_index])
            this.has_changed = true;
          }

          /* Assumption is that if we return early in anywhere in this function
     * there are no changes.
     * However if we get to end, then did some valid change.
     * By having it at end here we can expand to add more types of change /
     * moving handling.
     * And don't have to worry about how far down it is in these chains
     * ie if it's after a certain point or not etc.
     */

        },

        move_box: function (event) {
          /* Returns true if moved something.
     * TODO invert if statment so we can have default
     * path as true
     */
          if (this.instance_hover_index != undefined && this.instance_hover_type == 'box') {
            // why did I need vuex here again?
            // maybe only allow one at a time, and then if needed can do more??
            // (ie multi select more for delete?)
            if (this.$store.state.annotation_state.mouse_down == true) {

              let i = this.instance_hover_index
              let instance = this.instance_list[i]

              if (instance.soft_delete == true) {
                this.snackbar_warning = true
                this.snackbar_warning_text = "Undo delete first."
                return
              }

              if (instance.type != "box") {
                return
              }

              this.move_box_literal_points(instance, i, event)
              return true
            }
          }

        },

        move_polygon_line_or_point: function (event) {
          /*
      Returns true if moved something. This handles the movement of
      any of the following instances: point, polygon, line.

     */
          if(!this.instance_list){return}


          if (this.polygon_point_click_index != null) {
            if (this.$store.state.annotation_state.mouse_down == true) {
              var i = this.polygon_click_index
              var j = this.polygon_point_click_index

              if (this.instance_list[i] == true) {
                this.snackbar_warning = true
                this.snackbar_warning_text = "Undo delete first."
                return
              }
              if(!this.original_edit_instance && this.instance_list[this.polygon_click_index]){

                this.original_edit_instance = {
                  ...this.instance_list[this.polygon_click_index],
                  points: [...this.instance_list[this.polygon_click_index].points.map(p => ({...p}))]
                };
                this.original_edit_instance_index = this.polygon_click_index;
              }
              if(this.instance_list[i] && this.instance_list[i]['points'][j]){
                let x_new = parseInt(this.mouse_position.x)
                let y_new = parseInt(this.mouse_position.y)
                if(this.instance_list[i])
                  this.instance_list[i]['points'][j].x = x_new
                this.instance_list[i]['points'][j].y = y_new

                return true
              }

            }
          }

        },

        move_box_literal_points: function(instance: Object, i: Number, event) {

          /* Case #1 -> Move from center point of box
      * Case #2 -> Move from either min or max point
      *
      *
      *  Options: "x_min_y_min" "x_max_y_min"  "x_min_y_max" "x_max_y_max"],
      * as defined by the hover index
      *
      * See  determine_movement_point_for_box for where this gets generated
      *
      * because we detect that when mouse is first moving
      * but then this done as it drags
      *
      * Basically match up which direction with which
      * If both min and both max then straight forward,
      * if say one is min and one is max then match that direction
      *
      * Not sure if there is a better way to map this ,
      * despite looking similar each pair is different
      *
      * we check lock both for the individual thing within the box,
      * and for which of the boxes in the instance list we are on.
      */

          // why parseInt: backend expects this as an integer like value

          if (instance.type != "box") { return }

          let x_new = parseInt(this.mouse_position.x)
          let y_new = parseInt(this.mouse_position.y)

          let x_movement = parseInt((event.movementX / this.canvas_scale_combined))
          let y_movement = parseInt((event.movementY / this.canvas_scale_combined))

          if(!this.original_edit_instance){
            this.original_edit_instance = {...instance};
            this.original_edit_instance_index = i;
          }

          if (this.box_edit_point_hover == "x_min_y_min") {
            instance.x_min = x_new
            instance.y_min = y_new
          }
          else if (this.box_edit_point_hover == "x_max_y_max") {
            instance.x_max = x_new
            instance.y_max = y_new
          }

          else if (this.box_edit_point_hover == "x_min_y_max") {
            instance.x_min = x_new
            instance.y_max = y_new
          }
          else if (this.box_edit_point_hover == "x_max_y_min") {
            instance.x_max = x_new
            instance.y_min = y_new
          }
          // move whole box
          else if (this.box_edit_point_hover == "not_intersecting_special_points") {
            instance.x_min += this.mouse_down_delta_event.x
            instance.y_min += this.mouse_down_delta_event.y

            instance.x_max += this.mouse_down_delta_event.x
            instance.y_max += this.mouse_down_delta_event.y
          }

          /* Interpolated set to false motivation:
       *  Any movement removes the interpolated flag when we save
       *  (through a different process)
       *  so pro-actively show this here so it's clearer to user
       */
          if (instance.interpolated) {
            instance.interpolated = false
          }

          this.box_update_position(instance, i)

        },

        get_media_promise: function () {
          return new Promise((resolve) => {
            resolve(this.get_media())
          })
        },

        addImageProcess: function (src) {
          return new Promise((resolve, reject) => {
            let image = new Image()
            image.src = src
            if(process.env.NODE_ENV === 'testing'){
              image.crossOrigin = "anonymous";
            }
            image.onload = () => resolve(image)
            image.onerror = reject
          })
        },
        video_update_core: async function(){
          // TODO change this to update video component?

          this.canvas_width = this.$props.file.video.width
          this.canvas_height = this.$props.file.video.height
          this.video_mode = true;
          this.current_video = this.$props.file.video;
          this.current_video_file_id = this.$props.file.id
          await this.get_instances();
          // We need to trigger components and DOM updates before updating frames and sequences.
          // To read more: https://medium.com/javascript-in-plain-english/what-is-vue-nexttick-89d6878c1162
          await this.$nextTick();

          //console.debug('VIDEO UPDATE COREE', this.current_file.video);
          await this.$refs.video_controllers.current_video_update();
          // Update the frame data.

          await this.$refs.sequence_list.clear_sequence_list_cache()
          await this.$refs.sequence_list.get_sequence_list()
          // We need to update sequence lists synchronously to know when to remove the placeholder.
        },
        prepare_canvas_for_new_file: async function () {
          if (this.$props.file!= undefined) {
            if (this.$props.file.type == "image") {
              await this.image_update_core()
            }
            if (this.$props.file.type == "video") {
              await this.video_update_core();
            }
            if (this.$props.file.type == "text") {
              this.video_mode = false;
              this.show_text_file_place_holder = true;
              this.loading = false;
              this.annotations_loading = false;
            }
          } else {
            this.loading = false
            this.annotations_loading = false
            // The two different loading flags relate to differential between loading files,
            // and loading annotations which need to be different in current design
          }

          // Even though we call update_canvas on multiple places, it doesnt always update as expected because we have to
          // wait for the next tick to happen
          await this.$nextTick();
          this.update_canvas();


        },

        logout() {
          if (this.$store.state.user.current.is_super_admin != true) {
            this.$store.dispatch('log_out')
            this.$router.push('/user/login')
          }
        },

        image_update_core: async function () {

          /*
        Performs updates to image.
        Shared between project images method and annotation assignment methods.

      */
          if (!this.$props.file) {
            this.loading = false
          }
          else{
            this.$emit('current_file', this.$props.file)
          }

          /*
      1.  creates new Image()
      1.1 attaches src to html image
      1.2 load() triggers resolve()

      2.0 resolve() updates vue js html_image with html image

      */
          //console.debug("loaded image")
          this.canvas_wrapper.style.display = ""

          await this.get_instances()

          this.canvas_width = this.$props.file.image.width
          this.canvas_height = this.$props.file.image.height

          await this.addImageProcess_with_canvas_refresh()


        },

        addImageProcess_with_canvas_refresh: async function () {
          try{
            const new_image = await this.addImageProcess(
              this.$props.file.image.url_signed);
            this.html_image = new_image;
            this.update_canvas();
            this.loading = false
            this.refresh = Date.now();
          }
          catch(error){
            console.error(error)
          }
        },

        get_colour_map: function () {

          axios.get('/api/project/' + this.project_string_id +
            '/labels/colour_map')
            .then(response => {
              if (response.data.success === true) {
                this.label_file_colour_map = response.data.label_file_colour_map
              }
              this.loading = false
            })
            .catch(error => {
              console.debug(error);
            });

        },









        toInt: function (n) { return Math.round(Number(n)); },

        onRendered: function (ctx) {

          // IMPORTANT   restore canvas from various transform operations
          ctx.restore()
        },

        test: function () {
          console.debug(Date.now())
        },

        mouse_transform: function (event, mouse_position) {
          this.populate_canvas_element();
          return this.canvas_mouse_tools.mouse_transform(
            event, mouse_position, this.canvas_element, this.update_canvas, this.canvas_transform)
        },

        helper_difference_absolute: function (a, b) { return Math.abs(a - b) },


        move_position_based_on_mouse: function (movementX, movementY) {

          // using local could work if we also "dragged" it... but feels funny for free move
          // let x = this.canvas_translate.x + (movementX / this.canvas_scale_local)
          // let y = this.canvas_translate.y + (movementY / this.canvas_scale_local)
          let x = this.canvas_translate.x + movementX
          let y = this.canvas_translate.y + movementY

          /* Below are Locks so it doesn't go out of bounds.
       * if it goes out of boudnds (ie negative or greater then image actual)
       * then it causes severe rendering error.
       *
       * careful, we assume we need to compare to scaled value
       * base on rest of context
       * This is wishy washy answer but basically console logged
       * and it was clear neeeded scaled value from that.
       */
          if (x >= 0 && x < this.canvas_width_scaled){
            this.canvas_translate.x = x
          }
          if (y >= 0 && y < this.canvas_height_scaled){
            this.canvas_translate.y = y
          }

        },

        mouse_move: function (event) {

          // want view only mode to access this so updates zoom properly

          /*
      // https://stackoverflow.com/questions/17389280/check-if-window-has-focus/17389334
      if (document.hasFocus() == false) {
        console.debug("refocused")
        window.focus()
      }
      */
          this.mouse_position = this.mouse_transform(event, this.mouse_position);
          if (this.ctrl_key == true) {
            this.move_position_based_on_mouse(event.movementX, event.movementY)
            return
          }
          this.move_something(event)

          this.update_mouse_style()

          if (this.draw_mode == true) {

            if (this.instance_type == "polygon") {
              this.detect_other_polygon_points();
              if (this.current_polygon_point_list.length >= 1) {

                if (this.shift_key == true) {
                  let x_diff = this.helper_difference_absolute(this.mouse_position.x, this.current_polygon_point_list[this.current_polygon_point_list.length - 1].x)
                  let y_diff = this.helper_difference_absolute(this.mouse_position.y, this.current_polygon_point_list[this.current_polygon_point_list.length - 1].y)
                  //console.debug(x_diff, y_diff)
                  if (x_diff > 10 || y_diff > 10) {
                    //TODO this is a hacky way to do it!!!
                    this.mouse_down_position.x = this.mouse_position.x
                    this.mouse_down_position.y = this.mouse_position.y
                    this.polygon_insert_point()
                  }
                }
              }
            }
          }

          // For refactored instance types (eventually all should be here)
          const mouse_move_interaction = this.generate_event_interactions(event);
          if(mouse_move_interaction){
            mouse_move_interaction.process();
          }
          //console.debug(this.mouse_position)
        },

        polygon_point_limits: function() {
          // snap to edges
          let current_point = this.current_polygon_point;
          // Set Autoborder point if exists
          if(this.is_actively_drawing &&
            this.auto_border_polygon_p1 &&
            !this.auto_border_polygon_p2){
            current_point.x = this.auto_border_polygon_p1.x;
            current_point.y = this.auto_border_polygon_p1.y
            current_point.point_set_as_auto_border = true;
          }
          if(this.is_actively_drawing &&
            this.auto_border_polygon_p1 &&
            this.auto_border_polygon_p2){
            current_point.x = this.auto_border_polygon_p2.x;
            current_point.y = this.auto_border_polygon_p2.y;
            current_point.point_set_as_auto_border = true;
          }
          // TODO look at if this should be 0 or 1  and width or width -1
          if (this.current_polygon_point.x <= this.snap_to_edges) {
            current_point.x = 1
          }
          if (this.current_polygon_point.y <= this.snap_to_edges) {
            current_point.y = 1
          }
          if (this.current_polygon_point.x >= this.canvas_width - this.snap_to_edges) {
            current_point.x = this.canvas_width - 1
          }
          if (this.current_polygon_point.y >= this.canvas_height - this.snap_to_edges) {
            current_point.y = this.canvas_height - 1
          }
          return current_point;
        },
        perform_auto_bordering: function(path_type){
          const auto_border_polygon = this.instance_list[this.auto_border_polygon_p2_instance_index];
          let points = auto_border_polygon.points;
          if(this.auto_border_polygon_p1_figure){
            points = auto_border_polygon.points.filter(p => p.figure_id === this.auto_border_polygon_p1_figure)
          }

          // Forward Path
          let current_index = this.auto_border_polygon_p1_index;
          let forward_count = 0;
          let forward_index_list = []
          while(current_index != this.auto_border_polygon_p2_index){
            // Don't add p1 index
            if(current_index !== this.auto_border_polygon_p1_index){
              forward_index_list.push(current_index);
            }
            if(current_index >= points.length){
              current_index = 0;
              forward_count += 1;
              continue
            }
            current_index += 1;
            forward_count += 1;
          }

          // Backwards path
          current_index = this.auto_border_polygon_p1_index;
          let backward_count = 0;
          let backward_index_list = []
          while(current_index != this.auto_border_polygon_p2_index){
            // Don't add p1 index
            if(current_index !== this.auto_border_polygon_p1_index){
              backward_index_list.push(current_index);
            }
            if(current_index < 0){
              current_index = points.length ;
              backward_count += 1;
              continue
            }
            current_index -= 1;
            backward_count += 1;
          }
          const longest = forward_count > backward_count ? 'forward' : 'backward'
          const shortest = forward_count <= backward_count ? 'forward' : 'backward'
          if(path_type === 'long_path'){
            if(longest === 'forward'){
              for(const index of forward_index_list){
                if(points[index] == undefined){continue}
                this.current_polygon_point_list.push({...points[index], figure_id: undefined})
              }
            }
            else{
              for(const index of backward_index_list){
                if(points[index] == undefined){continue}
                this.current_polygon_point_list.push({...points[index], figure_id: undefined})
              }
            }
          }
          else{
            if(shortest === 'forward'){
              for(const index of forward_index_list){
                if(points[index] == undefined){continue}
                //console.debug('indexx2', index, auto_border_polygon.points[index]);
                this.current_polygon_point_list.push({...points[index], figure_id: undefined})
              }
            }
            else{
              for(const index of backward_index_list){
                if(points[index] == undefined){continue}
                //console.debug('indexx', index, auto_border_polygon.points[index]);
                this.current_polygon_point_list.push({...points[index], figure_id: undefined})
              }
            }
          }

          this.current_polygon_point_list.push({...this.auto_border_polygon_p2, figure_id: undefined})
          this.auto_border_polygon_p1 = undefined;
          this.auto_border_polygon_p1_index = undefined;
          this.auto_border_polygon_p1_figure = undefined;
          this.auto_border_polygon_p1_instance_index = undefined;
          this.auto_border_polygon_p2 = undefined;
          this.auto_border_polygon_p2_index = undefined;
          this.auto_border_polygon_p2_figure = undefined;
          this.auto_border_polygon_p2_instance_index = undefined;
          this.show_polygon_border_context_menu = false;




        },
        polygon_insert_point: function () {
          const current_point = this.polygon_point_limits()

          // check if we should auto complete polygon (or can use enter)
          if (this.current_polygon_point_list.length >= 2){
            let first_point = this.current_polygon_point_list[0]

            if (this.point_is_intersecting_circle(this.mouse_position, first_point) && this.instance_type === 'polygon') {
              const command = new CreateInstanceCommand(this.current_instance, this);
              this.command_manager.executeCommand(command);
              return
            }
          }

          // console.debug('auto_border_polygon_p1', this.auto_border_polygon_p1)
          // console.debug('auto_border_polygon_p2', this.auto_border_polygon_p2)
          if(this.auto_border_polygon_p1 && this.auto_border_polygon_p2){
            this.show_polygon_border_context_menu = true;
          }
          else{
            this.current_polygon_point_list.push(current_point) // points only
          }

        },

        curve_mouse_up: function(){

          if (this.instance_type == "curve" && this.current_polygon_point_list.length == 2) {
            const command = new CreateInstanceCommand(this.current_instance, this);
            this.command_manager.executeCommand(command);
          }
        },
        bounding_box_mouse_up_edit: function(){
          if(this.instance_hover_type !== 'box'){return}
          if(!this.instance_hover_index == undefined){return}
          if(!this.original_edit_instance){ return }

          const new_instance = this.instance_list[this.instance_hover_index];
          const command = new UpdateInstanceCommand(new_instance, this.instance_hover_index, this.original_edit_instance, this);
          this.command_manager.executeCommand(command);
          this.original_edit_instance = undefined;
          this.original_edit_instance_index = undefined;
        },
        polygon_mouse_up_edit: function(){
          if(!this.original_edit_instance){ return }
          if(this.original_edit_instance.type != 'polygon'){ return }
          if(this.original_edit_instance_index == undefined){ return }

          const command = new UpdateInstanceCommand(this.instance_list[this.original_edit_instance_index],
            this.original_edit_instance_index,
            this.original_edit_instance,
            this)
          this.command_manager.executeCommand(command);

          if (this.instance_hover_index != undefined &&
            typeof this.instance_list[this.instance_hover_index]['points'][this.polygon_point_hover_index] != "undefined") {
            this.instance_list[this.instance_hover_index]['points'][this.polygon_point_hover_index].selected = false
          }
          this.original_edit_instance = undefined;
          this.original_edit_instance_index = undefined;
        },
        line_mouse_up_edit: function(){
          if(!this.original_edit_instance){ return }
          if(this.original_edit_instance.type != 'line'){ return }
          if(this.original_edit_instance_index == undefined){ return }
          const command = new UpdateInstanceCommand(this.instance_list[this.original_edit_instance_index],
            this.instance_hover_index,
            this.original_edit_instance,
            this)
          this.command_manager.executeCommand(command);
          if (this.instance_hover_index != undefined &&
            typeof this.instance_list[this.instance_hover_index]['points'][this.polygon_point_hover_index] != "undefined") {
            this.instance_list[this.instance_hover_index]['points'][this.polygon_point_hover_index].selected = false

          }
          this.original_edit_instance = undefined;
          this.original_edit_instance_index = undefined;
        },
        point_mouse_up_edit: function(){
          if(!this.original_edit_instance){ return }
          if(this.original_edit_instance.type != 'point'){ return }
          if(this.original_edit_instance_index == undefined){ return }
          const command = new UpdateInstanceCommand(this.instance_list[this.original_edit_instance_index],
            this.instance_hover_index,
            this.original_edit_instance,
            this)
          this.command_manager.executeCommand(command);
          if (this.instance_hover_index != undefined &&
            typeof this.instance_list[this.instance_hover_index]['points'][this.polygon_point_hover_index] != "undefined") {
            this.instance_list[this.instance_hover_index]['points'][this.polygon_point_hover_index].selected = false

          }
          this.original_edit_instance = undefined;
          this.original_edit_instance_index = undefined;
        },
        cuboid_mouse_up_edit: function(){
          if(!this.original_edit_instance){ return }
          if(this.original_edit_instance.type != 'cuboid'){ return }
          if(this.original_edit_instance_index == undefined){ return }
          const command = new UpdateInstanceCommand(this.instance_list[this.original_edit_instance_index],
            this.original_edit_instance_index,
            this.original_edit_instance,
            this)
          this.command_manager.executeCommand(command);
          this.is_moving_cuboid_corner = false;
          this.original_edit_instance = undefined;
          this.original_edit_instance_index = undefined;
        },
        curve_mouse_up_edit: function(){
          if(!this.original_edit_instance){ return }
          if(this.original_edit_instance.type != 'curve'){ return }
          if(this.original_edit_instance_index == undefined){ return }
          const command = new UpdateInstanceCommand(this.instance_list[this.original_edit_instance_index],
            this.original_edit_instance_index,
            this.original_edit_instance,
            this)
          this.command_manager.executeCommand(command);
          this.original_edit_instance = undefined;
          this.original_edit_instance_index = undefined;
        },
        keypoint_mouse_up_edit: function(){
          if(!this.original_edit_instance){ return }
          if(this.original_edit_instance.type != 'keypoints'){ return }
          if(this.original_edit_instance_index == undefined){ return }

          const command = new UpdateInstanceCommand(
            this.instance_list[this.original_edit_instance_index],
            this.original_edit_instance_index,
            this.original_edit_instance,
            this)
          this.command_manager.executeCommand(command);
          this.original_edit_instance = undefined;
          this.original_edit_instance_index = undefined;
        },
        polygon_delete_point: function(polygon_point_index){
          if(this.draw_mode){return}
          if(!this.selected_instance){return}
          if(this.selected_instance.type !== 'polygon'){return}
          let i = 0;
          if(polygon_point_index != undefined){
            this.selected_instance.points.splice(polygon_point_index, 1);
          }
          else{
            for(const point of this.selected_instance.points){
              if(this.point_is_intersecting_circle(this.mouse_position, point, 8)){
                this.selected_instance.points.splice(i, 1);
                break;
              }
              i+=1
            }
          }

          this.instance_list.splice(this.selected_instance_index, 1, this.selected_instance)
        },

        get_node_hover_index: function () {
          if (!this.instance_hover_index) { return }
          let instance = this.instance_list[this.instance_hover_index]
          if (!instance.node_hover_index) { return }
          return instance.node_hover_index
        },

        double_click_keypoint_special_action: function(){
          let node_hover_index = this.get_node_hover_index()
          if (node_hover_index == undefined) {return }
          let update = {
            index: this.instance_hover_index,
            node_hover_index: node_hover_index,
            mode: "on_click_update_point_attribute"
          }
          this.instance_update(update)

        },

        double_click: function($event){
          this.mouse_position = this.mouse_transform($event, this.mouse_position)
          this.polygon_delete_point();
          this.double_click_keypoint_special_action()
        },

        mouse_up: function () {

          // start LIMITS, returns immediately
          if (this.$props.view_only_mode == true) { return }
          if (this.seeking == true) { return }

          if (this.mouse_down_limits_result == false) { return }


          if (this.draw_mode == false) {
            if (this.is_actively_resizing == true) {
              this.is_actively_resizing = false
            }
          }

          this.$store.commit('mouse_state_up')

          this.polygon_click_index = null
          this.polygon_point_click_index = null

          if (this.draw_mode == false) {
            //console.debug('mouse upp edit', this.instance_hover_index, this.instance_hover_type);
            if (this.instance_list != undefined) {
              this.point_mouse_up_edit();
              this.line_mouse_up_edit();
              if (this.ellipse_hovered_instance) {
                this.stop_ellipse_resize()
              }
              this.polygon_mouse_up_edit();
              this.bounding_box_mouse_up_edit()
              this.cuboid_mouse_up_edit();
              this.curve_mouse_up_edit();
              this.keypoint_mouse_up_edit()
            }
          }

          // TODO clarify difference between mode, and action, ie drawing.
          if (this.draw_mode == true) {
            if (this.instance_type == "cuboid") {
              this.cuboid_mouse_up()
            }
            if (this.instance_type == "ellipse") {
              this.ellipse_mouse_up()
            }
            if(this.instance_template_selected){
              this.instance_template_mouse_up()
            }

            // careful, polygon does not want to take off active drawing until
            // it's finished
            // for now it seeems like we are handling this on the "per instance" level
            // polygon sets is_actively_drawing to false with "enter"
            if (["polygon", "line", "curve"].includes(this.instance_type)) {
              this.is_actively_drawing = true
              this.polygon_insert_point()
            }

            if (this.instance_type == "line" && this.current_polygon_point_list.length == 2) {
              const command = new CreateInstanceCommand(this.current_instance, this)
              this.command_manager.executeCommand(command);
            }

            if (this.instance_type == "point" ) {
              this.polygon_insert_point()
              const command = new CreateInstanceCommand(this.current_instance, this)
              this.command_manager.executeCommand(command);
            }

            if (this.instance_type == "curve") {
              this.curve_mouse_up()
            }

            if (this.instance_type == "box") {

              if (this.$store.state.annotation_state.draw == false) {
                this.is_actively_drawing = true       // required for current_instance visual to display
                this.$store.commit('init_draw')
              }
              else {
                // is actively drawing negation handled by generic instance push method now
                this.$store.commit('finish_draw')
              }
            }


          }

          // For new Refactored instance types
          const mouse_up_interaction = this.generate_event_interactions(event);
          if(mouse_up_interaction){
            mouse_up_interaction.process();
          }
        },
        stop_ellipse_resize: function(){
          this.ellipse_hovered_instance = undefined;
          this.ellipse_hovered_instance_index = undefined;
          this.ellipse_hovered_corner = undefined;
          this.ellipse_hovered_corner_key = undefined;

          if(!this.original_edit_instance){ return }
          if(this.original_edit_instance.type != 'ellipse'){ return }
          if(this.original_edit_instance_index == undefined){ return }
          const command = new UpdateInstanceCommand(this.instance_list[this.original_edit_instance_index],
            this.original_edit_instance_index,
            this.original_edit_instance,
            this)
          this.command_manager.executeCommand(command);
        },
        ellipse_mouse_up: function () {

          if(!this.ellipse_current_drawing_face && this.draw_mode){
            this.$store.commit('init_draw');
            this.is_actively_drawing = true;
            this.ellipse_current_drawing_face = true;
          }
          else{
            this.$store.commit('finish_draw');
            this.is_actively_drawing = false;
            this.ellipse_current_drawing_face = false;
          }

        },
        cuboid_mouse_up: function () {

          if(!this.cuboid_current_drawing_face){
            this.is_actively_drawing = true;
            this.cuboid_current_drawing_face = 'first';
          }
          else if(this.cuboid_current_drawing_face === 'first'){
            this.is_actively_drawing = true;
            this.cuboid_current_drawing_face = 'second';
          }
          else{

            const create_box_command = new CreateInstanceCommand(this.current_instance, this);
            this.command_manager.executeCommand(create_box_command)
            this.cuboid_current_rear_face = undefined;
            this.cuboid_current_drawing_face = undefined;
            this.is_actively_drawing = false;
          }
        },
        lock_cuboid_rear_face: function(){
          var x_min = parseInt(this.mouse_down_position.x)
          var y_min = parseInt(this.mouse_down_position.y)
          var x_max = parseInt(this.mouse_position.x)
          var y_max = parseInt(this.mouse_position.y)

          // Handle inverting origin point
          if (x_max < x_min) {
            x_max = parseInt(this.mouse_down_position.x)
            x_min = parseInt(this.mouse_position.x)
          }

          if (y_max < y_min) {
            y_max = parseInt(this.mouse_down_position.y)
            y_min = parseInt(this.mouse_position.y)
          }

          if (x_min < 0) {x_min = 0}
          if (y_min < 0) {y_min = 0}

          // testing
          //x_max = 99999
          //y_max = 99999

          // 480 is from 0 to 479.
          if (this.canvas_width) {
            if (x_max >= this.canvas_width) {
              x_max = this.canvas_width - 1}

            if (y_max >= this.canvas_height) {
              y_max = this.canvas_height - 1}
          }

          var width = x_max - x_min
          var height = y_max - y_min

          this.cuboid_current_rear_face = {
            'width': width,
            'height': height,
            'top_left': {
              x: x_min,
              y: y_min
            },
            'top_right': {
              x: x_min + width,
              y: y_min
            },
            'bot_left': {
              x: x_min,
              y: y_min + height
            },
            'bot_right': {
              x: x_max,
              y: y_max
            }
          }
        },
        ellipse_mouse_down: function () {
          if(this.ellipse_current_drawing_face && this.draw_mode){
            const create_box_command = new CreateInstanceCommand(this.current_instance, this);
            this.command_manager.executeCommand(create_box_command)
          }
        },
        cuboid_mouse_down: function () {
          // WIP

          if (this.is_actively_drawing != true) {
            return
          }
          if(this.cuboid_current_drawing_face === 'first')
          {
            this.lock_cuboid_rear_face();
          }
          if (this.current_instance.x_max - this.current_instance.x_min <= 5
            && this.current_instance.y_max - this.current_instance.y_min <= 5) {
            // TODO raise error

            console.debug('Instance too small')
            return
          }
        },

        mouse_down_limits: function (event) {
          /* not a fan of having a value
       * and a flag... but also have to deal with both
       * mouse up and down firing, but not wanting to rerun this stuff twice
       * If there was a way to control the relation of mouse up/down
       * firing but that feels very unclear
       *
       * Also not sure if we don't return will it wait for the function
       * to complete as expected...
       *
       * So the default here is that it's true,
       * and we expect that if it's true mouse_up will also allow it to continue
       * It gets reset each time.
       *
       * In comparison to running this at save,
       * it means for current video boxes it will run twice
       * But the benefit is that then it prevents it from getting into broken state
       * in first place
       */

          // default
          this.mouse_down_limits_result = true

          // 1: left, 2: middle, 3: right, could be null
          // https://stackoverflow.com/questions/1206203/how-to-distinguish-between-left-and-right-mouse-click-with-jquery

          if (event.which == 2 || event.which == 3) {
            this.mouse_down_limits_result = false
            return false
          }

          if (this.show_context_menu == true) {
            this.mouse_down_limits_result = false
            return false
          }

          // this feels a bit funny
          if (this.draw_mode == false) { return true }

          if (this.space_bar == true || this.ctrl_key) {
            // note pattern of needing both... for now this
            // is so the mouse up respects this too
            this.mouse_down_limits_result = false
            return false
          }

          // TODO clarify if we could just do this first check
          if (!this.current_label_file || !this.current_label_file.id) {
            this.snackbar_warning = true
            this.snackbar_warning_text = "Please select a label first"
            this.mouse_down_limits_result = false
            return false
          }

          if (this.video_mode == true) {
            if (this.validate_sequences() == false) {
              this.mouse_down_limits_result = false
              return false
            }
          }

          return true

        },

        create_instance_events: function (instance_index=this.instance_list.length - 1) {
          this.event_create_instance = {...this.current_instance}
          this.request_change_current_instance = instance_index
          this.trigger_refresh_current_instance = Date.now()
        },

        bounding_box_mouse_down: function(){
          if (this.$store.state.annotation_state.draw == true) {
            if (this.current_instance.x_max - this.current_instance.x_min >= 5
              && this.current_instance.y_max - this.current_instance.y_min >= 5) {
              const create_box_command = new CreateInstanceCommand(this.current_instance, this);
              this.command_manager.executeCommand(create_box_command)
              this.create_instance_events()

            }
          }
        },
        polygon_mid_point_mouse_down: function(){
          if(!this.selected_instance){return}
          if(!this.is_actively_resizing){return}

          const instance = {...this.selected_instance};

          if(!instance){return}
          if(instance.type !== 'polygon'){return}
          if(instance.midpoint_hover == undefined){return}

          let points = instance.points.map(p => ({...p}));

          let rest_of_points = [];
          if(this.hovered_figure_id){
            points = instance.points.filter(p => p.figure_id === this.hovered_figure_id);
            rest_of_points = instance.points.filter(p => p.figure_id !== this.hovered_figure_id)
          }
          let midpoints_polygon = instance.midpoints_polygon;
          if(this.hovered_figure_id){
            midpoints_polygon = instance.midpoints_polygon[this.hovered_figure_id]
          }

          let new_point_to_add = midpoints_polygon[instance.midpoint_hover];
          if(new_point_to_add == undefined){
            return
          }
          points.splice(instance.midpoint_hover + 1, 0, {...new_point_to_add, figure_id: this.hovered_figure_id})
          this.polygon_point_hover_index = instance.midpoint_hover + 1;
          this.polygon_point_click_index = instance.midpoint_hover + 1;
          this.polygon_click_index = this.selected_instance_index;

          let hovered_point = points[this.polygon_point_hover_index];
          if(!hovered_point){
            return
          }
          hovered_point.selected = true;
          this.lock_point_hover_change = true;
          instance.midpoint_hover = undefined;
          instance.selected = true;
          if(this.hovered_figure_id){
            instance.points = points.concat(rest_of_points);
          }
          else{
            instance.points = points;
          }
          this.instance_list.splice(this.selected_instance_index, 1, instance);
        },
        get_polygon_figures: function(polygon_instance){
          let figure_list = [];
          if(!polygon_instance || polygon_instance.type !== 'polygon'){
            return []
          }
          for(const p of polygon_instance.points){
            if(!p.figure_id){
              continue
            }
            if(!figure_list.includes(p.figure_id)){
              figure_list.push(p.figure_id)
            }
          }
          return figure_list;
        },
        find_auto_border_point: function(polygon, points, instance_index){
          let found_point = false;
          let point_index = 0;
          for (const point of points){
            if(point.hovered_while_drawing){
              if(!this.auto_border_polygon_p1){
                this.auto_border_polygon_p1 = point;
                this.auto_border_polygon_p1_index = point_index;
                this.auto_border_polygon_p1_figure = point.figure_id;
                this.auto_border_polygon_p1_instance_index = instance_index;
                point.point_set_as_auto_border = true;
                found_point = true;
                this.show_snackbar_auto_border = true;
                break;
              }
              else if(!this.auto_border_polygon_p2 && point != this.auto_border_polygon_p1 && instance_index === this.auto_border_polygon_p1_instance_index){
                this.auto_border_polygon_p2 = point;
                this.auto_border_polygon_p2_index = point_index;
                this.auto_border_polygon_p2_figure = point.figure_id;
                point.point_set_as_auto_border = true;
                this.auto_border_polygon_p2_instance_index = instance_index;
                this.show_snackbar_auto_border = false;
                found_point = true;
                break;
              }
            }
            point_index += 1;
          }
          return found_point;
        },
        polygon_auto_border_mouse_down: function(){
          if(!this.draw_mode){return}
          if(!this.is_actively_drawing){return}
          if(!this.auto_border_polygon_p1 && this.auto_border_polygon_p2){return}
          let found_point = false;
          for(let instance_index =0; instance_index < this.instance_list.length; instance_index++){
            const polygon = this.instance_list[instance_index];
            if(polygon.type !== 'polygon' || polygon.soft_delete){continue}

            let points = polygon.points;
            let figure_list = this.get_polygon_figures(polygon);
            if(figure_list === 0){
              let autoborder_point_exists = this.find_auto_border_point(polygon, points, instance_index);
              if(autoborder_point_exists){
                found_point = true;
              }
            }
            else{
              for(const figure_id of figure_list){
                points = polygon.points.filter(p => p.figure_id === figure_id)
                let autoborder_point_exists = this.find_auto_border_point(polygon, points, instance_index);
                if(autoborder_point_exists){
                  found_point = true;
                }
              }
            }
            if(found_point){
              break;
            }
          }

        },
        instance_template_mouse_down: function(){

        },
        add_label_file_to_instance(instance){
          instance.label_file = this.current_label_file;
          instance.label_file_id = this.current_label_file_id;
          return instance
        },
        add_instance_template_to_instance_list(){
          this.current_instance_template.instance_list.forEach(instance => {
            let new_instance = this.duplicate_instance(instance);
            if (this.video_mode == true) {
              new_instance.number = this.current_sequence_from_sequence_component.number
              new_instance.sequence_id = this.current_sequence_from_sequence_component.id
            }
            this.add_label_file_to_instance(new_instance)
            if (new_instance.type === 'keypoints') {
              new_instance.set_new_xy_to_scaled_values();
            } else if (new_instance.type === 'box'){
              new_instance.x_min = parseInt(this.mouse_position.x, 10);
              new_instance.y_min = parseInt(this.mouse_position.y, 10);
              new_instance.x_max = parseInt(this.mouse_position.x + new_instance.width, 10);
              new_instance.y_max = parseInt(this.mouse_position.y + new_instance.height, 10);
            } else if (new_instance.type === 'polygon'){
              let x_diff = this.mouse_position.x - new_instance.points[0].x;
              let y_diff = this.mouse_position.y - new_instance.points[0].y;
              new_instance.points.forEach(point => {
                point.x += x_diff;
                point.y += y_diff;
              });

            }
            this.push_instance_to_instance_list_and_buffer(new_instance, this.current_frame)
            //const command = new CreateInstanceCommand(new_instance, this);
            //this.command_manager.executeCommand(command);

          })
        },
        instance_template_mouse_up: function(){
          if(this.instance_template_draw_started){
            this.add_instance_template_to_instance_list();
            this.instance_template_draw_started = undefined;
            this.is_actively_drawing = undefined;
            this.instance_template_start_point = undefined;
          }
          else{
            // TODO: Might need to change this logic when we support more than one instance per instance template.

            if(this.instance_template_has_keypoints_type(this.current_instance_template)){

              this.instance_template_draw_started = true;
              this.is_actively_drawing = true;
              this.instance_template_start_point = {
                x: this.mouse_position.x,
                y: this.mouse_position.y
              }
            }
            else{
              this.add_instance_template_to_instance_list();
              this.instance_template_draw_started = undefined;
              this.is_actively_drawing = undefined;
              this.instance_template_start_point = undefined;
            }
          }
        },
        generate_event_interactions: function(event){
          const interaction_generator = new AnnotationCoreInteractionGenerator(
            event,
            this.instance_hover_index,
            this.instance_list
          )
          return interaction_generator.generate_interaction()

        },
        key_points_mouse_down: function(){
          if(this.instance_hover_index == undefined){return}
          let instance = this.instance_list[this.instance_hover_index];
          if (!instance.is_node_hovered && !instance.is_bounding_box_hovered) {
            return
          }
          instance.start_movement();

        },
        mouse_down: function (event) {

          // TODO review using local variables instead of vuex
          // here for performance

          // TODO new method ie
          // this.is_actively_drawing = true

          if (this.$props.view_only_mode == true) {
            return
          }

          if (this.mouse_down_limits(event) == false) {
            return
          }

          this.ghost_may_promote_instance_to_actual()

          // For new refactored instance types (eventually all should be here)
          const mouse_down_interaction = this.generate_event_interactions(event);
          if(mouse_down_interaction){
            mouse_down_interaction.process();
          }
          if (this.seeking == false) {
            this.$store.commit('mouse_state_down')

            this.select_something()
            this.select_issue();

            if (this.instance_type == "cuboid") {
              this.cuboid_mouse_down()
            }

            if (this.instance_type == "ellipse") {
              this.ellipse_mouse_down()
            }
            if (this.instance_type == "box") {
              this.bounding_box_mouse_down();
            }
            if (this.instance_type == "keypoints") {
              this.key_points_mouse_down();
            }
            if(this.instance_template_selected){
              this.instance_template_mouse_down();
            }
          }

          if (this.draw_mode == false) {
            if (this.is_actively_resizing == false) {
              this.is_actively_resizing = true
            }
          }


          if (this.canvas_element) {
            var canvas_rectangle = this.canvas_element.getBoundingClientRect()
          }




          this.polygon_auto_border_mouse_down()
          this.mouse_down_position = this.mouse_transform(event, this.mouse_down_position)
          this.mouse_down_position.request_time = Date.now()
          this.lock_polygon_corner();
          this.polygon_mid_point_mouse_down()



        },
        lock_polygon_corner: function(){
          this.polygon_point_click_index = this.polygon_point_hover_index
          this.polygon_click_index = this.instance_hover_index

        },
        get_instances_core: function (response) {
          // TODO improve to take dict instead of response
          // since may use in other contexts
          this.show_annotations = true

          // Not sure if a "silent" null check is right here
          if (response.data['file_serialized']) {
            this.instance_list = this.create_instance_list_with_class_types(
              response.data['file_serialized']['instance_list']
            );


          }
          this.loading = false

          this.trigger_refresh_with_delay()

        },

        trigger_refresh_with_delay: function () {
          /* Jan 2, 2020, there is some kind of timing issue
       * with the way that the vue_canvas components detect
         a refresh.

         If we trigger $vm0.refresh = Date.now()
         after it's loaded it works.

         It also clears this is the user mouses over it
         but this way
         it covers that timing issue.
       *
       */

          setTimeout(() => this.refresh = Date.now(), 80)

        },

        get_instance_list_diff: async function () {
          this.loading = true
          try{
            const response = await axios.post('/api/v1/task/diff', {
              task_alpha_id: this.$props.task.id,
              mode_data: this.task_mode_prop,  // TODO clarify task_mode_prop vs mode_data
            })
            if (response.data.log.success === true) {
              this.instance_list = this.create_instance_list_with_class_types(
                response.data.instance_list
              )
              this.annotations_loading = false
              this.show_annotations = true
            }
          }
          catch(error){
            this.loading = false
            console.error(error)
          }
          finally{
            this.loading = false
          }
        },

        get_instances_file_diff: async function () {
          try{
            const response = await axios.get('/api/project/' + this.project_string_id + '/file/' + this.$props.file.id + '/diff/previous')
            if (response.data.success === true) {
              this.instance_list = this.create_instance_list_with_class_types(response.data.instance_list)
              this.annotations_loading = false
              this.show_annotations = true
            }
            this.loading = false
          }
          catch(error){
            console.error(error);
          }

        },
        get_instance_list_for_image: async function(){
          let url = undefined;
          let file = this.$props.file;
          if(this.$store.getters.is_on_public_project){
            url = `/api/project/${this.$props.project_string_id}/file/${String(this.$props.file.id)}/annotation/list`;

            const response = await axios.post(url, {
              directory_id : this.$store.state.project.current_directory.directory_id,
              job_id : this.job_id,
              attached_to_job: file.attached_to_job
            })
            this.get_instances_core(response)
            this.annotations_loading = false

          }
          else if (this.$store.state.builder_or_trainer.mode == "builder") {
            if (this.task && this.task.id) {
              // If a task is present, prefer this route to handle permissions
              url = '/api/v1/task/' + this.task.id + '/annotation/list';
              file = this.$props.task.file;

            } else {

              url = `/api/project/${this.$props.project_string_id}/file/${String(this.$props.file.id)}/annotation/list`
            }
            try{
              const response = await axios.post(url, {
                directory_id : this.$store.state.project.current_directory.directory_id,
                job_id : this.job_id,
                attached_to_job: file.attached_to_job
              })
              this.get_instances_core(response)
              this.annotations_loading = false

            }
            catch(error){
              console.debug(error);
              this.loading = false
            }
            return
          }
          else if (this.$store.state.builder_or_trainer.mode == "trainer") {
            url = '/api/v1/task/' + this.task.id +
              '/annotation/list'
            try{
              const response = await axios.get(url, {})
              this.get_instances_core(response)
              this.annotations_loading = false
            }
            catch(error){
              console.debug(error);
              this.loading = false
            }
          }

        },
        add_override_colors_for_model_runs: function(){
          if(!this.model_run_list){
            return
          }
          for(const instance of this.instance_list){
            if(instance.model_run_id){
              let model_run = this.model_run_list.filter(m => m.id === instance.model_run_id);
              if(model_run.length > 0){
                model_run = model_run[0];
                instance.override_color = model_run.color;
              }

            }
          }
        },
        get_instances: async function (play_after_success=false) {
          if(this.get_instances_loading){ return }
          this.get_instances_loading = true;
          this.annotations_loading = true;
          this.show_annotations = false;


          // Diffing Context
          // TODO: discuss if should remove or move to another place (separate component)
          if (this.$props.task) {
            if (this.task_mode_prop == 'compare_review_to_draw') {
              await this.get_instance_list_diff();
              this.get_instances_loading = false;
              return
            }
          }


          // Fetch Instance list for either video or image.
          if (this.video_mode == true) {
            /*  Caution, if this is firing twice
          *    Look at vidue.vue   get_video_single_image()
          *    It's spawning a 'video_file_update' event this is waiting for.
          */
            /*
          * Key observation here is that, if the frame exists in the dict,
          * then we don't need to get a new buffer list,
          * otherwise we do. And we can trigger  this.get_video_instance_buffer()
          * seperetly for special event handling
          *
          */
            await this.update_instance_list_from_buffer_or_get_new_buffer(play_after_success)
          }
          else{
            // Context of Images Only
            await this.get_instance_list_for_image();
          }
          this.add_override_colors_for_model_runs();
          this.get_instances_loading = false;
          this.update_canvas();

        },

        async update_instance_list_from_buffer_or_get_new_buffer(play_after_success) {

          if (this.current_frame in this.instance_buffer_dict) {
            // Initialize instances to class objects before assigning pointer.
            this.initialize_instance_buffer_dict_frame(this.current_frame);
            // Instance list is always a pointer to the actual instance_buffer dict.
            // IMPORTANT  This is a POINTER not a new object. This is a critical assumption.
            // See https://docs.google.com/document/d/1KkpccWaCoiVWkiit8W_F5xlH0Ap_9j4hWduZteU4nxE/edit

            this.instance_list = this.instance_buffer_dict[this.current_frame];
            this.add_override_colors_for_model_runs();
            this.show_annotations = true
            this.loading = false
            this.annotations_loading = false
            if(this.instance_buffer_metadata[this.current_frame] && this.instance_buffer_metadata[this.current_frame].pending_save){
              this.has_changed = true;
            }

          } else {
            await this.get_video_instance_buffer(play_after_success)
          }
        },
        async get_instance_buffer_parallel(url_base, frame_start, frames_end){
          const step_size = 5; // We will fetch 5 frames per call
          const limit = pLimit(15); // 10 Max concurrent request.
          const total_frames = frames_end - frame_start;

          // Build frames start/end
          const frames_tuples = [];
          for(let i = frame_start; i < frames_end; i+= step_size + 1){
            frames_tuples.push([i, i + step_size])
          }
          const promises = frames_tuples.map(frame_tuple => {
            return limit(() => {
              let new_url =`${url_base}/instance/buffer/start/${frame_tuple[0]}/end/${frame_tuple[1]}/list`
              return axios.post(new_url, {
                directory_id : this.$store.state.project.current_directory.directory_id
              })
            })
          });

          let all_responses = await Promise.all(promises);
          let new_instance_buffer_dict = {};
          for(const response of all_responses){
            new_instance_buffer_dict = {
              ...new_instance_buffer_dict,
              ...response.data.instance_buffer_dict
            }
          }
          return new_instance_buffer_dict


        },
        async get_video_instance_buffer(play_after_success) {
          /*
       * Directly triggers getting buffer
       * Caution, this should rarely be called directly
       * normally it's called in conjunction with something
       * that checks if we already have a local copy like
       *
       * Using project id from store for case of single file
       * permissions ie file/:file_id
       *
       */

          this.show_annotations = false
          this.loading = true
          this.annotations_loading = true

          this.instance_buffer_error = {}

          this.instance_frame_start = this.current_frame

          let url = ""

          if (this.task && this.task.id) {
            url += '/api/v1/task/' + this.task.id +
              '/video/file_from_task'
          } else {
            url += '/api/project/' + this.$props.project_string_id +
              '/video/' + String(this.current_video_file_id)
            // careful it's the video file we want here
          }

          try{
            // Get the buffer from the Server. Note that at this point it is not initialized.
            // We'll initialize class instances as per frame and not all at once for performance reasons.
            this.instance_buffer_dict = await this.get_instance_buffer_parallel(
              url,
              this.current_frame,
              this.current_frame + this.label_settings.instance_buffer_size
            )

            this.instance_buffer_metadata = {};
            // Now set the current list from buffer
            if (this.instance_buffer_dict) {
              // We want to do the equals because that creates the reference on the instance list to buffer dict
              this.initialize_instance_buffer_dict_frame(this.current_frame)
              this.instance_list = this.instance_buffer_dict[this.current_frame]
            }
            else {
              // handle if buffer list doesn't load all the way?
              this.instance_list = []
            }

            this.show_annotations = true
            this.loading = false
            this.annotations_loading = false
            this.trigger_refresh_with_delay();
            this.update_canvas();

            if (play_after_success == true) {
              this.video_play = Date.now()
            }
          }
          catch (error) {
            this.instance_buffer_error = this.$route_api_errors(error)
            console.debug(error);
            this.loading = false
          }
        },

        sleep: function (ms) {
          return new Promise(resolve => setTimeout(resolve, ms))
          // bottom of https://www.sitepoint.com/delay-sleep-pause-wait/
          // use aysnc in front of function
        },
        next_issue_task: async function(task){
          if (this.loading == true || this.annotations_loading == true) { return }

          if (this.has_changed) {
            this.save();
            await this.sleep(1000)
          }

          this.reset_for_file_change_context()

          this.loading = true;

          try {
            const response = await axios.post(`/api/v1/task/${task.id}/next-task-with-issues`, {
              task_id: task.id,
            });
            if (response.data) {
              if (response.data.task_id && response.data.task_id !== task.id) {
                this.$router.push(`/task/${response.data.task_id}`)
              }

            }
          }
          catch (error) {
            console.debug(error);
          }
          finally{
            this.loading = false;
          }
        },
        trigger_task_change: async function(direction, task){
          // Keyboard shortcuts case
          if (this.loading == true || this.annotations_loading == true) { return }

          if (this.has_changed) {
            await this.save();
          }

          // Set the UI to loading state until a new task is provided in the props.
          // The watcher of 'task' will make sure to set loading = false and full_file_loading = false
          this.reset_for_file_change_context()

          // Ask parent for a new task
          this.$emit('request_new_task', direction, task)
        },

        reset_for_file_change_context: function (){
          this.current_sequence_annotation_core_prop = {
            id: null,
            number: null
          }
          this.video_mode = false   // if we don't have this can be issues switching to say an image
          this.instance_buffer_dict = {}
          this.instance_buffer_metadata = {}
          this.instance_list = []
          if(this.video_mode){
            this.$refs.video_controllers.reset_cache();
          }

        },
        change_file(direction, file){
          if (direction == "next" || direction == "previous") {
            this.$emit('request_file_change', direction, file);
          }
        },
        on_change_current_task: async function(){
          if (!this.$props.task) { return }
          if (!this.$props.task.id) { return }

          if (this.loading == true || this.annotations_loading == true || this.full_file_loading) {
            return
          }
          this.show_default_navigation = false

          this.full_file_loading = true;
          if (this.has_changed) {
            await this.save();
          }
          this.reset_for_file_change_context()
          await this.refresh_attributes_from_current_file(this.$props.task.file);

          this.current_file_updates(this.$props.task.file);
          await this.prepare_canvas_for_new_file();

          this.full_file_loading = false;
          this.ghost_clear_for_file_change_context()

        },
        on_change_current_file: async function () {
          if (!this.$props.file) { return }
          if (!this.$props.file.id) { return }

          if (this.loading == true || this.annotations_loading == true || this.full_file_loading) {
            // Don't change file while loading
            // The button based method catches this but keyboard short cut doesn't
            console.debug("Loading")
            return
          }
          this.full_file_loading = true;

          if (this.has_changed) {
            await this.save();
          }
          this.reset_for_file_change_context()

          this.$addQueriesToLocation({'file': this.$props.file.id})


          await this.refresh_attributes_from_current_file(this.$props.file);

          this.current_file_updates(this.$props.file);
          await this.prepare_canvas_for_new_file();

          this.full_file_loading = false;
          this.ghost_clear_for_file_change_context()
        },

        refresh_attributes_from_current_file: async function (file) {
          if(!file){
            throw new Error('Provide file.')
          }
          // Change mode  ?
          if (file.type == "image") {
            // TODO a better way... this is so the watch on current video changes
            this.current_video_file_id = null
            this.video_mode = false
            this.current_video =  {
              frame_count: 0,
              current_frame: 0
            }
            // maybe this.current_file should store width/height? ...
            try{
              const new_image = await this.addImageProcess(file.image.url_signed);
              this.html_image = new_image;
              this.refresh = Date.now();
              await this.get_instances()
              this.canvas_width = file.image.width
              this.canvas_height = file.image.height
              this.update_canvas();
            }
            catch(error){
              console.error(error)
            }
          }
          if (file.type === "video") {
            this.video_mode = true;   // order matters here, downstream things need this to pull right stuff
            // may be a good opportunity to think about a computed property here

            this.current_video_file_id = file.id;
            this.current_video = file.video;
            // Trigger update of child props before fetching frames an sequences.
            await this.$nextTick();

            // We need to update sequence lists synchronously to know when to remove the placeholder.
            this.$refs.sequence_list.clear_sequence_list_cache()
            await this.$refs.sequence_list.get_sequence_list()
            // Update the frame data.
            await this.$refs.video_controllers.current_video_update();
            const new_sequence_list = this.$refs.sequence_list.sequence_list;
            this.$refs.sequence_list.change_current_sequence(new_sequence_list[0])



          }

        },

        task_update: function (mode) {
          /*
       *
       *
       *  Hijacks save_error for now so we trigger other loading stuff?
       *
       */

          this.save_error = {}

          let current_frame = undefined;
          if(this.video_mode){
            current_frame = parseInt(this.current_frame, 10);
          }

          this.set_save_loading(true, current_frame)

          axios.post('/api/v1/task/update',
            {
              'task_id': this.task.id,
              'mode': mode
            })
            .then(response => {

              this.set_save_loading(false, current_frame)
              if (mode == 'toggle_deferred') {

                this.snackbar_success = true
                this.snackbar_success_text = "Deferred for review. Moved to next."

                //
                // Question, change_file() seems to save by default here
                // do we want that?
                // maybe a good idea since a deferred task could still have work done
                this.trigger_task_change('next', this.$props.task)

              }

            }).catch(error => {

            this.set_save_loading(false, current_frame)
            if (error.response.status == 400) {
              this.save_error = error.response.data.log.error
            }

          })


        },

        keyboard_events_local_up: function (event) {
          // TODO would it be better to have a dictionary or somthing to map this?
          if (event.keyCode === 46) {  // delete
            this.delete_instance();
          }

        },

        copy_previous_instance_list: function () {

          // TODO: For now I'm commenting this this as we'll need a bit more discussion on what this feature is for.
          // this.instance_list = this.instance_list.concat(this.instance_list_cache);

        },

        keyboard_events_local_down: function (event) {


        },

        // hotkey hotkeys
        keyboard_events_global_up: function (event) {
          /*
       *  So one thing to think about is having all annotation
       *  hotkeys in one place
       *  -> Things like the new label lock
       *  -> ease of reference / **preventing overlap**
       *  -> Event listeners are not great to have to setup and take down
       *  in each component
       *
       *  BUT that's not for context relevant things I guess
       *  Was thinking in context of where to add a hotkey for
       *  sequences and at first thinking there and then realizing
       *  maybe not.
       *
       */
          var   ctrlKey = 17;
          if(this.show_context_menu){
            return
          }
          if (event.keyCode === 16) { // shift
            //
            this.shift_key = false
          }
          if(event.keyCode === 91){ // cmd key
            this.ctrl_key = false;
          }
          if (event.keyCode === ctrlKey) { // ctrlKey
            this.ctrl_key = false
          }

          if (event.keyCode === 72) { // h key
            this.show_annotations = !this.show_annotations;
          }

          if (this.$store.state.user.is_typing_or_menu_open == true) {
            return
          }

          if (event.key === "f") {
            this.force_new_sequence_request = Date.now()
          }

          if (event.key === "g") {
            this.label_settings.show_ghost_instances = !this.label_settings.show_ghost_instances
          }

          if (event.keyCode === 83) { // save
            this.save();
          }

          if (event.keyCode === 13) {  // enter
            if (this.instance_type == "polygon") {
              this.push_instance_to_instance_list_and_buffer(this.current_instance, this.current_frame)
            }
          }

          if (event.keyCode === 32) { // space
            this.toggle_pause_play();
            this.space_bar = false
            this.canvas_element.style.cursor = 'pointer'
          }
          if (event.keyCode === 46) {  // delete
            this.delete_instance();
          }


        },

        // more hotkeys

        may_toggle_instance_transparency: function (event) {
          if (event.keyCode === 84) { // shift + t
            if (this.shift_key) {
              if(this.default_instance_opacity === 1){
                this.default_instance_opacity = 0.25;
              }
              else{
                this.default_instance_opacity = 1;
              }
            }
          }
        },

        may_toggle_file_change_left: function (event) {
          if (event.keyCode === 37 || event.key === "a") { // left arrow or A
            if (this.shift_key) {
              this.change_file("previous");
            } else {
              this.shift_frame_via_store(-1)
            }
          }
        },

        may_toggle_file_change_right: function (event) {
          if (event.keyCode === 39 || event.key === "d") { // right arrow
            if (this.shift_key) {
              this.change_file("next");
            } else {
              this.shift_frame_via_store(1)
            }
          }
        },

        keyboard_events_global_down: function (event) {
          var ctrlKey = 17,
            cmdKey = 91,
            shiftKey = 16,
            vKey = 86,
            cKey = 67;
          if (event.keyCode == ctrlKey || event.keyCode == cmdKey) {this.ctrl_key = true;}
          if (event.keyCode === shiftKey) { // shift
            //
            this.shift_key = true
          }
          if(event.keyCode === 17){
            this.ctrl_key = true;
            this.canvas_element.style.cursor = 'move'
          }

          if (this.$store.state.user.is_typing_or_menu_open == true) {
            //console.debug("Blocked by is_typing_or_menu_open")
            return
          }

          this.may_toggle_file_change_left(event)
          this.may_toggle_file_change_right(event)

          this.may_toggle_instance_transparency(event)

          if (event.key === "N") { // shift + n
            if (this.shift_key) {
              this.$refs.video_controllers.next_instance();
            }
          }
          if(event.keyCode == 88){ // x key
            this.reset_drawing();
          }
          if (event.keyCode === 67 && this.shift_key) { // c

            if (this.$props.file.ann_is_complete == true || this.$props.view_only_mode == true) {
              return
            }

            this.save(true);  // and_complete == true
          }

          if (event.keyCode === 27) { // Esc
            if (this.$props.view_only_mode == true) { return }
            if(this.instance_select_for_issue || this.view_issue_mode){return}
            if(this.instance_select_for_merge){return}

            this.draw_mode = !this.draw_mode
            this.edit_mode_toggle( this.draw_mode)
            this.is_actively_drawing = false
            // careful, can't include this direclty in edit_mode_toggle
            // since veutify switch does this behaviour too
          }

          if (event.keyCode === 32) { // space

            event.preventDefault()  // rationale stop space bar from opening focused elements (eg dataset list)
            this.space_bar = true

            // we update this directly otherwise it has to wait for mousemove
            // and that could be confusing

          }
          if (this.ctrl_key && (event.keyCode == cKey)){
            this.copy_instance(true);
          }
          if (this.ctrl_key && (event.keyCode == vKey)) {
            this.paste_instance();
          }

          if(event.keyCode === 90 && this.ctrl_key){ // ctrl + z
            this.undo();
          }

          if(event.keyCode === 89 && this.ctrl_key){ // ctrl + z
            this.redo();
          }

        },
        reset_drawing: function(){
          if (this.$props.view_only_mode == true) {
            return
          }
          this.lock_point_hover_change = false // reset
          this.ellipse_current_drawing_face = false // reset
          this.show_polygon_border_context_menu = false;
          if (this.auto_border_polygon_p2_index != undefined) {
            const instance = this.instance_list[this.auto_border_polygon_p2_instance_index]
            instance.points[this.auto_border_polygon_p2_index].point_set_as_auto_border = false;
            instance.points[this.auto_border_polygon_p2_index].hovered_while_drawing = false;
          }
          if (this.auto_border_polygon_p1_index != undefined) {
            const instance = this.instance_list[this.auto_border_polygon_p1_instance_index]
            instance.points[this.auto_border_polygon_p1_index].point_set_as_auto_border = false;
            instance.points[this.auto_border_polygon_p1_index].hovered_while_drawing = false;
          }
          this.hide_context_menu()

          this.$store.commit('finish_draw')
          this.current_polygon_point_list = []
          this.auto_border_polygon_p1 = undefined;
          this.auto_border_polygon_p1_index = undefined;
          this.auto_border_polygon_p1_figure = undefined;
          this.auto_border_polygon_p1_instance_index = undefined;
          this.auto_border_polygon_p2 = undefined;
          this.auto_border_polygon_p2_index = undefined;
          this.auto_border_polygon_p2_figure = undefined;
          this.auto_border_polygon_p2_instance_index = undefined;
          this.instance_template_draw_started = false;
          this.is_actively_drawing = false;
          this.instance_template_start_point = undefined;
        },
        show_loading_paste: function(){
          this.show_snackbar_paste = true;
          this.snackbar_paste_message = 'Pasting Instances Please Wait....';
        },
        show_success_paste: function(){
          this.show_snackbar_paste = true;
          this.snackbar_paste_message = 'Instance Pasted on Frames ahead.';
        },
        initialize_instance: function(instance){
          // TODO: add other instance types as they are migrated to classes.
          if(instance.type === 'keypoints' && !instance.initialized){
            let initialized_instance = new KeypointInstance(
              this.mouse_position,
              this.canvas_element_ctx,
              this.instance_context,
              this.trigger_instance_changed,
              this.instance_selected,
              this.instance_deselected,
              this.mouse_down_delta_event,
              this.label_settings
            );
            initialized_instance.populate_from_instance_obj(instance);
            return initialized_instance
          }
          else{
            return instance
          }
        },
        save_multiple_frames: async function(frames_list){
          const limit = pLimit(25); // 25 Max concurrent request.
          try {
            this.save_multiple_frames_error = {};
            const promises = frames_list.map(frame_number => {
              return limit(() => this.save(false, frame_number, this.instance_buffer_dict[frame_number]))
            });
            const result = await Promise.all(promises);
            return result

          } catch (error) {
            this.save_multiple_frames_error = this.$route_api_errors(error);
            console.error(error);
          }
        },
        add_pasted_instance_to_instance_list: async function(instance_clipboard, next_frames, original_file_id){
          let on_new_frame_or_file = false;
          if(instance_clipboard.original_frame_number != this.current_frame || next_frames != undefined){
            on_new_frame_or_file = true;
          }
          if(this.$props.file && this.$props.file.id != original_file_id){
            on_new_frame_or_file = true;
          }
          if(this.$props.task && this.$props.task.file.id != original_file_id){
            on_new_frame_or_file = true;
          }
          if(instance_clipboard.type === 'point' && !on_new_frame_or_file){
            instance_clipboard.points[0].x += 50
            instance_clipboard.points[0].y += 50
          }
          else if(instance_clipboard.type === 'box' && !on_new_frame_or_file){
            instance_clipboard.x_min += 50
            instance_clipboard.x_max += 50
            instance_clipboard.y_min += 50
            instance_clipboard.y_max += 50
          }
          else if((instance_clipboard.type === 'line' || instance_clipboard.type === 'polygon') && !on_new_frame_or_file){
            for(const point of instance_clipboard.points){
              point.x += 50;
              point.y += 50;
            }
          }
          else if((instance_clipboard.type === 'keypoints') && !on_new_frame_or_file){
            for(const node of instance_clipboard.nodes){
              node.x += 50;
              node.y += 50;
            }
          }
          else if(instance_clipboard.type === 'cuboid'  && !on_new_frame_or_file){
            for(let key in instance_clipboard.front_face){
              if(['width', 'height'].includes(key)){continue}
              instance_clipboard.front_face[key].x += 85
              instance_clipboard.front_face[key].y += 85
              instance_clipboard.rear_face[key].x += 85
              instance_clipboard.rear_face[key].y += 85
            }
          }
          else if(instance_clipboard.type === 'ellipse'  && !on_new_frame_or_file){
            instance_clipboard.center_y += 50
            instance_clipboard.center_x += 50
          }
          else if(instance_clipboard.type === 'curve'  && !on_new_frame_or_file){
            instance_clipboard.p1.x += 50
            instance_clipboard.p1.y += 50
            instance_clipboard.p2.x += 50
            instance_clipboard.p2.y += 50
          }
          // Deselect instances.
          for(const instance of this.instance_list){
            instance.selected = false;
          }
          let pasted_instance = this.initialize_instance(instance_clipboard);
          if(next_frames != undefined){
            let next_frames_to_add = parseInt(next_frames, 10);
            const frames_to_save = [];
            for(let i = this.current_frame + 1; i <= (this.current_frame + next_frames_to_add); i++){
              // Here we need to create a new COPY of the instance. Otherwise, if we moved one instance
              // It will move on all the other frames.
              let new_frame_instance = this.duplicate_instance(pasted_instance);
              new_frame_instance = this.initialize_instance(new_frame_instance);
              // Set the last argument to true, to prevent to push to the instance_list here.
              this.add_instance_to_frame_buffer(new_frame_instance, i);
              frames_to_save.push(i);
            }
            this.create_instance_events()
            this.show_loading_paste()
            await this.save_multiple_frames(frames_to_save);
            this.show_success_paste()
          }
          else{
            this.push_instance_to_instance_list_and_buffer(pasted_instance, this.current_frame);
            // Auto select on label view detail for inmediate attribute edition.
            this.create_instance_events()
          }

        },
        paste_instance: async function(next_frames = undefined, instance_hover_index = undefined){
          const clipboard = this.clipboard;
          if(!clipboard && instance_hover_index == undefined){return}
          if(instance_hover_index != undefined){
            this.copy_instance(false, instance_hover_index)
          }
          // We need to duplicate on each paste to avoid double ID's on the instance list.
          const new_clipboard_instance_list = [];
          for(const instance_clipboard of this.clipboard.instance_list){
            let instance_clipboard_dup = this.duplicate_instance(instance_clipboard);
            await this.add_pasted_instance_to_instance_list(instance_clipboard_dup, next_frames, this.clipboard.file_id)
            new_clipboard_instance_list.push(instance_clipboard_dup)
          }
          this.set_clipboard(new_clipboard_instance_list)
        },
        set_clipboard: function(instance_list){
          let file_id = undefined;
          if(this.$props.file && this.$props.file.id){
            file_id = this.$props.file.id
          }
          if(this.$props.task && this.$props.task.file && this.$props.task.file.id){
            file_id = this.$props.task.file.id;
          }
          this.$store.commit('set_clipboard',{instance_list: instance_list, file_id: file_id})
        },
        on_context_menu_copy_instance: function(instance_index){
          this.copy_instance(false, instance_index);
        },
        duplicate_instance: function(instance_to_copy){
          let points = []
          let nodes = []
          let edges = []
          if(instance_to_copy.points) {
            points = [...instance_to_copy.points.map(p => ({...p}))]
          }
          if (instance_to_copy.nodes){
            nodes = [...instance_to_copy.nodes.map(node => ({...node}))]
          }
          if (instance_to_copy.edges){
            edges = [...instance_to_copy.edges.map(edge => ({...edge}))]
          }
          let result = {
            ...instance_to_copy,
            id: undefined,
            initialized: false,
            points: points,
            nodes: nodes,
            edges: edges,
            version: undefined,
            root_id: undefined,
            previous_id: undefined,
            action_type: undefined,
            next_id: undefined,
            creation_ref_id: undefined,
            attribute_groups: instance_to_copy.attribute_groups ? {...instance_to_copy.attribute_groups} : null
          };

          if(result.type === 'cuboid'){
            result.rear_face = {
              ...instance_to_copy.rear_face,
              top_right: {...instance_to_copy.rear_face.top_right},
              top_left: {...instance_to_copy.rear_face.top_left},
              bot_left: {...instance_to_copy.rear_face.bot_left},
              bot_right: {...instance_to_copy.rear_face.bot_right},
            }

            result.front_face = {
              ...instance_to_copy.front_face,
              top_right: {...instance_to_copy.front_face.top_right},
              top_left: {...instance_to_copy.front_face.top_left},
              bot_left: {...instance_to_copy.front_face.bot_left},
              bot_right: {...instance_to_copy.front_face.bot_right},
            }
          }

          result = this.initialize_instance(result);
          return result
        },
        copy_all_instances: function(){
          let new_instance_list = []
          for(const instance of this.instance_list){
            if(instance.soft_delete){
              continue
            }
            let instance_clipboard = this.duplicate_instance(instance);
            instance_clipboard.selected = false;
            instance_clipboard.original_frame_number = this.current_frame;
            new_instance_list.push(instance_clipboard)

          }
          this.set_clipboard(new_instance_list);
          this.show_snackbar('All Instances copied into clipboard.')
        },
        copy_instance: function(hotkey_triggered = false, instance_index = undefined){
          if(this.draw_mode){return}
          if(!this.label_settings.allow_multiple_instance_select){
            if(!this.selected_instance && instance_index == undefined){return}
            if(this.hotkey_triggered && !this.selected_instance){ return }
            const instance_to_copy = this.selected_instance ? this.selected_instance : this.instance_list[instance_index];
            this.instance_clipboard = this.duplicate_instance(instance_to_copy);
            this.instance_clipboard.selected = true;
            this.instance_clipboard.original_frame_number = this.current_frame;
            this.set_clipboard([this.instance_clipboard]);
          }
          else{
            alert('Copy paste not implements for multiple instnaces.')
            // TODO implement flag limit conditions for multi selects.
            if(!this.selected_instance && instance_index == undefined){return}
          }
        },
        update_draw_mode_on_instances: function(draw_mode){
          this.instance_context.draw_mode = draw_mode;
        },
        edit_mode_toggle: function (draw_mode) {
          this.reset_drawing();
          this.draw_mode = draw_mode    // context from external component like toolbar
          this.update_draw_mode_on_instances(draw_mode);
          this.is_actively_drawing = false    // QUESTION do we want this as a toggle or just set to false to clear
        },

        add_ids_to_new_instances_and_delete_old: function(response, request_video_data){
          /*
      * This function is used in the context of AnnotationUpdate.
      * The new created/deleted instances are merged without loss of the current
      * frontend data (like selected context for example).
      * This is done by destructuring the new instance (the one received from backend)
      * and then adding the original instance keys on top of the new one.
      * */
          // Add instance ID's to the newly created instances

          const new_added_instances = response.data.added_instances;
          const new_deleted_instances = response.data.deleted_instances;
          let instance_list = this.instance_list;
          if(this.video_mode){
            instance_list = this.instance_buffer_dict[request_video_data.current_frame]
          }
          for(let i = 0;  i < instance_list.length; i++){
            const current_instance = instance_list[i]
            if(!current_instance.id){
              // Case of a new instance added
              const new_instance = new_added_instances.filter(x => x.creation_ref_id === current_instance.creation_ref_id)
              if(new_instance.length > 0){
                // Now update the instance with the new ID's provided by the API
                current_instance.id = new_instance[0].id;
                current_instance.root_id =  new_instance[0].root_id;
                current_instance.version =  new_instance[0].version;
                current_instance.sequence_id = new_instance[0].sequence_id;
                current_instance.number = new_instance[0].number;
                instance_list.splice(i, 1, current_instance)

              }
            }
            else{
              // Case of an instance updated.
              const new_instance = new_added_instances.filter(x => x.previous_id === current_instance.id)
              if(new_instance.length > 0){
                // Now update the instance with the new ID's provided by the API
                current_instance.id = new_instance[0].id;
                current_instance.root_id =  new_instance[0].root_id;
                current_instance.previous_id =  new_instance[0].previous_id;
                current_instance.version =  new_instance[0].version;
                current_instance.sequence_id = new_instance[0].sequence_id;
                current_instance.number = new_instance[0].number;
                instance_list.splice(i, 1, current_instance)

              }
            }

          }


          const current_frontend_instances = instance_list.map(id => id);

        },
        hash_string: function(str){
          return sha256(str)
        },
        has_duplicate_instances: function(instance_list){
          if(!instance_list){
            return [false, [], []];
          }
          const hashes = {};
          const dup_ids = [];
          const dup_indexes = [];
          for(let i = 0; i < instance_list.length; i++){
            const inst = instance_list[i];
            if(inst.soft_delete){
              continue;
            }
            const inst_data = {
              type: inst.type,
              x_min: inst.x_min,
              y_min: inst.y_min,
              y_max: inst.y_max,
              x_max: inst.x_max,
              p1: inst.p1,
              p2: inst.p2,
              cp: inst.cp,
              center_x: inst.center_x,
              center_y: inst.center_y,
              angle: inst.angle,
              width: inst.width,
              height: inst.height,
              start_char: inst.start_char,
              end_char: inst.end_char,
              start_token: inst.start_token,
              end_token: inst.end_token,
              start_sentence: inst.start_sentence,
              end_sentence: inst.end_sentence,
              sentence: inst.sentence,
              label_file_id: inst.label_file_id,
              number: inst.number,
              rating: inst.rating,
              points: inst.points ? inst.points.map(point => {return {...point}}) : inst.points,
              front_face: {...inst.front_face},
              rear_face: {...inst.rear_face},
              soft_delete: inst.soft_delete,
              attribute_groups: {...inst.attribute_groups},
              machine_made: inst.machine_made,
              sequence_id: inst.sequence_id,
              pause_object: inst.pause_object
            }

            // We want a nested stringify with sorted keys. Builtin JS does not guarantee sort on nested objs.
            const inst_hash_data = stringify(inst_data)
            let inst_hash = this.hash_string(inst_hash_data)
            if(hashes[inst_hash]){
              dup_ids.push(inst.id ? inst.id : 'New Instance')
              dup_ids.push(hashes[inst_hash][0].id ? hashes[inst_hash][0].id : 'New Instance')

              dup_indexes.push(i)
              dup_indexes.push(hashes[inst_hash][1])
              return [true, dup_ids, dup_indexes];

            }
            else{
              hashes[inst_hash] = [inst, i]
            }

          }
          return [false, dup_ids, dup_indexes];

        },
        refresh_sequence_frame_list: function(instance_list, frame_number){

          for(const instance of instance_list){
            this.$refs.sequence_list.add_frame_number_to_sequence(instance.sequence_id, frame_number)
          }
        },
        save: async function (and_complete=false, frame_number_param = undefined, instance_list_param = undefined) {
          this.save_error = {}
          this.save_warning = {}
          if (this.$props.view_only_mode == true) {
            return
          }
          let current_frame = undefined;
          let instance_list = this.instance_list;
          if(this.video_mode){
            if(frame_number_param == undefined){
              current_frame = parseInt(this.current_frame, 10)
            }
            else{
              current_frame = parseInt(frame_number_param, 10)
            }

            if(instance_list_param != undefined){
              instance_list = instance_list_param;

            }


          }
          if(this.get_save_loading(current_frame) == true){
            // If we have new instances created while saving. We might still need to save them after the first
            // save has been completed.

            return
          }
          if (this.any_loading == true) {
            return
          }

          this.set_save_loading(true, current_frame);
          let [has_duplicate_instances, dup_ids, dup_indexes] = this.has_duplicate_instances(instance_list)
          let dup_instance_list = dup_indexes.map(i => ({...instance_list[i], original_index: i}))
          dup_instance_list.sort(function(a,b){
            return moment(b.client_created_time, 'YYYY-MM-DD HH:mm') - moment(a.client_created_time, 'YYYY-MM-DD HH:mm');
          })
          if(has_duplicate_instances){
            this.save_warning = {
              duplicate_instances: `Instance list has duplicates: ${dup_ids}. Please move the instance before saving.`
            }

            // We want to focus the most recent instance, if we focus the older one we can produce an error.
            this.$refs.instance_detail_list.toggle_instance_focus(dup_instance_list[0].original_index, undefined);

            this.set_save_loading(false, current_frame);

            return
          }
          this.instance_list_cache = instance_list.slice();
          let current_frame_cache = this.current_frame;
          let current_video_file_id_cache = this.current_video_file_id;
          let video_mode_cache = this.video_mode;



          // a video file can now be
          // saved from file id + frame, so the current file
          let current_file_id = null;
          if(this.$props.file){
            current_file_id = this.$props.file.id;
          }
          else if(this.$props.task){
            current_file_id = this.$props.task.file.id
          }
          else{
            throw new Error('You must provide either a file or a task in props in order to save.')
          }


          var url = null

          if (this.task && this.task.id) {
            url = '/api/v1/task/' + this.task.id +
              '/annotation/update'
          } else {

            if (this.$store.state.builder_or_trainer.mode == "builder") {
              url = '/api/project/' + this.project_string_id +
                '/file/' + current_file_id + '/annotation/update'
            }
          }

          video_data = null
          if (video_mode_cache == true) {
            var video_data = {
              video_mode: video_mode_cache,
              video_file_id: current_video_file_id_cache,
              current_frame: current_frame
            }
          }

          try {
            const response = await axios.post(url, {
              instance_list: this.instance_list_cache,
              and_complete: and_complete,
              directory_id: this.$store.state.project.current_directory.directory_id,
              gold_standard_file: this.gold_standard_file,    // .instance_list gets updated ie missing
              video_data: video_data
            })
            /*
           * TODO important,
           * in context of video, and wanting to allow the user to save and not wait for save
           * response from server, is there any of this stuff that gets "returned"
           * that we should *not* be updating?
           *
           * Context of https://github.com/swirlingsand/ai_vision/commit/ba405b6ab75de64457fc27f6e47cc7962328075c
           *
           * Basically realizing that so long as save succeeds, for video,
           * it should make minimal assumptions about the state.
           * ie the state after saving may not be the same as when save was initiated
           *
           * rightn now we blindly pass the updated sequence (which we DO want if the user stays
           * on the frame), and trust sequence to handle this distction, ie checking albel file id
           * is the same. As mentioned IF there ends up being some unified sequence thing
           * that may help avoid that issue, but either way anything chained to this could be
           * effected ... ie need to trace what save_response_callback was doing.
           *
           */

            this.save_count += 1;
            this.add_ids_to_new_instances_and_delete_old(response, video_data);


            this.check_if_pending_created_instance();
            this.$emit('save_response_callback', true)

            if(this.instance_buffer_metadata[this.current_frame]){
              this.instance_buffer_metadata[this.current_frame].pending_save = false;
            }
            else{
              this.instance_buffer_metadata[this.current_frame] = {pending_save: false};
            }

            if (response.data.sequence) {
              // Because: new color thing based on sequence id but seq id not assigned till response
              // not good code. just placeholder in current constraints until we can figure out something better.
              // ie maybe whole instance should be getting replaced
              let instance_list_request_frame = this.instance_list;
              if(this.video_mode){
                // Get the instance_list of the updated frame. Getting it from this.instance_list is bad
                // Because it could have potentially changed during save.
                instance_list_request_frame = this.instance_buffer_dict[video_data.current_frame]
              }
              let instance_index = instance_list_request_frame.findIndex(
                x => x.label_file_id == response.data.sequence.label_file_id &&
                  x.soft_delete === false &&
                  x.number == response.data.sequence.number)
              // just in case so we don't overwrite
              // maybe don't need this, but going to look at other options in the future there too
              // doesn't cover buffer case?
              if(instance_index
                &&  instance_list_request_frame[instance_index]
                && instance_list_request_frame[instance_index].sequence_id == undefined
                && instance_list_request_frame[instance_index].label_file_id == response.data.sequence.label_file_id) {
                instance_list_request_frame[instance_index].sequence_id = response.data.sequence.id
              }
              // end of temp sequence thing

              // Update any new created sequences
              if(response.data.new_sequence_list){
                for(let new_seq of response.data.new_sequence_list){
                  this.$refs.sequence_list.add_new_sequence_to_list(new_seq);
                }
              }
              if(this.video_mode){
                this.refresh_sequence_frame_list(instance_list_request_frame, video_data.current_frame);
              }
            }



            /* When we save the file and go to next, we don't rely upon the
         * newly returned file to be anything related to the next task
         * We simply go to the "well" so to speak and request the next task here
         * using the "change_file".
         */
            this.set_save_loading(false, current_frame);
            this.has_changed = false
            if (and_complete == true) {
              // now that complete completes whole video, we can move to next as expected.
              this.snackbar_success = true
              this.snackbar_success_text = "Saved and completed. Moved to next."

              if(this.task && this.task.id){   // props
                this.trigger_task_change('next', this.task)
              }
              else{
                this.trigger_task_change('next', 'none')    // important
              }


            }
            this.check_if_pending_created_instance();
            return true
          } catch (error) {
            console.error(error);
            this.set_save_loading(false, current_frame);
            if(error.response.data &&
              error.response.data.log &&
              error.response.data.log.error && error.response.data.log.error.missing_ids){
              this.display_refresh_cache_button = true;
              clearInterval(this.interval_autosave);
            }

            this.save_error = this.$route_api_errors(error)
            console.debug(error);
            //this.logout()
            return false
          }
        },
        complete_task() {
          if(!this.task){
            return
          }
          this.task.status = 'complete';
        },
        request_next_instance: function(label_file_id){
          this.$refs.video_controllers.next_instance(label_file_id);
        },
      }
    }
  ) </script>

<style>
  #canvas_wrapper, #annotation_core{
    outline: none;
    -webkit-tap-highlight-color: rgba(255, 255, 255, 0); /* mobile webkit */
  }
</style>
