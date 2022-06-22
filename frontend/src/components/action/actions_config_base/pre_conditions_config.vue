<template>

  <div class="mb-4">
    <h3 class="mr-6">2. Add Condition [Optional]: </h3>
    <v-select item-text="name" item-value="value"
              @change="on_pre_condition_change"
              :items="conditions_list"
              v-model="action.condition_data.event_name">

    </v-select>
  </div>

</template>

<script lang="ts">
import Vue from "vue";
import {Action} from "../Action";


export default Vue.extend({

    name: 'pre_conditions_config',
    components: {},
    props: {
      action: {
        type: Action,
        required: true
      },
      project_string_id: {
        type: String,
        required: true
      },
      actions_list: {
        required: true
      },
      action_template: {
        required: true
      },
      conditions_list_prop: {}
    },

    mounted() {
      this.set_pre_condition_list(this.action_template)
    },
    methods: {
      set_pre_condition_list: function(action_template){
        if(!action_template){
          return
        }
        if(!action_template.condition_data){
          return
        }
        if (action_template.condition_data && action_template.condition_data.event_list) {
          this.conditions_list = action_template.condition_data.event_list
          let selected = this.conditions_list.find(elm => elm.value === action_template.trigger_data.default_event_name)
          if(selected){
            this.action.condition_data.event_name = selected.value
          }

        }
      },
      on_pre_condition_change: function(elm){
        this.$emit('change', elm)
      }
    },
    data() {
      return {
        is_open: true,
        selected_condition: null,
        conditions_list: [],
        search: '',

      }
    },
    created() {
      if (this.action.condition_data.event_name) {
        this.selected_condition = this.conditions_list.find(elm => elm.value === this.action.condition_data.event_name)
      }
    },
    watch: {
      action_template: {
        deep: true,
        handler: function(new_val, old_val){
          this.set_pre_condition_list(new_val)
        }
      },
      selected_condition: function (new_val, old_val) {
        if (new_val && new_val.value) {
          this.action.condition_data.event_name = new_val.value
        }
      }
    },
    computed: {
      conditions_list: function () {
        if (this.conditions_list_prop) {
          return this.conditions_list_prop;

        }

        return this.conditions_list_default
      },

    },
  }
) </script>


<style>
code {
  width: 100%;
  height: 100% !important;
}
</style>
