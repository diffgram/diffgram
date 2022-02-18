<template>
  <v-expansion-panels
    v-if="global_attribute_groups_list"
    v-model="open"
    :accordion="true"
    :inset="false"
    :multiple="false"
    :focusable="true"
    :disabled="false"
    :flat="true"
    :hover="false"
    :tile="true"
  >
    <v-expansion-panel>

      <v-expansion-panel-header class="d-flex justify-start pa-0 sidebar-accordeon-header">

        <v-icon left class="ml-5 flex-grow-0" color="primary" size="18">
          mdi-file
        </v-icon>

        <h4>Global File Attributes</h4>

        <v-spacer></v-spacer>

        <v-chip x-small class="d-flex justify-center flex-grow-0">
            {{global_attribute_groups_list.length}}
        </v-chip>
      </v-expansion-panel-header>

      <v-expansion-panel-content>
        <attribute_group_list
          style="overflow-y:auto; max-height: 400px"
          v-if="current_global_instance
                              && global_attribute_groups_list
                              && global_attribute_groups_list.length != 0"
          :mode=" 'annotate' "
          :view_only_mode="view_only_mode"
          :attribute_group_list_prop = "global_attribute_groups_list"
          :current_instance = "current_global_instance"
          @attribute_change="$emit('attribute_change', $event)"
          key="global_attribute_groups_list"
        >
        </attribute_group_list>
      </v-expansion-panel-content>

    </v-expansion-panel>
  </v-expansion-panels>

</template>

<script lang="ts">

import attribute_group_list from './attribute_group_list.vue';


 import Vue from "vue"; export default Vue.extend( {

   name: 'global_attributes_list',

   components: {
     attribute_group_list: attribute_group_list
     },
    props: {
      'global_attribute_groups_list' : {
        default: null
      },
      'current_global_instance':{
        default: null
      },
      'view_only_mode': {
        default: false
      }
    },

    data() {
      return {

        loading: false,
        error: {},
        success: false,
        open: true
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

<style scoped>
.sidebar-accordeon-header{
  border-bottom: 1px solid #e0e0e0;
}
</style>

