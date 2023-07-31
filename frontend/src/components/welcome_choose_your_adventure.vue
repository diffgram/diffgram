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
              <v-btn  v-if="$store.state.system && $store.state.system.is_open_source == false"                
                      large
                      outlined
                      color="primary"
                      href="https://app.diffgram.com/studio/annotate/coco-dataset/explorer"
                      target="_blank">
                Explore Sample
              </v-btn>

              <v-btn  v-if="$store.state.system && $store.state.system.is_open_source == true"                
                      large
                      outlined
                      color="primary"
                      href="https://app.diffgram.com/studio/annotate/coco-dataset/explorer"
                      target="_blank">
                Explore Sample on Diffgram.com
              </v-btn>
             
            </div>


            <div class="pa-2">
              <v-btn  large
                      outlined
                      color="primary"
                      href="https://diffgram.readme.io/docs"
                      target="_blank">
                 Learn Concepts
              </v-btn>
            </div>

            <div class="pa-2">
              <v-btn  large
                      outlined
                      color="primary"
                      href="https://www.youtube.com/channel/UC4ZVmvMA6oa3Lwaq6Si17pg"
                      target="_blank">
                 Watch Videos
              </v-btn>
            </div>

          </div>
          <div style="min-height: 50px"> </div>

          <div v-if="!$store.state.project.current.project_string_id"
               class="text-center">
            Or Continue To your First Project
            <v-btn  x-large
                    block
                    outlined
                    color="primary"
                    @click="$router.push('/a/project/new')">
              Continue
            </v-btn>
          </div>

          <div v-if="$store.state.project.current.project_string_id"
               class="text-center">
            Or Continue To Annotate
            <v-btn  x-large
                    block
                    outlined
                    color="primary"
                    @click="$router.push('/me')">
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
    this.$store.commit('check_is_open_source')
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
