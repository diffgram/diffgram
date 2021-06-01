<template>
  <v-card class="ma-2" :elevation="0" style="background: #f6f7f8">
    <v-card-text class="pa-0 ma-0">
      <drawable_canvas
        :image_bg="image_bg"
        :canvas_height="320"
        :canvas_width="430"
        :editable="false"
        :auto_scale_bg="true"
      >

      </drawable_canvas>
    </v-card-text>
  </v-card cl>
</template>

<script>
  import Vue from "vue";
  import drawable_canvas from "../vue_canvas/drawable_canvas";
  export default Vue.extend({
    name: "file_preview",
    components:{
      drawable_canvas
    },
    props:{
      'project_string_id':{
        default: undefined
      },
      'file': {
        default: undefined
      },
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
