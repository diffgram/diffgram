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
            v-if="need_changes"
            name="input-7-4"
            label="Speciafy what need to be improved"
          />
        </v-card-text>

        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="primary" text> Cancel </v-btn>
          <v-btn color="green" text> Submit </v-btn>
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
      need_changes: false,
    };
  },
});
</script>