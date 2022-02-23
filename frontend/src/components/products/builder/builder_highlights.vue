<template>
  <div >
   <v-card>
    <v-container class="hidden-sm-and-down">

        <v-layout column>
        <v-flex md8 lg8>
          <v-card elevation-2 class="ma-2">

            <v-card elevation-1 color="primary">
              <h1 class="white--text text-center pt-4">
                Build Deep Learning Systems
              </h1>
              <h2 class="grey--text text--lighten-4 text-center pa-4">
                Build Quality Systems at Scale
              </h2>
            </v-card>

            <!-- Using datatable for more complex layouts was just confusing things -->

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

                <h2 class="blue--text pl-4 pt-4 pr-4">
                  Create Training Data
                </h2>
                <h4 class="text-xs-left pl-4 pt-2 pr-4">
                  <ul>
                    <li>
                  Images & Videos.
                    </li>
                    <li>
                      Boxes, Polygons, Keypoints, Lines, Tags, & Segmentation.
                    </li>
                    <li>
                  Attribute Groups.
                    </li>
                  </ul>
                </h4>

              </v-flex>

            </v-layout>


          <v-layout row>

            <v-flex md2>

              <h2 class="text-xs-left pl-4 pt-4">
                Task System
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

              <h2 class="blue--text pl-4 pt-4 pr-4">
                Scale Your Results
              </h2>
              <h4 class="text-xs-left pl-4 pt-2 pr-4">
                <ul>
                  <li>
                Create batches of work. Automatically organizes work into Tasks for you.
                  </li>
                  <li>
                Exams: Create repeatable work. Help your team practice and refine their skills before tackling real data.
                  </li>
                  <li>
                Control how work is presented. For example, what labels are shown.
                  </li>
                </ul>
              </h4>

            </v-flex>

          </v-layout>


        <v-layout row>

            <v-flex md2>

              <h2 class="text-xs-left pl-4 pt-4">
                System of Record
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

              <h2 class="blue--text  pt-2 pl-4 pb-2 pr-4">
                Organize and Create
              </h2>
              <h4 class="text-xs-left pl-4 pr-4 pb-4">
                <ul>
                  <li>
                  Organize and Create datasets inside Diffgram.
                  </li>
                  <li>
                  Iterative system allows the data to be improved over time.                         </li>
                  <li>
                  Flexible Import and Export through UI, API, or SDK. Pre-labelling support.

                  </li>
                </ul>
              </h4>

            </v-flex>

          </v-layout>

            <v-layout>
                <v-btn block
                        color="primary"
                        href="https://diffgram.readme.io/docs/features"
                        target="_blank"
                        >
                  <v-icon left>mdi-feature-search</v-icon>
                  Full Feature List
                  <v-icon right>mdi-open-in-new</v-icon>
                </v-btn>
            </v-layout>

          </v-card>
        </v-flex>
      </v-layout>

    </v-container>
  </v-card>

  </div>
</template>

<script lang="ts">

import Vue from "vue"; export default Vue.extend( {
  name: 'products_builder_highlights',
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

