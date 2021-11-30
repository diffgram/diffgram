<template>
  <div>

    <!-- Assumes not logged in -->

    <v-menu attach
            v-model="menu"
            offset-y
            
            open-on-hover
            >

      <template v-slot:activator="{on }">
        <v-btn v-on="on"
               color="primary"
               text>
          Company
        </v-btn>
      </template>

      <v-card>

        <v-layout column>

          <v-flex>

            <v-btn color="primary"
                   text
                   @click="$router.push('/about')">
              <v-icon left>mdi-information</v-icon>
              About
            </v-btn>


          </v-flex>

          <v-flex>

            <v-btn color="primary"
                   text              
                   target="_blank"
                   href="https://medium.com/diffgram">
              <v-icon left>mdi-medium</v-icon>
              Blog
              <v-icon right color="primary"> mdi-open-in-new </v-icon>
            </v-btn>

          </v-flex>

          <v-flex>

            <v-btn color="primary"
                   text
                   @click="$router.push('/enterprise/contact')">
              <v-icon left>mdi-email</v-icon>
              Contact
            </v-btn>

          </v-flex>

          <v-divider> </v-divider>

        </v-layout>
      </v-card>
    </v-menu>

  </div>

</template>

<script lang="ts">


import Vue from "vue"; export default Vue.extend( {
  name: 'menu_company',

  components: {
  },

  data() {
    return {

      menu: false

    }
  },
  computed: {

  },
  methods: {


  }
}
) </script>
