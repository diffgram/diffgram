<template>
  <div class="d-flex flex-column" style="height: 100%">
    <action_config_wizard_base
      v-if="display_mode === 'wizard'"
      :action="action"
      :actions_list="actions_list"
      :steps_config_prop="steps_config"
      @open_action_selector="$emit('open_action_selector')"
      :project_string_id="project_string_id">
      <template v-slot:triggers>
        <slot name="wizard_triggers"></slot>
      </template>
      <template v-slot:pre_conditions>
        <slot name="wizard_pre_conditions"></slot>
      </template>
      <template v-slot:action_config>
        <slot name="wizard_action_config">
          Your Action specific configuration goes here.
        </slot>
      </template>
      <template v-slot:completion_trigger>
        <slot name="wizard_completion_trigger"></slot>
      </template>

    </action_config_wizard_base>


    <action_config_form_base
      v-if="display_mode === 'form'"
      :project_string_id="project_string_id"
      :action="action"
      :actions_list="actions_list"
    >
      <template v-slot:triggers>
        <slot name="form_triggers"></slot>
      </template>
      <template v-slot:pre_conditions>
        <slot name="form_pre_conditions"></slot>
      </template>
      <template v-slot:action_config>
        <slot name="form_action_config">
          Your Action specific configuration goes here.
        </slot>
      </template>
      <template v-slot:completion_trigger>
        <slot name="form_completion_trigger"></slot>
      </template>

    </action_config_form_base>

    <div v-if="display_mode === 'ongoing_usage'">
      <slot name="ongoing_usage">
        <h1> YOUR ONGOING USAGE TEMPLATE CODE GOES HERE</h1>
      </slot>

    </div>



  </div>
</template>

<script>
import Action_config_wizard_base from "@/components/action/actions_config_base/action_config_wizard_base";
import action_config_form_base from "@/components/action/actions_config_base/action_config_form_base";
import {default_steps_config} from "@/components/action/actions_config_base/default_steps_config";
import action_config_mixin from "../action_configurations/action_config_mixin.js";
export default {
  name: "action_config_base",
  mixins: [action_config_mixin],
  props:{
    steps_config_prop: {
      type: Object,
      required: false
    }
  },
  mounted() {
    this.steps_config = {...default_steps_config}
    if (this.steps_config_prop){
      this.steps_config = {...this.steps_config_prop}
    }
  },
  watch:{
    steps_config_prop:{
      deep: true,
      handler: function(new_val, old_val){
        if(new_val){
          this.steps_config = {...new_val}
        }
      }
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

  },
  computed:{
    on_directories_updated: function(){

    }
  }
}
</script>

<style scoped>

</style>
