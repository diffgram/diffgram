<template>
  <v-container fluid>
    <div class="d-flex flex-column">
      <div class="mb-4">
        <h2 class="font-weight-light mr-6">1. Trigger When: </h2>
        <v-select item-text="name" item-value="value" :items="triggers_list" v-model="action.trigger_data.trigger_event_name"></v-select>
      </div>

      <div class="mb-4">
        <h2 class="font-weight-light mr-6">2. Add Condition [Optional]: </h2>
        <v-select   item-text="name" item-value="value" :items="conditions_list" v-model="action.condition_data.condition"></v-select>
      </div>


      <div class="mb-4">
        <h2 class="font-weight-light mb-4">3. Export Configuration: </h2>
        <div class="d-flex flex-column ml-10 pl-8 pa-4" style="border: 1px solid #e0e0e0; width: 60%">
          <diffgram_select
            :item_list="source_list"
            v-model="source"
            label="Source"
            :disabled="loading"
          >
          </diffgram_select>


          <v_directory_list
            v-if="source == 'directory' "
            :project_string_id="project_string_id"
            :show_new="false"
            :show_update="false"
            @change_directory="">
          </v_directory_list>


          <div class="pl-2 pr-2">
            <job_select
              v-if="source == 'job' "
              v-model="job"
              label="Job"
              :loading="loading"
            >
            </job_select>
          </div>

          <!-- TASK -->
          <v-text-field
            v-if="source == 'task'"
            v-model="task_id"
            label="Task ID">
          </v-text-field>


          <v-select :items="kind_list"
                    v-model="kind"
                    label="Kind"
                    item-value="text">
          </v-select>

          <div class="pl-4 pr-4">
            <v-checkbox v-model="ann_is_complete"
                        data-cy="complete-files-only-checkbox"
                        label="Complete Files Only">
            </v-checkbox>
          </div>
        </div>
      </div>

      <div class="mb-4">
        <h2 class="font-weight-light mr-6">4. Completes When: </h2>
        <v-select item-text="name" item-value="value" :items="completion_condition_list" v-model="action.complete_condition"></v-select>
      </div>

    </div>


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
      triggers_list: [
        {
          name: 'Task is Completed',
          value: 'task_completed'
        },
      ],
      source_list: [
        {
          'name': 'directory',
          'display_name': 'Dataset',
          'icon': 'mdi-folder',
          'color': 'primary'
        },
        {
          'name': 'job',
          'display_name': 'Job',
          'icon': 'mdi-inbox',
          'color': 'green'
        },
        {
          'name': 'task',
          'display_name': 'Task',
          'icon': 'mdi-flash-circle',
          'color': 'purple'
        }
      ],
      source: "directory",
      kind_list: ["Annotations"],
      completion_condition_list: [
        {
          name: 'Export is Generated Successfully',
          value: 'task_completed'
        }
      ],
      conditions_list: [
        {
          name: 'All Tasks completed',
          value: 'all_tasks_completed'
        }
      ],
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
