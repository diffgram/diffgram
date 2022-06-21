<template>
  <div class="d-flex flex-column" style="height: 100%">

    <action_config_base
      :project_string_id="project_string_id"
      :display_mode="display_mode"
      @open_action_selector="$emit('open_action_selector')"
      :steps_config_prop="steps_config"
      :actions_list="actions_list"
      :action="action">

      <template v-slot:wizard_action_config>
        <h1>wizard_action_config</h1>
      </template>

      <template v-slot:form_action_config>
        <h1>form_action_config</h1>
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
import Action_config_wizard_base from "@/components/action/actions_config_base/action_config_wizard_base";
import action_config_form_base from "@/components/action/actions_config_base/action_config_form_base";
import {default_steps_config} from "@/components/action/actions_config_base/default_steps_config";
import action_config_base from "@/components/action/actions_config_base/action_config_base";
import action_config_mixin from "../action_config_mixin";

export default {
  name: "HuggingFaceZeroShotAction",
  mixins: [action_config_mixin],
  mounted() {
    this.steps_config = {
      ...default_steps_config
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
    Action_config_wizard_base,
    action_config_base,
    action_config_form_base,
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
