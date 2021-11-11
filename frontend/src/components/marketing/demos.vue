<template>
<div >
   
  <v-container>
    <v-flex>
    <v-card>

      <!--

   
      -->

      <v-container>

        <v-img
        class="white--text align-end"
        height="200px"
        src="https://storage.cloud.google.com/diffgram-002/public/marketing/diffgram_dot_com/city_resized.jpg"
      >
        <v-card-title>Demos</v-card-title>
      </v-img>

     <v-card-text>

        <h3 class="pa-2 pt-4">Video Annotation</h3>

        <div class="text-center pt-4 pb-2">
          <iframe
                  width="100%"
                  height="473"
                  src="https://www.youtube-nocookie.com/embed/YeB_APnN6wk?rel=0"
                  frameborder="0"
                  allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture"
                  allowfullscreen>

          </iframe>
        </div>


    <v-card>
      <v-container>

        <call_to_action
           :show_learn_more="false">
        </call_to_action>
              
      </v-container>
    </v-card>


    <h3 class="pa-2 pt-4">Browsing and Transferring Files</h3>

      <v-card color="blue darken-3">
        <v-container class="white--text">
          <ol>
            <li> Transferring files to a directory </li>
            <li> Resizing and working with Annotation UI </li>
            <li> Different views of files, and changing columns, re ordering, then creating new label. </li>
          </ol>
        </v-container>
      </v-card>

      <div class="text-center pt-4 pb-2">
        <iframe
                  width="100%"
                height="473"
                src="https://www.youtube-nocookie.com/embed/7usdRK2RTLI?rel=0"
                frameborder="0"
                allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture"
                allowfullscreen>

        </iframe>
      </div>


    <v-card>
      <v-container>

        <call_to_action
           :show_learn_more="false">
        </call_to_action>
              
      </v-container>
    </v-card>


      <h3 class="pa-2 pt-4">Batch Work Overview</h3>

      <v-card color="green darken-2">
         <v-container class="white--text">
            <ol>
             <li> A list view of work, jumping into a specific batch, and reviewing that work</li>
             <li> Selecting files from a directory to be added to a new batch of work. 
Removing a few we decided after we didn't want in that batch.
Selecting and editing guides for the Annotators to see.
Creating and editing awards for them.
Going into the work, review the guide.
Paging across the files </li>
             <li> Applying to the Batch of work as a new Annotator.
Reviewing the guide as it comes up.
Paging through work, deferring some tasks  </li>
            </ol>
          </v-container>
        </v-card>


        <div class="text-center pt-4 pb-2">
          <iframe
                 width="100%"
                  height="473"
                  src="https://www.youtube-nocookie.com/embed/_1_kv_S3NYc?rel=0"
                  frameborder="0"
                  allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture"
                  allowfullscreen>

          </iframe>
        </div>




    <h3 class="pa-2 pt-4">Exporting Data And Export Format Overview</h3>

    <v-card color="blue darken-3">
      <v-container class="white--text">
        <ol>
          <li> Showing some of source options for export </li>
          <li> Generate and download in JSON format </li>
          <li> Scroll through downloaded format </li>
        </ol>
      </v-container>
    </v-card>

    <div class="text-center pt-4 pb-2">
      <iframe
              width="100%"
              height="473"
              src="https://www.youtube-nocookie.com/embed/EDGHXjTb0ao?rel=0"
              frameborder="0"
              allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture"
              allowfullscreen>

      </iframe>
    </div>


  <h3 class="pa-2 pt-4">Docs Scroll, Org and Project Settings</h3>

    <v-card color="green darken-2">
      <v-container class="white--text">
        <ol>
          <li> Scroll through docs </li>
          <li> Invite an Annotator to join the Org.
Scroll existing users and projects in the Org. </li>
          <li> Project settings. Create a new dev key. Revoke the dev key. </li>
        </ol>
      </v-container>
    </v-card>


  <div class="text-center pt-4 pb-2">
    <iframe
      width="100%"
      height="473"
      src="https://www.youtube-nocookie.com/embed/0W2FUmCdzII?rel=0"
      frameborder="0"
      allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture"
      allowfullscreen>

    </iframe>
  </div>


    <v-card>
      <v-container>

        <call_to_action
           :show_learn_more="false">
        </call_to_action>
              
      </v-container>
    </v-card>




        </v-card-text>

      </v-container>

    </v-card>

   </v-flex>
  </v-container>

</div>
</template>

<script lang="ts">

import call_to_action from './call_to_action'

import Vue from "vue";

export default Vue.extend( {
  name: 'demos',

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

