<template>
  <div id="discover_ai">
    <v-layout>
      <v-flex xs12>


        <v-jumbotron :gradient="gradient"
                     dark
                     color="primary">
          <v-container fill-height>
            <v-layout align-center>
              <v-flex>

                <h3 class="display-3">
                  <v-icon x-large>edit</v-icon>
                  Expert annotations service
                </h3>

                <v-divider class="my-3"></v-divider>

                <div class="title mb-3">
                  Expert human annotators create custom annotations for your project.
                </div>
                <div class="title mb-3">
                  Perfect for training custom deep learning based vision AIs.
                </div>

                <v-btn v-scroll-to="'#v_request_updates'"
                       large color="primary" class="mx-0">
                  Request access
                </v-btn>

              </v-flex>
            </v-layout>
          </v-container>
        </v-jumbotron>


        <v-container>
          <iframe width="100%" height="600px"
                  frameborder="0" src="https://www.youtube.com/embed/_E4ZDKZIMFc"></iframe>
        </v-container>


        <v-container grid-list>
          <v-layout row>

            <v-flex xs-6>
              <v-card>

                <code style="width: 100%">
                  // Example

                  - annotations:
                  - image:
                  height: 720
                  id: 103
                  width: 1280
                  original_filename: CRS-8 _000063.jpg
                  - boxes:
                  - label_id: 8
                  label_name: rocket
                  x_max: 659
                  x_min: 609
                  y_max: 593
                  y_min: 395

                </code>
                <v-card-media height="450px"
                              src="https://storage.googleapis.com/eminent-century-190103/public/annotation_examples/rocket.jpg">
                </v-card-media>

                <v-card-actions>
                  <v-btn dark color="primary"
                         href="https://storage.googleapis.com/eminent-century-190103/public/annotation_examples/annotations_rocket_example.yaml
">
                    Download larger sample
                    <v-icon right dark>file_download</v-icon>
                  </v-btn>
                </v-card-actions>
              </v-card>
            </v-flex>

          </v-layout>
        </v-container>




        <v-jumbotron :gradient="gradient_light"
                     dark color="primary">
          <v-container fill-height>
            <v-layout align-center>
              <v-flex>

                <h3 class="display-3">
                  Quality annotations
                </h3>

                <span class="subheading">
                </span>
                <v-divider class="my-3"></v-divider>

                <div class="title mb-3">
                  Get custom annotations for your project.
                </div>
                <div class="title mb-3">
                  Available for images or video
                </div>



              </v-flex>
            </v-layout>
          </v-container>
        </v-jumbotron>

        <v-jumbotron :gradient="gradient_light"
                     dark color="primary">
          <v-container fill-height>
            <v-layout align-center>
              <v-flex>

                <h3 class="display-3">
                  Easy access
                </h3>

                <span class="subheading">
                </span>
                <v-divider class="my-3"></v-divider>

                <div class="title mb-3">
                  Download your custom annotations as a YAML or JSON file
                </div>
                <div class="title mb-3">
                  Or optionally use with Cerbra auto vision service
                </div>



              </v-flex>
            </v-layout>
          </v-container>
        </v-jumbotron>



        <v-card-title primary-title>
          <div>
            <h1 class="headline mb-0">Annotations on demand </h1>
          </div>
        </v-card-title>

        <v-data-table v-bind:headers="annotations.header"
                      :items="annotations.items"
                      hide-default-footer
                      v-bind:options.sync="annotations.options"
                      class="elevation-1">

          <template slot="item" slot-scope="props">

            <td>{{ props.item.name }}</td>

            <td class="text-right">
              $ {{props.item.day}}
            </td>
            <td class="text-right">
              $ {{props.item.week}}
            </td>



          </template>


        </v-data-table>


        <sub>
          Terms and conditions apply.
        </sub>

        <div id="v_request_updates">

          <v_request_updates :request_name="request_name">
          </v_request_updates>

        </div>


      </v-flex>
    </v-layout>
  </div>
</template>

<script lang="ts">

  import axios from 'axios';

  import Vue from "vue"; export default Vue.extend( {
    name: 'annotation_on_demand',
    data() {
      return {
        gradient: 'to top right, rgba(63,81,181, .7), rgba(25,32,72, .7)',
        gradient_light: 'to top left, rgba(63,81,181, .3), rgba(25,32,72, .3)',

        request_name: "access",

        annotations: {
          options: {
            sortBy: 'day'
          },

          header: [
            {
              text: 'Annotations',
              align: 'left',
              sortable: false,
              value: 'name'
            },
            {
              text: '1 day', value: 'day', sortable: false,
              align: 'right',
            },
            {
              text: '1 week', value: 'week', sortable: false,
              align: 'right'
            }
          ],

          items: [
            {
              name: 'Objected detection (bounding box)',
              day: '0.10 / image + 0.09 / box drawn',
              week: '0.08 / image + 0.08 / box drawn'
            },
            {
              name: 'Semantic segmentation (polygon)',
              day: '0.95 / image + 0.70 / class drawn',
              week: '0.85 / image + 0.65 / class drawn'
            }
          ]
        }

      }
    },
    created() {

    },
    methods: {

    }
  }
) </script>

