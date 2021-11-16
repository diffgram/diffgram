<template>
  <div class="text-center">
    <v-dialog v-model="dialog" width="500">
      <v-card>
        <v-card-title class="text-h5 grey lighten-2">
          Submit to review
        </v-card-title>

        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="primary" text @click="dialog = false"> Cancel </v-btn>
          <v-btn color="green" text @click="dialog = false"> Submit </v-btn>
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
});
</script>