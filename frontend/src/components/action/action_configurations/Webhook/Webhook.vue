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
                <v-chip color="success" v-if="item.output && item.output.status_code===200">{{
                    item.output.status_code
                  }}
                </v-chip>
                <v-chip color="warning" v-else>{{ item.output.status_code }}</v-chip>
              </td>
              <td class="hover-pointer" width="250px">
                <div @click="open_full_payload_dialog(item.output.event_payload)">
                  <code>
                    {{ JSON.stringify(item.output.event_payload, 2) | truncate(75) }}
                  </code>
                </div>
              </td>
              <td class="hover-pointer" width="250px">
                <div @click="open_full_payload_dialog(item.output.response)">
                  <code>
                    <pre>
                      {{ JSON.stringify(item.output.response, 2) | truncate(75) }}
                    </pre>
                  </code>
                </div>

              </td>
            </tr>
            </tbody>
          </template>
        </v-simple-table>

      </template>

    </action_config_base>

    <v-dialog v-model="payload_dialog_open"
              width="800">

      <v-card>
        <v-card-text>
          <div>
            <code>
          <pre>
            {{ payload_detail }}
          </pre>
            </code>
          </div>
        </v-card-text>
      </v-card>

    </v-dialog>
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
    action: {
      required: true,
    },
    project_string_id: {
      required: true
    },
  },
  data() {
    return {
      steps_config: null,
      payload_detail: null,
      payload_dialog_open: false,
      action_run_list: [],
    }
  },
  mounted() {
    this.steps_config = new ActionStepsConfig()
    this.steps_config.hide_step('pre_conditions')
    this.get_action_runs()
  },
  methods: {
    open_full_payload_dialog: function (data) {
      this.payload_detail = data;
      this.payload_dialog_open = true
    },
    close_full_payload_dialog: function () {
      this.payload_detail = null;
      this.payload_dialog_open = false
    },
    get_action_runs: async function () {
      let [data, err] = await get_action_run_list(this.project_string_id, this.action.id)
      if (err) {truncate(50)
        console.error(err)
      }
      this.action_run_list = data
    }
  },
  filters: {
    truncate: function (value, numchars) {
      let result = value
      if(typeof value === 'object'){
        result = JSON.stringify(value)
      }
      return result && result.length > numchars ? result.substring(0, numchars) + "..." : result
    },
  },
}
</script>

<style scoped>
.hover-pointer{
  cursor: pointer !important;
}
</style>
