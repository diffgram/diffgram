<template>
  <div class="mb-4">
    <h3 class="mr-6">When:</h3>

    <v-select item-text="name"
              @change_directory="$emit('change')"
              item-value="value"
              :items="triggers_list"
              v-model="action.trigger_data.event_name"
    >
    </v-select>

    <v_directory_list
      v-model="action.trigger_data.upload_directory_id_list"
      v-if="action.trigger_data.event_name === 'input_file_uploaded'"
      :project_string_id="project_string_id"
      :show_new="true"
      :show_update="true"
      @change_directory="$emit('change')">
    </v_directory_list>
  </div>
</template>

<script lang="ts">
import Vue from "vue";
import {Action} from "../Action";

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
      triggers_list_prop: {}
    },
    mounted() {
      if (!this.action.trigger_data.trigger_event_name) {
        this.action.trigger_data.trigger_event_name = 'action_completed'
      }
      this.set_trigger_list(this.action_template)
    },

    data() {
      return {
        is_open: true,
        search: '',
        selected_trigger: {},
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
          console.log('eweweww', this.action_template)
          this.set_trigger_list(new_val)
        }
      },
      selected_trigger: function (new_val, old_val) {
        if (new_val && new_val.value) {

          this.action.trigger_data.event_name = new_val.value
        }
      },
      action: {
        deep: true,
        handler: function (new_val, old_val) {

        }
      }
    },
    created: function () {

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
          let selected = this.default_triggers_list.find(elm => elm.value === action_template.trigger_data.default_event_name)
          if(selected){
            this.action.trigger_data.event_name = selected.value
          }

        }
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
