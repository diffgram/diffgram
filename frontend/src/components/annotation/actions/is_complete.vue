<template>
  <div v-cloak>
    <!--
     Problem:  both v-alert and v-card Both have tons of issues with controlling width in toolbar setting
     Solution: button component that seems to control width better
    -->

    <!-- Complete File -->
    <tooltip_button
      :tooltip_message="complete_message"
      v-if="
        !task_id &&
        current_file.ann_is_complete != true &&
        view_only_mode != true
      "
      @click="is_complete_toggle_file(true)"
      :loading="is_complete_toggle_loading"
      :disabled="is_complete_toggle_loading || disabled"
      color="primary"
      icon="mdi-check-circle-outline"
      :icon_style="true"
      :bottom="true"
    >
    </tooltip_button>

    <!-- Complete Task -->
    <tooltip_button
      :tooltip_message="task_attributes.message"
      v-if="task && task.id && task.status !== 'complete'"
      @click="complete_dialog()"
      :loading="is_complete_toggle_loading"
      :disabled="is_complete_toggle_loading || disabled"
      color="primary"
      :icon="task_attributes.icon"
      :icon_style="true"
      :bottom="true"
    >
    </tooltip_button>

    <regular_chip
      v-if="task && task.status === 'complete'"
      class="pt-2 d-flex align-center"
      message="Complete"
      tooltip_message="Task Status"
      color="success"
      tooltip_direction="bottom"
    >
      <template slot="chip">
        <v-icon dark left> mdi-check-circle </v-icon>
      </template>
    </regular_chip>
    <!-- Just disable, don't show loading while saving,
        it's too distracting to show loading,
        and could confuse user (ie they think they clicked different button)

        Make button smaller in context of videos that
        take a lot of time per video and really don't need such a big
        button.
      -->

    <!-- Already complete -->

    <regular_chip
      v-if="!task && current_file.ann_is_complete == true"
      class="pt-2"
      message="Complete"
      tooltip_message="File Status"
      color="success"
      tooltip_direction="bottom"
    >
      <template slot="chip">
        <v-icon dark left> mdi-check-circle </v-icon>
      </template>
    </regular_chip>

    <tooltip_button
      tooltip_message="Mark File As Not Complete"
      @click="is_complete_toggle_file()"
      v-if="!task && current_file.ann_is_complete == true && !view_only_mode"
      icon="cancel"
      :loading="is_complete_toggle_loading"
      :disabled="is_complete_toggle_loading"
      :icon_style="true"
      color="warning"
      :bottom="true"
    >
    </tooltip_button>
    <review_dialog :dialog="review_dialog" @complete="on_submit_review" />
  </div>
</template>

<script lang="ts">
import axios from "axios";
import review_dialog from "../../dialogs/review_dialog.vue";
import { submitTaskReview } from "../../../services/tasksServices";

import Vue from "vue";

export default Vue.extend({
  name: "is_complete",
  components: {
    review_dialog,
  },
  props: {
    project_string_id: {},
    current_file: {},
    task: undefined,
    complete_on_change_trigger: {},
    view_only_mode: {},
    save_and_complete: {},
    loading: {
      default: false,
      type: Boolean,
    },
    disabled: {
      default: false,
      type: Boolean,
    },
    task_id: {
      default: null,
      type: Number,
    },
  },
  data() {
    return {
      is_complete_toggle_loading: false,
      review_dialog: false,
    };
  },
  computed: {
    complete_message: function () {
      if (this.current_file.video_id) {
        return "Complete Video";
      } else {
        return "Complete";
      }
    },
    task_attributes: function () {
      if (this.task.status === "review_requested")
        return {
          icon: "mdi-archive-eye-outline",
          message: "Complete task review",
        };
      return {
        icon: "mdi-check-circle-outline",
        message: "Complete task",
      };
    },
  },

  watch: {
    complete_on_change_trigger: "is_complete_toggle",
  },
  methods: {
    complete_dialog: function () {
      if (this.task.status === "review_requested")
        return (this.review_dialog = true);

      this.is_complete_toggle_task(true);
    },
    close_dialog: function () {
      this.review_dialog = false;
    },
    on_submit_review: async function (payload) {
      const { data } = await submitTaskReview(this.task.id, payload);
      const new_task_status = data.task.status;
      if (new_task_status === "complete") this.task.status = "complete";
      this.close_dialog();
      this.$emit("on_next");
    },
    is_complete_toggle_file: function (on_complete_only = false) {
      // save_and_complete prop, ie so only do this when used in menu
      // on_complete_only so "cancel" button doesn't push to next page
      if (this.save_and_complete == true && on_complete_only == true) {
        this.$store.commit("save_and_complete");
        return;
      }

      let endpoint =
        "/api/project/" +
        this.project_string_id +
        "/file/" +
        this.current_file.id +
        "/annotation/is_complete_toggle";

      axios
        .post(endpoint, {
          directory_id:
            this.$store.state.project.current_directory.directory_id,
        })
        .then((response) => {
          this.is_complete_toggle_loading = false;
          this.$emit("replace_file", response.data.new_file);
        })
        .catch((error) => {});
    },
    is_complete_toggle_task: function (on_complete_only = false) {
      // save_and_complete prop, ie so only do this when used in menu
      // on_complete_only so "cancel" button doesn't push to next page
      if (this.save_and_complete == true && on_complete_only == true) {
        this.$emit("on_task_annotation_complete_and_save");
        return;
      }
      const endpoint = `/api/v1/task/${this.task_id}/file/is_complete_toggle`;

      axios
        .post(endpoint, {
          directory_id:
            this.$store.state.project.current_directory.directory_id,
        })
        .then((response) => {
          this.is_complete_toggle_loading = false;
          this.$emit("replace_file", response.data.new_file);
        })
        .catch((error) => {});
    },
  },
});
</script>
