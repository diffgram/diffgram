<template>
<div>

    <!-- Assumes not logged in -->

  <!--  standard method buttons
    assume we want a tool tip but here we don't so declaring template
    with activator -->

  <v-layout>
    <v-menu v-model="menu"
            offset-y
            open-on-hover
            attach
            >

      <template v-slot:activator="{ on }">
        <v-btn v-on="on"
               color="primary"
               text>
          Learn
        </v-btn>
      </template>

      <v-card>

        <v-layout column>



          <!--
          <v-flex>

            <v-btn color="primary"
                   text
                   href="https://github.com/diffgram/diffgram"
                   target="_blank"
                   >
              <v-icon left>mdi-github-circle</v-icon>
              SDK
              <v-icon right color="primary"> mdi-open-in-new </v-icon>
            </v-btn>

          </v-flex>
          -->

          <v-flex>

            <v-btn color="primary"
                   text
                   @click="$router.push('/learn/build_vs_buy')"
                   >
              <v-icon left>mdi-flash-circle</v-icon>
              Build vs Buy
            </v-btn>

          </v-flex>

          <v-flex>

            <v-btn color="primary"
                   text              
                   target="_blank"
                   href="https://diffgram.readme.io/docs/training-data">
              <v-icon left>mdi-book-open-page-variant</v-icon>
              Tutorials
              <v-icon right color="primary"> mdi-open-in-new </v-icon>
            </v-btn>


          </v-flex>


          <v-flex>

            <v-btn color="primary"
                   text
                   @click="$router.push('/markets')"
                   >
              <v-icon left>mdi-cash-multiple</v-icon>
              Markets
            </v-btn>

          </v-flex>

          
          <v-divider> </v-divider>

        </v-layout>
      </v-card>
    </v-menu>

  </v-layout>
</div>

</template>

<script lang="ts">



import Vue from "vue"; export default Vue.extend( {
  name: 'menu_learn',

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
