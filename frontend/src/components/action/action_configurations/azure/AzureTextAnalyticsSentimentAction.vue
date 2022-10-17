<template>
  <div class="d-flex flex-column" style="height: 100%">

    <!-- WIP to call `action_manual_trigger` service
         Also probably not right spot for it maybe should be inside wizard etc-->
    <standard_button
        tooltip_message="Manual Trigger"
        @click="move_frame"
        icon="help"
        :text_style="true"
        color="primary">
    </standard_button>

    <action_config_wizard_base
      v-if="display_mode === 'wizard' && steps_manager"
      :action="action"
      :actions_list="actions_list"
      :steps_config="steps_manager.generate()"
      @open_action_selector="$emit('open_action_selector')"
      :project_string_id="project_string_id">
      <template v-slot:action_config>

      </template>
    </action_config_wizard_base>


    <action_config_form_base
      v-if="display_mode === 'form' && steps_manager"
      :steps_config="steps_manager.generate()"
      :project_string_id="project_string_id"
      :action="action"
      :actions_list="actions_list"
    >
      <template v-slot:action_config>


      </template>
    </action_config_form_base>

    <div v-if="display_mode === 'ongoing_usage'">

      <!-- TBD -->
      
    </div>



  </div>
</template>

<script>
import {Action} from './../../Action'
import Action_config_wizard_base from "@/components/action/actions_config_base/action_config_wizard_base";
import action_config_form_base from "@/components/action/actions_config_base/action_config_form_base";
import ActionStepsConfig from '../ActionStepsConfig'

export default {
  name: "AzureTextAnalyticsSentimentAction",
  components: {
    Action_config_wizard_base,
    action_config_form_base,
  },
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
  data: function(){
    return{
      job_selected: null,
      show_task_template_wizard: false,
      switch_loading: false,
      steps_manager: null
    }
  },
  mounted() {
    this.steps_manager = new ActionStepsConfig()
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
