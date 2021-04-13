<template>
  <div v-cloak class="member-list-inline">
    <v-layout>
      <div
        v-for="(member_id, i) in member_list_internal.slice(0, 3)"
        :key="i"
      >
        <v_user_icon :member_id="member_id" :size="48" fontSize="12px !important"/>
      </div>
      <div
        v-if="member_list_internal.slice(3).length"
        class="avatar count"
      >
        <v_user_icon :message="'+' + member_list_internal.slice(3).length"/>
      </div>
    </v-layout>
  </div>

</template>

<!--

Example usage

<member_inline_view
    :member_list_ids="member_list_ids">
</member_inline_view>

-->

<script lang="ts">

import Vue from "vue";

export default Vue.extend({
  name: 'member_inline_view',
  props: {
    'member_list_ids': { // ids
      type: Array
    },
    'member_list': { // objects
      type: Array
    }
  },

  watch: {

  },
  created() {
  },

  computed: {
    member_list_internal: function () {
      if (this.$props.member_list_ids){
        return this.$props.member_list_ids
      }
      let out = []
      for (let member of this.$props.member_list) {
        out.push(member.member_id)
      }
      return out
    }
  },
  data() {
    return {
    }
  },
  methods: {

  }
})
</script>

<style>

.member-list-inline {
    z-index: 10;
    position: relative;
}

.member-list-inline .avatar {
  margin: 0 -.3rem;
  border: 3px solid white;
  border-radius: 60rem;
  padding: 0;
}

  .member-list-inline .avatar:nth-child(4) {
    z-index: -4;
  }

  .member-list-inline .avatar:nth-child(3) {
    z-index: -3;
  }

  .member-list-inline .avatar:nth-child(2) {
    z-index: -2;
  }

  .member-list-inline .avatar:nth-child(1) {
    z-index: -1;
  }

  .member-list-inline .avatar:last-child {
    margin: 0;
  }

</style>
