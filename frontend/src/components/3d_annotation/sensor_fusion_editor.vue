<template>
  <div id="3d-editor-container">
    <div style="position: relative">
      <main_menu :height="`100px`">

        <template slot="second_row" >

          <toolbar_sensor_fusion :height="50"
                    class="pa-0"
                   :save_loading="this.video_mode ? this.save_loading_frame[this.current_frame] : this.save_loading_scene"
                   :annotations_loading="false"
                   :loading="false"
                   :view_only_mode="false"
                   :label_settings="editor_3d_settings"
                   :project_string_id="project_string_id"
                   :task="task"
                   :file="file"
                   :canvas_scale_local="canvas_scale_local"
                   :has_changed="has_changed"
                   :label_list="label_list"
                   :draw_mode="draw_mode"
                   :label_file_colour_map="label_file_colour_map"
                   @label_settings_change="label_settings = $event, refresh = Date.now()"
                   @change_label_file="change_label_file"
                   @update_label_file_visibility=""
                   @change_instance_type="change_instance_type($event)"
                   @edit_mode_toggle="edit_mode_toggle($event)"
                   @save="save()"
                   @change_file="change_file($event)"
                   @change_task="trigger_task_change($event, task)"
                   @next_issue_task="next_issue_task(task)"
                   @complete_task="complete_task()"
                   @new_tag_instance="insert_tag_type()"
                   @replace_file="$emit('replace_file', $event)"
                   :full_file_loading="full_file_loading"
                   :instance_type="instance_type"
                   :instance_type_list="instance_type_list"
                   :view_issue_mode="view_issue_mode"
          >
          </toolbar_sensor_fusion>



        </template>

      </main_menu>

      <v_error_multiple :error="warning" type="warning" data-cy="save_warning">
      </v_error_multiple>
      <v_error_multiple :error="error">
      </v_error_multiple>
    </div>
    <div class="editor-body d-flex">

      <div class="sidebar-left-container" :style="{width: `${editor_3d_settings.left_nav_width}px`, overflow: 'hidden', paddingLeft: '12px'}">
        <instance_detail_list_view  ref="instance_detail_list"
                                    v-if="file && current_label_file && label_file_colour_map"
                                    :instance_list="instance_list"
                                    :model_run_list="undefined"
                                    :label_file_colour_map="label_file_colour_map"
                                    :refresh="refresh"
                                    @toggle_instance_focus="()=>{}"
                                    @show_all="()=>{}"
                                    @update_canvas="()=>{}"
                                    @instance_update="instance_update"
                                    :video_mode="false"
                                    :task="task"
                                    :view_only_mode="view_only_mode"
                                    :label_settings = "label_settings"
                                    :label_list = "label_list"
                                    :draw_mode = "draw_mode"
                                    :current_frame = "current_frame"
                                    :current_video_file_id = "file.id"
                                    :current_label_file_id = "current_label_file.id"
                                    :video_playing="video_playing"
                                    :external_requested_index="request_change_current_instance"
                                    :trigger_refresh_current_instance="trigger_refresh_current_instance"
                                    :current_file="file ? file : task"
        >
        </instance_detail_list_view>

      </div>
      <div class="canvas-container" >
        <div id="main_3d_canvas_container"  style="position: relative" @contextmenu="open_context_menu">
          <canvas_3d
            v-if="main_canvas_height && main_canvas_width && point_cloud_mesh"
            ref="main_3d_canvas"
            :show_loading_bar="true"
            :width="main_canvas_width"
            :point_cloud_mesh="point_cloud_mesh"
            :height="main_canvas_height"
            :zoom_speed="editor_3d_settings.zoom_speed"
            :pan_speed="editor_3d_settings.pan_speed"
            :allow_navigation="true"
            :instance_list="instance_list"
            :current_label_file="current_label_file"
            :draw_mode="draw_mode"
            :container_id="'main_screen'"
            :with_keyboard_controls="true"
            @instance_drawn="on_instance_drawn"
            @updated_mouse_position="on_update_mouse_position"
            @instance_hovered="on_instance_hovered"
            @instance_unhovered="on_instance_unhovered"
            @instance_selected="on_instance_selected"
            @scene_ready="on_scene_ready"
            @instance_updated="on_instance_updated">

          </canvas_3d>
          <div  class="ma-auto d-flex flex-column justify-center"
                v-else
                :style="{width: `${main_canvas_width}px`, height: `${main_canvas_height}px`, background: 'white'}">
            <h2 class="ma-auto mb-0">Loading 3D Data...</h2>
            <v-progress-linear
              height="50"
              class="ma-auto mr-4 ml-4"
              striped
              :value="percentage">

            </v-progress-linear>
          </div>

          <context_menu_3d_editor
            :mouse_position="mouse_position"
            :show_context_menu="show_context_menu"
            :instance_clipboard="instance_clipboard"
            :draw_mode="draw_mode"
            :selected_instance_index="selected_instance_index"
            :project_string_id="project_string_id"
            :task="task"
            :instance_hover_index="instance_hover_index"
            :instance_list="instance_list"
            @instance_update="instance_update($event)"
            @share_dialog_open="open_share_dialog"
            @delete_instance="delete_instance"
            @copy_instance="on_context_menu_copy_instance"
            @paste_instance="paste_instance"
            @open_instance_history_panel="show_instance_history_panel"
            @close_instance_history_panel="close_instance_history_panel"
            ref="context_menu"
            @share_dialog_close="close_share_dialog"
            @close_context_menu="show_context_menu = false"
          ></context_menu_3d_editor>
        </div>
        <div id="secondary_3d_canvas_container" class="d-flex">
          <div class="mr-1 mt-1">
            <canvas_3d
              v-if="secondary_canvas_width && secondary_canvas_height && point_cloud_mesh"
              ref="x_axis_3d_canvas"
              :point_cloud_mesh="point_cloud_mesh"
              :create_new_scene="false"
              camera_type="ortographic"
              :width="secondary_canvas_width"
              :height="secondary_canvas_height"
              :allow_navigation="true"
              :instance_list="instance_list"
              :current_label_file="current_label_file"
              :draw_mode="draw_mode"
              :container_id="'x_axis_3d_canvas'"
              :with_keyboard_controls="true">
            </canvas_3d>
          </div>
          <div class="mr-1 mt-1">

            <canvas_3d
              v-if="secondary_canvas_width && secondary_canvas_height && point_cloud_mesh"
              ref="y_axis_3d_canvas"
              :create_new_scene="false"
              camera_type="ortographic"
              :width="secondary_canvas_width"
              :point_cloud_mesh="point_cloud_mesh"
              :height="secondary_canvas_height"
              :allow_navigation="true"
              :instance_list="instance_list"
              :current_label_file="current_label_file"
              :draw_mode="draw_mode"
              :container_id="'y_axis_3d_canvas'"
              :with_keyboard_controls="true">
            </canvas_3d>
          </div>
          <div class="mr-1 mt-1">

            <canvas_3d
              v-if="secondary_canvas_width && secondary_canvas_height && point_cloud_mesh"
              ref="z_axis_3d_canvas"
              :point_cloud_mesh="point_cloud_mesh"
              :create_new_scene="false"
              camera_type="ortographic"
              :width="secondary_canvas_width"
              :height="secondary_canvas_height"
              :allow_navigation="true"
              :instance_list="instance_list"
              :current_label_file="current_label_file"
              :draw_mode="draw_mode"
              :container_id="'z_axis_3d_canvas'"
              :with_keyboard_controls="true">
            </canvas_3d>
          </div>
        </div>

      </div>
    </div>
    <v-snackbar v-model="show_snackbar" :timeout="3000" color="secondary">
      {{snackbar_text}}

      <template v-slot:action="{ attrs }">
        <v-btn
          color="white"
          text
          v-bind="attrs"
          @click="snackbar_success = false"
        >
          Close
        </v-btn>
      </template>
    </v-snackbar>
  </div>

