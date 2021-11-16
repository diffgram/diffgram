<template>
  <v-container fluid data-cy="task-template-reviewer-step">
    <div>
      <div class="d-flex mb-8 justify-space-between">
        <h1
          data-cy="task-template-reviewer-step-title"
          class="font-weight-medium text--primary mr-4"
        >
          Would you like to enable reviews for this task?
        </h1>
      </div>
      <v-radio-group v-model="job.allow_reviews">
        <v-radio
          data-cy="task-template-reviewer-radio-no"
          label="No"
          :value="false"
        />
        <v-radio
          data-cy="task-template-reviewer-radio-yes"
          label="Yes"
          :value="true"
        />
      </v-radio-group>
    </div>
    <div v-if="job.allow_reviews">
      <div class="d-flex mb-8 justify-space-between">
        <h1 class="font-weight-medium text--primary mr-4">
          Who is assigned to review these tasks?
        </h1>
      </div>

      <v_error_multiple :error="error"></v_error_multiple>
      <p class="text--primary">Select the Users assigned to the tasks.</p>

      <member_select
        datacy="reviwer-select"
        v-model="job.reviewer_list_ids"
        label="Select Specific Users"
        :member_list="$store.state.project.current.member_list"
        :multiple="true"
        :init_all_selected="mode === 'update' ? false : true"
        :initial_value="job.id != undefined ? job.reviewer_list_ids : ['all']"
        :allow_all_option="true"
      >
      </member_select>

      <div class="d-flex mb-8 justify-space-between">
        <h1 class="font-weight-medium text--primary mr-4">
          What percent of the tasks should be reviewed?
        </h1>
      </div>
      <v-slider
        v-model="job.review_chance"
        :disabled="review_all"
        thumb-color="green"
        thumb-label="always"
      />
      <v-checkbox
        data-cy="task-template-reviewer-review-all"
        v-model="review_all"
        :label="`Review all`"
      />
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
      review_all: false,
    };
  },
  created() {
    console.log(this.job);
  },
  methods: {
    verify_members: function () {
      if (
        !this.$props.job.reviewer_list_ids ||
        this.$props.job.reviewer_list_ids.length === 0
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
      if (this.review_all) this.job.review_chance = 100;
      if (memers_ok) {
        this.$emit("next_step");
      }
    },
  },
});
</script>
