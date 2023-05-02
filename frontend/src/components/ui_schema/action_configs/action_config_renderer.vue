<template>

  <attribute_set_value_config
    v-if="action.type === CUSTOM_BUTTON_ACTION_TYPE.set_attribute"
    :action="action" :project_string_id="project_string_id">

  </attribute_set_value_config>

</template>

<script lang="ts">

import Vue from 'vue';
import {CUSTOM_BUTTON_ACTION_TYPE} from '../../../types/ui_schema/CustomButtonWorkflow'
import attribute_set_value_config from './attribute_set_value_config.vue'
import attribute_select from '../../attribute/attribute_select.vue'
import {types} from "sass";
import String = types.String;
export default Vue.extend({
  name: 'action_config_renderer',
  components: {
    attribute_set_value_config,
    attribute_select
  },
  props: {
    'project_string_id': {type: String, required: true},
    'action': {required: true}

  },
  mounted: async function(){
    console.log('config action', this.action)
  },
  data() {
    // move context menu off the page out of view when hidden
    return {
      CUSTOM_BUTTON_ACTION_TYPE: CUSTOM_BUTTON_ACTION_TYPE
    }
  },
  methods: {

  }
});
</script>

<style>
.custom-text-field {
  font-size: 16px;
}
</style>
