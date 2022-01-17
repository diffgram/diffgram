<template>
  <v-container fluid v-if="!preparing_payload">
    <v_error_multiple :error="batch_error">
    </v_error_multiple>
    <v-layout class="d-flex column justify-center" v-if="!loading_create_batch && !downloading_batch_pre_labels">
      <h1 class="pa-10 black--text">Confirm the Upload</h1>

      <h2 class="ma-8 black--text" v-if="upload_mode === 'new'">You are about to upload {{file_list.length}} file(s):
        to Dataset:
        <v-icon>mdi-folder</v-icon>
        <strong v-if="current_directory">{{current_directory.nickname}}</strong>
      </h2>
      <h2 v-if="upload_mode === 'update' && !total_instance_count">You will Update {{files_to_update_list().length}}
        File(s): </h2>
      <h2 v-if="upload_mode === 'update' && total_instance_count">You will Add {{total_instance_count}} Instances: </h2>

      <v-container fluid class="d-flex flex-column" style="max-height: 450px; overflow-y: auto">
        <div
          v-for="(item, i) in summarized_file_list.slice(0, 500)"
          :key="i"
        >
          <v-list-item class="d-flex ma-auto align-center">
            <v-list-item-icon>
              <v-icon v-text="'mdi-file'"></v-icon>
            </v-list-item-icon>
            <v-list-item-title v-text="upload_mode === 'new' ? item.name : `File ID: ${item.file_id}`">

            </v-list-item-title>
          </v-list-item>
          <v-list-item v-if="item.instances" class="d-flex ma-0 flex-column ml-8" style="align-items: start">
            <h5 class="font-weight-medium" v-text="`Total Instances to add: ${item.instances.length}`"></h5>
            <h5 class="font-weight-light ml-8 "
                v-if="item.box_instances.length > 0"
                v-text="`Boxes: ${item.box_instances.length}`">
            </h5>
            <h5 class="ml-8 font-weight-light" v-if="item.point_instances.length > 0"
                v-text="`Points: ${item.point_instances.length}`"></h5>
            <h5 class="ml-8 font-weight-light" v-if="item.polygon_instances.length > 0"
                v-text="`Polygons: ${item.polygon_instances.length}`"></h5>
            <h5 class="ml-8 font-weight-light" v-if="item.line_instances.length > 0"
                v-text="`Lines: ${item.line_instances.length}`"></h5>
            <h5 class="ml-8 font-weight-light" v-if="item.cuboid_instances.length > 0"
                v-text="`Cuboids: ${item.cuboid_instances.length}`"></h5>
            <h5 class="ml-8 font-weight-light" v-if="item.ellipse_instances.length > 0"
                v-text="`Ellipses: ${item.ellipse_instances.length}`"></h5>

            <h5 class="font-weight-medium" v-if="item.labels"
                v-text="`Total Labels: ${Object.keys(item.labels).length} [${Object.keys(item.labels)}]`">

            </h5>
            <h5 class="font-weight-light ml-8" v-for="key in Object.keys(item.labels)"
                v-text="`- '${key}' => Num instances: ${item.labels[key]}`">

            </h5>
          </v-list-item>

        </div>
        <div v-if="summarized_file_list.length > 500">
          <h2>and {{summarized_file_list.length - 500}} More items...</h2>
        </div>
      </v-container>
      <v-container fluid class="d-flex justify-end align-center">
        <v-btn :loading="loading" x-large data-cy="start_files_upload_button" class="success ma-8"
               @click="start_upload">Upload to
          Diffgram
        </v-btn>
      </v-container>
    </v-layout>
    <v-container fluid class="align-center justify-center" v-if="loading_create_batch">
      <h1 class="pa-10 black--text text-center"> [1/2] Creating Upload Batch...
        <v-progress-circular indeterminate></v-progress-circular>
      </h1>
    </v-container>
    <v-container fluid class="align-center justify-center" v-if="downloading_batch_pre_labels">
      <h1 class="pa-10 black--text text-center"> [2/2] Creating Batch Prelabeled Data...
        <v-progress-circular indeterminate></v-progress-circular>
      </h1>
    </v-container>
  </v-container>

  <v-container fluid v-else class="align-center justify-center">
    <h1 class="pa-10 black--text text-center">Preparing your data
      <v-progress-circular indeterminate></v-progress-circular>
    </h1>
  </v-container>

</template>

