<template>
  <div class="d-flex flex-column" style="height: 100%">

    <action_config_base
      v-if="steps_config"
      :project_string_id="project_string_id"
      :display_mode="display_mode"
      @open_action_selector="$emit('open_action_selector')"
      :steps_config="steps_config.generate()"
      :actions_list="actions_list"
      :select_dataset="true"
      :action="action"
    >

      <template v-slot:wizard_action_config >
        <task_template_config_details
          :action="action"
          :project_string_id="project_string_id"
          :actions_list="actions_list"
          @action_updated="on_action_updated"
        ></task_template_config_details>
      </template>

      <template v-slot:wizard_pre_conditions>
        <h3>Select label:</h3>
        <p>(leave blank to allow all)</p>
        <v-select
          v-if="previous_action"
          :items="previous_action.output_interface.output_labels.options"
          :label="previous_action.output_interface.output_labels.label"
          :value="action.precondition ? action.precondition.output_labels : null"
          multiple
          return-object
          item-text="name"
          item-value="id"
          @change="change_pre_condition"
        />
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
import action_config_base from "@/components/action/actions_config_base/action_config_base";
import action_config_mixin from "../action_config_mixin";
import ActionStepsConfig from '../ActionStepsConfig';
import axios from 'axios';

export default {
  name: "create_task_action_config",
  mixins: [action_config_mixin],
  components: {
    action_config_base,
    task_template_config_details,
    Job_detail,
    task_template_wizard: task_template_wizard,
  },
  data: function(){
    return{
      job_selected: null,
      show_task_template_wizard: false,
      switch_loading: false,
      steps_config: null,
      previous_action: null
    }
  },
  async mounted() {
    this.steps_config = new ActionStepsConfig()
    await this.set_step()
  },
  watch: {
    action: {
      deep: true,
      async handler(newValue, oldValue) {
        await this.set_step()
      }
    }
  },
  methods: {
    set_step: async function() {
        if (this.action.trigger_data.event_name === 'action_completed') {
          this.steps_config.show_step('pre_conditions')
          const { data } = await axios.get(`/api/v1/project/${this.project_string_id}/action/previous/${this.action.id}`)
          this.previous_action = data.previous_action
        } else {
          this.steps_config.hide_step('pre_conditions')
          this.previous_action = null
        }
    },
    change_pre_condition: function(event) {
      if (this.action.precondition) {
        this.action.precondition.output_labels = event
      } else {
        this.action.precondition = { 'output_labels': event }
      }
      this.$emit('action_updated', this.action)
    },
  }
}
</script>

<style scoped>

</style>
