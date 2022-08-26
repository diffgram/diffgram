<template>
  <div id="">
      <diffgram_select
        v-model="selected_attributes"
        name_key="prompt"
        :multiple="true"
        :label="label"
        :item_list="attribute_list"
      />
      <div v-if="selected_attributes.length > 0">
          <diffgram_select 
            v-for="attribute in selected_attributes"
            :key="attribute"
            :multiple="true"
            :label="`Attribute: ${attribute}`"
            :item_list="[{ name: 'One' }, { name: 'Two' }, { name: 'Tree' }]"
          />
      </div>
  </div>
</template>

<script lang="ts">
import Vue from "vue";
import diffgram_select from "../regular/diffgram_select.vue";

export default Vue.extend( {
    name: 'attribute_select',
    components: { 
      diffgram_select 
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
