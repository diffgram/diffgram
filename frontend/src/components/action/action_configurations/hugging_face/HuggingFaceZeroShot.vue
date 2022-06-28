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
        <task_template_config_details
          :action="action"
          :project_string_id="project_string_id"
          :actions_list="actions_list"
          @action_updated="on_action_updated"
        >
        <h3>
          Select attribute for Zero Shot Classification:
        </h3>
        <br />
        <h4>Select schema</h4>
        <label_schema_selector
            :project_string_id="project_string_id"
            @change="change_schema"
            @update_label_file_visible="$emit('update_label_file_visibility', $event)"
          >
        </label_schema_selector>

        <br />

        <div v-if="selected_schema">
          <h4>Select Attribute</h4>
          <p v-if="loading_attributes">
            Loading...
          </p>
          <v-radio-group v-if="global_attribute_groups_list.length > 0 && !loading_attributes" v-model="radioGroup">
            <v-radio
              v-for="attribute in global_attribute_groups_list"
              :key="attribute.id"
              :label="attribute.prompt"
              :value="attribute.id"
            ></v-radio>
          </v-radio-group>
          <p v-else>There are no global attributes in this schema</p>
        </div>
        </task_template_config_details>
      </template>

      <template v-slot:form_action_config>
        <task_template_config_details
          :action="action"
          :project_string_id="project_string_id"
          :actions_list="actions_list"
        ></task_template_config_details>
      </template>

      <!-- <template v-slot:ongoing_usage>
        <job_detail
          v-if="action.config_data"
          :job_id="action.config_data.task_template_id">
        </job_detail>
      </template> -->

    </action_config_base>
  </div>
</template>

<script>
import task_template_wizard from '../../../task/job/task_template_wizard_creation/task_template_wizard'
import Job_detail from "@/components/task/job/job_detail";
import Action_config_wizard_base from "@/components/action/actions_config_base/action_config_wizard_base";
import action_config_form_base from "@/components/action/actions_config_base/action_config_form_base";
import action_config_base from "@/components/action/actions_config_base/action_config_base";
import action_config_mixin from "../action_config_mixin";
import label_schema_selector from "../../../label/label_schema_selector.vue"
import global_attributes_list from "../../../attribute/global_attributes_list.vue"
import ActionStepsConfig from '../ActionStepsConfig';
import { get_labels } from '../../../../services/labelServices';

export default {
  name: "hf_zero_shot",
  mixins: [action_config_mixin],
  components: {
    Action_config_wizard_base,
    action_config_base,
    action_config_form_base,
    Job_detail,
    task_template_wizard: task_template_wizard,
    label_schema_selector,
    global_attributes_list
  },
  props: {
    action:{
      required: true,
    },
    project_string_id: {
      required: true
    },
  },
  data: function(){
    return{
      job_selected: null,
      show_task_template_wizard: false,
      switch_loading: false,
      steps_config: null,
      selected_schema: null,
      loading_attributes: false,
      global_attribute_groups_list: [],
      allowed_attributes_kinds: [
        'select',
        'radio',
        'multiple_select'
      ],
    }
  },
  mounted() {
    this.steps_config = new ActionStepsConfig()
    this.steps_config.hide_step('pre_conditions')

    this.get_attributes()
  },
  watch: {
    selected_schema: function() {
      this.get_attributes()
    }
  },
  methods: {
    change_schema: function(event) {
      this.selected_schema = event.id
    },
    get_attributes: async function() {
      this.loading_attributes = true
      let [result, error] = await get_labels(this.project_string_id, this.selected_schema)
      if (error) {
        console.error(error)
        return
      }
      if (result) {
        this.global_attribute_groups_list = result.global_attribute_groups_list
          .filter(attribute => attribute.is_global && this.allowed_attributes_kinds.includes(attribute.kind))
      }
      this.loading_attributes = false
    }
  }
}
</script>

<style scoped>

</style>

