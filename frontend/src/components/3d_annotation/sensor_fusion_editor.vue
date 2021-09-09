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
    <div class="mt-4">
      <canvas_3d></canvas_3d>
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
        draw_mode: false,
        label_file_colour_map: null,
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


    },
    methods: {
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
      change_label_file: function(){

      },
      edit_mode_toggle: function(){

      },
    }
  })
</script>

<style scoped>

</style>
