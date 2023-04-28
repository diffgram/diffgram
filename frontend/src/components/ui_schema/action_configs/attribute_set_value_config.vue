<template>
  <div>
    <label_schema_selector
      v-if="action && action.type === 'set_attribute'"
      @change="on_change_schema"
      :project_string_id="project_string_id">

    </label_schema_selector>
    <attribute_select
      ref="attribute_select"
      :multiple="false"
      label="Select Attribute to set"
      v-if="selected_schema_id"
      :project_string_id="project_string_id"
      :schema_id="selected_schema_id"
      :attribute_list="attribute_list"
      @change_selected="attribute_change_event"
      @attribute_change="attribute_change_value"
    />
  </div>

</template>

<script lang="ts">

import Vue from 'vue';
import label_schema_selector from '../../label/label_schema_selector.vue'
import attribute_select from '../../attribute/attribute_select.vue'
import {types} from "sass";
import String = types.String;
import {attribute_group_list} from "../../../services/attributesService";
export default Vue.extend({
  name: 'attribute_set_value_config',
  components: {
    label_schema_selector,
    attribute_select
  },
  props: {
    'project_string_id': {type: String, required: true},
    'action': {
      required: true,

    }

  },
  mounted: async function(){
    this.initialize_attribute_config()
  },
  data() {
    // move context menu off the page out of view when hidden
    return {
      label_schema: null,
      attribute_value: null,
      attribute_list: [],
      selected_schema_id: undefined,
    }
  },
  methods: {

    attribute_change_value: function(attr_value_payload){
      let attribute_template = attr_value_payload[0]
      let attribute_selected_value = attr_value_payload[1]
      this.action.set_metadata('attribute_value_id', attribute_selected_value.id)
      this.attribute_value = attribute_selected_value
    },
    attribute_change_event: function(attr){
      this.action.set_metadata('attribute_template_id', attr.id)
      this.attribute = attr
    },
    on_change_schema: async function(val){
      this.selected_schema_id = val.id
      if(this.action){
        this.action.set_metadata('schema_id', val.id)
      }
      this.label_schema = val
      await this.get_schema_attributes()
    },
    get_schema_attributes: async function () {
      const [data, error] = await attribute_group_list(this.project_string_id, undefined, this.selected_schema_id, 'from_project')

      if (!error) {
        this.attribute_list = [...data.attribute_group_list]
      }
    },
    initialize_attribute_config: async function(){
      let attr_template_id = this.action.metadata.attribute_template_id
      if(this.action.metadata.schema_id){
        this.selected_schema_id = this.action.metadata.schema_id
      }
      if(attr_template_id){
        await this.get_schema_attributes()
        await this.$nextTick();
        const attr_select = this.$refs.attribute_select;
        if(!attr_select){
          return
        }
        await attr_select.select_attribute_by_id(attr_template_id)
        const attr_value_id = this.action.metadata.attribute_value_id
        await this.$nextTick();
        if(attr_value_id){
          const attr_list_ref = attr_select.$refs.attribute_groups_list

          const attr_ref = attr_list_ref.$refs[`attribute_group_${attr_template_id}`]

          if(attr_ref && attr_ref.length > 0){
            attr_ref[0].set_attribute_value(attr_value_id)
          }
        }
      }
    }
  }
});
</script>

<style>
.custom-text-field {
  font-size: 16px;
}
</style>
