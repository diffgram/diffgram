<template>
  <div id="">

    <v-card elevation=0>
      <v-container>
        <v-layout column>

          <div v-if="mode == 'NEW' ">
            <v-card-title>
              New Attribute
            </v-card-title>
          </div>

          <div v-if="mode == 'UPDATE' ">
            <v-card-title>
              Update Attribute
            </v-card-title>
          </div>


          <v-text-field label="Name"
                        data-cy="attribute_option_name"
                        v-model="name">
          </v-text-field>

            <!-- Future, could have option to select
              another GROUP here -->

          <!-- TODO if enter value, numeric or string -->

          <!-- TODO if enter open children, then open children -->



          <!-- Hide on overlay since already created -->

          <v-btn v-if="mode == 'NEW'"
                 data-cy="create_attribute_option"
                  @click="api_attribute_update_or_new('NEW')"
                 :loading="loading"
                 :disabled="loading"
                 color="primary">
            Create
          </v-btn>

           <v-btn v-if="mode == 'UPDATE' "

                  @click="api_attribute_update_or_new('UPDATE')"
                 :loading="loading"
                 :disabled="loading"
                 color="primary">
            Update
          </v-btn>

          <v_error_multiple :error="error">
          </v_error_multiple>

          <v-alert type="success"
                   :value="success"
                   dismissible
                   >
            Success.
          </v-alert>

        </v-layout>
      </v-container>

    </v-card>

  </div>
</template>

<script lang="ts">


import axios from 'axios';


 import Vue from "vue"; export default Vue.extend( {

   name: 'attribute_new_or_update',

   components: {

    },

    props: {
      'project_string_id' : {
        default: null
      },

      // only id not object easier for updates??
      // shouldn't really matter or?
      'group_id' : {
        default: null
      },
      'mode' : {
        default: 'NEW'
      },

      'attribute_prop' : {
        default: null
      }
    },

    data() {
      return {

        loading: false,
        error: {},
        success: false,


        name: null,

        attribute_id : null


      }
    },

    computed: {

      attribute: function () {

        return {
          id: this.attribute_id,
          name: this.name,
          group_id: Number(this.group_id)
        }


      }

    },
    created() {

      if (this.mode == "UPDATE") {
        this.load_existing_action()
      }

    },
    mounted() {

    },
    methods: {


      load_existing_action: function () {

        this.attribute_id = this.attribute_prop.id
        this.name = this.attribute_prop.name


      },

      recieve_label_file: function (label_file) {

        this.count.label_file_id = label_file.id

        this.overlay.label_file_id = label_file.id

      },

      recieve_brain: function (brain) {

        // TODO maybe just to "brain" not "brain_run"

        this.brain_run.id = brain.id

      },


      api_attribute_update_or_new: function (mode) {

        this.loading = true
        this.error = {}
        this.success = false

        axios.post(
          '/api/v1/project/' + this.project_string_id +
          '/attribute',
          {
            attribute: this.attribute,
            mode: mode

          }).then(response => {


            // TODO not a huge fan of it doing bulk reset of entire
            // attribute thing

            this.$store.commit('attribute_refresh_group_list')

            this.success = true
            this.loading = false

            // reset
            if (this.mode == "NEW") {

              this.name = null
              this.kind = null
            }

          }).catch(error => {

            if (error)  {
              if (error.response.status == 400) {
                this.error = error.response.data.log.error
              }
              this.loading = false
              console.log(error)
            }
          });

      }

    }
  }
) </script>
