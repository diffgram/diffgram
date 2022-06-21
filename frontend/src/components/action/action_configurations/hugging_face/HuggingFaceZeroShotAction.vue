<template>
  <div class="d-flex flex-column" style="height: 100%">

    <!-- WIP to call `action_manual_trigger` service
         Also probably not right spot for it maybe should be inside wizard etc-->
    <tooltip_button
        tooltip_message="Manual Trigger"
        @click="move_frame"
        icon="help"
        :text_style="true"
        color="primary">
    </tooltip_button>

    <action_config_wizard_base
      v-if="display_mode === 'wizard'"
      :action="action"
      :actions_list="actions_list"
      :steps_config_prop="steps_config"
      @open_action_selector="$emit('open_action_selector')"
      :project_string_id="project_string_id">
      <template v-slot:action_config>

      </template>
    </action_config_wizard_base>


    <action_config_form_base
      v-if="display_mode === 'form'"
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
import {Action} from '../../Action'
import Action_config_wizard_base from "@/components/action/actions_config_base/action_config_wizard_base";
import action_config_form_base from "@/components/action/actions_config_base/action_config_form_base";
import {default_steps_config} from "@/components/action/actions_config_base/default_steps_config";
import {action_manual_trigger} from '@/services/workflowServices';


export default {
  name: "HuggingFaceZeroShotAction",
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
    Action_config_wizard_base,
    action_config_form_base,
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
