<template>
  <div>

    <v-sheet fluid>

      <div class="d-flex align-center justify-center screen-height"
           style="max-height: 600px">
        <div>
          <div class="text-center">
            <v-icon size="250">mdi-summit</v-icon>
          </div>
          <h1 ><span class="hero">Choose your Adventure</span></h1>

          <div class="text-center pt-2 d-flex">

            <div class="pa-2">
              <v-btn  large
                      outlined
                      color="primary"
                      @click="">
                Explore Sample
              </v-btn>
            </div>

            <div class="pa-2">
              <v-btn  large
                      outlined
                      color="primary"
                      @click="">
                 Learn Concepts
              </v-btn>
            </div>

            <div class="pa-2">
              <v-btn  large
                      outlined
                      color="primary"
                      @click="">
                 Join an Existing Project
              </v-btn>
            </div>

          </div>
          <div style="min-height: 50px"> </div>
          <div class="text-center">
            Or Continue To your First Project
            <v-btn  x-large
                    block
                    outlined
                    color="primary"
                    @click="">
              Continue
            </v-btn>
          </div>
        </div>
      </div>

    </v-sheet>

  </div>
</template>


<script lang="ts">
import Vue from 'vue'


export default Vue.extend( {
  name: 'welcome_social',
  props: {

  },

  data () {
    return {

    }
  },
  watch: {

  },
  created() {

  },
  computed: {

  },
  methods: {

    
  }
}
) </script>

<style>
  .hero {
    font-size: 2em;
  }
</style>
