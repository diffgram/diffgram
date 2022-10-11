<template>

  <v-tooltip v-if="file"
             :top="top" :bottom="bottom" :right="right" :left="left">

    <template v-slot:activator="{on}">

      <div v-on="on">
        <file_preview
          v-if="file.type === 'image' || file.type === 'video'"
          :class="`d-flex file-preview ${file.type}-preview`"
          :file_preview_width="file_preview_width"
          :file_preview_height="file_preview_height"
          :key="file.id"
          :project_string_id="project_string_id"
          :file="file"
          :instance_list="file.instance_list"
          :show_ground_truth="true"
          :show_video_nav_bar="false"
          :enable_go_to_file_on_click="false"
        ></file_preview>
        <v-icon v-if="file.type === 'sensor_fusion'" size="64" color="primary">mdi-printer-3d</v-icon>
        <v-icon v-if="file.type === 'text'" size="64" color="primary">mdi-text-long</v-icon>
       </div>

    </template>

      <file_preview
        v-if="file.type === 'image' || file.type === 'video'"
        :class="`d-flex file-preview ${file.type}-preview`"
        :file_preview_width="500"
        :file_preview_height="500"
        :key="file.id + 'expanded'"
        :project_string_id="project_string_id"
        :file="file"
        :instance_list="file.instance_list"
        :show_ground_truth="true"
        :show_video_nav_bar="false"
        :enable_go_to_file_on_click="false"
      ></file_preview>
    <h3 v-if="file.type === 'sensor_fusion'">3D File</h3>


    </v-tooltip>

</template>


<script lang="ts">


import Vue from "vue";

export default Vue.extend( {
  name: 'hover_preview_card',
  props: {
    'file_preview_width': {
      default: 150
    },
    'file_preview_height': {
      default: 150
    },
    'file': {
      default: null
    },
    'project_string_id': {
      default: {}
    },
    'tooltip_direction': {      // left, right, bottom, top
      default: "bottom",
      type: String
    },
  },
  data() {
    return {
      top: false,
      right: false,
      left: false,
      bottom: false
    }
  },

  computed: {

    custom_style() {
      if (this.is_clickable == true) {
        return "cursor: pointer"
      }
      else {
        return "cursor: default"
      }
    }
  },

  created(){
    this[this.tooltip_direction] = true
  },

  methods:{
  }
}

) </script>

<style scoped>
  .v-tooltip__content {
    opacity: 1 !important;
    border-radius: 16px;
    padding: 0px 0px;
    background-color: white;
  }
</style>
