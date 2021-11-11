<template>
<div >
 
 <v-container>
  <v-flex>
    <v-card>

      <!--

        Edit in google doc

      -->
    <v-container>
      <v-img
      class="white--text align-end"
      height="200px"
      src="https://storage.cloud.google.com/diffgram-002/public/marketing/diffgram_dot_com/path_resized.jpg"
    >
      <v-card-title>Features</v-card-title>
    </v-img>


    <v-card>
      <v-container>

        <call_to_action> </call_to_action>
              
      </v-container>
    </v-card>

        <!-- Import -->
    <img src="https://storage.googleapis.com/diffgram_public/marketing/annotation/Flexible%20data%20intake%20(1).svg">

    <h2 class="pl-4">
      How to
      <a href="https://diffgram.readme.io/docs/importing-your-data"
          target="_blank">
          upload media.</a>
    </h2>

    <!-- Video -->
    <img src="https://storage.googleapis.com/diffgram_public/marketing/annotation/Video%20Interpolation.svg">

    <h2 class="pl-4">
      Learn more about
    <a href="https://diffgram.readme.io/docs/video-introduction"
      target="_blank">
      video.</a>
      </h2>

    <v-card>
      <v-container>

        <call_to_action> </call_to_action>
              
      </v-container>
    </v-card>
              
    <!-- Active learning -->
    <img src="https://storage.googleapis.com/diffgram_public/marketing/annotation/Active%20learning%20(1).svg">

    <h2 class="pl-4">
      Learn more about
                
    <a target="_blank"
        href="https://medium.com/diffgram/fast-annotation-net-a-framework-for-active-learning-in-2018-1c75d6b4af92">
          
      Active Learning
        </a>

    </h2>
 
    <!-- Interface -->
    <img src="https://storage.googleapis.com/diffgram_public/marketing/annotation/Annotation%20Interface.svg"
          width="100%"
          >

    <h2 class="pl-4">
      Learn more about scaling 
    <a href="https://medium.com/diffgram/scale-annotation-quality-7dd285a22d01"
      target="_blank">
      Annotation Quality.</a>
      </h2>

    <!-- Hybrid -->
    <img src="https://storage.googleapis.com/diffgram_public/marketing/annotation/Hybrid%20in-house%20and%20out-source%20approach.svg">


    <!-- Coding example -->
    <img src="https://storage.googleapis.com/diffgram-002/public/marketing/os/Diffgram%20coding%20example%20-%20getting%20started.svg"
        width="100%"
        >

    <!-- Value chain -->
    <img src="https://storage.googleapis.com/diffgram_public/marketing/annotation/Diffgram%20Value%20Chain%20(3).svg"
        >

    <img src="https://storage.googleapis.com/diffgram-002/public/marketing/os/Primary%20flow%20of%20using%20diffgram%20Activate%20data%2C%20active%20models%20%20Diffgram%20%20Diffgram%20system%20overview.svg"
        width="100%"
        >

        <!-- Annotation / Diffgram service -->
      <img src="https://storage.googleapis.com/diffgram_public/marketing/annotation/Iceberg%20Service%20vs%20Annotation%20(1).svg">


      <!-- Dataset creation -->
      <img src="https://storage.googleapis.com/diffgram_public/marketing/annotation/Dataset%20Creation.svg"
          width="100%"
          >
              
      <h2 class="pl-4">
        Learn more about working with
        <a href="https://diffgram.readme.io/docs/data-directories-introduction"
            target="_blank">
            files and directories</a>.
      </h2>

    <v-card>
      <v-container>

        <call_to_action> </call_to_action>
              
      </v-container>
    </v-card>

    <v_products_builder_highlight>
    </v_products_builder_highlight>



    </v-container>

    </v-card>

   </v-flex>
  </v-container>

</div>
</template>

<script lang="ts">


import Vue from "vue";
import call_to_action from './call_to_action'

export default Vue.extend( {
  name: 'features',
  components: {
    call_to_action
  },
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
