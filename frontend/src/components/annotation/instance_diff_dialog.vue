<template>
  <v-dialog v-model="is_open" width="1000px" :click:outside="close">
    <v-card class="pa-4 pl-0">
      <v-card-title class="d-flex">
        <span class="flex-grow-1">Instance Diff</span>
      </v-card-title>
      <v-card-text v-if="loading || (old_instance_text === undefined && new_instance_text === undefined)" class="d-flex justify-center">
        <v-progress-circular color="primary" indeterminate v-if="loading || (old_instance_text === undefined && new_instance_text === undefined)"></v-progress-circular>
      </v-card-text>
      <v-card-text v-if="!loading">
        <CodeDiff :new-string="new_instance_text"
                  v-if="(new_instance || old_instance)
                  && (new_instance.action_type === 'edited' || new_instance.action_type === 'created')"
                  :old-string="old_instance_text"
                  :outputFormat="old_instance != undefined && new_instance != undefined ? `side-by-side` : ``"/>

        <!--    Restore Case    -->
        <CodeDiff :new-string="new_instance_text"
                  v-if="(new_instance || old_instance) && (new_instance.action_type === 'undeleted')"/>

        <h2 class="text--primary text-center" v-if="(new_instance || old_instance) && new_instance.action_type === 'deleted'">
          <v-icon x-large color="error">mdi-delete-alert-outline</v-icon>
          Instance was deleted by user

        </h2>
      </v-card-text>
      <v-card-actions class="d-flex justify-center">
        <v-btn @click="close" icon align="right"> <v-icon>mdi-close</v-icon>Close</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>


</template>

<script>
  import Vue from 'vue';
  import axios from 'axios';
  import CodeDiff from 'vue-code-diff'

  export default Vue.extend({
    name: "instance_diff_dialog",
    components: {
      CodeDiff
    },
    props: {
      'old_instance':{
        default: undefined
      },
      'new_instance':{
        default: undefined
      }
    },
    data: function(){
      return {
        instance_history_list: [],
        loading: false,
        is_open: false,
        old_instance_text: '',
        new_instance_text: ''
      }
    },
    watch:{
      old_instance: function(newVal, oldVal){
        if(newVal != undefined){
          this.old_instance_text = this.render_instance_text(newVal)
        }
      },
      new_instance: function(newVal, oldVal){
        if(newVal != undefined){
          this.new_instance_text = this.render_instance_text(newVal);
        }
      }
    },
    methods: {
      open: function(){
        this.is_open = true;
      },
      close: function(){
        this.is_open = false;
      },
      render_instance_text(instance){
        if(!instance){
          return ''
        }
        if(instance.type === 'box'){
          return JSON.stringify({
            x_min: instance.x_min,
            x_max: instance.x_max,
            y_min: instance.y_max,
            width: instance.width,
            height: instance.height,
            undefined
          }, undefined, 2)
        }
        else if(instance.type === 'point'){
          return JSON.stringify({
            points: instance.points
          }, undefined, 2)
        }
        else if(instance.type === 'line'){
          return JSON.stringify({
            points: instance.points,
          },undefined, 2)
        }
        else if(instance.type === 'polygon'){
          return JSON.stringify({
            points: instance.points
          },undefined, 2)
        }
        else if(instance.type === 'ellipse'){
          return JSON.stringify({
            center_x: instance.center_x,
            center_y: instance.center_y,
            angle: instance.angle,
          },undefined, 2)
        }
        else if(instance.type === 'cuboid'){
          return JSON.stringify({
            front_face: instance.front_face,
            rear_face: instance.rear_face,
          },undefined, 2)
        }
        else if(instance.type === 'keypoints'){
          return JSON.stringify({
            nodes: instance.nodes,
            edges: instance.edges,
          },undefined, 2)
        }
        else if(instance.type === 'curve'){
          return JSON.stringify({
            p1: instance.p1,
            p2: instance.p2,
            cp: instance.cp,
          }, undefined, 4)
        }
      }
    },

  })
</script>

<style scoped>

</style>
