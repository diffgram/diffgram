<template>
  <div id="app">
    <v-app>

      <main_menu v-if="get_meta($route).hide_default_menu != true">
      </main_menu>

      <v-main>
          <router-view></router-view>
      </v-main>

      <v_footer v-if="get_meta($route).external_page == true">

      </v_footer>

    </v-app>
    <v-snackbar color="warning" timeout="5000" v-model="network_error" v-if="!!network_error">
     <strong> Network Issue Detected: Check your Connection to the Services.</strong>
    </v-snackbar>
  </div>
</template>

<script lang="ts">

import Vue from "vue";
import v_footer from './components/footer/footer'
import { mapGetters } from 'vuex'

export default Vue.extend({
    data() {
      return {
      }
    },
    computed: {
      ...mapGetters({
        network_error: 'get_network_error'
      })
    },
    components: {
      v_footer: v_footer
    },
    methods: {
      get_meta: function (route) {
        if (typeof(route.meta) === 'function') {
          return route.meta(route)
        } else {
          return route.meta
        }
      }
    }
  })
</script>
