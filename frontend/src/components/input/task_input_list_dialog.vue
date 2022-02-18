<template>
  <v-dialog v-model="is_open" max-width="1000px" id="task-input-list-dialog">
    <v-card elevation="0">
      <v_input_view :task_id="task_id"
                    :show_filters="false"
                    ref="input_view"
                    :project_string_id="project_string_id">
      </v_input_view>
    </v-card>
  </v-dialog>
</template>

<script lang="ts">
import Vue from "vue";

export default Vue.extend( {
  name: 'task_input_list_dialog',

  props: {
    'project_string_id': {
      default: null
    },
    'task_id':{
      default: null
    }
  },

  data() {

    return {
      is_open: false,
    }


  },
  computed: {

  },
  watch: {},
  mounted() {},

  beforeDestroy() {

  },

  methods: {
    async open() {
      this.is_open = true;
    }
  }
}
) </script>

