<template>
  <div id="">
      <diffgram_select
        :label="label"
        :item_list="[]"
      />
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
      return {}
    },
    mounted() {
        console.log("Munted")
    },
    methods: {}
  }
) </script>
