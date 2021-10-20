<template>
<div id="">

  <v-container class="d-flex">

    <h2 class="font-weight-medium text--primary flex-grow-1">
      Attributes:
    </h2>

    <!--
    <v-icon>mdi-collage</v-icon>
    -->
    <v-spacer></v-spacer>

    <tooltip_button
      datacy="new_attribute_button"
      button_color="primary"
      tooltip_message="Create Attribute"
      button_message="Create Attribute"
      @click="api_attribute_group_new"
      icon="add"
      :large="true"
      :loading="loading"
      :disabled="loading"
      color="white">
    </tooltip_button>

  </v-container>

  <v_error_multiple :error="error">
  </v_error_multiple>

</div>
</template>

<script lang="ts">

import axios from 'axios';

 import Vue from "vue"; export default Vue.extend( {

   name: 'attribute_group_new',

   components: {
    },
    props: {
      'project_string_id' : {
        default: null
      }
    },
    data() {
      return {

        loading: false,
        error: {},
        success: false,

        flow: {
        }
      }
    },
    computed: {
    },
    methods: {

      // NOT TESTED YET

      api_attribute_group_new: function () {

        this.loading = true
        this.error = {}
        this.success = false

        axios.post(
          '/api/v1/project/' + this.project_string_id +
          '/attribute/group/new',
          {

          }).then(response => {

            // TODO check if syntax is right for emit
            //this.$emit('attribute_template_group',
            //  response.data.attribute_template_group)

            this.$store.commit('attribute_refresh_group_list')

            this.success = true
            this.loading = false

          }).catch(error => {

            if (error.response.status == 400) {
              this.error = error.response.data.log.error
            }
            this.loading = false
            console.log(error)
          });

      }

    }
  }
) </script>
