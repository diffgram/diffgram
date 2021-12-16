<template>
  <div class="text-center">
    <v-dialog v-if="dialog" v-model="dialog" width="500" data-cy="review_dialog" @keydown.esc="on_cancel()" @click:outside="on_cancel()">
      <v-card>
        <v-card-title class="text-h5 grey lighten-2"> Review </v-card-title>

        <v-card-text>
          <h3>Do you want to approve or request changes?</h3>
          <v-radio-group v-model="no_need_changes">
            <v-radio label="Approve" :value="true" />
            <v-radio label="Reject" :value="false" />
          </v-radio-group>

          <v-textarea
            solo
            v-model="comment"
            name="input-7-4"
            label="Review comment"
          />
        </v-card-text>

        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn id="review-dialog-cancel" color="primary" @click="on_cancel()" text> Cancel </v-btn>
          <v-btn data-cy="review-the-task" id="review-dialog-submit" color="green"  @click="on_submit()" text> Submit </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import Vue from "vue";

export default Vue.extend({
  name: "review_dialog",
  props: {
    dialog: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      no_need_changes: true,
      comment: null,
    };
  },
  methods: {
    on_submit: async function () {
      const payload = {
        action: this.no_need_changes ? "approve" : "request_change",
        comment: this.comment,
      };
      this.$emit("complete", payload);
    },
    on_cancel: function () {
      this.$emit("close_dialog");
    },
  },
});
</script>