<script lang="ts">
  import axios from 'axios';
  import Vue from "vue";
  import {v4 as uuidv4} from 'uuid'
  import sizeof from "object-sizeof";

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
        'total_instance_count': {
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
        },
        'upload_mode': {
          default: null
        },
        'diffgram_export_ingestor':{
          default: null
        }
      },
      data() {
        return {
          input_batch: null,
          preparing_payload: false,
          loading_create_batch: false,
          downloading_batch_pre_labels: false,
          loading: false,
          file_list_update: [],
          batch_error: [],
          summarized_file_list: [],
          supported_video_files: ['video/mp4', 'video/x-msvideo', 'video/quicktime', 'video/x-m4v'],
          supported_image_files: ['image/jpg', 'image/jpeg', 'image/png']
        }
      },
      computed: {},
      watch: {
        file_list: function (new_val, old_val) {
          if (new_val) {
            this.preparing_payload = true;
            this.compute_attached_instance_per_file();
            this.summarized_file_list = this.file_list_for_summary();
            this.preparing_payload = false;
          }
        },
      },
      async mounted() {
        this.preparing_payload = true;
        await this.$nextTick();
        await new Promise(resolve => setTimeout(resolve, 500));
        this.compute_attached_instance_per_file();
        this.summarized_file_list = this.file_list_for_summary();
        this.preparing_payload = false;
      },

      beforeDestroy() {

      },
      methods: {
        file_list_for_summary: function () {
          if (this.$props.upload_mode === 'update') {
            if (this.file_list_update) {
              return this.file_list_update;
            } else {
              return []
            }
          } else if (this.$props.upload_mode === 'new') {
            return this.$props.file_list
          }
          else if(this.$props.upload_mode === 'from_diffgram_export'){
            return this.$props.diffgram_export_ingestor.get_instance_count_per_file();
          }
        },
        files_to_update_list: function () {
          if (!this.pre_labeled_data) {
            return []
          }
          const result = [];
          const result_dict = {};
          const pre_labels = JSON.parse(JSON.stringify(this.pre_labeled_data))
          for (const inst of pre_labels) {
            if (inst[this.diffgram_schema_mapping.file_id] && !result_dict[inst[this.diffgram_schema_mapping.file_id]]) {
              result.push(inst[this.diffgram_schema_mapping.file_id]);
              result_dict[inst[this.diffgram_schema_mapping.file_id]] = true;
            }
          }
          Object.freeze(result)
          return result
        },
        request_upload_raw_media: function (labels_payload) {
          if (this.upload_mode === 'new') {
            this.$emit('upload_raw_media', [...this.$props.file_list]);

          } else if (this.upload_mode === 'update') {
            this.$emit('upload_raw_media', labels_payload);
          }
          else if(this.upload_mode === 'from_diffgram_export'){
            this.$emit('upload_raw_media', labels_payload);
          }

        },
        attach_batch_to_files: function (batch) {
          if(this.$props.upload_mode === 'from_diffgram_export'){
            this.$props.diffgram_export_ingestor.add_batch_to_export_data(batch)
          }
          else{
            for (const file of this.$props.file_list) {
              file.input_batch_id = batch.id
            }

          }

        },
        chunked_batch_data_upload: async function (batch_id, blob, chunk_size_bytes) {
          const fileClone = blob.slice();
          let bytes_sent = 0;
          let chunk_start = 0;
          let chunk_end = chunk_start + chunk_size_bytes;
          let index = 0;
          let total_chunks = Math.ceil(parseFloat(fileClone.size) / chunk_size_bytes);
          while(bytes_sent < fileClone.size){
            const uuid = uuidv4();
            const formData = new FormData();
            const slicedPart = blob.slice(chunk_start, chunk_end);
            const headers = {
              'Content-Type': 'multipart/form-data',
              'Content-Range': `bytes ${chunk_start}-${chunk_end - 1}/${fileClone.size}`,
              'Content-Range-Index': index,
              'Content-Range-Total-Chunks': total_chunks ,
              'chunk-file-id': `${uuid}`,
            }
            formData.set('file', slicedPart);
            try{
              const response = await axios.post(
                `/api/v1/project/${this.$props.project_string_id}/input-batch/${batch_id}/append-data`,
                formData,
                {headers: headers}
              );
              if(response.status === 200){
                bytes_sent = chunk_end;
                index += 1;
                chunk_start = chunk_end;
                chunk_end = chunk_start + chunk_size_bytes
                if(chunk_end >= fileClone.size){
                  chunk_end = fileClone.size
                }
              }
              else{
                return
              }
            }
            catch (e) {
              console.error(e);
              this.batch_error = this.$route_api_errors(e)
              return
            }
          }
          return true

        },

        create_batch: async function (labels_payload) {
          try {
            this.loading_create_batch = true;
            const chunk_size_bytes = 6 * 1024 * 1024; // 6 mb
            // const chunk_size_bytes = 256 * 1024 // 256KB;
            const str = JSON.stringify(labels_payload);
            const bytes = new TextEncoder().encode(str);
            const blob = new Blob([bytes], {
              type: "application/json;charset=utf-8"
            });
            const total_size = blob.size;
            console.log('total size', total_size, chunk_size_bytes)
            if (total_size < chunk_size_bytes){
              const response = await axios.post(`/api/v1/project/${this.$props.project_string_id}/input-batch/new`, {
                pre_labeled_data: {...labels_payload}
              });
              if (response.status === 200) {
                this.input_batch = response.data.input_batch;
                this.$emit('created_batch', this.input_batch)
                this.loading_create_batch = false
                return true
              }
            } else {
              const response = await axios.post(`/api/v1/project/${this.$props.project_string_id}/input-batch/new`, {});
              if (response.status === 200) {
                this.input_batch = response.data.input_batch;

                const result = await this.chunked_batch_data_upload(this.input_batch.id, blob, chunk_size_bytes);
                if(result){
                  // Wait for pre labeled data download
                  this.loading_create_batch = false
                  this.downloading_batch_pre_labels = true;
                  let download_pending = true;
                  let num_request = 0;
                  while(download_pending){
                    try{
                      const response = await axios.post(
                        `/api/v1/project/${this.$props.project_string_id}/input-batch/${this.input_batch.id}`, {}
                      );

                      if(response.data.input_batch.download_status_pre_labeled_data === 'success'){
                        download_pending = false;
                      }
                      else if(response.data.input_batch.download_status_pre_labeled_data === 'failed'){
                        this.batch_error = {};
                        this.batch_error.creation_failed = 'Prelabels creation failed.';
                        download_pending = false;
                        return false
                      }
                      if(num_request > 4800){
                        this.batch_error = {};
                        this.batch_error.timeout_pre_labels = 'Timed out waiting for prelabels creation.';
                        download_pending = false;
                        return false
                      }
                      num_request += 1;
                      await new Promise(resolve => setTimeout(resolve, 3000));
                    }
                    catch (e) {
                      console.error(e);
                      this.batch_error = this.$route_api_errors(e);
                      download_pending = false;
                      return false

                    }
                  }

                  this.$emit('created_batch', this.input_batch);
                  return true
                }

              }
            }

          } catch (e) {
            console.error(e)
            this.loading_create_batch = false
            this.downloading_batch_pre_labels = false
            this.batch_error = this.$route_api_errors(e);
          } finally {

          }
        },
        prepare_pre_labeled_data_payload: function (pre_labeled_data_prop, diffgram_schema, file_list) {
          // This function Creates the final payload accepted by the API based on the schema mapping.
          if (!pre_labeled_data_prop) {
            return
          }
          const pre_labeled_data = JSON.parse(JSON.stringify(pre_labeled_data_prop))
          const pre_labeled_dict = {}
          for (const inst of pre_labeled_data) {
            let key = diffgram_schema.file_name;
            if (this.upload_mode === 'new') {
              key = inst[diffgram_schema.file_name];
            } else {
              key = inst[diffgram_schema.file_id];
            }
            if (!pre_labeled_dict[key]) {
              pre_labeled_dict[key.toString()] = [inst]
            } else {
              pre_labeled_dict[key.toString()].push(inst)
            }
          }
          const result = {};
          for (const file of file_list) {
            const uuid = uuidv4();
            let file_instances = [];

            let value = null;
            if (this.upload_mode === 'new') {
              value = file.name;
            } else {
              value = file.file_id;
            }
            file_instances = pre_labeled_dict[value.toString()]
            if(file_instances == undefined){
              file_instances = []
            }
            file.uuid = uuid;
            result[file.uuid] = {instance_list: [], frame_packet_map: {}, file_id: file.file_id};
            if (file.name) {
              result[file.name] = {instance_list: [], frame_packet_map: {}, file_id: file.file_id};
            }

            for (const instance of file_instances) {
              const type = instance[diffgram_schema.instance_type]
              let machine_made = false;
              if (instance[diffgram_schema.model_run_id] || instance[diffgram_schema.model_id]) {
                machine_made = true;
              }
              if (!file.metadata && instance[diffgram_schema.file_metadata]) {
                file.metadata = {
                  ...instance[diffgram_schema.file_metadata]
                }
                result[file.uuid].file_metadata = {...file.metadata};
                if (file.name) {
                  result[file.name].file_metadata = {...file.metadata};
                }
              } else if (file.metadata && instance[diffgram_schema.file_metadata]) {
                file.metadata = {
                  ...file.metadata,
                  ...instance[diffgram_schema.file_metadata]
                }
              }
              const diffgram_formatted_instance = {
                file_uuid: uuid,
                type: type,
                file_id: file.file_id,
                label_file_id: instance.label_file_id,
                file_name: instance[diffgram_schema.file_name],
                name: instance[diffgram_schema.name],
                model_ref: instance[diffgram_schema.model_id],
                model_run_ref: instance[diffgram_schema.model_run_id],
                frame_number: instance[diffgram_schema.frame_number],
                number: instance[diffgram_schema.number],
                machine_made: machine_made,
              }
              if (type === 'box') {

                diffgram_formatted_instance.x_max = parseInt(instance[diffgram_schema.box.x_max], 10);
                diffgram_formatted_instance.x_min = parseInt(instance[diffgram_schema.box.x_min], 10);
                diffgram_formatted_instance.y_max = parseInt(instance[diffgram_schema.box.y_max], 10);
                diffgram_formatted_instance.y_min = parseInt(instance[diffgram_schema.box.y_min], 10);

                const width = diffgram_formatted_instance.x_max - diffgram_formatted_instance.x_min;
                const height = diffgram_formatted_instance.y_max - diffgram_formatted_instance.y_min;
                diffgram_formatted_instance.width = width;
                diffgram_formatted_instance.height = height;
              } else if (type === 'point') {
                diffgram_formatted_instance.points = [
                  {x: parseInt(instance[diffgram_schema.point.x], 10), y: parseInt(instance[diffgram_schema.point.y], 10)}
                ]
              } else if (type === 'line') {
                diffgram_formatted_instance.points = [
                  {
                    x: parseInt(instance[diffgram_schema.line.x1], 10),
                    y: parseInt(instance[diffgram_schema.line.y1], 10)
                  },
                  {x: parseInt(instance[diffgram_schema.line.x2], 10), y: parseInt(instance[diffgram_schema.line.y2], 10)}
                ]
              } else if (type === 'polygon') {
                diffgram_formatted_instance.points = instance[diffgram_schema.polygon.points]
              } else if (type === 'cuboid') {
                diffgram_formatted_instance.front_face = {
                  top_left: {
                    x: parseInt(instance[diffgram_schema.cuboid.front_face_top_left_x], 10),
                    y: parseInt(instance[diffgram_schema.cuboid.front_face_top_left_y], 10)
                  },
                  top_right: {
                    x: parseInt(instance[diffgram_schema.cuboid.front_face_top_right_x], 10),
                    y: parseInt(instance[diffgram_schema.cuboid.front_face_top_right_y], 10)
                  },
                  bot_left: {
                    x: parseInt(instance[diffgram_schema.cuboid.front_face_bot_left_x], 10),
                    y: parseInt(instance[diffgram_schema.cuboid.front_face_bot_left_y], 10)
                  },
                  bot_right: {
                    x: parseInt(instance[diffgram_schema.cuboid.front_face_bot_right_x], 10),
                    y: parseInt(instance[diffgram_schema.cuboid.front_face_bot_right_y], 10)
                  },
                }
                diffgram_formatted_instance.rear_face = {
                  top_left: {
                    x: parseInt(instance[diffgram_schema.cuboid.rear_face_top_left_x], 10),
                    y: parseInt(instance[diffgram_schema.cuboid.rear_face_top_left_y], 10)
                  },
                  top_right: {
                    x: parseInt(instance[diffgram_schema.cuboid.rear_face_top_right_x], 10),
                    y: parseInt(instance[diffgram_schema.cuboid.rear_face_top_right_y], 10)
                  },
                  bot_left: {
                    x: parseInt(instance[diffgram_schema.cuboid.rear_face_bot_left_x], 10),
                    y: parseInt(instance[diffgram_schema.cuboid.rear_face_bot_left_y], 10)
                  },
                  bot_right: {
                    x: parseInt(instance[diffgram_schema.cuboid.rear_face_bot_right_x], 10),
                    y: parseInt(instance[diffgram_schema.cuboid.rear_face_bot_right_y], 10)
                  },
                }
              } else if (type === 'ellipse') {
                diffgram_formatted_instance.center_x = parseInt(instance[diffgram_schema.ellipse.center_x], 10);
                diffgram_formatted_instance.center_y = parseInt(instance[diffgram_schema.ellipse.center_y], 10);
                diffgram_formatted_instance.angle = parseFloat(instance[diffgram_schema.ellipse.angle]);
                diffgram_formatted_instance.width = parseInt(instance[diffgram_schema.ellipse.width], 10);
                diffgram_formatted_instance.height = parseInt(instance[diffgram_schema.ellipse.height], 10);
              }
              if (this.upload_mode === 'update') {
                // Assumption on update is that if instance has a frame_number it should be a video.
                if (diffgram_formatted_instance.frame_number) {
                  result[file.uuid].frame_packet_map[diffgram_formatted_instance.frame_number].push(
                    diffgram_formatted_instance
                  )
                  if (file.name) {
                    result[file.name].frame_packet_map[diffgram_formatted_instance.frame_number].push(
                      diffgram_formatted_instance
                    )
                  }


                } else {
                  result[file.uuid].instance_list.push(diffgram_formatted_instance)
                  if (file.name) {
                    result[file.name].instance_list.push(diffgram_formatted_instance)
                  }

                }
              } else if (this.upload_mode === 'new') {
                if (this.supported_image_files.includes(file.type)) {
                  result[file.uuid].instance_list.push(diffgram_formatted_instance)
                  result[file.name].instance_list.push(diffgram_formatted_instance)

                } else if (this.supported_video_files.includes(file.type)) {
                  if (!result[file.uuid].frame_packet_map[diffgram_formatted_instance.frame_number]) {
                    result[file.uuid].frame_packet_map[diffgram_formatted_instance.frame_number] = [diffgram_formatted_instance]
                    result[file.name].frame_packet_map[diffgram_formatted_instance.frame_number] = [diffgram_formatted_instance]
                  } else {
                    result[file.uuid].frame_packet_map[diffgram_formatted_instance.frame_number].push(
                      diffgram_formatted_instance
                    )
                    result[file.name].frame_packet_map[diffgram_formatted_instance.frame_number].push(
                      diffgram_formatted_instance
                    )
                  }
                } else {
                  throw new Error(`${file.type} is not a supported file format.`)
                }
              }
            }
          }
          return result;
        },
        start_upload: async function () {
          this.loading = true;
          let labels_payload = undefined;
          if(this.$props.upload_mode === 'from_diffgram_export'){
            labels_payload = this.$props.diffgram_export_ingestor.get_payload_for_batch_creation();
          }
          else{
             labels_payload = this.prepare_pre_labeled_data_payload(
              this.$props.pre_labeled_data,
              this.$props.diffgram_schema_mapping,
              this.file_list_for_summary()
            )
          }

          const result = await this.create_batch(labels_payload)
          if(!result){
            throw Error('Error creating input batch')
            return
          }
          this.attach_batch_to_files(this.input_batch);

          this.request_upload_raw_media(labels_payload);
          this.$emit('complete_question', 18)
          this.loading = false;
        },
        compute_attached_instance_per_file: function () {
          if (!this.$props.pre_labeled_data) {
            return
          }
          if (this.upload_mode === 'new') {
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
              for (const instance of all_instances) {
                if (!file.instances[instance[this.$props.diffgram_schema_mapping.name]]) {
                  file.labels[instance[this.$props.diffgram_schema_mapping.name]] = all_instances.filter(inst => inst[this.$props.diffgram_schema_mapping.name] === instance[this.$props.diffgram_schema_mapping.name]).length;
                }
              }
            }
          } else if (this.upload_mode === 'update') {
            this.file_list_update = []
            const file_ids = this.files_to_update_list();
            const pre_labels_dict = {}
            for (const inst of this.$props.pre_labeled_data) {
              if (!pre_labels_dict[inst[this.$props.diffgram_schema_mapping.file_id]]) {
                pre_labels_dict[inst[this.$props.diffgram_schema_mapping.file_id]] = [inst]
              } else {
                pre_labels_dict[inst[this.$props.diffgram_schema_mapping.file_id]].push(inst)
              }

            }
            for (let i = 0; i < file_ids.length; i++) {
              const file_id = file_ids[i];
              const file = {
                file_id: file_id,
                labels: {},
                instances: [],
                box_instances: [],
                point_instances: [],
                polygon_instances: [],
                line_instances: [],
                cuboid_instances: [],
                ellipse_instances: [],
              }
              const all_instances = pre_labels_dict[file_id]
              file.instances = all_instances;
              if (file_ids.length > 500) {
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
                for (const instance of all_instances) {
                  if (!file.instances[instance[this.$props.diffgram_schema_mapping.name]]) {
                    file.labels[instance[this.$props.diffgram_schema_mapping.name]] = all_instances.filter(inst => inst[this.$props.diffgram_schema_mapping.name] === instance[this.$props.diffgram_schema_mapping.name]).length;
                  }
                }
              }

              this.file_list_update.push(file)
            }
          }
        }

      }
    }
  ) </script>

