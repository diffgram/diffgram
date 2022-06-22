<template>
  <action_config_base
    v-if="action"
    :project_string_id="project_string_id"
    :display_mode="display_mode"
    @open_action_selector="$emit('open_action_selector')"
    :actions_list="actions_list"
    :steps_config_prop="steps_config"
    :action="action">

    <template slot="ongoing_usage">
      <h1>Deep Checks Result: </h1>
      <div v-if="!action.output || !action.output.html" class="d-flex flex-column justify-center align-center">
        <h3 class="font-weight-light mt-8">Report Will Show up here when action gets triggered for the first time</h3>
        <v-icon size="128">mdi-file-chart</v-icon>
      </div>
      <div v-else v-html="action.output.html">

      </div>
    </template>

    <template slot="wizard_action_config">
      <batch_config @action_updated="$emit('action_updated', action)" :action="action"></batch_config>
    </template>
    <template slot="form_action_config">
      <batch_config @action_updated="$emit('action_updated', action)" :action="action"></batch_config>
    </template>

  </action_config_base>
</template>

<script>
import action_config_base from '../../../actions_config_base/action_config_base'
import action_config_mixin from '../../../action_configurations/action_config_mixin'
import batch_config from './batch_config'
import {default_steps_config} from "@/components/action/actions_config_base/default_steps_config";

export default {
  mixins: [action_config_mixin],
  name: "img_properties_outliers_config",
  components: {
    action_config_base: action_config_base,
    batch_config: batch_config
  },
  data: function(){
    return{
      steps_config: null,
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
      hide: false
    }
    this.steps_config.completion_trigger = {
      ...this.steps_config.completion_trigger,
      number: -1,
      hide: true
    }
  }
}
</script>

<style scoped>

</style>
