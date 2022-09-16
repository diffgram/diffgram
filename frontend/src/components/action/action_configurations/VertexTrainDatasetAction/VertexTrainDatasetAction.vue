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
        <v-text-field
          v-model="action.config_data.gcp_project_id"
          label="Project name"
        />
        <v-text-field
          v-model="action.config_data.connection_id"
          label="Connection ID"
        />
        <v-text-field
          v-model="action.config_data.staging_bucket_name_without_gs_prefix"
          hint="Bucket name without gs prefix"
          label="GCP bucket name"
        />
        <v-text-field
          v-model="action.config_data.location"
          label="Bucket location"
        />
        <v-text-field
          v-model="action.config_data.experiment"
          label="Experiment"
        />
        <v-text-field
          v-model="action.config_data.experiment_description"
          label="Experiment description"
        />
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
    await axios.put(`/api/v1/project/${this.project_string_id}/workflow/90/actions/212/manual_trigger`)
    console.log("HERE", this.action)
    this.$emit('action_updated', this.action)
  }
}
</script>