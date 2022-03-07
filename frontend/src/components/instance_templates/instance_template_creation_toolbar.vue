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
    <v-spacer></v-spacer>

    <guided_1_click_mode_selector ref="mode_selector" @mode_set="on_mode_set"></guided_1_click_mode_selector>
    <node_order_picker @order_updated="on_nodes_order_updated" :nodes="instance.nodes"ref="node_order_picker"></node_order_picker>
  </v-layout>
</template>

<script>
  import Vue from "vue";
  import guided_1_click_mode_selector from './guided_1_click_mode_selector';
  import node_order_picker from './node_order_picker';
  export default Vue.extend({
    name: "instance_template_creation_toolbar",
    props: {
      project_string_id: undefined,
      instance: {
        default: () => ({
          nodes: []
        })
      },
    },
    components:{
      guided_1_click_mode_selector: guided_1_click_mode_selector,
      node_order_picker: node_order_picker
    },
    data: function(){
      return {
        draw_mode: true,
      }
    },
    mounted() {


    },

    methods: {
      on_nodes_order_updated: function(new_nodes){
        this.instance.nodes = new_nodes;
      },
      set_mode: function(mode){
        if(mode === '1_click'){
          this.$refs.mode_selector.set_active(0)
        }
        else if(mode === 'guided'){
          this.$refs.mode_selector.set_active(1)
        }
      },
      on_mode_set: function(mode){
        this.$emit('mode_set', mode)
      },
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
