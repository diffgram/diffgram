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
            v-if="action && !loading"
            :disabled="true"
            :project_string_id="project_string_id"
            :initial_schema="selected_schema"
            @change="change_schema"
          >
        </label_schema_selector>

        <br />

        <div v-if="selected_schema">
          <h4>Select Attribute</h4>
          <p v-if="loading_attributes">
            Loading...
          </p>
          <div v-if="global_attribute_groups_list.length > 0 && !loading_attributes" >
            <v-select
              :items="global_attribute_groups_list"
              :value="selected_attribute_group"
              item-text="prompt"
              item-value="id"
              label="Attribute"
              @change="change_attribute"
            >
              <template v-slot:item="data">
                <v-layout class="d-flex align-center justify-start">
                  <v-icon v-if="data.item.kind === 'multiple_select'" color="#9c27b0">
                    mdi-select-multiple
                  </v-icon>
                  <v-icon v-if="data.item.kind === 'radio'" color="#e91e63">
                    mdi-radiobox-marked
                  </v-icon>
                  <v-icon v-if="data.item.kind === 'select'">
                    mdi-selection
                  </v-icon>
                  <div style="width: 20px" />
                  <div>
                    {{ data.item.prompt }}
                </div>
                </v-layout>
              </template>
            </v-select>
            <p>Options that will bepassed to the action: {{ options }}</p>
          </div>
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
import { get_task_template_details } from '../../../../services/taskTemplateService'

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
      loading: false,
      show_task_template_wizard: false,
      switch_loading: false,
      steps_config: null,
      selected_schema: null,
      selected_attribute_group: null,
      loading_attributes: false,
      global_attribute_groups_list: [],
      allowed_attributes_kinds: [
        'select',
        'radio',
        'multiple_select'
      ],
    }
  },
  watch: {
    selected_schema: function() {
      if (this.selected_schema) this.get_attributes()
    }
  },
  computed: {
    options: function() {
      let option_string = '';
      if (!this.global_attribute_groups_list || !this.selected_attribute_group) return option_string

      const current_attribute = this.global_attribute_groups_list.find(attr => attr.id === this.selected_attribute_group)

      if (!current_attribute) return option_string

      current_attribute.attribute_template_list.map(attr => {
        option_string += attr.name + ' ,'
      })

      return option_string.slice(0, -2)
    }
  },
  async mounted() {
    this.loading = true
    this.steps_config = new ActionStepsConfig()
    this.steps_config.hide_step('pre_conditions')

    if (this.action) {
      if (this.action.trigger_data.event_name === 'task_created' && this.action.config_data.task_template_id) {
        const { label_schema } = await get_task_template_details(this.action.config_data.task_template_id)
        this.change_schema(label_schema)
      }
      else {
        if (this.action.config_data.schema_id) {
          this.selected_schema = this.action.config_data.schema_id
        }
      }
      if (this.action.config_data.group_id) {
        this.selected_attribute_group = this.action.config_data.group_id
      }
    } 
    this.loading = false
  },
  methods: {
    change_schema: function(event) {
      if (this.action && event.id) {
        this.selected_schema = event.id
        this.action.config_data.schema_id = event.id;
        this.action.config_data.project_id = event.project_id;
        if (this.action.trigger_data.event_name !== 'task_created') {
          this.action.config_data.group_id = null
          this.selected_attribute_group= null
        }
        this.$emit('action_updated', this.action)
      }
    },
    change_attribute: function(event) {
      this.action.config_data.group_id = event
      this.selected_attribute_group= event
      this.$emit('action_updated', this.action)
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

