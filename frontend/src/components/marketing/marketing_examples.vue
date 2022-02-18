<!-- LEGACY -->

<template>
<div >

<v-container>
  <v-card>
    <v-layout>
      <v-flex xs12>

        <v-card>

          <h1 class="green--text text--darken-1 text-center pa-4">
            Examples of things you can detect
          </h1>


          <template>

              <v-carousel
                  height="600"
                          >
                <v-carousel-item
                  v-for="(item,i) in examples"
                  :key="i"
                  :src="item.src"
                ></v-carousel-item>
              </v-carousel>

          </template>

        </v-card>
      </v-flex>

    </v-layout>

  </v-card>
</v-container>
  

</div>
</template>

<script lang="ts">
import Vue from "vue"; export default Vue.extend( {
  name: 'marketing_examples',
  data () {
    return {
      examples: [
          {
            src: 'https://storage.googleapis.com/diffgram_public/marketing/output_examples/crop%20weed%20detection%200.jpg'
          },
          {src: 'https://storage.googleapis.com/diffgram_public/marketing/output_examples/self%20driving%20traffic%20light%203.jpeg'},
          {src: 'https://storage.googleapis.com/diffgram_public/marketing/output_examples/red_pepper.png'},
          {src: 'https://storage.googleapis.com/diffgram_public/marketing/output_examples/package%20thief.jpg'},
          {src: 'https://storage.googleapis.com/diffgram_public/marketing/output_examples/68747470733a2f2f73746f726167652e676f6f676c65617069732e636f6d2f646966666772616d2d3030322f7075626c69632f6769746875622f67726170685f6578616d706c652e706e67.jpg'},
          {
            src: 'https://storage.googleapis.com/diffgram_public/marketing/output_examples/deformatino_public_som.PNG'
          },
          {
            src: 'https://storage.googleapis.com/diffgram_public/marketing/output_examples/markers.png'
          },
          {
            src: 'https://storage.googleapis.com/diffgram_public/marketing/output_examples/earthquake_damage_public_som.PNG'
          },
          {
            src: 'https://storage.googleapis.com/diffgram_public/marketing/output_examples/measurement_from_optical_SOM_public.PNG'
          },
           {
            src: 'https://storage.googleapis.com/diffgram_public/marketing/output_examples/property_assessment_0.PNG'
          },
           {
            src: 'https://storage.googleapis.com/diffgram_public/marketing/output_examples/property_assessment_1.PNG'
          },
           {
            src: 'https://storage.googleapis.com/diffgram_public/marketing/output_examples/shop_drawing_reading_SOM_public.png'
          },
          {
            src: 'https://storage.googleapis.com/diffgram_public/marketing/output_examples/weed%20detection.jpg'
          },
          {
            src: 'https://storage.googleapis.com/diffgram_public/marketing/output_examples/self%20driving%20traffic%20light.jpeg'
          }
        ]
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

