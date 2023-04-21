<template>
  <div id="">
    <diffgram_select
      v-model="selected_attributes"
      name_key="prompt"
      key_to_seperate_objects="id"
      return_object
      :multiple="multiple"
      :label="label"
      :item_list="attribute_list_computed"
      @change="$emit('change_selected', $event)"
    />
    <div v-if="selected_attributes_computed && selected_attributes_computed.length > 0">
      <attribute_group_list
        :project_string_id="project_string_id"
        :mode="'annotate'"
        :view_only_mode="false"
        :schema_id="schema_id"
        :attribute_group_list_prop="selected_attributes_computed"
        key="attribute_groups_list"
        @attribute_change="$emit('attribute_change', $event)"
      />
    </div>
  </div>
</template>

<script lang="ts">
import Vue from "vue";
import diffgram_select from "../regular/diffgram_select.vue";
import attribute_group_list from "./attribute_group_list.vue";

export default Vue.extend({
    name: 'attribute_select',
    components: {
      diffgram_select,
      attribute_group_list
    },
    props: {
      multiple: {
        type: Boolean,
        default: true
      },
      project_string_id: {
        type: String,
        required: true
      },
      schema_id: {
        type: Number,
        required: true
      },
      label: {
        type: String,
        required: true
      },
      attribute_list: {
        type: Array,
        default: []
      }
    },
    data() {
      return {
        selected_attributes: [],
      }
    },
    methods: {
      set_selected_attributes: function(selected_attributes){
        this.selected_attributes = selected_attributes
      }
    },
    computed: {
      selected_attributes_computed: function () {
        if (Array.isArray(this.selected_attributes)) {
          return this.selected_attributes
        }
        if (this.selected_attributes && typeof this.selected_attributes === 'object') {
          return [this.selected_attributes]
        }
        return []

      },
      attribute_list_computed: function () {
        let ordered_attributes = this.attribute_list.sort((a, b) => a.ordinal - b.ordinal);
        return ordered_attributes.map(elm => {
          elm.prompt = !elm.prompt ? 'Untitled Attribute Group' : elm.prompt
          return elm
        })
      }
    }
  }
)
</script>
