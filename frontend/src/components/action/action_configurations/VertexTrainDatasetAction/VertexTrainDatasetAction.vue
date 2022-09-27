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

      <template v-slot:wizard_action_config>
          <v-text-field
            v-model="action.config_data.model_name"
            label="Model name"
          />
          <v-text-field
            v-model="action.config_data.staging_bucket_name_without_gs_prefix"
            label="Bucket name"
          />
          <connection_select v-model="action.config_data.connection_id" />
          <v-text-field
            v-model="action.config_data.experiment"
            label="Experiment"
          />
          <v-text-field
            v-model="action.config_data.experiment_description"
            label="Experiment description"
          />
          <v-checkbox
            v-model="advanced"
            label="Advanced configuration"
          />
          <v-text-field
            v-model="action.config_data.training_node_hours"
            v-if="advanced"
            label="Training node hours"
            type="number"
          />
          <diffgram_select
            v-model="action.config_data.autoML_model"
            v-if="advanced"
            :item_list="autoML_models"
            :return_object="true"
          />
      </template>

      <template v-slot:ongoing_usage>
        <v-btn @click="train_dataset" color="success">Train</v-btn>
        <h1>VertexAI model trainings: </h1>
        <v-simple-table>
          <template v-slot:default>
            <thead>
            <tr>
              <th class="text-left">
                Status
              </th>
              <th class="text-left">
                Model Name
              </th>
            </tr>
            </thead>
            <tbody>
            <tr
              v-for="item in action_run_list"
              :key="item.id"
            >
              <td style="text-transform: capitalize">{{ item.status }}</td>
              <td v-if="item.output && item.output.model_name">{{ item.output.model_name }}</td>
            </tr>
            </tbody>
          </template>
        </v-simple-table>

      </template>

    </action_config_base>
  </div>
</template>

<script>
import action_config_base from "@/components/action/actions_config_base/action_config_base";
import action_config_mixin from "../action_config_mixin";
import ActionStepsConfig from '../ActionStepsConfig';
import { get_action_run_list, trigger_action } from '../../../../services/actionService';
import connection_select from '../../../connection/connection_select.vue';
import diffgram_select from '../../../regular/diffgram_select.vue';

export default {
  name: "VertexTrainDatasetAction",
  mixins: [action_config_mixin],
  components: {
    action_config_base,
    connection_select,
    diffgram_select,
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
      advanced: false,
      steps_config: null,
      action_run_list: [],
      autoML_models: [
        {
          value: 'CLOUD_LOW_LATENCY_1',
          name: 'Low latency (AutoML)'
        },
        {
          value: 'CLOUD_HIGH_ACCURACY_1',
          name: 'Higher prediction quality (AutoML)'
        },
        {
          value: 'MOBILE_TF_VERSATILE_1',
          name: 'General purpose usage (AutoML Edge)'
        },
        {
          value: 'MOBILE_TF_LOW_LATENCY_1',
          name: 'Low Latency (AutoML Edge)'
        },
        {
          value: 'MOBILE_TF_HIGH_ACCURACY_1',
          name: 'Higher prediction quality (AutoML Edge)'
        },
      ]
    }
  },
  async mounted() {
    this.steps_config = new ActionStepsConfig()
    this.steps_config.hide_step('pre_conditions')
    this.$emit('action_updated', this.action)

    let [data, err] = await get_action_run_list(this.project_string_id, this.action.id)

    this.action_run_list = data
  },
  methods: {
    train_dataset: async function() {
      await trigger_action(this.project_string_id, this.workflow.id, this.action.id)
    }
  }
}
</script>