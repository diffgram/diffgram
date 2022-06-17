<template>
  <v-container fluid style="height: 100%">
    <action_config_wizard_base
      v-if="display_mode === 'wizard'"
      :action="action"
      :actions_list="actions_list"
      @open_action_selector="$emit('open_action_selector')"
      :project_string_id="project_string_id">
      <template v-slot:triggers>
        <trigger_config
          @change="on_action_updated"
          :project_string_id="project_string_id"
          :actions_list=actions_list
          :action="action"
          :triggers_list_prop="triggers_list"></trigger_config>
      </template>
      <template v-slot:action_config>
        <export_config_details :action="action" :project_string_id="project_string_id"></export_config_details>
      </template>
      <template v-slot:pre_conditions>
        <pre_conditions_config
          @change="on_action_updated"
          :project_string_id="project_string_id"
          :actions_list=actions_list
          :conditions_list_prop=pre_conditions_list
          :action="action">

        </pre_conditions_config>
      </template>
      <template v-slot:completion_trigger>
        <complete_conditions_config
          :completion_condition_list_prop="completion_condition_list_prop"
          :project_string_id="project_string_id"
          :actions_list=actions_list
          :action="action">

        </complete_conditions_config>
      </template>
    </action_config_wizard_base>

    <action_config_form_base
      v-if="display_mode === 'form'"
      :project_string_id="project_string_id"
      :action="action"
      :actions_list="actions_list"
    >
      <template v-slot:pre_conditions>
        <pre_conditions_config
          @change="on_action_updated"
          :project_string_id="project_string_id"
          :actions_list=actions_list
          :conditions_list_prop=pre_conditions_list
          :action="action">

        </pre_conditions_config>
      </template>
      <template v-slot:triggers>
        <trigger_config
          @change="on_action_updated"
          :project_string_id="project_string_id"
          :actions_list=actions_list
          :action="action"
          :triggers_list_prop="triggers_list"></trigger_config>
      </template>
      <template v-slot:action_config>
        <export_config_details :action="action" :project_string_id="project_string_id"></export_config_details>
      </template>
    </action_config_form_base>

    <div v-if="display_mode === 'ongoing_usage'">
      <v_export_view
          v-if="action.config_data"
          :project_string_id="$store.state.project.current.project_string_id">
      </v_export_view>
    </div>

  </v-container>
</template>

<script>
import directory_list from '../../../source_control/directory_list'
import action_config_wizard_base from '../../actions_config_base/action_config_wizard_base'
import action_config_form_base from '../../actions_config_base/action_config_form_base'
import Export_config_details from "@/components/action/action_configurations/export/export_config_details";
import trigger_config from "@/components/action/actions_config_base/trigger_config";
import pre_conditions_config from "@/components/action/actions_config_base/pre_conditions_config";
import complete_conditions_config from "@/components/action/actions_config_base/complete_conditions_config";
import action_config_mixin from "../action_config_mixin";

export default {
  name: "export_action_config",
  mixins: [action_config_mixin],
  components: {
    Export_config_details,
    action_config_wizard_base,
    action_config_form_base,
    trigger_config,
    pre_conditions_config,
    complete_conditions_config,
    directory_list: directory_list
  },
  props:{

  },
  data: function(){
    return{
      completion_condition_list_prop: [
        {
          name: 'Export Finishes Generating',
          value: 'export_generate_success'
        }
      ],
      pre_conditions_list: [
        {
          name: 'All tasks completed.',
          value: 'all_tasks_completed'
        }
      ],
      triggers_list: [
        {
          name: 'Task is Completed',
          value: 'task_completed'
        },
        {
          name: 'Previous Step Completed',
          value: 'action_completed'
        },
      ],
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

  computed:{

  },
  methods: {

  }
}
</script>

<style scoped>

</style>
