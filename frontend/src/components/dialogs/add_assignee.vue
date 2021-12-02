<template>
  <div class="text-center">
    <v-dialog v-if="dialog" v-model="dialog" width="500" @keydown.esc="on_cancel">
      <v-card>
        <v-card-title class="text-h5 grey lighten-2"> Assign </v-card-title>

        <v-card-text>
          <h3>Who should be assigned to this task?</h3>

        <member_select
          v-model="member_list_ids"
          label="Select Specific Users"
          :member_list="member_list"
          :multiple="true"
          :init_all_selected="false"
        >
        </member_select>

        </v-card-text>

        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn id="review-dialog-cancel" color="primary" @click="on_cancel" text> Cancel </v-btn>
          <v-btn :loading="loading" data-cy="review-the-task" id="review-dialog-submit" color="green" @click="on_assign" text> Assign </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import Vue from "vue";
import user_icon from "../user/user_icon.vue";

export default Vue.extend({
  name: "review_dialog",
  components: {
      user_icon
  },
  props: {
    dialog: {
      type: Boolean,
      default: false,
    },
    assignees: {
      type:  Array,
      default: []
    },
    loading: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      member_list: [],
      member_list_ids: []
    };
  },
  watch: {
    assignees: {
      handler: function (newValue) {
         this.member_list_ids = newValue.map(assignee => assignee.user_id)
      }
    }
  },
  mounted () {
      this.member_list = [...this.$store.state.project.current.member_list];
  },
  methods: {
      on_assign: function() {
          this.$emit("assign", this.member_list_ids)
      },
      on_cancel: function() {
          this.$emit("close")
      }
  },
});
</script>