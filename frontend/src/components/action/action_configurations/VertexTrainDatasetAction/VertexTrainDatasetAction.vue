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
      :action="action">

      <template v-slot:wizard_action_config>
        <h3>Select Vertex AI dataset</h3>
      </template>

      <template v-slot:ongoing_usage>

      </template>

    </action_config_base>
  </div>
</template>

<script>
import action_config_base from "@/components/action/actions_config_base/action_config_base";
import action_config_mixin from "../action_config_mixin";
import ActionStepsConfig from '../ActionStepsConfig';
import axios from 'axios'

export default {
  name: "VertexTrainDatasetAction",
  mixins: [action_config_mixin],
  components: {
    action_config_base,
  },
  props: {
    action:{
      required: true,
    },
    project_string_id: {
      required: true
    },
  },
  data (){
    return {
      steps_config: null,
    }
  },
  async mounted() {
    this.steps_config = new ActionStepsConfig()
    this.steps_config.hide_step('pre_conditions')
    await axios.put(`/api/v1/project/${this.project_string_id}/workflow/89/actions/203/manual_trigger`)
    console.log("HERE", this.action)
  }
}
</script>