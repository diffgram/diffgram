<template>
<div id="">

  <v-card-title>

    Attributes

    <!--
    <v-icon>mdi-collage</v-icon>
    -->

    <tooltip_button
      datacy="new_attribute_button"
      tooltip_message="New Attribute Group"
      @click="api_attribute_group_new"
      icon="add"
      :large="true"
      :icon_style="true"
      :loading="loading"
      :disabled="loading"
      color="primary">
    </tooltip_button>

  </v-card-title>

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
