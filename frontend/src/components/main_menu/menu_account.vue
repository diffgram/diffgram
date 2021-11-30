<template>
  <div>

    <!-- Only show an account if there is no org id...
         this needs a lot of work
        $store.state.org.current.id
         We want to show account for say a "regular"
        Diffgram trainer but don't want to confuse this for
        say an org customer's signup
        -->


    <!-- Dec 24, 2019, don't show this till we change
         other stuff with account to make more sense here... -->
    <!-- and if we do will need to use new standard menu thing -->

    <v-menu v-if="false && $store.state.builder_or_trainer.mode == 'builder'"
            v-model="account_menu"
            :nudge-width="100"
            
            open-on-hover
            offset-y>

      <v-btn color="primary"
             text
             @click=route_overview()
             :disabled="false">
        <v-icon left> mdi-bank </v-icon>
        Account
      </v-btn>


      <v-card>
        <v-layout column>
          <!-- Buttons wrapped in v-flex to help with alignemnt -->
          <!-- Dialog components appear to not need it-->


          <v-flex>
            <v-btn color="primary"
                   dark
                   text
                   @click=route_overview()>
              <v-icon left>mdi-finance</v-icon>
              Overview
            </v-btn>
          </v-flex>


          <v-divider></v-divider>

          <v-flex v-if="mode=='builder'">
            <v-btn color="primary"
                   text
                   @click="route_payment_settings">
              <v-icon left>mdi-credit-card</v-icon>
              Payment settings
            </v-btn>
          </v-flex>


        </v-layout>
      </v-card>


    </v-menu>


  </div>

</template>

<script lang="ts">

import Vue from "vue"; export default Vue.extend( {
  name: 'main_menu_account',
  props: {
    mode: {
      default: null
    }
  },

  data() {
    return {

      account_menu: false
    }
  },
  computed: {

  },
  methods: {

    route_overview() {
      this.$router.push("/account/overview")
    },
    route_payment_settings() {
      this.$router.push("/account/payment/settings")
    }

  }
}
) </script>
