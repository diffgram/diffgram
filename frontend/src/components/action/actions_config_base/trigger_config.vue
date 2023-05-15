<template>
  <div class="mb-4">
    <h3 class="mr-6">When:</h3>

    <v-select item-text="name"
      item-value="value"
      :items="triggers_list"
      v-model="action.trigger_data.event_name"
    />

    <global_dataset_selector
      v-if="action && select_dataset"
      :show_new="true"
      :show_update="true"
      :set_current_dir_on_change="false"
      :set_from_id="action.config_data.directory_id"
      @change_directory="on_update_directory"
    />

    <job_select
        v-if="action.trigger_data.event_name === 'task_created'"
        v-model="action.config_data.task_template_id"
        ref="job_select"
        class="mr-4"
        label="Select Task Template"
        :select_this_id="action.config_data.task_template_id"
    />
    <div v-if="action.trigger_data.event_name === 'time_trigger'">
      <h2>Trigger Every: </h2>
      <CronVuetify v-model="action.trigger_data.cron_expression" @error="error=$event"></CronVuetify>
      <div class="mt-2 grey--text text--darken-1">cron expression: {{action.trigger_data.cron_expression}}</div>

    </div>
  </div>
</template>

<script lang="ts">
import Vue from "vue";
import {Action} from "../Action";
import global_dataset_selector from "../../attached/global_dataset_selector.vue"
// import {CronVuetify} from '@vue-js-cron/vuetify'
export default Vue.extend({
    name: 'trigger_config',
    props: {
      action: {
        type: Action,
        required: true
      },
      action_template: {
        required: true
      },
      project_string_id: {
        type: String,
        required: true
      },
      actions_list: {
        required: true
      },
      select_dataset: {
        type: Boolean,
        default: false
      },
      triggers_list_prop: {}
    },
    components: {
      global_dataset_selector
    },
    mounted() {
      this.set_trigger_list(this.action_template)
    },
    data() {
      return {
        is_open: true,
        error: null,
        search: '',
        cron: '',
        default_triggers_list: [
          {
            name: 'Previous Step Completed',
            value: 'action_completed'
          },
        ],

      }
    },
    watch: {
      action_template: {
        deep: true,
        handler: function (new_val, old_val) {
          this.set_trigger_list(new_val)
        }
      }
    },
    computed: {
      triggers_list: function () {
        if (this.triggers_list_prop) {
          return this.triggers_list_prop;

        }
        return this.default_triggers_list.filter(elm => {
          if (elm.value === 'action_completed' && !this.prev_action) {
            return false
          }
          return true
        })
      },
      prev_action: function () {
        if (!this.actions_list) {
          return
        }
        for (let i = 0; i < this.actions_list.length; i++) {
          let current = this.actions_list[i]
          if (current === this.action) {
            if (i === 0) {
              return undefined
            }
            return this.actions_list[i - 1]
          }
        }
      },
      actions_list_filtered: function () {
        if (!this.search || this.search === '') {
          return this.actions_list
        }
        return this.actions_list.filter(elm => elm.node.title.includes(this.search))
      }
    },
    methods: {
      set_trigger_list: function (action_template) {
        if(!action_template){
          return
        }
        if(!action_template.trigger_data){
          return
        }
        if (action_template.trigger_data && action_template.trigger_data.event_list) {
          this.default_triggers_list = action_template.trigger_data.event_list
          let action_completed_event = this.default_triggers_list.find(elm => elm.name === 'action_completed')
          if (this.prev_action && !action_completed_event){
            this.default_triggers_list.push({name: 'action_completed', value: 'action_completed'})
          }
          let selected = this.default_triggers_list.find(elm => elm.value === action_template.trigger_data.default_event_name)
          if(selected && selected.trigger_data && !selected.trigger_data.event_name){
            this.action.trigger_data.event_name = selected.value
          }

        }
      },
      on_update_directory: function(e) {
        this.action.config_data.directory_id = e.directory_id
      },
      close() {
        this.input = undefined;
        this.is_open = false;
      },
      open() {
        this.is_open = true;
      },
    }
  }
) </script>


<style>
.v-select__selections input {
  font-size: 1.6em;
  line-height: 24px;
}

.list-item__title input {
  font-size: 1.6em;
  line-height: 24px;
}
</style>
