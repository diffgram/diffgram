<template>
  <v-card class="ma-2" :elevation="0" style="background: #f6f7f8">
    <v-card-text class="pa-0 ma-0">
      <drawable_canvas
        ref="drawable_canvas"
        :image_bg="image_bg"
        :canvas_height="320"
        :canvas_width="430"
        :editable="false"
        :auto_scale_bg="true"
      >
        <instance_list :ord="1"
                              slot-scope="props"
                              :instance_list="instance_list"
                              :vertex_size="3"
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
    },
    data: function(){
      return{
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
    computed:{
      image_bg: function(){
        if(!this.$props.file){
          return undefined
        }
        else{
          if(this.$props.file.image){
            const image = new Image();
            image.style.width = '430px'
            image.style.height = 'auto'
            image.src = this.$props.file.image.url_signed;
            return image
          }
        }
      }
    }
  });
</script>

<style scoped>

</style>
