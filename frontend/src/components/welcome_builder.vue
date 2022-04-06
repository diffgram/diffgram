<template>
  <div>

    <v-sheet fluid>

      <div class="d-flex align-center justify-center screen-height"
           style="max-height: 600px">
        <div>
          <div class="text-center">
            <v-icon size="250">mdi-human-greeting</v-icon>
          </div>
          <h1 ><span class="hero">{{$store.state.user.current.first_name}}, welcome to Diffgram</span></h1>
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
import VueConfetti from 'vue-confetti'

Vue.use(VueConfetti)

export default Vue.extend( {
  name: 'welcome_builder',
  props: {

  },

  data () {
    return {
      confetti: undefined

    }
  },
  watch: {

  },
  created() {
    this.welcome_confetti()
  },
  computed: {

  },
  methods: {

    welcome_confetti(){
      clearTimeout(this.confetti)
      this.start_confetti()
      this.confetti = setTimeout(() => {
        this.stop_confetti()
      }, 2500)
    },

    start_confetti() {
      this.$confetti.start();
    },

    stop_confetti() {
      this.$confetti.stop();
    },
  }
}
) </script>

<style>
  .hero {
    font-size: 2em;
  }
</style>
