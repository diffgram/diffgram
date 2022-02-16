<template>
<div >
   
  <v-container>
    <v-card>

      <v-card elevation-1 color="primary">
        <h1 class="white--text text-center pt-4">
          Diffgram sticker!
        </h1>
        <h2 class="grey--text text--lighten-4 text-center pa-4">
          Get 1,000 free instances per month by placing this on your website. Choose one:

        </h2>
      </v-card>

        <v-layout column>
          <v-flex>

            <v-card elevation-2 class="ma-2">

              <h1 class="text-center pl-4 pt-4">
                Transparent Option
              </h1>

              <div class="text-center pl-4 pt-4">
                  <a href="https://diffgram.com/"
                    target="_blank">
                  <img height=128px
                        src="https://storage.googleapis.com/diffgram-002/public/marketing/sticker/diffgram_os_transparent_svg.svg">
                </a>
                </div>

              <div class="text-center pa-4">
                  <kbd class="text-xs-left">
                &lt;a href="https://diffgram.com/"
                    target="_blank"&gt;
                  &lt;img height=128px
                        src="https://storage.googleapis.com/diffgram-002/public/marketing/sticker/diffgram_os_transparent_svg.svg"&gt;
                &lt;/a&gt;
                    </kbd>
              </div>

            </v-card>

          </v-flex>

          <v-flex>

            <v-card elevation-4 class="ma-2">

              <h1 class="text-center pl-4 pt-4">
                White Option
              </h1>

              <div class="text-center pl-4 pt-4">

                    <a href="https://diffgram.com/"
                      target="_blank">
                    <img height=128px
                          src="https://storage.googleapis.com/diffgram-002/public/marketing/sticker/diffgram_os_white_svg.svg">
                  </a>
                </div>

              <div class="text-center pa-4">
                  <kbd class="text-xs-left">

            &lt;a href="https://diffgram.com/"
                target="_blank"&gt;
              &lt;img height=128px
                    src="https://storage.googleapis.com/diffgram-002/public/marketing/sticker/diffgram_os_white_svg.svg"&gt;
            &lt;/a&gt;
                    </kbd>
              </div>

               

            </v-card>

          </v-flex>

        

        </v-layout>

      </v-card>

      <v-card elevation-2 class="ma-2">

      </v-card>

  </v-container>


</div>
</template>

<script lang="ts">

import Vue from "vue"; export default Vue.extend( {
  name: 'sticker',
  data () {
    return {

    }
  },
  created() {

  },
    mounted() {

  },

  methods: {

  }
}
) </script>

