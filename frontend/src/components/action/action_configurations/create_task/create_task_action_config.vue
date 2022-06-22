<template>
  <div class="d-flex flex-column" style="height: 100%">

    <action_config_base
      :project_string_id="project_string_id"
      :display_mode="display_mode"
      @open_action_selector="$emit('open_action_selector')"
      :steps_config_prop="steps_config"
      :actions_list="actions_list"
      :action="action">

      <template v-slot:wizard_action_config >
        <task_template_config_details
          :action="action"
          :project_string_id="project_string_id"
          :actions_list="actions_list"
          @action_updated="on_action_updated"
        ></task_template_config_details>
      </template>

      <template v-slot:form_action_config>
        <task_template_config_details
          :action="action"
          :project_string_id="project_string_id"
          :actions_list="actions_list"
        ></task_template_config_details>
      </template>

      <template v-slot:ongoing_usage>
        <job_detail
          v-if="action.config_data"
          :job_id="action.config_data.task_template_id">
        </job_detail>
      </template>

    </action_config_base>
  </div>
</template>

<script>
import task_template_wizard from '../../../task/job/task_template_wizard_creation/task_template_wizard'
import Job_detail from "@/components/task/job/job_detail";
import task_template_config_details from './task_template_config_details';
import {default_steps_config} from "@/components/action/actions_config_base/default_steps_config";
import action_config_base from "@/components/action/actions_config_base/action_config_base";
import action_config_mixin from "../action_config_mixin";
export default {
  name: "create_task_action_config",
  mixins: [action_config_mixin],
  mounted() {
    this.steps_config = {
      ...default_steps_config
    }
    this.steps_config.pre_conditions = {
      ...this.steps_config.pre_conditions,
      hide: true,
      number: -1,
    }
    this.steps_config.action_config = {
      ...this.steps_config.action_config,
      number: 2,
    }
    this.steps_config.completion_trigger = {
      ...this.steps_config.completion_trigger,
      number: 3,
    }
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
    action_config_base,
    task_template_config_details,
    Job_detail,
    task_template_wizard: task_template_wizard,
  },
  methods: {

  },
  computed:{
    on_directories_updated: function(){

    }
  }
}
</script>

<style scoped>

</style>
