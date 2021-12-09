<template>
<div>

  <v-layout>

    <v-menu v-model="why_menu"
          offset-y
          open-on-hover
          attach
          >

      <template v-slot:activator="{ on }">
        <v-btn v-on="on"
               color="primary"
                text
               style="text-transform: none !important;"
               >
           Why
        </v-btn>
      </template>

      <v-card>
        <v-layout column>

          <v-flex>
            <ahref_seo_optimal href="/about">
              <v-btn color="primary"
                     text
                     style="text-transform: none !important;"
                     >
                <v-icon left> mdi-compass-rose</v-icon>
                Our Why
              </v-btn>
            </ahref_seo_optimal>
          </v-flex>

          <v-flex>

            <ahref_seo_optimal href="/your_next_step">
              <v-btn color="primary"
                     text style="text-transform: none !important;">
                <v-icon left> mdi-fast-forward</v-icon>
                Your Next Step
              </v-btn>
            </ahref_seo_optimal>

          </v-flex>

          
          <v-flex>

            <ahref_seo_optimal href="/single_application">
              <v-btn color="primary"
                     text style="text-transform: none !important;">
                <v-icon left> mdi-circle-slice-8</v-icon>
                Single Application
              </v-btn>
            </ahref_seo_optimal>

          </v-flex>        


          <v-flex>

            <ahref_seo_optimal href="/open_source">
              <v-btn color="primary"
                     text style="text-transform: none !important;">
                <v-icon left> mdi-github</v-icon>
                 Open Source
              </v-btn>
            </ahref_seo_optimal>

          </v-flex>

          <v-flex>

            <ahref_seo_optimal href="/engineering_led_support">
              <v-btn color="primary"
                     text style="text-transform: none !important;">
                <v-icon left> mdi-face-agent</v-icon>
                 Engineering Led Support
              </v-btn>
            </ahref_seo_optimal>

          </v-flex>
         
        </v-layout>
      </v-card>    
    </v-menu>



    <v-menu v-model="product"
            offset-y
            open-on-hover
            attach
            >

   
      <template v-slot:activator="{ on }">
        <v-btn v-on="on"
               color="primary"
              text style="text-transform: none !important;">
           Product
        </v-btn>
      </template>

      <v-card>

        <v-layout column>


          <v-flex>

            <ahref_seo_optimal href="/software">
              <v-btn color="primary"
                    text style="text-transform: none !important;">
                <v-icon left> mdi-image-filter-hdr</v-icon>
                Software Overview
              </v-btn>
            </ahref_seo_optimal>

          </v-flex>

          
          <v-divider></v-divider>

          <div class="pa-2">Select Benefits:</div>

          <v-flex>

            <ahref_seo_optimal href="/ease_of_use">
              <v-btn color="primary"
                    text style="text-transform: none !important;">
                <v-icon left> mdi-check</v-icon>
                Ease of Use
              </v-btn>
            </ahref_seo_optimal>

          </v-flex>


          <v-flex>

            <ahref_seo_optimal href="/white_label_customization">
              <v-btn color="primary"
                    text style="text-transform: none !important;">
                <v-icon left> mdi-puzzle-edit</v-icon>
                White-label Customization
              </v-btn>
            </ahref_seo_optimal>

          </v-flex>

         
          <v-flex>

            <ahref_seo_optimal href="/automation">
              <v-btn color="primary"
                    text style="text-transform: none !important;">
                <v-icon left> mdi-creation</v-icon>
                Automation
              </v-btn>
            </ahref_seo_optimal>

          </v-flex>


          <!--
          <v-flex>

            <ahref_seo_optimal href="/stream-to-training-pytorch-tensorflow">
              <v-btn color="primary"
                    text style="text-transform: none !important;">
                <v-icon left> mdi-flash</v-icon>
                Stream to Training
              </v-btn>
            </ahref_seo_optimal>

          </v-flex>
          -->

          <v-flex>

            <ahref_seo_optimal href="/human_tasks_workflow">
              <v-btn color="primary"
                    text style="text-transform: none !important;">
                <v-icon left>mdi-human-greeting</v-icon>
                Human Tasks Workflow
              </v-btn>
            </ahref_seo_optimal>

          </v-flex>

          <!--
          <v-flex>

            <ahref_seo_optimal href="/streaming">
              <v-btn color="primary"
                    text style="text-transform: none !important;">
                <v-icon left> mdi-compass</v-icon>
                Query & Explore
              </v-btn>
            </ahref_seo_optimal>

          </v-flex>

          -->
          <v-flex>

            <ahref_seo_optimal href="/secure">
              <v-btn color="primary"
                     text style="text-transform: none !important;">
                <v-icon left> mdi-lock</v-icon>
                Security & Privacy
              </v-btn>           
            </ahref_seo_optimal>

          </v-flex>
          

          <v-divider></v-divider>
        

          <div class="pa-2">Select Deep Dives:</div>

          <v-flex>

          <ahref_seo_optimal href="/segmentation">
            <v-btn color="primary"
                  text style="text-transform: none !important;">
              <v-icon left>mdi-shape-polygon-plus</v-icon>
              Segmentation
            </v-btn>
          </ahref_seo_optimal>

          </v-flex>

          <v-flex>

          <ahref_seo_optimal href="/video">
            <v-btn color="primary"
                  text style="text-transform: none !important;">
              <v-icon left>mdi-video</v-icon>
              Video
            </v-btn>
          </ahref_seo_optimal>

          </v-flex>

          <v-flex>

            <ahref_seo_optimal href="/versioning">
              <v-btn color="primary"
                    text style="text-transform: none !important;">
                <v-icon left> mdi-source-branch</v-icon>
                Versioning
              </v-btn>
            </ahref_seo_optimal>

          </v-flex>



          <!-- Hide while pro network concept is a WIP --> 
          <!--
          <v-flex>

          <ahref_seo_optimal href="/data_platform">
            <v-btn color="primary"
                  text style="text-transform: none !important;">
              <v-icon left>mdi-professional-hexagon</v-icon>
              Hire Pros On Demand
            </v-btn>
          </ahref_seo_optimal>

          </v-flex>

          
          <v-flex>

          <ahref_seo_optimal href="/pro">
            <v-btn color="primary"
                  text style="text-transform: none !important;">
              <v-icon left>mdi-professional-hexagon</v-icon>
              Sign Up to Be a Pro
            </v-btn>
          </ahref_seo_optimal>

          </v-flex>
          -->

          <v-divider> </v-divider>

        </v-layout>
      </v-card>
    </v-menu>

    <v-menu v-model="enterprise"
            offset-y
            open-on-hover
            attach
            >

   
      <template v-slot:activator="{ on }">
        <v-btn v-on="on"
               color="primary"
              text style="text-transform: none !important;">
           Enterprise
        </v-btn>
      </template>

      <v-card>

        <v-layout column>

          <v-flex>

        <ahref_seo_optimal href="/enterprise">
            <v-btn color="primary"
                  text style="text-transform: none !important;">
              <v-icon left>mdi-domain</v-icon>
              Enterprise
            </v-btn>
        </ahref_seo_optimal>

          </v-flex>

          <v-flex>

          <ahref_seo_optimal href="/enterprise/hub">
            <v-btn color="primary"
                  text style="text-transform: none !important;">
              <v-icon left>mdi-earth</v-icon>
              Enterprise Hub
            </v-btn>
          </ahref_seo_optimal>

          </v-flex>

          <v-divider> </v-divider>

        </v-layout>
      </v-card>
    </v-menu>

    <!-- Want to rethink how we do this comparison -->

    <!--
    <v-menu v-model="compare"
            offset-y
            open-on-hover
            attach
            >

   
      <template v-slot:activator="{ on }">
        <v-btn v-on="on"
               color="primary"
              text style="text-transform: none !important;">
           Compare
        </v-btn>
      </template>

      <v-card>

        <v-layout column>

          <v-flex>

        <ahref_seo_optimal href="/diffgram-vs-sagemaker">
            <v-btn color="primary"
                  text style="text-transform: none !important;">
              <v-icon left>mdi-aws</v-icon>
              Diffgram and Amazon Sagemaker Groundtruth
            </v-btn>
        </ahref_seo_optimal>

          </v-flex>

          <v-flex>

          <ahref_seo_optimal href="/diffgram-vs-labelbox">
            <v-btn color="primary"
                  text style="text-transform: none !important;">
              <v-icon left>mdi-ab-testing</v-icon>
              Diffgram vs Labelbox
            </v-btn>
          </ahref_seo_optimal>

          </v-flex>

          <v-divider> </v-divider>

        </v-layout>
      </v-card>
    </v-menu>
    -->

    <!-- Solutions section is a work in progress-->
    <!--
    <v-menu v-model="solutions"
            offset-y
            open-on-hover
            attach
            >

   
      <template v-slot:activator="{ on }">
        <v-btn v-on="on"
               color="primary"
               v-model="solutions"
              text style="text-transform: none !important;">
           Solutions
        </v-btn>
      </template>

      <v-card>

        <v-layout column>

          <v-flex>

            <v-btn color="primary"
                  text style="text-transform: none !important;"
                   @click="$router.push('/medical')">
              <v-icon left>mdi-medical-bag</v-icon>
              Medical & Healthcare
            </v-btn>

          </v-flex>

          <v-flex>

            <v-btn color="primary"
                  text style="text-transform: none !important;"
                   @click="$router.push('/video')">
              <v-icon left>mdi-video</v-icon>
              Retail
            </v-btn>

          </v-flex>

          <v-flex>

            <v-btn color="primary"
                  text style="text-transform: none !important;"
                   @click="$router.push('/software')">
              <v-icon left> mdi-database</v-icon>
              Something
            </v-btn>


          </v-flex>

          <v-divider> </v-divider>

        </v-layout>
      </v-card>
    </v-menu>
      -->


    <v-spacer> </v-spacer>


    

    <ahref_seo_optimal href="/install">
      <v-btn color="primary"
            text style="text-transform: none !important;"
             class="hidden-sm-and-down"
             v-if="$store.state.user.logged_in != true"
            >
        Install
      </v-btn>
    </ahref_seo_optimal>

    <ahref_seo_optimal href="https://diffgram.readme.io/docs/introduction-to-diffgram"
                       target="_blank">
      <v-btn color="primary"
            text style="text-transform: none !important;">
        Docs
        <v-icon right> mdi-open-in-new </v-icon>
      </v-btn>
    </ahref_seo_optimal>

    <!--
    <menu_company>

    </menu_company>
    -->

    <!--
    <menu_learn>

    </menu_learn>
    -->

  </v-layout>
</div>

</template>

<script lang="ts">


import menu_company from './menu_company'
import menu_learn from './menu_learn'


import Vue from "vue"; export default Vue.extend( {
  name: 'menu_marketing',

  components: {
    menu_company: menu_company,
    menu_learn: menu_learn
  },

  data() {
    return {
      solutions: false,
      compare: false,
      product: false,
      enterprise: false,
      why_menu: false

    }
  },
  computed: {

  }
}
) </script>
