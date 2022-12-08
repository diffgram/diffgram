<template>
  <div class="mb-4">
    <h2 class="font-weight-light mb-4">3. Export Configuration: </h2>
    <div class="d-flex flex-column ml-10 pl-8 pa-4" style="border: 1px solid #e0e0e0; width: 60%">
      <diffgram_select
        :item_list="source_list"
        v-model="action.config_data.source"
        label="Source"
        :disabled="loading"
      >
      </diffgram_select>


      <global_dataset_selector
        v-model="action.config_data.directory_id"
        v-if="action.config_data.source === 'directory' "
        @change_directory="on_change_directory"
      />

      <div class="pl-2 pr-2">
        <job_select
          v-if="action.config_data.source === 'job' "
          v-model="action.config_data.task_template"
          @change="on_task_template_changed"
          label="Job"
          :loading="loading"
          :select_this_id="action.config_data.task_template_id"
        >
        </job_select>
      </div>

      <!-- TASK -->
      <v-text-field
        v-if="action.config_data.source === 'task'"
        v-model="action.config_data.task_id"
        label="Task ID">
      </v-text-field>


      <v-select :items="kind_list"
                v-model="action.config_data.kind"
                label="Kind"
                item-value="text">
      </v-select>

      <div class="pl-4 pr-4">
        <v-checkbox v-model="action.config_data.ann_is_complete"
                    data-cy="complete-files-only-checkbox"
                    label="Complete Files Only">
        </v-checkbox>
      </div>
    </div>
  </div>
</template>

<script>
import directory_selector from '../../../source_control/directory_selector'
import action_config_wizard_base from '../../actions_config_base/action_config_wizard_base'
import global_dataset_selector from "../../../attached/global_dataset_selector.vue"

export default {
  name: "export_config_details",
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
  components: {
    global_dataset_selector
  },
  methods: {
    on_task_template_changed: function(tt){
      this.action.config_data.task_template_id = tt.id
    },
    on_change_directory: function(dir){
      this.action.config_data.directory_id = dir.directory_id
    },
  },
  data: function(){
    return{
      loading: false,

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
      kind_list: ["Annotations"],
    }
  },
  components: {
    directory_list: directory_selector
  },
  computed:{
    on_directories_updated: function(){

    }
  }
}
</script>

<style scoped>

</style>
