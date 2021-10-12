<template>

  <v-card class="ma-2"
          :elevation="0"
          style="background: #f6f7f8"
          :height="file_preview_height">

    <v-card-text class="pa-0 ma-0 drawable-wrapper" v-if="image_bg" @click="view_file_details(undefined)" >
      <drawable_canvas
        v-if="image_bg"
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
        >
        </instance_list>


      </drawable_canvas>
    </v-card-text>
    <v-card-text class="pa-0 ma-0" v-if="file.video">
      <video_drawable_canvas
        :allow_zoom="false"
        :project_string_id="project_string_id"
        :filtered_instance_by_model_runs="filtered_instance_list"
        :video="file.video"
        :file="file"
        :canvas_height="file_preview_height"
        :canvas_width="file_preview_width"
        :editable="false"
        :auto_scale_bg="true"
        :label_settings="label_settings"
        :refresh="refresh"
        :show_video_nav_bar="show_video_nav_bar"
        :canvas_wrapper_id="`canvas_wrapper__${file.id}__${file_preview_width}__${file_preview_height}`"
        :canvas_id="`canvas__${file.id}__${file_preview_width}__${file_preview_height}`"
        @on_click_details="view_file_details"
        ref="video_drawable_canvas"
        @update_instance_list="set_video_instance_list"
      >
      </video_drawable_canvas>
    </v-card-text>
  </v-card>
</template>

<script>
  import Vue from "vue";

  import instance_list from "../vue_canvas/instance_list";
  import drawable_canvas from "../vue_canvas/drawable_canvas";
  import video_drawable_canvas from "../vue_canvas/video_drawable_canvas";
  import {KeypointInstance} from "../vue_canvas/instances/KeypointInstance";
  import {InstanceContext} from "../vue_canvas/instances/InstanceContext";
  export default Vue.extend({
    name: "file_preview",
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
      'instance_list': {
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
      if (this.$props.file) {
        await this.set_bg(this.$props.file);
      }
    },
    watch: {
      file: function (newFile, oldFile) {
        this.set_bg(newFile);
        this.prepare_filtered_instance_list();
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
      set_video_instance_list: function(new_list){
        this.video_instance_list = new_list;
        this.prepare_filtered_instance_list();
        this.refresh = Date.now()
      },
      initialize_instance: function(instance){

        if(instance.type === 'keypoints' && !instance.initialized){

          // In this case we can send empty object for mouse position since we don't want drawing controls.
          let initialized_instance = new KeypointInstance(
            {},
            {},
            this.instance_context,
            () =>{},
            () =>{},
            () =>{},
            {},
            this.label_settings
          );
          initialized_instance.populate_from_instance_obj(instance);
          return initialized_instance
        }
        else{
          return instance
        }
      },
      prepare_filtered_instance_list: function () {
        this.filtered_instance_list = []
        if (this.$props.base_model_run) {
          this.filtered_instance_list = this.global_instance_list.filter(inst => {
            return inst.model_run_id === this.$props.base_model_run.id;
          })
          this.filtered_instance_list = this.filtered_instance_list.map(inst => {
            inst = this.initialize_instance(inst)
            inst.override_color =this.$props.base_model_run.color
            return inst
          })
        }


        if (this.$props.compare_to_model_run_list) {
          let added_ids = this.filtered_instance_list.map(inst => inst.id);
          for (const model_run of this.$props.compare_to_model_run_list) {

            let filtered_instances = this.global_instance_list.filter(inst => {
              return inst.model_run_id === model_run.id;
            })
            filtered_instances = filtered_instances.map(inst => {
              inst = this.initialize_instance(inst)
              inst.override_color = model_run.color
              return inst
            })
            for(const instance of filtered_instances){
              if(!added_ids.includes(instance.id)){
                let initialized_instance = this.initialize_instance(instance);
                this.filtered_instance_list.push(initialized_instance);
                added_ids.push(initialized_instance.id)
              }
            }
          }

        }


        if(this.$props.show_ground_truth){
          const ground_truth_instances = this.global_instance_list.filter(inst => !inst.model_run_id);
          for(const inst of ground_truth_instances){
            let initialized_instance = this.initialize_instance(inst);
            this.filtered_instance_list.push(initialized_instance)
          }
        }
      },

      set_bg: async function (newFile) {
        return new Promise((resolve, reject) => {
          if (!newFile) {
            this.image_bg = undefined;
            this.refresh = new Date();
          }
          else {
            if (newFile.image) {
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

      view_file_details: function(current_frame){
        let model_runs = [];
        let color_list = [];
        if(this.base_model_run){
          model_runs.push(this.$props.base_model_run)
          color_list.push(this.$props.base_model_run.color)
        }
        if(this.$props.compare_to_model_run_list){
          model_runs = model_runs.concat(this.$props.compare_to_model_run_list);
          color_list = color_list.concat(this.$props.compare_to_model_run_list.map(m => m.color));
        }
        const model_run_ids = model_runs.map(run => run.id);
        this.$router.push({
          path: `/studio/annotate/${this.$props.project_string_id}`,
          query: {
            file: this.$props.file.id,
            model_runs:  model_runs.length > 0 ? encodeURIComponent(model_run_ids): undefined,
            color_list:  color_list.length > 0 ? encodeURIComponent(color_list): undefined,
            frame: current_frame

          }
        }).catch(()=>{});
        this.$emit('view_file_detail', this.$props.file, model_runs, color_list)
      }


    },
    computed:{
      global_instance_list: function(){
        // This instance list can either be the image instance list of the video instance list at current frame.
        if(this.$props.file.image){
          return this.$props.instance_list;
        }
        if(this.$props.file.video){
          return this.video_instance_list;
        }
        return []
      }
    },
  });
</script>

<style>
.drawable-wrapper:hover{
  cursor: pointer;
}
</style>
