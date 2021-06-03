<template>
  <v-card class="ma-2" :elevation="0" style="background: #f6f7f8" v-if="image_bg">
    <v-card-text class="pa-0 ma-0">
      <drawable_canvas
        :image_bg="image_bg"
        :canvas_height="file_preview_height"
        :canvas_width="file_preview_width"
        :editable="false"
        :auto_scale_bg="false"
        :refresh="refresh"
        :canvas_wrapper_id="`canvas_wrapper__${file.id}`"
        :canvas_id="`canvas__${file.id}`"
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
  </v-card>
</template>

<script>
  import Vue from "vue";
  import instance_list from "../vue_canvas/instance_list";
  import drawable_canvas from "../vue_canvas/drawable_canvas";
  export default Vue.extend({
    name: "file_preview",
    components:{
      drawable_canvas,
      instance_list
    },
    props:{
      'project_string_id':{
        default: undefined
      },
      'file': {
        default: undefined
      },
      'instance_list': {
        default: undefined
      },
      'file_preview_width':{
        default: 430
      },
      'file_preview_height':{
        default: 325
      },
      'base_model_run':{
        default: null
      },
      'compare_to_model_run':{
        default: null
      }
    },
    data: function(){
      return{
        image_bg: undefined,
        refresh: null,
        filtered_instance_list: [],
        label_settings:{
          font_size: 20,
          show_removed_instances: false,
          spatial_line_size: 2,
          show_text: false,
          show_label_text: false,
          show_attribute_text: false,
        }
      }
    },
    mounted() {
      if(this.$props.file){
        this.set_bg(this.$props.file);
        this.filtered_instance_list = this.$props.instance_list;
        this.prepare_base_instance_list();
        this.prepare_compare_instance_lists();
      }
      this.$forceUpdate();
    },
    watch:{
      file: function(newFile, oldFile){
        this.set_bg(newFile);
        this.prepare_compare_instance_lists();
      },
      base_model_run: function(){
        this.prepare_base_instance_list();
      },
      compare_to_model_run: function(){
        this.prepare_compare_instance_lists();
      }
    },
    methods: {
      prepare_base_instance_list: function(){
        if(!this.$props.base_model_run){return}

        this.filtered_instance_list = this.$props.instance_list.filter(inst => {
          return inst.model_run_id === this.$props.base_model_run.id;
        })
        this.filtered_instance_list = this.filtered_instance_list.map(inst => {
          return {
            ...inst,
            override_color: this.$props.base_model_run.color
          }
        })
      },
      prepare_compare_instance_lists: function(){

      },
      set_bg: async function(newFile){
        if(!newFile){
          this.image_bg = undefined;
          this.refresh = new Date();
        }
        else{
          if(newFile.image){
            const image = new Image();
            image.onload = () =>{
              this.image_bg = image;
              this.refresh = new Date();
            }
            image.src = this.$props.file.image.url_signed;

          }
        }
        this.$forceUpdate();
      }
    }
  });
</script>

<style scoped>

</style>
