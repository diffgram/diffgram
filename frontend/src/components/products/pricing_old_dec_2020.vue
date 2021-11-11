<template>
  <div id="pricing">

 <v-card>
  <v-container>

<!--
    There's a lot of custom formatting choices here.

    Because of that the data table thing doesn't really work

    This actually appears to be somewhat reasonable , main known issues

  -> requires fixed min width for column alignment
  -> a little fiddly to know where to jump to
  -> we current use icons that have same colors as background to maintain
  spacing, ie each thing always has at least one spacing item.

    -->

  <v-row :class="row_padding" style="max-width: 1100px" center>

    <v-col cols="5"
           style="min-width: 350px">

      <v-card elevation="0">


        <!-- spacer for plan info -->
        <div style="height: 160px">

        </div>

   
        <v-container>

          <div :style="sub_header_height">
            <v-card-title class="pl-1">  Core </v-card-title>
          </div>

          <v-row :class="row_padding">
              Users
          </v-row>

          <v-row :class="row_padding">
              Instance Label Usage
          </v-row>

          <v-row :class="row_padding">
            <div>
            <a target="_blank"
               href="https://diffgram.readme.io/docs/project">
              Role-based</a> access control
            </div>
          </v-row>

          <v-row :class="row_padding">
            Box, Polygons, Lines, Keypoints, Classification
          </v-row>

          <v-row :class="row_padding">
            Segmentation
          </v-row>

          <v-row :class="row_padding">
            <a target="_blank"
               href="https://diffgram.readme.io/docs/attributes-1">
              Attributes </a> : Nested, Multiple Select, Free Text
          </v-row>

          <v-row :class="row_padding">
            Dataset Creator
          </v-row>

          <v-row :class="row_padding">
            <a target="_blank"
               href="https://diffgram.readme.io/docs/video-introduction">
              Video </a>
          </v-row>

        </v-container>


        <v-container>

          <div :style="sub_header_height">
            <v-card-title class="pl-1">  Quality and Performance </v-card-title>
          </div>

          <v-row :class="row_padding">
              Review Tasks
          </v-row>

          <v-row :class="row_padding">
              Exams (Gold Standard)
          </v-row>

          <v-row :class="row_padding">
             Performance Tracking
          </v-row>

          <v-row :class="row_padding">
             Consensus
          </v-row>

        </v-container>


        <v-container>
          
          <div :style="sub_header_height">
            <v-card-title class="pl-1">  Integrations and Extensions </v-card-title>
          </div>

          <v-row :class="row_padding">
            <a target="_blank"
               href="https://github.com/diffgram/diffgram">
             Python SDK </a> 
          </v-row>

          <v-row :class="row_padding">
             <a target="_blank"
               href="https://diffgram.readme.io/reference">
              API Access </a>
          </v-row>

        </v-container>

        <v-container>
          
          <div :style="sub_header_height">
            <v-card-title class="pl-1">  Automation </v-card-title>
          </div>

          <v-row :class="row_padding">
            <div>
              Model Based
            <a target="_blank"
               href="https://diffgram.readme.io/docs/importing-instances-walkthrough">
              Pre-Labeling  </a>
            </div>

          </v-row>

          <v-row :class="row_padding">
              Near real time human in the loop
          </v-row>

          <v-row :class="row_padding">
             Active Learning
          </v-row>

        </v-container>

        <v-container>

          <div :style="sub_header_height">
            <v-card-title class="pl-1">  Support </v-card-title>
          </div>

          <v-row :class="row_padding">
              Email & Chat
          </v-row>

          <v-row :class="row_padding">
              Live Video Training
          </v-row>

          <v-row :class="row_padding">
              Success Manager
          </v-row>
        </v-container>


        <v-container>

          <div :style="sub_header_height">
            <v-card-title class="pl-1">  Security and Admin </v-card-title>
          </div>

          <v-row :class="row_padding">
              Single Sign On
          </v-row>

          <v-row :class="row_padding">
              Service Level Objectives (SLO)
          </v-row>

          <v-row :class="row_padding">
              Custom Terms
          </v-row>

          <v-row :class="row_padding">
             Private Deploy (Customer Controls Data)
          </v-row>

        </v-container>




      </v-card>

    </v-col>



    <!-- Explorer -->
    <v-col cols="2" style="min-width: 170px">

      <v-card elevation="0" color="grey lighten-5">

        <div style="height: 160px">

          <v-row justify="center">
            <v-card-title> Explorer </v-card-title>

            <div class="pa-4" style="height: 100px">
              Free to evaluate core features. Free for students.
            </div>

            <v-btn v-if="$store.state.user.logged_in != true"
                        color="primary"
                        @click="$router.push('/user/new')"
                          >
                Try Now
            </v-btn>

          </v-row>
        </div>


        <!-- CORE -->
        <v-container>

          <div :style="sub_header_height">
            <!-- Spacer to match left column--> 
          </div>

          <v-row :class="row_padding_icon" justify="center">
              Evaluation Team
          </v-row>

          <v-row :class="row_padding_icon" justify="center">
              Limited
          </v-row>


          <div v-for="(n, index) in 6">
            <v-row :class="row_padding_icon" justify="center">
      
              <tooltip_icon
                :icon="tooltip_icon"
                :color="color">
              </tooltip_icon>
     
            </v-row>
          </div>
          
         </v-container>


        <!-- Quality and Performance -->

        <v-container>

          <div :style="sub_header_height">
            <!-- Spacer to match left column--> 
          </div>

          <!-- If we want to have a custom message color etc.
            we can either pull it out of the loop
            or change the loop to use a list of items -->

          <div v-for="(n, index) in 3">
            <v-row :class="row_padding_icon" justify="center">
      
              <tooltip_icon
                :icon="tooltip_icon"
                :color="color">
              </tooltip_icon>
     
            </v-row>
          </div>

          <v-row :class="row_padding_icon" justify="center">
            <tooltip_icon
                :icon="tooltip_icon"
                color="grey lighten-5">
            </tooltip_icon>
          </v-row>

        </v-container>


        <!-- Integrations Explorer / Free -->

        <v-container>

          <div :style="sub_header_height">
            <!-- Spacer to match left column--> 
          </div>

          <div v-for="(n, index) in 2">
            <v-row :class="row_padding_icon" justify="center">
      
              <tooltip_icon
                :icon="tooltip_icon"
                :color="color">
              </tooltip_icon>
     
            </v-row>
          </div>

        </v-container>


        <!-- Automation  for explorer-->

        <v-container>

          <div :style="sub_header_height">
            <!-- Spacer to match left column--> 
          </div>

          <!-- Restrict automation for  white means None..-->
          <div v-for="(n, index) in 3">
            <v-row :class="row_padding_icon" justify="center">

              <tooltip_icon
                :icon="tooltip_icon"
                color="grey lighten-5">
              </tooltip_icon>
     
            </v-row>
          </div>

        </v-container>

        <!-- Support -->

        <v-container>

          <div :style="sub_header_height">
            <!-- Spacer to match left column--> 
          </div>

          <v-row :class="row_padding_icon" justify="center">
            <tooltip_icon
              :icon="tooltip_icon"
              :color="color">
            </tooltip_icon>
          </v-row>

          <div v-for="(n, index) in 2">
            <v-row :class="row_padding_icon" justify="center">
      
               <tooltip_icon
                :icon="tooltip_icon"
                color="grey lighten-5">
              </tooltip_icon>

            </v-row>
          </div>

        </v-container>


        <!-- Security and admin for explorer -->

        <v-container>

          <div :style="sub_header_height">
            <!-- Spacer to match left column--> 
          </div>

          <div v-for="(n, index) in 4">
            <v-row :class="row_padding_icon" justify="center">
      
              <tooltip_icon
                :icon="tooltip_icon"
                color="grey lighten-5">
              </tooltip_icon>
     
            </v-row>
          </div>

        </v-container>




      </v-card>

    </v-col>










    <!-- TEAMS -->

    <v-col cols="2" style="min-width: 180px">

      <v-card elevation="0">

        <div style="height: 160px">
          <v-row justify="center">
            <v-card-title> Teams </v-card-title>

            <div class="pa-4" style="height: 100px">
              Developing, shipping & maintaining products
            </div>

            <v-btn v-if="$store.state.user.logged_in == true"
                            color="teal"
                            dark
                            @click="$router.push('/order?name=Teams')"
                            >
                    Order Teams
            </v-btn>

            
            <v-btn color="primary"
                    @click="$router.push('/enterprise/contact')"
                          >
                Contact Us
            </v-btn>

          </v-row>
        </div>


        <!-- Core for teams -->

        <v-container>

          <div :style="sub_header_height">
            <!-- Spacer to match left column--> 
          </div>

          <v-row :class="row_padding_icon" justify="center">
              Cost Per User
          </v-row>

          <v-row :class="row_padding_icon" justify="center">
              Unlimited
          </v-row>


          <div v-for="(n, index) in 5">
            <v-row :class="row_padding_icon" justify="center">
      
              <tooltip_icon
                :icon="tooltip_icon"
                :color="color">
              </tooltip_icon>
     
            </v-row>
          </div>

          <v-row :class="row_padding_icon" justify="center">
      
              <tooltip_icon
                tooltip_message="Up to 30 FPS & 2k"
                :icon="tooltip_icon"
                color="green">
              </tooltip_icon>
     
          </v-row>
          
         </v-container>


        <!-- Quality and Performance -->

        <v-container>

          <div :style="sub_header_height">
            <!-- Spacer to match left column--> 
          </div>

          <!-- If we want to have a custom message color etc.
            we can either pull it out of the loop
            or change the loop to use a list of items -->

          <div v-for="(n, index) in 4">
            <v-row :class="row_padding_icon" justify="center">
      
              <tooltip_icon
                :icon="tooltip_icon"
                :color="color">
              </tooltip_icon>
     
            </v-row>
          </div>

        </v-container>


        <!-- Integrations -->

        <v-container>

          <div :style="sub_header_height">
            <!-- Spacer to match left column--> 
          </div>

          <div v-for="(n, index) in 2">
            <v-row :class="row_padding_icon" justify="center">
      
              <tooltip_icon
                :icon="tooltip_icon"
                :color="color">
              </tooltip_icon>
     
            </v-row>
          </div>

        </v-container>


        <!-- Automation for teams -->

        <v-container>

          <div :style="sub_header_height">
            <!-- Spacer to match left column--> 
          </div>

          <div v-for="(n, index) in 3">
            <v-row :class="row_padding_icon" justify="center">
      
              <tooltip_icon
                :icon="tooltip_icon"
                color="green"
                tooltip_message="Available"
                            >
              </tooltip_icon>
     
            </v-row>
          </div>

        </v-container>

        <!-- Support -->

        <v-container>

          <div :style="sub_header_height">
            <!-- Spacer to match left column--> 
          </div>

          <div v-for="(n, index) in 3">
            <v-row :class="row_padding_icon" justify="center">
      
              <tooltip_icon
                :icon="tooltip_icon"
                :color="color">
              </tooltip_icon>
     
            </v-row>
          </div>

        </v-container>


        <!-- Security and admin for teams -->

        <v-container>

          <div :style="sub_header_height">
            <!-- Spacer to match left column--> 
          </div>

          <v-row :class="row_padding_icon" justify="center">
      
            <tooltip_icon
              :icon="tooltip_icon"
              color="white">
            </tooltip_icon>
     
          </v-row>


          <!-- SLA for teams -->
          <v-row :class="row_padding_icon" justify="center">
      
              <tooltip_icon
                :icon="tooltip_icon"
                color="primary">
              </tooltip_icon>
     
            </v-row>

          <!-- white means don't show it -->
          <div v-for="(n, index) in 1">
            <v-row :class="row_padding_icon" justify="center">
      
              <tooltip_icon
                :icon="tooltip_icon"
                color="white">
              </tooltip_icon>
     
            </v-row>
          </div>


          <v-row :class="row_padding_icon" justify="center">
      
            <tooltip_icon
              :icon="tooltip_icon"
              color="green"
              tooltip_message="Available"
                          >
            </tooltip_icon>
     
          </v-row>

        </v-container>


      </v-card>

    </v-col>


    <!-- END Teams -->


    <!-- ENTERPRISE  column -->

    <v-col cols="2" style="min-width: 170px">

      <v-card elevation="0" color="grey lighten-5">

        <div style="height: 160px">
          <v-row justify="center">
            <v-card-title> Enterprise </v-card-title>

            <div class="pa-4" style="height: 100px">
              Large distributed data science teams
            </div>


            <v-btn color="primary"
                    @click="$router.push('/enterprise/contact')"
                          >
                Contact Us
            </v-btn>

          </v-row>
        </div>

        <!-- core for enterprise -->
        <v-container>

          <div :style="sub_header_height">
            <!-- Spacer to match left column--> 
          </div>

          <v-row :class="row_padding_icon" justify="center">

              Flexible

          </v-row>

          <v-row :class="row_padding_icon" justify="center">
  
              Unlimited

          </v-row>

          <!-- Enterprise role message -->
          <v-row :class="row_padding_icon" justify="center">
            <tooltip_icon
                tooltip_message="Additional Org level scope"
                :icon="tooltip_icon"
                color="amber darken-1">
            </tooltip_icon>
          </v-row>

          <div v-for="(n, index) in 2">
            <v-row :class="row_padding_icon" justify="center">
      
              <tooltip_icon
                :icon="tooltip_icon"
                :color="color">
              </tooltip_icon>
     
            </v-row>
          </div>

          <!-- Multiple attributes -->
          <v-row :class="row_padding_icon" justify="center">
            <tooltip_icon
                tooltip_message="Multiple nested attributes"
                :icon="tooltip_icon"
                color="amber darken-1">
            </tooltip_icon>
          </v-row>

          <v-row :class="row_padding_icon" justify="center">
            <tooltip_icon
                :icon="tooltip_icon"
                color="primary">
            </tooltip_icon>
          </v-row>

          <!-- Video enterprise -->
          <v-row :class="row_padding_icon" justify="center">
      
              <tooltip_icon
                tooltip_message="Up to 120 FPS & 4k"
                :icon="tooltip_icon"
                color="amber darken-1">
              </tooltip_icon>
     
          </v-row>

         </v-container>


                <!-- Quality and Performance -->

        <v-container>

          <div :style="sub_header_height">
            <!-- Spacer to match left column--> 
          </div>

          <!-- If we want to have a custom message color etc.
            we can either pull it out of the loop
            or change the loop to use a list of items -->

          <div v-for="(n, index) in 4">
            <v-row :class="row_padding_icon" justify="center">
      
              <tooltip_icon
                :icon="tooltip_icon"
                :color="color">
              </tooltip_icon>
     
            </v-row>
          </div>

        </v-container>


        <!-- Integrations -->

        <v-container>

          <div :style="sub_header_height">
            <!-- Spacer to match left column--> 
          </div>

          <div v-for="(n, index) in 2">
            <v-row :class="row_padding_icon" justify="center">
      
              <tooltip_icon
                :icon="tooltip_icon"
                :color="color">
              </tooltip_icon>
     
            </v-row>
          </div>

        </v-container>


        <!-- Automation -->

        <v-container>

          <div :style="sub_header_height">
            <!-- Spacer to match left column--> 
          </div>

          <div v-for="(n, index) in 3">
            <v-row :class="row_padding_icon" justify="center">
      
              <tooltip_icon
                :icon="tooltip_icon"
                :color="color">
              </tooltip_icon>
     
            </v-row>
          </div>

        </v-container>

        <!-- Support  enterprise-->

        <v-container>

          <div :style="sub_header_height">
            <!-- Spacer to match left column--> 
          </div>

          <v-row :class="row_padding_icon" justify="center">    
            <tooltip_icon
              tooltip_message="1 Business Day Response"
              :icon="tooltip_icon"
              color="amber darken-1">
            </tooltip_icon>  
          </v-row>

          <v-row :class="row_padding_icon" justify="center">    
            <tooltip_icon
              tooltip_message="Live video support during business hours."
              :icon="tooltip_icon"
              color="amber darken-1">
            </tooltip_icon>  
          </v-row>

          <v-row :class="row_padding_icon" justify="center">    
            <tooltip_icon
              :icon="tooltip_icon"
              color="primary">
            </tooltip_icon>  
          </v-row>
        
        

        </v-container>


        <!-- Security and admin -->

        <v-container>

          <div :style="sub_header_height">
            <!-- Spacer to match left column--> 
          </div>

          <div v-for="(n, index) in 3">
            <v-row :class="row_padding_icon" justify="center">
      
              <tooltip_icon
                :icon="tooltip_icon"
                :color="color">
              </tooltip_icon>
     
            </v-row>
          </div>


          <v-row :class="row_padding_icon" justify="center">
      
            <tooltip_icon
              :icon="tooltip_icon"
              :color="color">
            </tooltip_icon>
     
          </v-row>

        </v-container>



      </v-card>
    

    </v-col>
  </v-row>

  </v-container>

  <v-container>

    <v-layout>

        <v-card class="hidden-sm-and-up" elevation="0">
          Please view on larger screen.
        </v-card>
        

        <!-- need word -only  too -->
          <v-card class="hidden-xs-only" elevation="0">
                  <!-- Header -->
           

              <v-layout>
                  <v-btn class="white--text"
                         color="green"
                         href="/why"
                         >
                    Why Choose Diffgram?
                  </v-btn>
              </v-layout>

            <!-- Hide while WIP -->
            <!--
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
              -->
  

          <h3 class="pa-2"> 
            Students may <a href="https://docs.google.com/forms/d/e/1FAIpQLSdN_r59LF7BnyjMCamiFKEV-oo2Ry-cQKOXqm1UqRKAdi1Jeg/viewform"
                      target="_blank"> request free access.</a>
          </h3>

          <sub class="pa-4"> As of April 29th, 2020. Terms and conditions apply.
      See <a @click="$router.push('/policies')"> policies </a>
      for more info. </sub>

            </v-card>
    
        </v-layout>
    </v-container>
   </v-card>

  </div>
</template>

<script lang="ts">


import Vue from "vue";

  export default Vue.extend( {
  name: 'pricing',
  data () {
    return {
      row_padding: "pl-4 pt-2 pb-2",
      row_padding_icon: "pt-2 pb-2",
      sub_header_height: "height: 60px",
      color: "primary",
      tooltip_icon: "mdi-check-circle"
    }
  },
  created() {

  },
  methods: {

  }
}
) </script>

<style>


</style>
