<template>
  <div id="">
      <diffgram_select
        v-model="selected_attributes"
        :multiple="true"
        :label="label"
        :item_list="[{ name: 'One' }, { name: 'Two' }, { name: 'Tree' }]"
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
    components: { diffgram_select },
    props: {
      'project_string_id' : {
        required: true
      },
      'schema_id': {
        required: true
      },
      'global': {
        type: Boolean,
        default: false
      },
      'label': {
          required: true
      }
    },
    data() {
      return {
          selected_attributes: []
      }
    },
    mounted() {
        console.log("Munted")
    },
    methods: {}
  }
) </script>
