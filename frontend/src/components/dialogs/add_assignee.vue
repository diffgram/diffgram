<template>
  <div class="text-center">
    <v-dialog v-if="dialog" v-model="dialog" width="500">
      <v-card>
        <v-card-title class="text-h5 grey lighten-2"> Assign </v-card-title>

        <v-card-text>
          <h3>Who should be assigned to this task?</h3>
        </v-card-text>

        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn id="review-dialog-cancel" color="primary" @click="on_cancel" text> Cancel </v-btn>
          <v-btn data-cy="review-the-task" id="review-dialog-submit" color="green" @click="on_submit" text> Assign </v-btn>
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
  },
});
</script>