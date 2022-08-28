<template>
  <div id="">
      <diffgram_select
        v-model="selected_attributes"
        name_key="prompt"
        key_to_seperate_objects="id"
        return_object
        :multiple="true"
        :label="label"
        :item_list="attribute_list"
      />
      <div v-if="selected_attributes.length > 0">
          <attribute_group_list
            :project_string_id="project_string_id"
            :mode="'annotate'"
            :view_only_mode="false"
            :schema_id="schema_id"
            :attribute_group_list_prop="selected_attributes"
            key="attribute_groups_list"
        />
      </div>
  </div>
</template>

<script lang="ts">
import Vue from "vue";
import diffgram_select from "../regular/diffgram_select.vue";
import attribute_group_list from "./attribute_group_list.vue";

export default Vue.extend( {
    name: 'attribute_select',
    components: { 
      diffgram_select,
      attribute_group_list
    },
    props: {
      project_string_id : {
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
    mounted() {},
    methods: {}
  }
) 
</script>
