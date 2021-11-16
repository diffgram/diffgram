<template>
  <div class="text-center">
    <v-dialog v-model="dialog" width="500">
      <v-card>
        <v-card-title class="text-h5 grey lighten-2"> Review </v-card-title>

        <v-card-text>
          <h3>Any changes to this task required?</h3>
          <v-radio-group v-model="need_changes">
            <v-radio label="No" :value="false" />
            <v-radio label="Yes" :value="true" />
          </v-radio-group>

          <v-textarea
            solo
            v-model="comment"
            v-if="need_changes"
            name="input-7-4"
            label="Speciafy what need to be improved"
          />
        </v-card-text>

        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="primary" @click="on_cancel" text> Cancel </v-btn>
          <v-btn color="green" @click="on_submit" text> Submit </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import Vue from "vue";
import axios from "axios";

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
      need_changes: false,
      comment: null,
    };
  },
  methods: {
    on_submit: async function () {
      const payload = {
        action: this.need_changes ? "request_change" : "approve",
        comment: this.comment,
      };
      this.$emit("complete", payload);
    },
    on_cancel: function () {
      this.$emit("on_task_action");
    },
  },
});
</script>