<template>
<div id="">


  <!-- All for a given project? -->
  <attribute_group_list
      :schema_id="schema_id"
      :project_string_id="project_string_id"
      :mode = " 'edit' "
      :draggable="true">
  </attribute_group_list>


</div>
</template>

<script lang="ts">

import attribute_group_list from './attribute_group_list.vue';


 import Vue from "vue"; export default Vue.extend( {

   name: 'attribute_home',

   components: {
     attribute_group_list: attribute_group_list
     },
    props: {
      'project_string_id' : {
        default: null
      },
      'schema_id':{
        required: true
      }
    },

    data() {
      return {

        loading: false,
        error: {},
        success: false
      }
    },

    watch: {

    },

    created() {


    },
    computed: {
    },
    methods: {


    }
  }
) </script>
