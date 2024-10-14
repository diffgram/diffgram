<template>
  <div v-cloak>
    <!-- Uses Vuetify's layout component to fill the available height -->
    <v-layout fill-height>

      <!-- The button_with_menu component is used to create a button with a dropdown menu -->
      <button_with_menu
        <!-- tooltip_message prop is used to display a tooltip message when the user hovers over the button -->
        tooltip_message="Guide"
        <!-- icon prop is used to display an icon on the button -->
        icon="mdi-book-open"
        <!-- close_by_button prop is used to specify whether the menu should be closed when the user clicks on the button -->
        :close_by_button="true"
        <!-- color prop is used to style the button with a specific color -->
        color="primary"
        <!-- offset prop is used to position the menu relative to the button -->
        offset="y"
      >

        <!-- The content of the dropdown menu is defined using the slot "content" -->
        <template slot="content">
          <v-layout column>

            <!-- Displays the name and markdown content of the task guide if it exists -->
            <div v-if="task.guide">
              {{ task.guide.name }}

              <VueMarkDown :source="task.guide.markdown"></VueMarkDown>

            </div>

          </v-layout>
        </template>

      </button_with_menu>

    </v-layout>
  </div>
</template>

<script lang="ts">
import Vue from "vue";

// Exports a Vue component called "annotation_trainer_menu"
export default Vue.extend({
  name: "annotation_trainer_menu",

  // Declares props for the component
  props: {
    job_id: {
      // Sets a default value for the job_id prop
      default: null,
    },
    task: {
      // Sets a default value for the task prop
      default: null,
    },
  },

  // Declares data for the component
  data() {
    return {};
  },

  // Declares computed properties for the component
  computed: {},

  // Declares watchers for the component
  watch: {},

  // Declares methods for the component
  methods: {},

  // Defines lifecycle hooks for the component
  created() {},
});
</script>
