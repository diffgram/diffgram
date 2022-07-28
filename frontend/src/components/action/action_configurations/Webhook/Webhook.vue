<template>
  <div class="d-flex flex-column" style="height: 100%">

    <action_config_base
      v-if="steps_config"
      :project_string_id="project_string_id"
      :display_mode="display_mode"
      @open_action_selector="$emit('open_action_selector')"
      :steps_config="steps_config.generate()"
      :actions_list="actions_list"
      :action="action">

      <template v-slot:wizard_action_config>
        <v-text-field
          label="URL"
          v-model="action.config_data.url"
          hint="eg: https://myservice.com/process-event"
        ></v-text-field>
        <v-text-field
          label="Security Token"
          v-model="action.config_data.token"
          hint="eg: https://myservice.com/process-event"
        ></v-text-field>
      </template>

      <template v-slot:ongoing_usage>
        <h1>Webhook Executions: </h1>
        <v-simple-table>
          <template v-slot:default>
            <thead>
            <tr>
              <th class="text-left">
                URL
              </th>
              <th class="text-left">
                Status
              </th>
              <th class="text-left">
                Request Payload
              </th>

              <th class="text-left">
                Response
              </th>
            </tr>
            </thead>
            <tbody>
            <tr
              v-for="item in action_run_list"
              :key="item.name"
            >
              <td>{{ item.output.url }}</td>
              <td>
                <v-chip color="success" v-if="item.output && item.output.status_code===200">{{ item.output.status_code }}</v-chip>
                <v-chip color="warning" v-else>{{ item.output.status_code }}</v-chip>
              </td>
              <td>
                <div>
                  <code>
                    {{ item.output.event_payload }}
                  </code>
                </div>
              </td>
              <td>{{ item.output.response }}</td>
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
import {get_action_run_list} from '../../../../services/actionService'

export default {
  name: "Webhook",
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
      action_run_list: [],
    }
  },
  mounted() {
    this.steps_config = new ActionStepsConfig()
    this.steps_config.hide_step('pre_conditions')
    this.get_action_runs()
  },
  methods: {
    get_action_runs: async function(){
      let [data, err] = await get_action_run_list(this.project_string_id, this.action.id)
      if (err) {
        console.error(err)
      }
      this.action_run_list = data
    }
  }
}
</script>
