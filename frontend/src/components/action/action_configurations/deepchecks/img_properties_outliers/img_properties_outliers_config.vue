<template>
  <action_config_base
    v-if="steps_config"
    :project_string_id="project_string_id"
    :display_mode="display_mode"
    @open_action_selector="$emit('open_action_selector')"
    :steps_config="steps_config.generate()"
    :actions_list="actions_list"
    :action="action">

    <template slot="ongoing_usage">
      DEEP CHECKS REPORT GOES HERE
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
  components:{
    action_config_base: action_config_base
  },
  mounted() {
    this.steps_config = new ActionStepsConfig()
    // this.steps_config.pre_conditions = {
    //   ...this.steps_config.pre_conditions,
    //   hide: true,
    //   number: -1,
    // }
    // this.steps_config.action_config = {
    //   ...this.steps_config.action_config,
    //   number: -1,
    //   hide: true
    // }
    // this.steps_config.completion_trigger = {
    //   ...this.steps_config.completion_trigger,
    //   number: 2,
    // }
  }
}
</script>

<style scoped>

</style>
