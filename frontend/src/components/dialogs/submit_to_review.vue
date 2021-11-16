<template>
  <div class="text-center">
    <v-dialog v-model="dialog" width="500">
      <v-card>
        <v-card-title class="text-h5 grey lighten-2">
          Submit to review
        </v-card-title>

        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="primary" text @click="cancel"> Cancel </v-btn>
          <v-btn color="green" text @click="submit"> Submit </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import Vue from "vue";

export default Vue.extend({
  name: "submit_to_review",
  props: {
    dialog: {
      type: Boolean,
      default: false,
    },
  },
  methods: {
    submit: function () {
      this.$emit("complete");
      this.$emit("on_task_action");
    },
    cancel: function () {
      this.$emit("on_task_action");
    },
  },
});
</script>