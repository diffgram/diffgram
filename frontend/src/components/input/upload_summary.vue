<template>
  <v-container>
    <h1 class="pa-10 black--text">Confirm the Upload</h1>
    <v-layout class="d-flex column justify-center">
      <h2 class="ma-8 black--text">You are about to upload {{file_list.length}} file(s):</h2>

      <v-list-item
        v-for="(item, i) in file_list"
        :key="i"
        dense
        two-line
      >
        <v-list-item-icon>
          <v-icon v-text="'mdi-file'"></v-icon>
        </v-list-item-icon>
        <v-list-item-title>
          <v-list-item-title v-text="item.name"></v-list-item-title>
          <v-list-item v-if="item.instances" class="d-flex flex-column justify-start align-baseline">
            <v-list-item-title class="align-self-baseline" v-text="`Total Instances to add: ${item.instances.length}`">

            </v-list-item-title>
            <v-list-item-subtitle
              class="ml-4"
              v-if="item.box_instances.length > 0"
              v-text="`Boxes: ${item.box_instances.length}`">
            </v-list-item-subtitle>
            <v-list-item-subtitle class="ml-4" v-if="item.point_instances.length > 0" v-text="`Points: ${item.point_instances.length}`"></v-list-item-subtitle>
            <v-list-item-subtitle class="ml-4"  v-if="item.polygon_instances.length > 0" v-text="`Polygons: ${item.polygon_instances.length}`"></v-list-item-subtitle>
            <v-list-item-subtitle class="ml-4"  v-if="item.line_instances.length > 0" v-text="`Lines: ${item.line_instances.length}`"></v-list-item-subtitle>
            <v-list-item-subtitle class="ml-4"  v-if="item.cuboid_instances.length > 0" v-text="`Cuboids: ${item.cuboid_instances.length}`"></v-list-item-subtitle>
            <v-list-item-subtitle class="ml-4"  v-if="item.ellipse_instances.length > 0" v-text="`Ellipses: ${item.ellipse_instances.length}`"></v-list-item-subtitle>
          </v-list-item>
        </v-list-item-title>
      </v-list-item>
      <v-btn x-large class="success ma-8" @click="start_upload">Upload to Diffgram</v-btn>
    </v-layout>
  </v-container>

</template>

<script lang="ts">
  import axios from 'axios';
  import Vue from "vue";

  export default Vue.extend({
      name: 'upload_wizard_dialog',
      components: {},
      props: {
        'project_string_id': {
          default: null
        },
        'file_list': {
          default: null
        },
        'pre_labeled_data': {
          default: null
        },
        'diffgram_schema_mapping': {
          default: null
        }
      },
      data() {
        return {}
      },
      computed: {},
      watch: {
        file_list: function (new_val, old_val) {
          if (new_val) {
            this.compute_attached_instance_per_file();
          }
        },
      },
      mounted() {
      },
      created() {
        this.compute_attached_instance_per_file()
      },
      beforeDestroy() {

      },
      methods: {
        start_upload: function () {
          alert('start upload');
          this.close();
        },
        compute_attached_instance_per_file: function () {
          for (let i = 0; i < this.$props.file_list.length; i++) {
            const file = this.$props.file_list[i];
            const all_instances = this.$props.pre_labeled_data.filter(inst => inst[this.$props.diffgram_schema_mapping.file_name] == file.name)
            console.log('file file', file);
            console.log('file all_instances', all_instances);
            console.log('file this.$props.pre_labeled_data', this.$props.pre_labeled_data);
            console.log('file this.$props.diffgram_schema_mapping', this.$props.diffgram_schema_mapping);
            file.instances = all_instances;
            const box_instances = all_instances.filter(inst => inst[this.$props.diffgram_schema_mapping.instance_type] == 'box')
            const point_instances = all_instances.filter(inst => inst[this.$props.diffgram_schema_mapping.instance_type] == 'point')
            const polygon_instances = all_instances.filter(inst => inst[this.$props.diffgram_schema_mapping.instance_type] == 'polygon')
            const line_instances = all_instances.filter(inst => inst[this.$props.diffgram_schema_mapping.instance_type] == 'line')
            const cuboid_instances = all_instances.filter(inst => inst[this.$props.diffgram_schema_mapping.instance_type] == 'cuboid')
            const ellipse_instances = all_instances.filter(inst => inst[this.$props.diffgram_schema_mapping.instance_type] == 'ellipse')
            file.box_instances = box_instances;
            file.point_instances = point_instances;
            file.polygon_instances = polygon_instances;
            file.line_instances = line_instances;
            file.cuboid_instances = cuboid_instances;
            file.ellipse_instances = ellipse_instances;
          }
        }

      }
    }
  ) </script>