</template>

<script>
  import Vue from "vue";
  import {
    has_duplicate_instances,
    add_ids_to_new_instances_and_delete_old,
    check_if_pending_created_instance
  } from '../annotation/utils/AnnotationUtills';
  import toolbar_sensor_fusion from "./toolbar_sensor_fusion";
  import instance_detail_list_view from "../annotation/instance_detail_list_view";
  import context_menu_3d_editor from "./context_menu_3d_editor";
  import canvas_3d from "./canvas_3d";
  import moment from "moment";
  import axios from "axios";
  import * as instanceServices from '../../services/instanceServices';
  import FileLoader3DPointClouds from "./FileLoader3DPointClouds";
  import * as instance_utils from "../../utils/instance_utils"
  import * as THREE from "three";
  import {UpdateInstanceCommand} from "../annotation/commands/update_instance_command.ts";
  import {CommandManagerAnnotationCore} from "../annotation/annotation_core_command_manager";

  export default Vue.extend({
    name: "sensor_fusion_editor_3d",
    components:{
      toolbar_sensor_fusion,
      instance_detail_list_view,
      context_menu_3d_editor,
      canvas_3d
    },
    props: {
      'project_string_id': {
        default: null
      },
      'file': {
        default: null
      },
      'task': {
        default: null
      },
      'view_only_mode':{
        default: true
      },
      'label_file_colour_map':{
        default: null
      },
      'label_list':{
        default: null
      },
      'video_mode':{
        default: false,
      }

    },
    data(){
      return{
        instance_type_list: [
          {'name': 'cuboid_3d',
            'display_name': 'Cuboid 3D',
            'icon': 'mdi-cube-outline'
          },
        ],
        error: null,
        warning: null,
        percentage: 0,
        has_changed: false,
        save_loading_scene: false,
        show_context_menu: false,
        instance_type: 'cuboid_3d',
        snackbar_text: '',
        show_snackbar: false,
        draw_mode: false,
        request_change_current_instance: null,
        instance_hover_index: null,
        save_loading_frame: {},
        instance_hover: null,
        current_frame: null,
        instance_list_cache: [],
        video_playing: null,
        trigger_refresh_current_instance: null,
        instance_clipboard: undefined,
        secondary_3d_canvas_container: null,
        mouse_position: {
          raw: {
            x: 0,
            y: 0
          },
          x: 150,
          y: 150
        },

        current_label_file: null,
        point_cloud_mesh: null,
        full_file_loading: false,
        instance_list: [],
        view_issue_mode: false,
        canvas_scale_local: 1,  // for actually scaling dimensions within canvas
        canvas_translate: {
          x: 0,
          y: 0
        },

        editor_3d_settings: {
          show_text: true,
          show_label_text: true,
          show_attribute_text: true,
          show_list: true,
          allow_multiple_instance_select: false,
          save_loading_frame: false,
          font_size: 20,
          spatial_line_size: 2,
          vertex_size: 3,
          show_removed_instances: false,

          target_reticle_size: 20,
          filter_brightness: 100, // Percentage. Applies a linear multiplier to the drawing, making it appear more or less bright.
          filter_contrast: 100, // Percentage. A value of 0% will create a drawing that is completely black. A value of 100% leaves the drawing unchanged.
          filter_grayscale: 0, //  A value of 100% is completely gray-scale. A value of 0% leaves the drawing unchanged.
          instance_buffer_size: 60,
          zoom_speed: 1,
          pan_speed: 1,
          canvas_scale_global_is_automatic: true,
          canvas_scale_global_setting: 0.5,
          left_nav_width: 450,
          on_instance_creation_advance_sequence: true,
          ghost_instances_closed_by_open_view_edit_panel: false,

        },
        main_canvas_width: undefined,
        command_manager: undefined,
        main_canvas_height: undefined,
        secondary_canvas_width: undefined,
        secondary_canvas_height: undefined,
      }
    },
    async created(){
      await this.initialize_file();
      this.command_manager = new CommandManagerAnnotationCore();

    },

    async mounted() {
      window.addEventListener( 'resize', this.on_window_resize );
      window.addEventListener( 'keydown', this.key_down_handler, false );
      document.addEventListener('mousedown', this.mouse_events_global_down);

      this.calculate_main_canvas_dimension();
      this.calculate_secondary_canvas_dimension();



    },
    beforeDestroy() {
      window.removeEventListener( 'resize', this.on_window_resize );
      window.removeEventListener( 'keydown', this.key_down_handler, false );
      document.removeEventListener('mousedown', this.mouse_events_global_down);
    },
    computed:{
      any_loading: function(){
        return this.save_loading_scene
      },
      selected_instance_index: function(){
        if(!this.$refs.main_3d_canvas){
          return
        }
        let scene_ctrl = this.$refs.main_3d_canvas.scene_controller;
        if(scene_ctrl.selected_instance){
          return scene_ctrl.selected_instance
        }
      },
      pcd_url: function(){
        if(!this.$props.file){
          return
        }
        return this.$props.file.point_cloud.url_signed;
      },
    },
    watch:{
      file: function(new_val, old_val){
        if(new_val != old_val){
          this.reload_file_data();
        }

      }
    },
    methods: {
      delete_instance: function(){
        if (this.$props.view_only_mode == true) { return }

        for (var i in this.instance_list) {
          if (this.instance_list[i].selected == true) {
            this.instance_update({
              index: i,
              mode: "delete"
            })
          }
        }
      },
      create_update_command(index, instance, initial_instance, update) {
        const command = new UpdateInstanceCommand(instance, index, initial_instance, this, this.$refs.main_3d_canvas.scene_controller);
        this.command_manager.executeCommand(command);
        return true

      },
      instance_update: function (update) {
        if (this.$props.view_only_mode == true) { return }


        let index = update.index
        if (index == undefined) { return }  // careful 0 is ok.


        let initial_instance = this.instance_list[index];
        initial_instance = instance_utils.initialize_instance_object(initial_instance);
        // since sharing list type component need to determine which list to update
        // could also use render mode but may be different contexts
        if (!update.list_type || update.list_type == "default") {
          var instance = this.instance_list[index]
        }

        if (!instance) {
          console.error("Invalid index")
          return
        }


        if (update.mode === 'on_click_update_point_attribute'){
          instance.toggle_occluded(update.node_hover_index)
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

        if (update.mode == "delete") {
          instance.soft_delete = true
          console.log('INSTANCE', instance)
          this.$refs.main_3d_canvas.scene_controller.deselect_instance();
          this.$refs.main_3d_canvas.scene_controller.remove_from_scene(instance.mesh);

        }

        if (update.mode == "delete_undo") {
          instance.soft_delete = false;
          instance.draw_on_scene()
          this.$refs.main_3d_canvas.scene_controller.select_instance(instance, index);

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
          if (!instance.attribute_groups) {
            instance.attribute_groups = {}
          }
          let group = update.payload[0]
          let value = update.payload[1]

          // we assume this represents a group
          initial_instance.prev_attribute = {
            group: group.id,
            value: {...instance.attribute_groups[group.id]}
          }
          instance.attribute_groups[group.id] = value
          //console.debug(group, value)
        }

        // end instance update

        this.create_update_command(index, instance, initial_instance, update)

        this.has_changed = true;

      },
      load_pcd: async function () {
        let file_loader_3d = new FileLoader3DPointClouds(this);
        this.point_cloud_mesh = await file_loader_3d.load_pcd_from_url(this.pcd_url);
        console.log('this.pcd_url', this.pcd_url)
        this.point_cloud_mesh.material = new THREE.MeshBasicMaterial({
          color: new THREE.Color('white'),
          opacity: 1,
          transparent: false,
        });
        console.log('point_cloud_mesh', this.point_cloud_mesh)
        return this.point_cloud_mesh

      },
      add_meshes_to_scene: function(instance_list){
        if(!this.$refs.main_3d_canvas.scene_controller){
          return
        }
        let i = 0;
        for(const inst of instance_list){
          if(inst.type === 'cuboid_3d'){
            this.$refs.main_3d_canvas.scene_controller.add_mesh_to_scene(inst.mesh, false);
            this.$refs.main_3d_canvas.scene_controller.add_mesh_user_data_to_instance(inst, i)
          }
          else{
            throw Error(`Cannot render 3D instance type ${inst.type}`)
          }
          i +=1;
        }

      },
      load_instance_list: async function(){
        let file_data;
        this.instance_list.length = 0;
        if(this.file){
          file_data = await instanceServices.get_instance_list_from_file(this.project_string_id, this.file.id)
        }
        else if(this.task){
          file_data = await instanceServices.get_instance_list_from_task(this.project_string_id, this.task.id)
        }
        else{
          throw Error('A task or a file must be provided in props to fetch instances.')
        }
        let instance_list = file_data.file_serialized.instance_list;

        instance_list = instance_utils.create_instance_list_with_class_types(instance_list, this, this.$refs.main_3d_canvas.scene_controller);
        for(let inst of instance_list){
          this.instance_list.push(inst)
        }
        this.add_meshes_to_scene(this.instance_list);


      },
      initialize_file: async function(){
        await this.load_pcd();
        await this.load_instance_list();
      },
      reload_file_data: async function(){
        if(!this.$refs.main_3d_canvas){
          return
        }
        this.$refs.x_axis_3d_canvas.destroy_canvas()
        this.$refs.y_axis_3d_canvas.destroy_canvas()
        this.$refs.z_axis_3d_canvas.destroy_canvas()
        this.$refs.main_3d_canvas.destroy_canvas();
        await this.load_pcd();
        await this.$nextTick();
        await this.$refs.main_3d_canvas.load_canvas();
        this.calculate_main_canvas_dimension();
        this.calculate_secondary_canvas_dimension();
        await this.load_instance_list();
      },
      set_save_loading: function(value, frame){
        if(this.video_mode){
          this.save_loading_frame[frame] = value;
        }
        else{
          this.save_loading_scene = value;
        }
        this.$forceUpdate();
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
          return this.save_loading_scene;
        }
      },

      save: async function(and_complete=false, frame_number_param = undefined, instance_list_param = undefined){
        this.error = {}
        this.warning = {}
        if (this.$props.view_only_mode) {
          return
        }
        let current_frame = undefined;
        let instance_list = this.instance_list.map(inst => inst.get_instance_data());

        if(this.get_save_loading(current_frame)){
          // If we have new instances created while saving. We might still need to save them after the first
          // save has been completed.
          return
        }
        if (this.any_loading) {
          return
        }

        this.set_save_loading(true, current_frame);
        let [has_duplicate_instances_result, dup_ids, dup_indexes] = has_duplicate_instances(instance_list);
        let dup_instance_list = dup_indexes.map(i => ({...instance_list[i], original_index: i}));
        dup_instance_list.sort(function(a,b){
          return moment(b.client_created_time, 'YYYY-MM-DD HH:mm') - moment(a.client_created_time, 'YYYY-MM-DD HH:mm');
        });

        if(has_duplicate_instances_result){
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
          url = `/api/v1/task/${this.task.id}/annotation/update`
        } else {

          if (this.$store.state.builder_or_trainer.mode == "builder") {
            url = `/api/project/${this.project_string_id}/file/${current_file_id}/annotation/update`
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
          console.log('response', response);
          this.save_count += 1;
          add_ids_to_new_instances_and_delete_old(response, video_data, this.instance_list, this.$props.video_mode)

          this.has_changed = check_if_pending_created_instance(this.instance_list);
          this.$emit('save_response_callback', true)

          if(this.$props.video_mode){
            if(this.instance_buffer_metadata[this.current_frame]){
              this.instance_buffer_metadata[this.current_frame].pending_save = false;
            }
            else{
              this.instance_buffer_metadata[this.current_frame] = {pending_save: false};
            }
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
          this.has_changed = check_if_pending_created_instance(this.instance_list);
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
      hide_context_menu: function(){
        this.show_context_menu = false;
      },
      open_context_menu: function(){
        this.show_context_menu = true;
      },
      close_instance_history_panel: function(){

      },
      show_instance_history_panel: function(){

      },
      paste_instance: function(){

      },
      close_share_dialog: function(){

      },
      open_share_dialog: function(){

      },
      on_context_menu_copy_instance: function(){

      },
      on_instance_selected: function(instance, index){
        console.log('instance sleected', instance, index)
        this.center_secondary_cameras_to_instance(instance)
        this.$refs.instance_detail_list.change_instance(instance, index)

      },
      calculate_main_canvas_dimension: function(){
        let main_3d_canvas_container = document.getElementById('main_3d_canvas_container')
        if(main_3d_canvas_container){
          this.main_canvas_width = parseInt(window.innerWidth - this.editor_3d_settings.left_nav_width);
          this.main_canvas_height = parseInt(window.innerHeight * 0.65);
        }
      },
      calculate_secondary_canvas_dimension: function(){
        let secondary_3d_canvas_container = document.getElementById('main_3d_canvas_container')
        if(secondary_3d_canvas_container){
          let width = this.main_canvas_width * 0.333;
          width = parseInt(width, 10);
          this.secondary_canvas_width =  width;

          let height = window.innerHeight * 0.235;
          height = parseInt(height, 10);
          this.secondary_canvas_height = height;
        }
      },
      on_window_resize: function(event){
        this.calculate_main_canvas_dimension();
        this.calculate_secondary_canvas_dimension();
      },
      on_scene_ready: function(scene_controller){
        let main_scene = scene_controller.scene;
        this.setup_secondary_scene_controls(main_scene);
        this.$refs.main_3d_canvas.set_current_label_file(this.current_label_file);
      },
      setup_secondary_scene_controls: async function(main_scene){
        // Set scene for secondary canvas
        await this.$nextTick();
        this.secondary_3d_canvas_container = document.getElementById('secondary_3d_canvas_container')
        this.$refs.x_axis_3d_canvas.setup_scene(main_scene)
        this.$refs.y_axis_3d_canvas.setup_scene(main_scene)
        this.$refs.z_axis_3d_canvas.setup_scene(main_scene)
      },
      on_instance_updated: function(instance){
        this.center_secondary_cameras_to_instance(instance)
        this.has_changed = true
      },
      on_instance_hovered: function(instance, index){
        this.instance_hover_index = index;
        this.instance_hovered = instance;

      },
      on_instance_unhovered: function(){
        this.instance_hover_index = null;
        this.instance_hovered = null;

      },
      on_update_mouse_position: function(mouse){
        this.mouse_position = mouse;
      },
      on_instance_drawn: function(instance){
        this.center_secondary_cameras_to_instance(instance);
        this.edit_mode_toggle(false);
        this.has_changed = true;
      },
      center_secondary_cameras_to_instance: function(instance){
        this.$refs.x_axis_3d_canvas.scene_controller.center_camera_to_mesh(instance.mesh, 'x')
        this.$refs.y_axis_3d_canvas.scene_controller.center_camera_to_mesh(instance.mesh, 'y')
        this.$refs.z_axis_3d_canvas.scene_controller.center_camera_to_mesh(instance.mesh, 'z')
      },

      key_down_handler: function(event){
        console.log('lololololo', event.keyCode)
        if (event.keyCode === 27) { // ESC
          if(this.$refs.main_3d_canvas &&
            !this.$refs.main_3d_canvas.scene_controller.object_transform_controls.controls_transform.object){
            this.edit_mode_toggle(!this.draw_mode)
          }

        }

        if (event.keyCode === 46) { // DEL
          this.delete_instance();

        }
      },
      insert_tag_type: function(){

      },
      complete_task: function(){

      },
      next_issue_task: function(){

      },
      trigger_task_change: function(){

      },
      change_file: function(){

      },
      change_instance_type: function(instance_type){
        this.instance_type = instance_type;
      },
      change_label_file: function(label_file){
        this.current_label_file = label_file;

        if(!this.$refs.main_3d_canvas){
          return
        }

        this.$refs.main_3d_canvas.set_current_label_file(label_file)
      },
      hide_snackbar: function(){
        this.show_snackbar = false;
      },
      show_info_snackbar_for_drawing: function(){
        if(this.instance_type === 'cuboid_3d'){
          this.snackbar_text = 'Double click to start drawing a cuboid.'
        }
        this.show_snackbar = true;
      },
      edit_mode_toggle: function(draw_mode){
        this.draw_mode = draw_mode;
        this.$refs.main_3d_canvas.set_draw_mode(draw_mode)
        if(this.draw_mode){
          this.show_info_snackbar_for_drawing();
        }
        else{
          this.hide_snackbar();
        }
      },
    }
  })
</script>

<style scoped>

</style>
