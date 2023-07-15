<template>
  <div>
    <v-layout column>

      <h1> Super Admin Menu </h1>

      <h2> Install Info </h2>

       <div class="pa-4">
          <v-btn @click="$router.push('/admin/install/info')">
            View Install Info
          </v-btn>
        </div>

      <h2> Application Admin </h2>

        <div class="pa-4">
          <v-btn @click="$router.push('/admin/queue/status')">
            Queue Status
          </v-btn>
        </div>


        <div class="pa-4">
          <v-btn @click="$router.push('/admin/logo')">
            Set Install Logo
          </v-btn>
        </div>


      <div class="pa-4">
          <v-btn @click="$router.push('/admin/')">
            View All Projects
          </v-btn>
        </div>

      <h2> UI Preferences: </h2>
        <div class="pa-4">
          <p>
            IDs are showing: {{$store.state.user.settings.show_ids}}
          </p>
          <v-btn @click="$store.commit('set_user_setting', [
                'show_ids',
                !$store.state.user.settings.show_ids,
              ])">
            Show/Hide IDs
          </v-btn>
        </div>

        <div class="pa-4">
          <p>
            Super Admin / Regular User Frontend:
          </p>
          <v-btn @click="$store.commit('super_admin_toggle')">
            Super Admin Toggle
          </v-btn>
        </div>

      <h2> Mock Data </h2>

        <div class="pa-4">
          <v-btn @click="$router.push('/admin/mock')">
            Mock Annotations
          </v-btn>
        </div>

    </v-layout>
  </div>

</template>

<script lang="ts">

import Vue from "vue";

export default Vue.extend( {
  name: 'menu_super_admin',
  props: {
    mode: {
      default: null
    }
  },

  data() {
    return {

    }
  },
  computed: {

  },
  methods: {



  }
}
) </script>
