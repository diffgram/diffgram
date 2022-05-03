<template>

  <div class="mb-4">
    <h2 class="font-weight-light mr-6">2. Add Condition [Optional]: </h2>
    <v-select item-text="name" item-value="value" :items="conditions_list"
              v-model="action.condition_data.condition"></v-select>
  </div>

</template>

<script lang="ts">
import Vue from "vue";


export default Vue.extend({

    name: 'pre_conditions_config',
    components: {

    },
    props: ['action', 'project_string_id', 'actions_list', 'conditions_list_prop'],

    mounted() {

    },

    data() {
      return {
        is_open: true,
        search: '',
        conditions_list_default: [

        ],

      }
    },
    watch: {},
    computed: {
      conditions_list: function () {
        if (this.conditions_list_prop) {
          return this.conditions_list_prop;

        }

        return this.conditions_list_default
      },

    },
    methods: {

    }
  }
) </script>


<style>
code {
  width: 100%;
  height: 100% !important;
}
</style>
