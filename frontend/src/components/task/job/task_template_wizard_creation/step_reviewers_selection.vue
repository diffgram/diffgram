<template>
  <v-container fluid data-cy="task-template-users-step">
    <div>
      <div class="d-flex mb-8 justify-space-between">
        <h1
          data-cy="task-template-users-step-title"
          class="font-weight-medium text--primary mr-4"
        >
          Would you like to enable reviews for this task?
        </h1>
      </div>
      <v-radio-group v-model="enabled">
        <v-radio label="No" :value="false" />
        <v-radio label="Yes" :value="true" />
      </v-radio-group>
    </div>
    <div v-if="enabled">
      <div class="d-flex mb-8 justify-space-between">
        <h1
          data-cy="task-template-users-step-title"
          class="font-weight-medium text--primary mr-4"
        >
          Who is assigned to review these tasks?
        </h1>
      </div>

      <v_error_multiple :error="error"></v_error_multiple>
      <p data-cy="task-template-users-step-subtitle" class="text--primary">
        Select the Users assigned to the tasks.
      </p>

      <member_select
        datacy="member-select"
        v-model="job.member_list_ids"
        label="Select Specific Users"
        :member_list="$store.state.project.current.member_list"
        :multiple="true"
        :init_all_selected="mode === 'update' ? false : true"
        :initial_value="job.id != undefined ? job.member_list_ids : ['all']"
        :allow_all_option="true"
      >
      </member_select>

      <div class="d-flex mb-8 justify-space-between">
        <h1
          data-cy="task-template-users-step-title"
          class="font-weight-medium text--primary mr-4"
        >
          What percent of the tasks should be reviewed?
        </h1>
      </div>
      <v-slider
        v-model="review_percent"
        :disabled="review_all"
        thumb-color="green"
        thumb-label="always"
      />
      <v-checkbox v-model="review_all" :label="`Review all`" />
    </div>
    <wizard_navigation
      @next="on_next_button_click"
      @back="$emit('previous_step')"
      :skip_visible="false"
      :loading_next="loading_steps"
      :disabled_next="loading_steps"
    >
    </wizard_navigation>
  </v-container>
</template>

<script lang="ts">
import label_select_only from "../../../label/label_select_only.vue";
import label_manager_dialog from "../../../label/label_manager_dialog.vue";

import Vue from "vue";

export default Vue.extend({
  name: "step_reviewers_selection",
  props: ["project_string_id", "job", "loading_steps", "mode"],

  components: {
    label_select_only,
    label_manager_dialog,
  },

  data() {
    return {
      error: {},
      request_refresh_labels: new Date(),
      enabled: false,
      review_percent: null,
      review_all: false,
    };
  },
  methods: {
    verify_members: function () {
      if (
        !this.$props.job.member_list_ids ||
        this.$props.job.member_list_ids.length === 0
      ) {
        this.error = {
          name: "At least 1 user should be assigned.",
        };
        return false;
      }
      return true;
    },
    on_next_button_click: function () {
      this.error = {};
      let memers_ok = this.verify_members();
      if (memers_ok) {
        this.$emit("next_step");
      }
    },
  },
});
</script>
