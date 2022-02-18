<template>
<v-card column style="z-index: 99999">
  <v-card-title>Set Node Name: </v-card-title>

  <v-container>
    <v-text-field v-model="node_name" label="Node name: " ></v-text-field>

    <v-btn  @click="on_close_click">Close</v-btn>
    <v-btn color="success" @click="set_node_name">Save</v-btn>
  </v-container>
</v-card>

</template>

<script lang="ts">

import Vue from "vue";

export default Vue.extend( {

  name: 'node_name_editor_keypoint_instance',
  components: {
  },
  props: {
    'node_index':{
      default: null
    },
    'instance_list':{
      default: null
    },
    'instance_index':{
      default: null
    },
    'instance':{
      default: null
    }
  },
  data() {
    return {
      node_name: ''
    }
  },
  watch: {
    instance_index: function(){
      this.set_existing_node_name();
    },
    node_index: function(){
      this.set_existing_node_name();
    }

  },
  mounted() {
    this.set_existing_node_name();
  },
  computed: {
    current_instance: function(){
      if(this.$props.instance){
        return this.$props.instance
      }
      if(this.node_index == undefined){return}
      if(this.instance_index == undefined){return}
      if(this.instance_list == undefined){return}
      return this.instance_list[this.instance_index].nodes[this.node_index].name;
    }
  },
  methods: {
    set_existing_node_name: function(){
      if(this.current_instance == undefined){return}

      this.node_name = this.current_instance.nodes[this.node_index].name;
    },
    on_close_click: function(){
      this.$emit('close')
    },
    set_node_name: function(){
      if(this.current_instance == undefined){return}
      let instance = this.current_instance;
      let node = instance.nodes[this.node_index];
      node.name = this.node_name;
      this.$emit('node_updated')
    }

  }
}

) </script>
