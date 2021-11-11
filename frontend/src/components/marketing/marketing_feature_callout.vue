<template>
<div >

<v-row >

  <v-col cols="4">
    <v-card elevation="0">

      <v-img
       src="https://storage.googleapis.com/diffgram_public/marketing/marketing_compatible_upload.svg"
       contain
             >
      </v-img>

      <v-card-title> Compatible with your Cloud and Frameworks. </v-card-title>

      <v-card-text>
      Compatible with your cloud data in AWS, Google, Azure, or Private cloud.
      Use frameworks like Tensorflow, Pytorch or commercial AutoML services.
      Connect your models for Pre Labeling.
      </v-card-text>
    </v-card>
  </v-col>

  <v-col cols="4">
    <v-card elevation="0" class="pt-4">

      <v-card-title> Robust Image & Video Labeling Editor. </v-card-title>

      <v-card-text>
        Customizable tooling supports spatial types including Box, Polygon, Lines and more.
        Attribute support for groups of nested labels, free text, and multiple select.
        Video up to 60 FPS and 4k.
      </v-card-text>

      <div class="pa-4">
        <v-img src="https://storage.googleapis.com/diffgram_public/marketing/video_ui_without_sequences.PNG"
          contain
          max-height="180px"
            >

        </v-img>
      </div>

    </v-card>
  </v-col>

  <v-col cols="4">
    <v-card elevation="0">

      <div class="pa-4">
        <v-img
          src="https://storage.googleapis.com/diffgram_public/marketing/build_for_teams.PNG"
          contain
          max-height="180px"
               >
        </v-img>
      </div>

      <v-card-title> Workflow Built for Teams </v-card-title>

     <v-card-text>
       Team collaboration. Labeling quality and automation.
       Real time human in the loop and training data management.
       Role-based access control and performance.
      </v-card-text>


    </v-card>
  </v-col>

  </v-row>


</div>
</template>

<script lang="ts">


import Vue from "vue";

export default Vue.extend( {
  name: 'marketing_feature_callout',
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

