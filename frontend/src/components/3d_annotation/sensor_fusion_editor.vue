<template>
  <div id="3d-editor-container">
    <div style="position: relative">
      <main_menu :height="`100px`">

        <template slot="second_row" >

          <toolbar_sensor_fusion :height="50"
                    class="pa-0"
                   :save_loading="false"
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
    <div class="editor-body">
      <div class="mt-4" style="max-height: 600px; overflow-y: hidden">
        <canvas_3d
          ref="main_3d_canvas"
          height="600px"
          :allow_navigation="true"
          :instance_list="instance_list"
          :current_label_file="current_label_file"
          :draw_mode="draw_mode"
          :container_id="'main_screen'"
          :with_keyboard_controls="true"
          @instance_drawn="on_instance_drawn"
          @instance_updated="on_instance_updated"
        >

        </canvas_3d>
      </div>
      <div id="secondary_3d_canvas_container"
           class="mt-4 d-flex flex-row"
           style="max-height: 200px;">
        <div class="ma-1">
          <canvas_3d
            ref="x_axis_3d_canvas"
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
        <div class="ma-1">

          <canvas_3d
            ref="y_axis_3d_canvas"
            :create_new_scene="false"
            camera_type="ortographic"
            :width="secondary_canvas_width"
            :height="secondary_canvas_height"
            :allow_navigation="true"
            :instance_list="instance_list"
            :current_label_file="current_label_file"
            :draw_mode="draw_mode"
            :container_id="'y_axis_3d_canvas'"
            :with_keyboard_controls="true">
          </canvas_3d>
        </div>
        <div class="ma-1">

          <canvas_3d
            ref="z_axis_3d_canvas"
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

</template>

<script>
  import Vue from "vue";

  import toolbar_sensor_fusion from "./toolbar_sensor_fusion";
  import canvas_3d from "./canvas_3d";

  export default Vue.extend({
    name: "annotation_editor_3d",
    components:{
      toolbar_sensor_fusion,
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
        has_changed: false,
        instance_type: 'cuboid_3d',
        instance_list: [],
        draw_mode: false,
        label_file_colour_map: null,
        secondary_3d_canvas_container: null,
        current_label_file: null,
        full_file_loading: false,
        view_issue_mode: false,
        canvas_scale_local: 1,  // for actually scaling dimensions within canvas
        label_list: [],
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
      }
    },
    mounted() {
      window.addEventListener( 'keydown', this.key_down_handler, false );
      this.setup_secondary_scene_controls();

    },
    computed:{
      secondary_canvas_width: function(){
          if(this.secondary_3d_canvas_container){
            let width = this.secondary_3d_canvas_container.clientWidth * 0.333;
            width = parseInt(width, 10);
            return `${width}px`
          }
      },
      secondary_canvas_height: function(){
        return '220px'
      },
    },
    watch:{
      // secondary_canvas_width: async function(new_val, old_val){
      //   console.log('watcher', new_val, old_val)
      //   if(new_val !== old_val){
      //     alert('aa');
      //
      //     this.setup_secondary_scene_controls()
      //   }
      //
      // },
      // secondary_canvas_height: function(new_val, old_val){
      //   if(new_val !== old_val){
      //     this.setup_secondary_scene_controls()
      //   }
      // }
    },
    methods: {
      setup_secondary_scene_controls: async function(){
        // Set scene for secondary canvas
        let main_scene = this.$refs.main_3d_canvas.scene_controller.scene;
        this.secondary_3d_canvas_container = document.getElementById('secondary_3d_canvas_container')
        console.log('WIDTH', this.secondary_canvas_width);
        await this.$nextTick();
        this.$refs.x_axis_3d_canvas.setup_scene_controls(main_scene)
        this.$refs.y_axis_3d_canvas.setup_scene_controls(main_scene)
        this.$refs.z_axis_3d_canvas.setup_scene_controls(main_scene)
      },
      on_instance_updated: function(instance){
        this.center_secondary_cameras_to_instance(instance)
      },
      on_instance_drawn: function(instance){
        this.center_secondary_cameras_to_instance(instance);
        this.edit_mode_toggle(false);
      },
      center_secondary_cameras_to_instance: function(instance){
        this.$refs.x_axis_3d_canvas.scene_controller.center_camera_to_mesh(instance.mesh, 'x')
        this.$refs.y_axis_3d_canvas.scene_controller.center_camera_to_mesh(instance.mesh, 'y')
        this.$refs.z_axis_3d_canvas.scene_controller.center_camera_to_mesh(instance.mesh, 'z')
      },

      key_down_handler: function(event){
        if (event.keyCode === 27) { // ESC
          this.edit_mode_toggle(!this.draw_mode)
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
      save: function(){

      },
      change_instance_type: function(){

      },
      change_label_file: function(label_file){
        this.current_label_file = label_file;
        this.$refs.main_3d_canvas.set_current_label_file(label_file)
      },
      edit_mode_toggle: function(draw_mode){
        this.draw_mode = draw_mode;
        this.$refs.main_3d_canvas.set_draw_mode(draw_mode)
      },
    }
  })
</script>

<style scoped>

</style>
