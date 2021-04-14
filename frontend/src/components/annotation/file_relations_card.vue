<template>
  <v-card v-if="file.id" :elevation="elevation" class="pa-0">
    <v-card-title class="pa-0"><h5 class="pa-0 ma-0">Related Tasks: </h5></v-card-title>
    <v-container class="pa-0" v-if="!loading">
      <div v-for="task in related_tasks"
           v-bind:key="task.id"
           class="d-flex align-center pa-1"
           style="border: 1px solid dimgrey;
          border-radius: 5px;
          background: #f0f0f0 "
           >

        <v-icon v-if="task.status === 'complete'" color="success" size="16">mdi-check-circle</v-icon>
        <v-icon v-if="task.status !== 'complete'" color="warning" size="16" >mdi-clock</v-icon>
        <v-icon color="primary" size="16">mdi-file</v-icon>
        <a :href="`/task/${task.id}`" target="_blank" style="font-size: 12px" ><strong>Task: {{task.id}} [{{task.job.name}}]</strong></a>
      </div>
    </v-container>
    <v-progress-circular indeterminate v-else></v-progress-circular>
  </v-card>
</template>

<script lang="ts">

  import axios from 'axios';
  import task_status_icons from '../regular_concrete/task_status_icons';

  import Vue from "vue";

  export default Vue.extend({
      name: 'file_relations_card',
      props: [
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
          related_tasks: []
        }
      },
      watch:{
        file: function(newfile, oldfile){
          if(newfile && newfile.id != undefined && newfile.id !== oldfile.id){
            this.fetch_related_task();
          }
        }
      },
      mounted() {
        this.fetch_related_task()
      },
      methods: {
        fetch_related_task: async function(){
          try{
            if(!this.$props.project_string_id){
              return;
            }
            if(!this.$props.file){
              return;
            }
            const file_id = this.$props.file.id;
            if(file_id == undefined){
              return
            }
            this.loading = true;
            const response = await axios.post(`/api/v1/project/${this.$props.project_string_id}/task/list`,
              {
                file_id: file_id,
                mode_data: 'list',
                project_string_id: this.$props.project_string_id
              })
            if(response.status === 200){
              this.related_tasks = response.data.task_list;
            }
          }
          catch (error) {
            this.related_tasks_error = this.$route_api_errors(error);
          }
          finally {
            this.loading = false;
          }
        }
      }
    }
  )
</script>

