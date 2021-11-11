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
      <v-layout>
        <v-flex xs9 md9>

          <h2>
            Tutorials and Guides
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

          <h3 class="pt-4"> Beta - Diffgram Actions </h3>

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

        </v-flex>
      </v-layout>
    </v-container>
  </v-card>




    </v-container>

    </v-card>

   </v-flex>
  </v-container>

</div>
</template>

<script lang="ts">


import Vue from "vue";

export default Vue.extend( {
  name: 'getting_started',
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

