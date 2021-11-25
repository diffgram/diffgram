<template>
  <div class="text-center">
    <v-dialog v-if="dialog" v-model="dialog" width="500" @keydown.esc="on_cancel">
      <v-card>
        <v-card-title class="text-h5 grey lighten-2"> Assign </v-card-title>

        <v-card-text>
          <h3>Who should be assigned to this task?</h3>

        <v-select
          v-model="member_to_assign"
          :items="member_list"
          :item-text="member => `${member.first_name} ${member.last_name}`"
          item-value="id"
          single-line
        >
        </v-select>

        </v-card-text>

        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn id="review-dialog-cancel" color="primary" @click="on_cancel" text> Cancel </v-btn>
          <v-btn data-cy="review-the-task" id="review-dialog-submit" color="green" @click="on_assign" text> Assign </v-btn>
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
  },
  data() {
    return {
      member_list: [],
      member_to_assign: null
    };
  },
  computed: {
    current_user() {
      const user = [...this.member_list].find(
        (item) => item.id === this.member_to_assign
      );
      return user;
    },
  },
  mounted () {
      this.member_list = [...this.$store.state.project.current.member_list];
  },
  methods: {
      on_assign: function() {
          this.$emit("assign", this.member_to_assign)
      },
      on_cancel: function() {
          this.$emit("close")
      }
  },
});
</script>