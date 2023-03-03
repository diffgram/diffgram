<template>
  <v-expansion-panels
    v-if="sorted_global_attribute_groups_list"
    v-model="open"
    :accordion="true"
    :inset="false"
    :multiple="false"
    :focusable="true"
    :disabled="false"
    :flat="true"
    :hover="true"
    :tile="true"
  >
    <v-expansion-panel>
      <v-expansion-panel-header
        class="d-flex justify-start pa-0 sidebar-accordeon-header"
      >
        <v-icon
          left
          class="ml-5 flex-grow-0"
          color="primary"
          size="18"
        >
          mdi-file
        </v-icon>

        <h4>{{ title }}</h4>

        <v-spacer></v-spacer>

        <v-chip
          x-small
          class="d-flex justify-center flex-grow-0"
        >
          {{ sorted_global_attribute_groups_list.length }}
        </v-chip>
      </v-expansion-panel-header>

      <v-expansion-panel-content>
        <attribute_group_list
          v-if="current_global_instance && sorted_global_attribute_groups_list && sorted_global_attribute_groups_list.length !== 0"
          style="overflow-y:auto; max-height: 400px"
          mode="annotate"
          key="global_attribute_groups_list"
          :schema_id="schema_id"
          :project_string_id="project_string_id"
          :view_only_mode="view_only_mode"
          :attribute_group_list_prop="sorted_global_attribute_groups_list"
          :current_instance="current_global_instance"
          @attribute_change="$emit('attribute_change', $event)"
        />
      </v-expansion-panel-content>
    </v-expansion-panel>
  </v-expansion-panels>

</template>

<script lang="ts">
import attribute_group_list from './attribute_group_list.vue';
import Vue from "vue";

export default Vue.extend({
    name: 'global_attributes_list',
    components: {
      attribute_group_list: attribute_group_list
    },
    props: {
      global_attribute_groups_list: {type: Array, default: null},
      current_global_instance: {type: Object, default: null},
      view_only_mode: {type: Boolean, default: false},
      schema_id: {type: Number, required: true},
      project_string_id: {type: String, required: true},
      open_state: {type: Boolean || undefined, default: undefined},
      title: {type: String, default: 'Active File Attributes:'},
    },
    data() {
      return {
        open: undefined
      }
    },
    watch: {
      open_state: function (newVal, oldVal) {
        if (newVal) {
          this.open = 0
        } else {
          this.open = undefined
        }
      }
    },
    mounted() {
      if (this.open_state === undefined) {
        if (this.global_attribute_groups_list.length > 0) this.open = 0
      } else {
        this.open = this.open_state ? 0 : undefined
      }
    },
    computed: {
      sorted_global_attribute_groups_list: function(){
        return this.global_attribute_groups_list.sort((a, b) => a.ordinal - b.ordinal);
      }
    }
  }
)
</script>

<style scoped>

</style>

