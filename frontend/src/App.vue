<template>
  <div id="app">
    <v-app>

      <main_menu v-if="$route.meta.hide_default_menu != true"
                 >
      </main_menu>

      <v-main>
          <router-view></router-view>   
      </v-main>

      <v_footer v-if="$route.meta.external_page == true">

      </v_footer>

    </v-app>
  </div>
</template>

<script lang="ts">

import Vue from "vue";
import v_footer from './components/footer/footer'

export default Vue.extend({
    data() {
      return {
      }
    },
    components: {
      v_footer: v_footer
    }
  })
</script>
