<template>
  <v-card v-if="task.id" :elevation="elevation" class="pa-0">
    <v-card-title class="pa-0"><h6 class="pa-0 ma-0">Related Files: </h6></v-card-title>
    <v-container class="pa-0">
      <div class="d-flex align-center pa-1" style="border: 1px solid dimgrey; border-radius: 5px; background: #f0f0f0 ">
        <v-icon v-if="file.ann_is_complete" color="success" size="16">mdi-check-circle</v-icon>
        <v-icon v-if="!file.ann_is_complete" color="warning" size="16" >mdi-clock</v-icon>
        <v-icon color="primary" size="16">mdi-file</v-icon>
        <a :href="`/file/${file.id}`" target="_blank" style="font-size: 12px" ><strong>{{file.original_filename}} [ID: {{file.id}}]</strong></a>
      </div>
      <h6 class="pa-0 ma-0">Related Tasks: </h6>

      <v-progress-circular :color="primary" indeterminate v-if="loading"></v-progress-circular>
      <v_error_multiple :error="error_related_tasks"></v_error_multiple>
      <div v-if="!loading" v-for="task in related_tasks" class="d-flex align-center pa-1" style="border: 1px solid dimgrey; border-radius: 5px; background: #f0f0f0 ">
        <v-icon v-if="task.status === 'complete'" color="success" size="16">mdi-check-circle</v-icon>
        <v-icon v-if="task.status !== 'complete'" color="warning" size="16" >mdi-clock</v-icon>
        <v-icon color="primary" size="16">mdi-file</v-icon>
        <a :href="`/task/${task.id}`" target="_blank" style="font-size: 12px" ><strong>Task: {{task.id}} [{{task.job.name}}]</strong></a>
      </div>
    </v-container>
  </v-card>
</template>

<script lang="ts">

  import axios from 'axios';
  import task_status_icons from '../regular_concrete/task_status_icons';

  import Vue from "vue";

  export default Vue.extend({
      name: 'task_relations_card',
      props: [
        'task',
        'file',
        'project_string_id',
        'elevation'
      ],
      components: {
        task_status_icons
      },
      data() {
        return {
          loading: false,
          related_tasks: [],
          error_related_tasks: {}
        }
      },
      mounted() {
        this.fetch_task_relations();
      },
      methods: {
        fetch_task_relations: async function(){
          try{
            this.loading = true;
            if(!this.$props.task){
              return
            }
            if(!this.$props.task.file){
              return
            }
            if(!this.$props.task.file.id != undefined){
              return
            }
            const response = await axios.post(`/api/v1/project/${this.$props.project_string_id}/task/list`, {
              file_id: this.$props.task.file.id,
              mode_data: 'list'
            })
            if(response.status === 200){
              this.related_tasks = response.data.task_list;
            }
          }
          catch (error) {
            this.error_related_tasks = this.$route_api_errors(error)
          }
          finally {
            this.loading = false;
          }

        }
      }
    }
  )
</script>

