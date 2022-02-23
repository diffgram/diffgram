<template>
  <v-layout class="d-flex flex-column">
    <h1 class="font-weight-medium text--primary">Invite Your Team</h1>
    <p class="pt-3 text--primary">Add people to your project.</p>
    <v-row >
      <v-col cols="12">
        <share_new_member
          :elevation="0"
          :show_sdk_share="false"
          :project_string_id="project_string_id"
          @member_invited="on_member_invited"
        >

        </share_new_member>

      </v-col>
    </v-row>

  </v-layout>
</template>

<script lang="ts">

import share_member_list from '../share/share_member_list';
import share_new_member from '../share/share_new_member';

import Vue from "vue";
export default Vue.extend( {
  name: 'project_members_step',
  components:{
    share_member_list,
    share_new_member,
  },
  props:{
    'project_string_id':{
      default: null
    }
  },
  data() {
    return {
      step: 1,
      global_progress: 0,
      project_string_id: null,
    }
  },
  computed: {

  },
  methods: {
    on_member_invited: function(){
      this.$emit('member_invited')
    }
  }
}

) </script>
