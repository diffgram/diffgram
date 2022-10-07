<template>

  <drawable_canvas
    ref="drawable_canvas"
    :allow_zoom="false"
    :image_bg="image_bg"
    :canvas_height="file_preview_height"
    :canvas_width="file_preview_width"
    :editable="false"
    :auto_scale_bg="true"
    :refresh="refresh"
    :canvas_wrapper_id="`canvas_wrapper__${file.id}__${file_preview_width}__${file_preview_height}`"
    :canvas_id="`canvas__${file.id}__${file_preview_width}__${file_preview_height}`"
  >

    <instance_list
      slot-scope="props"
      :instance_list="filtered_instance_list"
      :vertex_size="3"
      :refresh="refresh"
      :video_mode="false"
      :label_settings="label_settings"
      :show_annotations="true"
      :draw_mode="false"
      :canvas_transform="props.canvas_transform"
      slot="instance_drawer"
    />

  </drawable_canvas>
</template>

<script>
  import Vue from "vue";

  import instance_list from "../vue_canvas/instance_list";
  import drawable_canvas from "../vue_canvas/drawable_canvas";
  import video_drawable_canvas from "../vue_canvas/video_drawable_canvas";
  import {KeypointInstance} from "../vue_canvas/instances/KeypointInstance";
  import {InstanceContext} from "../vue_canvas/instances/InstanceContext";

  export default Vue.extend({
    name: "compound_file_preview",
    components: {
      video_drawable_canvas,
      drawable_canvas,
      instance_list
    },
    props: {
      'project_string_id': {
        default: undefined
      },
      'file': {
        default: undefined
      },
      'file_preview_width': {
        default: 440
      },
      'file_preview_height': {
        default: 325
      },
      'base_model_run': {
        default: null
      },
      'compare_to_model_run_list': {
        default: null
      },
      'show_ground_truth':{
        default: true
      },
      show_video_nav_bar:{
        default: true
      },
      'video':{
        default: null
      },
      'enable_go_to_file_on_click':{
        default: true
      }
    },
    data: function () {
      return {
        image_bg: undefined,
        refresh: null,
        filtered_instance_list: [],
        video_instance_list: [],
        instance_context: new InstanceContext(),
        compare_to_instance_list_set: [],
        label_settings: {
          font_size: 20,
          show_removed_instances: false,
          spatial_line_size: 2,
          show_text: false,
          show_label_text: false,
          show_attribute_text: false,
        }
      }
    },
    created() {
      this.prepare_filtered_instance_list();
    },

    async mounted() {
      await this.fetch_child_files()
      this.start_compound_file_thumb_rotation()

    },
    watch: {
      file: {
        deep: true,
        handler: async function(new_val, old_val){
          await this.set_bg(new_val);
          this.prepare_filtered_instance_list();
        }
      },
      base_model_run: function () {

        this.prepare_filtered_instance_list();
      },
      compare_to_model_run_list: function () {
        this.prepare_filtered_instance_list();
      },
      show_ground_truth: function(){
        this.prepare_filtered_instance_list();
      }
    },
    methods: {
      start_compound_file_thumb_rotation: function(){

      },
      set_bg: async function (newFile) {
        return new Promise((resolve, reject) => {
          if (!newFile) {
            this.image_bg = undefined;
            this.refresh = new Date();
            resolve();
          }
          else {
            if (newFile.image && newFile.image.url_signed) {
              const image = new Image();
              image.onload = () => {
                this.image_bg = image;
                this.refresh = new Date();
                image.onload = () => resolve(image)
              }
              image.src = this.$props.file.image.url_signed;
              image.onerror = reject
            }
            else{
              resolve();
            }

          }
        })

      },

    },
    computed:{
    },
  });
</script>

<style>
.drawable-wrapper:hover{
  cursor: pointer;
}
</style>
