<template>
  <div id="app">
    <v-app>

      <main_menu v-if="$route.meta.hide_default_menu != true">
      </main_menu>

      <v-main>
          <router-view></router-view>
      </v-main>

      <v_footer v-if="$route.meta.external_page == true">

      </v_footer>

    </v-app>
    <v-snackbar color="error" v-model="network_error ? true : false">
      Network error: Please Check your Connection to the Services, or contact us if this persists.
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
    }
  })
</script>
