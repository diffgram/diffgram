<template>
  <action_config_base
    v-if="steps_config"
    :project_string_id="project_string_id"
    :display_mode="display_mode"
    @open_action_selector="$emit('open_action_selector')"
    :steps_config="steps_config.generate()"
    :actions_list="actions_list"
    :steps_config_prop="steps_config"
    :action="action">

    <template slot="ongoing_usage">
      <h1>Deep Checks Result: </h1>
      <div v-if="!action.output" class="d-flex flex-column justify-center align-center">
        <h3 class="font-weight-light mt-8">Report Will Show up here when action gets triggered for the first time</h3>
        <v-icon size="128">mdi-file-chart</v-icon>
      </div>
      {{ action.output }}
    </template>

    <template slot="form_action_config">

    </template>

  </action_config_base>
</template>

<script>
import action_config_base from '../../../actions_config_base/action_config_base'
import action_config_mixin from '../../../action_configurations/action_config_mixin'
import ActionStepsConfig from '../../ActionStepsConfig';

export default {
  mixins: [action_config_mixin],
  name: "img_properties_outliers_config",
  components: {
    action_config_base: action_config_base
  },
  data: function(){
    return{
      steps_config: null
    }
  },
  mounted() {
    this.steps_config = new ActionStepsConfig()
    this.steps_config.hide_step('pre_conditions')
    this.steps_config.hide_step('completion_trigger')
  }
}
</script>

<style scoped>

</style>
