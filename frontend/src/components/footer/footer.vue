<template>
  <div>

    <v-footer height="auto"
              app
              class="hidden-sm-and-down"
              color="primary lighten-1">

      <v-layout justify-center
                row
                wrap>


        <v-btn color="white"
               text
               href="https://docs.google.com/forms/d/e/1FAIpQLSerK--qRwdjQPu_55zErFaBtBPcq90YUFlHHCCGFOmmaIpEGg/viewform"
               target="_blank"
               >
          Research Access
        </v-btn>

        <v-btn color="white"
               text
               href="https://angel.co/company/diffgram/jobs"
               target="_blank">
          Join Us
        </v-btn>

        <v-btn color="white"
               text
               href="https://docs.google.com/forms/d/e/1FAIpQLSeT4b5YkQF00XCSTwa_6Nx0NxSEPTN_a02OUJ5oOm81kCyzkg/viewform?fbzx=3737830607863843501"
               target="_blank">
          Partner With Us
        </v-btn>
        

        <v-btn color="white"
               text
               @click="$router.push('/policies')">
          Policies
        </v-btn>

              
        <tooltip_button
            href="https://diffgram.readme.io/docs"
            color="white"
            icon="help"
            tooltip_message="Help"
            :icon_style="true">
        </tooltip_button>
        
         <tooltip_button
            href="https://www.linkedin.com/company/diffgram"
            color="white"
            icon="mdi-linkedin"
            tooltip_message="LinkedIn"
            :icon_style="true">
        </tooltip_button>

        <tooltip_button
            href="https://medium.com/diffgram"
            color="white"
            icon="mdi-bullhorn"
            tooltip_message="Blog"
            :icon_style="true">
        </tooltip_button>

        <tooltip_button
            href="https://github.com/diffgram/diffgram"
            color="white"
            icon="mdi-github"
            tooltip_message="Github"
            :icon_style="true">
        </tooltip_button>



        <!-- WIP -->
        <!--
  <v-btn color="white"
         text
         @click="route_join_us">
    Contact Us
  </v-btn>
  -->

      </v-layout>

    </v-footer>


  </div>

</template>

<script lang="ts">


import Vue from "vue"; export default Vue.extend( {
  name: 'footer_main',
  components: {

  },
  data() {
    return {

    }
  },
  computed: {

  },
  methods: {

    route_join_us() {
      this.$router.push("/join")
    },

    route_org_new() {
      this.$router.push("/org/new")
    }

  }
}
) </script>
