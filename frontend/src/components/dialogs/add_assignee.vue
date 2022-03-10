<template>
  <div class="text-center">
    <v-dialog data-cy="add_assignee_dialog" v-if="dialog" v-model="dialog" width="600" @keydown.esc="on_cancel" @click:outside="on_cancel">
      <v-card>
        <v-card-title v-if="dialog_type === 'assignee'" class="text-h5 grey lighten-2"> {{ remove_mode ? 'Remove' : 'Manage'}} assignees </v-card-title>
        <v-card-title v-else class="text-h5 grey lighten-2"> {{ remove_mode ? 'Remove' : 'Manage'}} reviewers </v-card-title>

        <v-card-text>
          <h3 v-if="dialog_type === 'assignee'">Who should be {{ remove_mode ? 'removed' : 'assigned'}} to {{ !plural ? "this" : "these" }} task{{ !plural ? "" : "s" }}?</h3>
          <h3 v-else>Who should {{ remove_mode ? 'be removed from the' : 'review the'}} {{ !plural ? "this" : "these" }} task{{ !plural ? "" : "s" }}?</h3>

          <member_select
            datacy="member-select-assign-task"
            v-model="member_list_ids"
            label="Select Specific Users"
            :member_list="member_list"
            :multiple="true"
            :init_all_selected="false"
          >
          </member_select>

        </v-card-text>

        <v-card-actions class="mt-9">
          <v-spacer></v-spacer>
          <v-btn id="review-dialog-cancel" color="primary" @click="on_cancel" text> Cancel </v-btn>
          <v-btn :loading="loading" data-cy="finish-user-assignment" id="review-dialog-submit" :color="remove_mode ? 'error' : 'success'" @click="on_assign" text> Submit </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import Vue from "vue";
import user_icon from "../user/user_icon.vue";

export default Vue.extend({
  name: "add_assignee",
  components: {
      user_icon
  },
  props: {
    dialog: {
      type: Boolean,
      default: false,
    },
    remove_mode: {
      type: Boolean,
      default: false
    },
    assignees: {
      type:  Array,
      default: []
    },
    loading: {
      type: Boolean,
      default: false
    },
    dialog_type: {
      type: String,
      default: 'assignee'
    },
    plural: {
      type: Boolean,
      default: false
    },
    job:{
      type: Object,
      default: {}
    },
    members_list_prop:{
      type: Array,
      default: []
    },
    reviewers_list_prop:{
      type: Array,
      default: []
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
    },
    job: {
      handler: function(){
        this.populate_members();
      }
    },
    reviewers_list_prop: {
      handler: function(){
        this.populate_members();
      }
    },
    members_list_prop: {
      handler: function(){
        this.populate_members();
      }
    },
    dialog_type: {
      handler: function(){
        this.populate_members();
      }
    }
  },
  mounted () {

    this.populate_members();
  },
  methods: {
      populate_members: function(){
        this.member_list = [];
        console.log('POPULATE', this.$props.dialog_type)
        if(this.$props.dialog_type === 'reviewer'){
          this.member_list = this.reviewers_list_prop;
        }
        else{
          this.member_list = this.members_list_prop;
        }
        this.$forceUpdate();
      },
      on_assign: function() {
          this.$emit("assign", this.member_list_ids)
      },
      on_cancel: function() {
          this.$emit("close")
      }
  },
});
</script>
