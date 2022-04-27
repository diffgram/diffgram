<template>
  <v-container fluid>
    <h2>When do you want to export?</h2>
    <v-select v-model="action.export_on" :items="items" item-text="name" item-value="value"></v-select>
    <p v-if="prev_action && prev_action.job">Task Template Detected: <strong>{{prev_action.job.name}}</strong></p>


  </v-container>
</template>

<script>
import directory_list from '../../source_control/directory_list'
export default {
  name: "file_upload_action_config",
  props:{
    prev_action: {
      default: null
    },
    action:{
      required: true
    },
    project_string_id:{
      required: true
    }
  },
  data: function(){
    return{
      items:[
        {
          name: 'When All tasks completed',
          value: 'all_tasks_complete'
        }
      ]
    }
  },
  components: {
    directory_list: directory_list
  },
  computed:{
    on_directories_updated: function(){

    }
  }
}
</script>

<style scoped>

</style>
