<template>
  <div>

    <v-sheet fluid>

      <div class="d-flex align-center justify-center screen-height"
           style="max-height: 600px">
        <div>
          <div class="text-center">
            <v-icon class="pa-4" size="250">mdi-slack</v-icon>
          </div>

          <h1 ><span class="hero">The Diffgram community wants to meet you!</span></h1>

          <div class="text-center pa-4">
            <v-btn  block
                    x-large
                    outlined
                    color="primary"
                    href="https://join.slack.com/t/diffgram-workspace/shared_invite/zt-twn6529v-hhSPzpQrAxvoZB95PhfAFg"
                    target="_blank">
              Join Slack
            </v-btn>
          </div>
          <div style="min-height: 50px"> </div>
          <div class="text-center pa-4">
            <v-btn  x-large
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
