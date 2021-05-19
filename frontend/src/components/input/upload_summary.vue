<template>
  <v-container>
    <h1 class="pa-10 black--text">Confirm the Upload</h1>
    <v-layout class="d-flex column justify-center">
      <h2 class="ma-8 black--text">You are about to upload {{file_list.length}} file(s):
      to Dataset: <v-icon>mdi-folder</v-icon> <strong v-if="current_directory">{{current_directory.nickname}}</strong>
      </h2>

      <v-list-item
        v-for="(item, i) in file_list"
        :key="i"
        dense
        two-line
        style="min-height: 30px"
      >
        <v-list-item-icon class="ma-0">
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
            <v-list-item-subtitle class="ml-4" v-if="item.point_instances.length > 0"
                                  v-text="`Points: ${item.point_instances.length}`"></v-list-item-subtitle>
            <v-list-item-subtitle class="ml-4" v-if="item.polygon_instances.length > 0"
                                  v-text="`Polygons: ${item.polygon_instances.length}`"></v-list-item-subtitle>
            <v-list-item-subtitle class="ml-4" v-if="item.line_instances.length > 0"
                                  v-text="`Lines: ${item.line_instances.length}`"></v-list-item-subtitle>
            <v-list-item-subtitle class="ml-4" v-if="item.cuboid_instances.length > 0"
                                  v-text="`Cuboids: ${item.cuboid_instances.length}`"></v-list-item-subtitle>
            <v-list-item-subtitle class="ml-4" v-if="item.ellipse_instances.length > 0"
                                  v-text="`Ellipses: ${item.ellipse_instances.length}`"></v-list-item-subtitle>

            <v-list-item-title v-if="item.labels" class="align-self-baseline" v-text="`Total Labels: ${Object.keys(item.labels).length} [${Object.keys(item.labels)}]`">

            </v-list-item-title>
            <v-list-item-subtitle class="ml-4"
                                  v-for="key in Object.keys(item.labels)"
                                  v-text="`- '${key}' => Num instances: ${item.labels[key]}`">

            </v-list-item-subtitle>
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
  import {v4 as uuidv4} from 'uuid'

  export default Vue.extend({
      name: 'upload_summary',
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
        },
        'current_directory': {
          default: null
        }
      },
      data() {
        return {
          input_batch: null,
          supported_video_files: ['video/mp4', 'video/x-msvideo', 'video/quicktime', 'video/x-m4v'],
          supported_image_files: ['image/jpg', 'image/jpeg', 'image/png']
        }
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
        request_upload_raw_media: function(){
          this.$emit('upload_raw_media', [...this.$props.file_list]);
        },
        attach_batch_to_files: function(batch){
          for(const file of this.$props.file_list){
            file.input_batch_id = batch.id
          }
          this.$emit('created_batch', batch)
        },
        create_batch: async function (labels_payload) {
          try {
            const response = await axios.post(`/api/v1/project/${this.$props.project_string_id}/input-batch/new`, {
              pre_labeled_data: labels_payload
            });
            if (response.status === 200) {
              this.input_batch = response.data.input_batch;
            }
          } catch (e) {

          }
        },
        prepare_pre_labeled_data_payload: function (pre_labeled_data, diffgram_schema, file_list) {
          // This function Creates the final payload accepted by the API based on the schema mapping.
          if(!pre_labeled_data){return}
          const result = {};
          for (const file of file_list) {
            const uuid = uuidv4();
            const file_instances = pre_labeled_data.filter(inst => inst[diffgram_schema.file_name] === file.name);
            file.uuid = uuid;
            result[file.uuid] = {instance_list: [], frame_packet_map: {}};
            result[file.name] = {instance_list: [], frame_packet_map: {}};
            for (const instance of file_instances) {
              const type = instance[diffgram_schema.instance_type]
              const diffgram_formatted_instance = {
                file_uuid: uuid,
                type: type,
                file_name: instance[diffgram_schema.file_name],
                name: instance[diffgram_schema.name],
                model_id: instance[diffgram_schema.model_id],
                run_id: instance[diffgram_schema.run_id],
                frame_number: instance[diffgram_schema.frame_number],
                number: instance[diffgram_schema.number],
              }
              if (type === 'box') {

                diffgram_formatted_instance.x_max = instance[diffgram_schema.box.x_max];
                diffgram_formatted_instance.x_min = instance[diffgram_schema.box.x_min];
                diffgram_formatted_instance.y_max = instance[diffgram_schema.box.y_max];
                diffgram_formatted_instance.y_min = instance[diffgram_schema.box.y_min];

                const width = diffgram_formatted_instance.x_max - diffgram_formatted_instance.x_min;
                const height = diffgram_formatted_instance.y_max - diffgram_formatted_instance.y_min;
                diffgram_formatted_instance.width = width;
                diffgram_formatted_instance.height = height;
              } else if (type === 'point') {
                diffgram_formatted_instance.points = [
                  {x: instance[diffgram_schema.point.x], y: instance[diffgram_schema.point.y]}
                ]
              } else if (type === 'line') {
                diffgram_formatted_instance.points = [
                  {x: instance[diffgram_schema.line.x1], y: instance[diffgram_schema.line.y1]},
                  {x: instance[diffgram_schema.line.x2], y: instance[diffgram_schema.line.y2]}
                ]
              } else if (type === 'polygon') {
                diffgram_formatted_instance.points = instance[diffgram_schema.polygon.points]
              } else if (type === 'cuboid') {
                diffgram_formatted_instance.front_face = {
                  top_left: {
                    x: instance[diffgram_schema.cuboid.front_face_top_left_x],
                    y: instance[diffgram_schema.cuboid.front_face_top_left_y]
                  },
                  top_right: {
                    x: instance[diffgram_schema.cuboid.front_face_top_right_x],
                    y: instance[diffgram_schema.cuboid.front_face_top_right_y]
                  },
                  bot_left: {
                    x: instance[diffgram_schema.cuboid.front_face_bot_left_x],
                    y: instance[diffgram_schema.cuboid.front_face_bot_left_y]
                  },
                  bot_right: {
                    x: instance[diffgram_schema.cuboid.front_face_bot_right_x],
                    y: instance[diffgram_schema.cuboid.front_face_bot_right_y]
                  },
                }
                diffgram_formatted_instance.rear_face = {
                  top_left: {
                    x: instance[diffgram_schema.cuboid.rear_face_top_left_x],
                    y: instance[diffgram_schema.cuboid.rear_face_top_left_y]
                  },
                  top_right: {
                    x: instance[diffgram_schema.cuboid.rear_face_top_right_x],
                    y: instance[diffgram_schema.cuboid.rear_face_top_right_y]
                  },
                  bot_left: {
                    x: instance[diffgram_schema.cuboid.rear_face_bot_left_x],
                    y: instance[diffgram_schema.cuboid.rear_face_bot_left_y]
                  },
                  bot_right: {
                    x: instance[diffgram_schema.cuboid.rear_face_bot_right_x],
                    y: instance[diffgram_schema.cuboid.rear_face_bot_right_y]
                  },
                }
              } else if(type === 'ellipse'){
                diffgram_formatted_instance.center_x = instance[diffgram_schema.ellipse.center_x];
                diffgram_formatted_instance.center_y = instance[diffgram_schema.ellipse.center_y];
                diffgram_formatted_instance.angle = instance[diffgram_schema.ellipse.angle];
                diffgram_formatted_instance.width = instance[diffgram_schema.ellipse.width];
                diffgram_formatted_instance.height = instance[diffgram_schema.ellipse.height];
              }

              if(this.supported_image_files.includes(file.type)){
                result[file.uuid].instance_list.push(diffgram_formatted_instance)
                result[file.name].instance_list.push(diffgram_formatted_instance)

              }
              else if(this.supported_video_files.includes(file.type)){
                if(!result[file.uuid].frame_packet_map[diffgram_formatted_instance.frame_number]){
                  result[file.uuid].frame_packet_map[diffgram_formatted_instance.frame_number] = [diffgram_formatted_instance]
                  result[file.name].frame_packet_map[diffgram_formatted_instance.frame_number] = [diffgram_formatted_instance]
                }
                else{
                  result[file.uuid].frame_packet_map[diffgram_formatted_instance.frame_number].push(
                    diffgram_formatted_instance
                  )
                  result[file.name].frame_packet_map[diffgram_formatted_instance.frame_number].push(
                    diffgram_formatted_instance
                  )
                }
              }
              else{
                throw new Error(`${file.type} is not a supported file format.`)
              }

            }
          }
          return result;
        },
        start_upload: async function () {
          const labels_payload = this.prepare_pre_labeled_data_payload(
            this.$props.pre_labeled_data,
            this.$props.diffgram_schema_mapping,
            this.$props.file_list
          )
          await this.create_batch(labels_payload)
          this.attach_batch_to_files(this.input_batch);
          this.request_upload_raw_media();

        },
        compute_attached_instance_per_file: function () {
          if(!this.$props.pre_labeled_data){ return }
          for (let i = 0; i < this.$props.file_list.length; i++) {
            const file = this.$props.file_list[i];
            file.labels = {}
            const all_instances = this.$props.pre_labeled_data.filter(inst => inst[this.$props.diffgram_schema_mapping.file_name] == file.name)
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

            // Compute labels count
            for(const instance of all_instances){
              if(!file.instances[instance[this.$props.diffgram_schema_mapping.name]]){
                file.labels[instance[this.$props.diffgram_schema_mapping.name]] = all_instances.filter(inst => inst[this.$props.diffgram_schema_mapping.name] === instance[this.$props.diffgram_schema_mapping.name]).length;
              }
            }
          }
        }

      }
    }
  ) </script>

