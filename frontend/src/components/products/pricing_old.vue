<template>
  <div id="pricing">

  <v-container>

    <v-layout>

    <v-flex>

          <v_products_builder_highlight>
          </v_products_builder_highlight>

          <v-card class="hidden-sm-and-up">
            Please view on larger screen.
          </v-card>

        <!-- need word -only  too -->
          <v-card class="hidden-xs-only">
                  <!-- Header -->
              <v-card color="white lighten-5"
                  elevation-10>
                <v-layout row>


                  <v-flex md3>
                    <h2 class="text-xs-left pl-4 pt-4">
                      
                    </h2>
                   </v-flex>

                  <v-flex md3>

                    <h2 class="text-right pl-4 pt-4">
                    Free
                    </h2>

                    <h3 class="text-right pl-4 pb-4">
                     Access to Evaluate
                    </h3>

                  </v-flex>

                  <v-flex md3>

                    <h2 class="green--text  text-right pl-4 pt-4">
                      Explorer
                    </h2>
                    <h3 class="green--text text--darken-1 text-right pl-4 pb-4">
                     Research and Development
                    </h3>

                  </v-flex>

                  <v-flex md3>

                    <h2 class="teal--text text-right pl-4 pt-4 pr-4">
                      Teams
                    </h2>
                    <h3 class="teal--text text--darken-1 text-right pl-4 pb-4 pr-4">
                      Shipping Production Products
                    </h3>

                  </v-flex>

                </v-layout>
              </v-card>

                <!-- Instance limit -->

                  <v-layout row>

                    <v-flex md3>

                      <h2 class="text-xs-left pl-4 pt-4">
                        Annotation
                      </h2>
                      <h3 class="text-xs-left pl-4">
                        
                      </h3>

                     </v-flex>

                    <v-flex md3>

                      <h2 class="text-right pa-4">
                       Limited
                      </h2>

                    </v-flex>

                    <v-flex md3>

                      <h2 class="green--text text-right pa-4">
                        Unlimited
                      </h2>

                    </v-flex>

                    <v-flex md3>

                      <h2 class="teal--text text-right pa-4">
                        Unlimited
                      </h2>

                    </v-flex>

                  </v-layout>
  
               <!-- Instance limit -->

              <!-- Users -->
                <v-layout row>

                  <v-flex md3>

                    <h2 class="text-xs-left pl-4 pt-4">
                      Users
                    </h2>
                    <h3 class="text-xs-left pl-4">
                      
                    </h3>

                   </v-flex>

                  <v-flex md3>

                    <h2 class="text-right pa-4">
                      1
                    </h2>

                  </v-flex>

                  <v-flex md3>

                    <h2 class="green--text text-right pa-4">
                      3
                    </h2>

                  </v-flex>

                  <v-flex md3>

                    <h2 class="teal--text text-right pa-4">
                      5
                    </h2>

                  </v-flex>

                </v-layout>
                <!-- End Users -->

                <v-layout row>
                    <v-flex md3>

                      <h2 class="text-xs-left pl-4 pt-4">
                        Support
                      </h2>
                      <h3 class="text-xs-left pl-4">
                      </h3>

                     </v-flex>


                    <v-flex md3>

                      <h2 class="text-right pa-4">
                        Community & Pre Sales
                      </h2>

                    </v-flex>

                    <v-flex md3>

                      <h2 class="green--text text-right pa-4">
                       + Email & Chat
                      </h2>

                    </v-flex>

                    <v-flex md3>

                      <h2 class="teal--text text-right pa-4">
                       + Integration, Onboarding & Video Training
                      </h2>
                      <h2 class="teal--text text-right pr-4 pt-2 pb-2">
                       + Priority Support
                      </h2>

                    </v-flex>
                </v-layout>


                  <v-layout row>
                    <v-flex md3>

                      <h2 class="text-xs-left pl-4 pt-4">
                        New Feature Ideas 
                      </h2>
                      <h3 class="text-xs-left pl-4">
                      </h3>

                     </v-flex>


                    <v-flex md3>

                      <h2 class="text-right pa-4">
 
                      </h2>

                    </v-flex>

                    <v-flex md3>

                      <h2 class="green--text text-right pa-4">
                        Regular Queue
                      </h2>

                    </v-flex>

                    <v-flex md3>

                      <h2 class="teal--text text-right pa-4">
                         Priority Implementation
                      </h2>

                    </v-flex>
                </v-layout>

 




              <v-layout row>

                  <v-flex md3>

                    <h2 class="text-xs-left pl-4 pt-4">
                      Service Level Agreement
                    </h2>
                    <h3 class="text-xs-left pl-4">
                      
                    </h3>

                   </v-flex>

                  <v-flex md3>

                  </v-flex>

                  <v-flex md3>

                  </v-flex>

                  <v-flex md3>

                    <h2 class="teal--text text-right pa-4">
                      Yes
                    </h2>

                  </v-flex>

                </v-layout>


               <!-- Cost -->
              <v-layout row>
                  <v-flex md3>

                    <h2 class="text-xs-left pl-4 pt-4">
                      Monthly Cost
                    </h2>
                    <h3 class="text-xs-left pl-4">
                      USD
                    </h3>

                   </v-flex>

                  <v-flex md3>

                  </v-flex>

                  <v-flex md3>

                    <h2 class="green--text text-right pa-4">
                      $398
                    </h2>

                  </v-flex>

                  <v-flex md3>

                    <h2 class="teal--text text-right pa-4">
                      $994
                    </h2>

                  </v-flex>

                </v-layout>

              <v-layout>
                  <v-btn block
                         class="white--text"
                         color="green"
                         href="/why"
                         >
                    Why Choose Diffgram?
                  </v-btn>
              </v-layout>

              <v-layout>
                  <v-btn v-if="$store.state.user.logged_in != true"
                          color="primary"
                          @click="$router.push('/user/new')"
                         block
                          >
                  Create Account
                  </v-btn>
              </v-layout>


                <v-layout row>

                  <v-flex md3>

                    <h2 class="text-xs-left pl-4 pt-4">
                      
                    </h2>

                    <div class="text-xs-left pl-3 pb-4">
                    <v-btn v-if="$store.state.user.logged_in == true"
                            color="primary"
                            dark
                            outlined
                            href="https://diffgram.readme.io/docs/billing-intro"
                            target="_blank">
                      Ordering Help
                      <v-icon right>mdi-book</v-icon>
                    </v-btn>
                    </div>

                  </v-flex>


                  <v-flex md3 class="text-right pa-4">

                    <v-btn v-if="$store.state.user.logged_in == true"
                           color="green"
                           dark
                           @click="$router.push('/order?name=Explorer')"
                           >
                    Order Explorer
                    </v-btn>

                  </v-flex>

                  <v-flex md3 class="text-right pa-4">

                    <v-btn v-if="$store.state.user.logged_in == true"
                           color="teal"
                           dark
                           @click="$router.push('/order?name=Teams')"
                           >
                    Order Teams
                    </v-btn>
                                       


                  </v-flex>

                </v-layout>


              <!--

              <v-layout row>


                  <v-flex md2>

                    <h2 class="text-xs-left pl-4 pt-4">
                      Import / Export
                    </h2>
                    <h3 class="text-xs-left pl-4">
                      
                    </h3>

                  </v-flex>

                  <v-flex md2>
                    <img class="pl-4"
                         height="120px"
                         src="https://storage.googleapis.com/diffgram-002/public/marketing/diffgram_dot_com/alien_ship.png">


                   </v-flex>

                  <v-flex xs8>

                    <h2 class="blue--text   text-center pl-4 pt-4 pr-4">
                     Import images and video through our web interface or SDK.
                    </h2>
                    <h3 class="text-center pl-4 pr-4">
                      Export annotations data, trained models, and predictions
                    </h3>

                  </v-flex>

                </v-layout>

                  <v-layout row>

                    <v-flex md3>

                      <h2 class="text-xs-left pl-4 pt-4">
                        Video frame Limit
                      </h2>
                      <h3 class="text-xs-left pl-4">
                        Per video
                      </h3>

                     </v-flex>

                    <v-flex md3>

                      <h2 class="text-right pa-4">
                        256
                      </h2>

                    </v-flex>

                    <v-flex md3>

                      <h2 class="green--text text-right pa-4">
                        512
                      </h2>

                    </v-flex>

                    <v-flex md3>

                      <h2 class="teal--text text-right pa-4">
                        1028
                      </h2>

                    </v-flex>

                  </v-layout>

                    -->


  
        <v-card elevation-1 color="primary">
          <h1 class="white--text text-center pa-4">
             For Large Teams:
            <router-link class="white--text"
                         to="/enterprise"> Diffgram Enterprise.</router-link>
          </h1>

        </v-card>

          <h2 class="pa-2"> 
            Full Time Students may <a href="https://docs.google.com/forms/d/e/1FAIpQLSdN_r59LF7BnyjMCamiFKEV-oo2Ry-cQKOXqm1UqRKAdi1Jeg/viewform"
                      target="_blank"> request 3 years</a>
            of the Explorer plan at no cost.
          </h2>

          <sub class="pa-4"> As of November 25th, 2019. Terms and conditions apply.
      See <a @click="$router.push('/policies')"> policies </a>
      for more info. </sub>

            </v-card>
          </v-flex>
        </v-layout>
    </v-container>

  </div>
</template>

<script lang="ts">

import axios from 'axios';

import Vue from "vue"; export default Vue.extend( {
  name: 'pricing',
  data () {
    return {
      
    }
  },
  created() {

  },
  methods: {

  }
}
) </script>

