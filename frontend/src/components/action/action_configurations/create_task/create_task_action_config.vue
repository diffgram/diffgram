<template>
  <div class="d-flex flex-column">
    <action_config_wizard_base
      v-if="display_mode === 'wizard'"
      :action="action"
      :actions_list="actions_list"
      :project_string_id="project_string_id">
      <template v-slot:action_config>
        <task_template_config_details
          :action="action"
          :project_string_id="project_string_id"
          :actions_list="actions_list"
          @action_updated="on_action_updated"
        ></task_template_config_details>
      </template>
    </action_config_wizard_base>


    <action_config_form_base
      v-if="display_mode === 'form'"
      :project_string_id="project_string_id"
      :action="action"
      :actions_list="actions_list"
    >
      <template v-slot:action_config>
        <task_template_config_details
          :action="action"
          :project_string_id="project_string_id"
          :actions_list="actions_list"
        ></task_template_config_details>
      </template>
    </action_config_form_base>

    <div v-if="display_mode === 'ongoing_usage'">
      <job_detail
          v-if="action.config_data"
          :job_id="action.config_data.task_template_id">
      </job_detail>
    </div>



  </div>
</template>

<script>
import task_template_wizard from '../../../task/job/task_template_wizard_creation/task_template_wizard'
import {create_empty_job} from '../../../task/job/empty_job'
import {Action} from './../../Action'
import Job_detail from "@/components/task/job/job_detail";
import task_template_config_details from './task_template_config_details';
import Action_config_wizard_base from "@/components/action/actions_config_base/action_config_wizard_base";
import action_config_form_base from "@/components/action/actions_config_base/action_config_form_base";
import {default_steps_config} from "@/components/action/actions_config_base/default_steps_config";
export default {
  name: "create_task_action_config",
  props:{
    action:{
      required: true,
      type: Action
    },
    project_string_id: {
      required: true
    },
    actions_list: {
      required: true
    },
    display_mode:{
      default: "wizard"
    }
  },
  mounted() {
    this.steps_config = {
      ...default_steps_config
    }
    this.steps_config.pre_conditions.hide = true
    this.steps_config.action_config.number = 2
    this.steps_config.completion_trigger.number = 3
  },
  data: function(){
    return{
      job_selected: null,
      show_task_template_wizard: false,
      switch_loading: false,
      steps_config: null

    }
  },
  components: {
    Action_config_wizard_base,
    action_config_form_base,
    task_template_config_details,
    Job_detail,
    task_template_wizard: task_template_wizard,
  },
  methods: {
    on_action_updated: function(act){
      this.$emit('action_updated', act)
    },
  },
  computed:{
    on_directories_updated: function(){

    }
  }
}
</script>

<style scoped>

</style>
