<template>
  <div id="home">

    <v-container>
      <v-card>
        <v-layout>
          <v-flex xs12>

            <v-card>

              <h1 class="green--text text--darken-1 text-center pt-4">
                Operating System for Visual Deep Learning
              </h1>

              <h2 class="blue--text text--darken-1 text-center pa-2">
                Bring your ideas to life.
              </h2>
            

              <div class="text-center pa-4">

                <img width="300px"
                     src="https://storage.googleapis.com/diffgram-002/public/marketing/diffgram_dot_com/home/blocks_600.png">

              </div>

              <h2 class="black--text text--lighten-2 text-center pa-4">

                Diffgram-OS supports training and executing models,
                controlling file I/O, handling errors, scaling quality,
                and the annotation UI.

              </h2>


              <div class="text-center pt-4 pb-2">

                <v-btn large color="primary"
                       class="mx-0"
                       dark
                       @click="route_new_account()">
                  Create account
                </v-btn>

              
              <v-btn href="https://github.com/diffgram/diffgram/tree/master/sdk"
                     target="_blank">
                <v-icon left>mdi-github-circle</v-icon>
                View SDK Code
              </v-btn>

              </div>

              <div class="text-center pb-4">
                Join over 600 people using Diffgram today!

              </div>

            </v-card>
          </v-flex>

        </v-layout>

      </v-card>
    </v-container>

    <v-container>
      <v-card>
        <v-layout>
          <v-flex xs4>

            <v-card elevation-2 class="ma-2">
              <img class="pa-4"
                   width="100%"
                   src="https://storage.googleapis.com/diffgram-002/public/marketing/diffgram_dot_com/home/robotic_car.png">

              <h2 class="text-center pa-4">
                Robotics
              </h2>
            </v-card>

          </v-flex>

          <v-flex xs4>

            <v-card elevation-2 class="ma-2">
              <img class="pa-4"
                   width="100%"
                   src="https://storage.googleapis.com/diffgram-002/public/marketing/diffgram_dot_com/home/retail.png">

              <h2 class="text-center pa-4">
                Retail
              </h2>
            </v-card>

          </v-flex>

          <v-flex xs4>

            <v-card elevation-2 class="ma-2">
              <img class="pa-4"
                   width="100%"
                   src="https://storage.googleapis.com/diffgram-002/public/marketing/diffgram_dot_com/home/document.png">

              <h2 class="text-center pa-4">
                Documents
              </h2>
            </v-card>

          </v-flex>

        </v-layout>
        </v-card>
    </v-container>



    <v_products_builder_highlight>

    </v_products_builder_highlight>




    <!--
        hide while we are focusing on builders (and trainer orgs)
      <v_products_trainer_highlight>
      </v_products_trainer_highlight>
      -->

    <v-card>
      <v-container>
        <v-layout>
          <v-flex xs9 md9>

            <v-divider></v-divider>
            <br />
            <h2>
              Demo
            </h2>
            <br />
            <iframe src="https://player.vimeo.com/video/297864895?title=0&byline=0&portrait=0"
                    width="640" height="400" frameborder="0"
                    webkitallowfullscreen mozallowfullscreen allowfullscreen></iframe>

            <br />
            <br />
            <br />

            <h2>
              <a href="/pricing" > Paying</a> customers from Canada, USA, UK, Germany and more are saying:
            </h2>

            <h3 class="pt-2">“Diffgram has enabled us to be fast and agile with our deep learning workflow.
              It has cut our development time down by orders of magnitudes”
              Big Ag Tech Engineer</h3>

            <h3 class="pt-2">“Diffgram has allowed me to very simply upload,
              label and export exactly what I need.” Edo @ Nate tech </h3>

            <h3 class="pt-2">"Game changing"! Smart city software engineer </h3>

            <br />
            <br />


            <h2>
              Software Teams, Tutorials and Guides
            </h2>

           

            <h3 class="pt-4"> Create Training Data </h3>

            <ul>

              <li>
                <a target="_blank"
                   href="https://medium.com/diffgram/how-to-create-ai-ready-data-for-object-detection-e395f9dc6cb9">
                How to create AI ready data for object detection
                 </a>

              </li>


              <li>

                  <a target="_blank"
                   href="https://medium.com/diffgram/fast-annotation-net-a-framework-for-active-learning-in-2018-1c75d6b4af92">
          
                Fast Annotation Net - 
                    </a>
                Active learning is a way to save effort while doing annotation.
              </li>
               

              <li>
                 <a target="_blank"
                   href="https://medium.com/diffgram/scale-annotation-quality-7dd285a22d01">
                Scale annotation quality guide
                    </a>
              </li>

            </ul>

            <h3 class="pt-4"> Train and deploy models in your app using our SDK. </h3>

            <ul>
              <li>
                <a target="_blank"
                 href="https://medium.com/diffgram/red-pepper-chef-from-new-training-data-to-deployed-system-in-a-few-lines-of-code-8d25b77fe447">
                 Red Pepper Chef </a> - How to create a new system Tutorial

              </li>

              <li>
                  <a target="_blank"
                   href="https://hackernoon.com/how-to-run-many-deep-learning-models-locally-5fb8d2b4aa13">

                    Run Many Deep Learning Models Locally
                  </a> - Tutorial

              </li>

            </ul>

            <!--
            <h3> Coming soon! Get value out of a deep learning system with no code </h3>
             -->

            <h3 class="pt-4"> Validate an existing deep learning model </h3>

            <ul>
              <li>
                <a target="_blank"
                   href="https://medium.com/diffgram/how-to-validate-your-deep-learning-model-with-the-diffgram-sdk-tutorial-22234a9a35">
                  How to validate your deep learning model with the Diffgram SDK — Tutorial </a>
             </li>
              </ul>

 

            <h3 class="pt-4"> Enhancing the Built Environment through Artificial Intelligence </h3>

            <v-btn href="https://storage.googleapis.com/diffgram-002/public/marketing/building_thinking_machines-e.pdf"
                   color="primary"
                   target="_blank">
              Read the Paper
              <v-icon right>mdi-rocket</v-icon>
            </v-btn>

            <br />
            <br />
            <br />


              <br />
              <br />
              Santa Clara, CA <br />
              Diffgram Inc, a Delaware corporation.

            <br />
            <br />

          </v-flex>
        </v-layout>
      </v-container>
    </v-card>


    <div v-if="$store.state.user.logged_in">

      <v-card>
        <v-container>
          <v-layout>
            <v-flex>

              <v_search_query>
              </v_search_query>


            </v-flex>
          </v-layout>
        </v-container>
      </v-card>

      <v-card>
        <v-container>
          <v-layout>
            <v-flex>


              <h2>
                Featured projects:
              </h2>


            </v-flex>
          </v-layout>
        </v-container>
      </v-card>

    </div>

  </div>
</template>

<script lang="ts">

import axios from 'axios';

import Vue from "vue"; export default Vue.extend( {
  name: 'home',
  data () {
    return {

    }
  },
  created() {

  },
  mounted() {

  },

  methods: {
    route_join_us: function () {
      this.$router.push('/join')
    },
    route_new_account: function () {
      this.$router.push('/user/new')

    }
  }
}
) </script>

