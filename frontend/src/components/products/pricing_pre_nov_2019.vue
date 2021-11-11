<template>
  <div id="pricing">
    <v-layout justify-space-around>

    <v-flex md9 lg8>

     <v-container>
      <v-card>

        <v-card elevation-1 color="primary">
          <h1 class="white--text text-center pt-4">
            Build deep learning systems
          </h1>
          <h2 class="grey--text text--lighten-4 text-center pa-4">
            Practical and affordable way to build deep learning systems at scale
          </h2>
        </v-card>

          <v-layout column>
            <v-flex md8 lg8>
              <v-card elevation-2 class="ma-2">

                <!-- Using datatable for more complex layouts was just confusing things -->

                <!-- Header -->
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
                     Full access to try it
                    </h3>

                  </v-flex>

                  <v-flex md3>

                    <h2 class="green--text  text-right pl-4 pt-4">
                      Explorer
                    </h2>
                    <h3 class="green--text text--darken-1 text-right pl-4 pb-4">
                     For individual professionals
                    </h3>

                  </v-flex>

                  <v-flex md3>

                    <h2 class="teal--text text-right pl-4 pt-4 pr-4">
                      Teams
                    </h2>
                    <h3 class="teal--text text--darken-1 text-right pl-4 pb-4 pr-4">
                     Shipping production products
                    </h3>

                  </v-flex>

                </v-layout>


                <v-layout row>


                  <v-flex md2>

                    <h2 class="text-xs-left pl-4 pt-4">
                      Annotation
                    </h2>
                    <h3 class="text-xs-left pl-4">
                      
                    </h3>

                  </v-flex>

                  <v-flex md2>
                    <img class="pl-4"
                         height="120px"
                         src="https://storage.googleapis.com/diffgram-002/public/marketing/diffgram_dot_com/paint.png">


                   </v-flex>

                  <v-flex xs8>

                    <h2 class="blue--text  text-center pl-4 pt-4 pr-4">
                     Everything you need to annotate deep learning data
                    </h2>
                    <h3 class="text-center pl-4 pr-4">
                      Tags, Boxes, and Polygons. Keypoints, Cuboids and 3D Sensor Fusion coming soon
                    </h3>

                  </v-flex>

                </v-layout>

                <v-layout row>

                  <v-flex md2>

                    <h2 class="text-xs-left pl-4 pt-4">
                      Train & Deploy
                    </h2>
                    <h3 class="text-xs-left pl-4">
                      
                    </h3>

                  </v-flex>

                  <v-flex md2>
                    <img class="pl-4"
                         height="120px"
                         src="https://storage.googleapis.com/diffgram-002/public/marketing/diffgram_dot_com/home/big_mind.png">

                   </v-flex>

                  <v-flex xs8>

                    <h2 class="blue--text text-center pl-4 pt-4 pr-4">
                     Get your system deployed
                    </h2>
                    <h3 class="text-center pl-4 pr-4">
                     Train and deploy your system with a few lines of code
                    </h3>

                  </v-flex>

                </v-layout>


                <v-layout row>

                  <v-flex md2>

                    <h2 class="text-xs-left pl-4 pt-4">
                      Scale Quality 
                    </h2>
                    <h3 class="text-xs-left pl-4">
                      
                    </h3>

                  </v-flex>

                  <v-flex md2>
                    <img class="pl-4"
                         height="120px"
                         src="https://storage.googleapis.com/diffgram-002/public/marketing/diffgram_dot_com/home/tasks_person.png">

                   </v-flex>

                  <v-flex xs8>

                    <h2 class="blue--text  text-center pl-4 pt-4 pr-4">
                     Scale your results with our task management system
                    </h2>
                    <h3 class="text-center pl-4 pr-4">
                     Quality assurance flows, including Guides, Exams, and Credentials 
                    </h3>

                  </v-flex>

                </v-layout>



                <v-layout row>


                  <v-flex xs4>

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
                      $19
                    </h2>

                  </v-flex>

                  <v-flex md3>

                    <h2 class="teal--text text-right pa-4">
                      $144
                    </h2>

                  </v-flex>

                </v-layout>

                <!-- ROW 2 -->

                <v-layout row>


                  <v-flex xs4>

                    <v-tooltip right>
                      <span v-on="on">
                        <h2 class="text-xs-left pl-4 pt-4">
                            Cost Per 1,000 Instances
                        </h2>
                      </span>
                        ie. a box, polygon, cuboid.
                    </v-tooltip>
                    
                    <h3 class="text-xs-left pl-4">
                      First 100 free monthly
                    </h3>
                  </v-flex>

                  <v-flex md3>


                  </v-flex>

                  <v-flex md3>

                    <h2 class="green--text text-right pa-4">
                      $9
                    </h2>

                  </v-flex>

                  <v-flex md3>

                    <h2 class="teal--text text-right pa-4">
                      $9
                    </h2>

                  </v-flex>

                </v-layout>


                <!-- ROW 3 -->

                <v-layout row>


                  <v-flex xs4>
                    <h2 class="text-xs-left pl-4 pt-4">
                      Cost Per Hour of Training
                    </h2>
                    <h3 class="text-xs-left pl-4">
                      First hour free monthly
                    </h3>
                   </v-flex>

                  <v-flex md3>


                  </v-flex>

                  <v-flex md3>

                    <h2 class="green--text text-right pa-4">
                      $6
                    </h2>

                  </v-flex>

                  <v-flex md3>

                    <h2 class="teal--text text-right pa-4">
                      $6
                    </h2>

                  </v-flex>

                </v-layout>

                <!-- TODO line break here? -->

                <v-layout row>


                  <v-flex xs4>

                    <h2 class="text-xs-left pl-4 pt-4">
                      Order
                    </h2>

                    <div class="text-xs-left pl-3 pb-4">
                    <v-btn color="primary"
                            dark
                            outlined
                            href=""
                            target="_blank">
                      Ordering Help
                      <v-icon right>mdi-book</v-icon>
                    </v-btn>
                    </div>

                  </v-flex>

                  <v-flex md3 class="text-right pa-4">

                    <!-- If not logged in? -->
                    <v-btn v-if="$store.state.user.logged_in != true"
                           color="primary"
                           @click="$router.push('/user/new')"
                           >
                    Create Account
                    </v-btn>

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



              </v-card>
            </v-flex>
          </v-layout>



        </v-card>


        <v-card>

        <v-card elevation-1 color="primary">

        </v-card>

          <v-layout column>
            <v-flex>
              <v-card elevation-2 class="ma-2">

                <!-- Using datatable for more complex layouts was just confusing things -->

                <!-- Header -->
                <v-layout row>


                  <v-flex md3>
                    <h2 class="text-xs-left pa-4">
                      
                    </h2>
                   </v-flex>

                  <v-flex md3>

                    <h2 class="text-right pa-4">
                    Free
                    </h2>
                  </v-flex>

                  <v-flex md3>

                    <h2 class="green--text text-right pa-4">
                      Explorer
                    </h2>

                  </v-flex>

                  <v-flex md3>

                    <h2 class="teal--text text-right pa-4">
                      Teams
                    </h2>

                  </v-flex>

                </v-layout>


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

                  <v-flex md2>

                    <h2 class="text-xs-left pl-4 pt-4">
                      Outsourcing
                    </h2>
                    <h3 class="text-xs-left pl-4">
                      
                    </h3>

                  </v-flex>

                  <v-flex md2>
                    <img class="pl-4"
                         height="120px"
                         src="https://storage.googleapis.com/diffgram-002/public/marketing/diffgram_dot_com/knight.png">

                   </v-flex>

                  <v-flex xs8>

                    <h2 class="blue--text   text-center pl-4 pt-4 pr-4">
                      Fully integrated outsourcing
                    </h2>
                    <h3 class="text-center pl-4 pr-4">
                      Get high quality human annotations
                    </h3>

                  </v-flex>

                </v-layout>


                <v-layout row>

                  <v-flex md2>

                    <h2 class="text-xs-left pl-4 pt-4">
                      Source control
                    </h2>
                    <h3 class="text-xs-left pl-4">
                      
                    </h3>

                  </v-flex>

                  <v-flex md2>
                    <img class="pl-4"
                         height="120px"
                         src="https://storage.googleapis.com/diffgram-002/public/marketing/diffgram_dot_com/mountain.png">

                   </v-flex>

                  <v-flex xs8>

                    <h2 class="blue--text   text-center pl-4 pt-4 pr-4">
                      System of record for your data.
                    </h2>
                    <h3 class="text-center pl-4 pr-4">
                     View history, visually see file differentials, and export only changes for validation
                    </h3>

                  </v-flex>

                </v-layout>


                  <v-card color="white lighten-5"
                        elevation-10>
                  <v-layout row>

                    <v-flex xs4>

                      <h2 class="text-xs-left pl-4 pt-4">
                        Instance Limit
                      </h2>
                      <h3 class="text-xs-left pl-4 pb-4">
                        Per project
                      </h3>

                     </v-flex>

                    <v-flex md3>

                      <h2 class="text-right pa-4">
                        100
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
                </v-card>


                <v-layout row>


                  <v-flex xs4>

                    <h2 class="text-xs-left pl-4 pt-4">
                      Project Limit
                    </h2>
                    <h3 class="text-xs-left pl-4">
     
                    </h3>

                   </v-flex>

                  <v-flex md3>

                    <h2 class="text-right pa-4">
                      3
                    </h2>

                  </v-flex>

                  <v-flex md3>

                    <h2 class="green--text text-right pa-4">
                      10
                    </h2>

                  </v-flex>

                  <v-flex md3>

                    <h2 class="teal--text text-right pa-4">
                      30
                    </h2>

                  </v-flex>

                </v-layout>


                <v-layout row>

                  <v-flex xs4>

                    <h2 class="text-xs-left pl-4 pt-4">
                      Users
                    </h2>
                    <h3 class="text-xs-left pl-4">
                      Per project
                    </h3>

                   </v-flex>

                  <v-flex md3>

                    <h2 class="text-right pa-4">
                      3
                    </h2>

                  </v-flex>

                  <v-flex md3>

                    <h2 class="green--text text-right pa-4">
                      3
                    </h2>

                  </v-flex>

                  <v-flex md3>

                    <h2 class="teal--text text-right pa-4">
                      30
                    </h2>

                  </v-flex>

                </v-layout>

                  
                  <v-layout row>

                    <v-flex xs4>

                      <h2 class="text-xs-left pl-4 pt-4">
                        Video frame Limit
                      </h2>
                      <h3 class="text-xs-left pl-4">
                        Per video
                      </h3>

                     </v-flex>

                    <v-flex md3>

                      <h2 class="text-right pa-4">
                        310
                      </h2>

                    </v-flex>

                    <v-flex md3>

                      <h2 class="green--text text-right pa-4">
                        520
                      </h2>

                    </v-flex>

                    <v-flex md3>

                      <h2 class="teal--text text-right pa-4">
                        520
                      </h2>

                    </v-flex>

                  </v-layout>




                <v-layout row>
                    <v-flex xs4>

                      <h2 class="text-xs-left pl-4 pt-4">
                        Support
                      </h2>
                      <h3 class="text-xs-left pl-4">
                      
                      </h3>

                     </v-flex>

                    <v-flex xs6>

                      <h2 class="green--text text-right pa-4">
                        Community
                      </h2>

                    </v-flex>

                    <v-flex md3>

                      <h2 class="teal--text text-right pa-4">
                        Email & Chat
                      </h2>

                    </v-flex>
                </v-layout>
 




              <v-layout row>

                  <v-flex xs4>

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

                <v-layout row>

                  <v-flex xs4>

                    <h2 class="text-xs-left pl-4 pt-4">
                      Central User Management
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

                

              </v-card>
            </v-flex>
          </v-layout>

        <v-card elevation-1 color="primary">
          <h1 class="white--text text-center pa-4">
             For large companies:
            <router-link class="white--text"
                         to="/enterprise"> Diffgram Enterprise.</router-link>
          </h1>

        </v-card>

        </v-card>

    </v-container>



          <sub class="pa-4"> As of March 20th, 2019. Terms and conditions apply.
      See <a @click="$router.push('/policies')"> policies </a>
      for more info. </sub>

      
      </v-flex>
    </v-layout>

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

