<template>
  <v-layout class="d-flex align-center justify-start template-creation-toolbar">
    <tooltip_button
      tooltip_message="Zoom Out"
      @click="this.zoom_out"
      color="primary"
      icon="mdi-magnify-minus"
      :icon_style="true"
      :bottom="true"
    >
    </tooltip_button>
    <tooltip_button
      tooltip_message="Zoom In"
      @click="this.zoom_in"
      color="primary"
      icon="mdi-magnify-plus"
      :icon_style="true"
      :bottom="true"
    >
    </tooltip_button>
    <input type="file" ref="file" style="display: none" @change="setBackground">
    <tooltip_button
      tooltip_message="Upload Background Image"
      @click="$refs.file.click()"
      color="primary"
      icon="mdi-folder-image"
      :icon_style="true"
      :bottom="true"
    >
    </tooltip_button>

    <v-switch data-cy="edit_toggle_instance_template_create"
              v-model="draw_mode"
              @change="edit_mode_toggle"
              :label="mode_text">
    </v-switch>
  </v-layout>
</template>

<script>
  import Vue from "vue";

  export default Vue.extend({
    name: "instance_template_creation_toolbar",
    props: {
      project_string_id: undefined,
    },
    components:{},
    data: function(){
      return {
        draw_mode: true,
      }
    },
    mounted() {


    },

    methods: {
      zoom_in: function(){
        this.$emit('zoom_in');
      },
      zoom_out: function(){
        this.$emit('zoom_out');
      },
      setBackground: function(event){
        let img = new Image ()
        img.src = URL.createObjectURL(event.target.files[0]);
        const self = this;
        img.onload = function () {
          self.$emit('set_background', img)
        }
      },
      edit_mode_toggle: function(){
        this.$emit('draw_mode_update', this.draw_mode)
      }
    },
    computed:{
      mode_text: function(){
        if(this.draw_mode){
          return 'Drawing'
        }
        else{
          return 'Editing'
        }
      }
    }

  })
</script>

<style scoped>
</style>
