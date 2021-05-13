<template>
  <div id="annotation_assignment_review">


    Annotator review

    <v-text-field v-model="annotator_email"
                  label="annotator_email">
    </v-text-field>

    <v-btn color="primary"
           @click="Search_by_email">
      Search by email
    </v-btn>


    <div v-if="$store.state.annotation_project.instructions">
      <v-container>
        <v-card>
          <v-card-title>
            Instructions
          </v-card-title>
          <v-card-text>
            {{ $store.state.annotation_project.instructions }}
          </v-card-text>
        </v-card>
      </v-container>



    </div>


    <v_annotation_core @images_found="images_found_function"
                       :request_save="request_save"
                       @save_response_callback="save_response_callback_function"
                       :request_new_assignment="request_new_assignment"
                       @request_new_assignment_callback="request_new_assignment_callback"
                       :annotator_email="annotator_email"></v_annotation_core>



  </div>
</template>

<script lang="ts">

import axios from 'axios';

import Vue from "vue"; export default Vue.extend( {
  name: 'annotation_assignment_review',
  props: [''],

  data () {
    return {

      loading: false,
      images_found: true,
      request_save: false,
      request_new_assignment: false,

      annotator_email: null
    }
  },
  created() {
    
  },
  methods: {

    images_found_function: function (bool) {
      this.images_found = bool
    },

    save_response_callback_function: function (result) {

      if (result == true) {
        this.request_save = false
        // better error handling here?
      }

    },

    request_new_assignment_callback: function (result) {

      if (result == true) {
        this.request_new_assignment = false
        // better error handling here?
      }

    },

    Search_by_email: function () {
  
     this.request_new_assignment = true

    }
  }
}
) </script>
