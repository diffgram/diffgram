<template>
  <div id="">

    <v-list-item dense elevation=0 style="border: 1px solid #e0e0e0" class="pa-0">
      <v-container class="pa-2">

        <v-layout row>

          <!-- do we just send the "attribute" to front
              end and not worry about template part -->

        <h3 class="font-weight-medium ml-6 mt-2 text--primary flex-grow-1">{{ attribute.name }}</h3>

        <v_error_multiple :error="error">
        </v_error_multiple>

        <v-spacer></v-spacer>

        <!-- Edit menu -->
        <button_with_menu
            tooltip_message="Edit"
            icon="edit"
            :loading="loading"
            :disabled="loading"
            :icon_style="true"
            color="primary">

          <template slot="content">
            <v-layout column>

            <attribute_new_or_update
              :project_string_id="project_string_id"
              :attribute_prop = "attribute"
              :group_id = "attribute.group_id"
              :mode = " 'UPDATE' "
                  >
            </attribute_new_or_update>

            </v-layout>
          </template>

        </button_with_menu>

          <!-- Prior we had a more dots icon
              but it just seems like not needed
          and if we do want to bring it back should be a seperate
          button_with_menu  component
          -->

        <tooltip_button
            tooltip_message="Archive"
            @click="api_attribute_archive('ARCHIVE')"
            icon="archive"
            :loading="loading"
            :disabled="loading"
            :icon_style="true"
            :bottom="true"
            color="red">
        </tooltip_button>


        </v-layout>
      </v-container>

    </v-list-item>


  </div>
</template>

<script lang="ts">


import axios from '../../services/customAxiosInstance';
import attribute_new_or_update from './attribute_new_or_update.vue';


 import Vue from "vue";

export default Vue.extend( {
    name: 'attribute',
    components: {
      attribute_new_or_update
    },
    props: {

      'project_string_id' : {
        default: null
      },

      'attribute' : {
        default: {
        }
      }
    },

    data() {
      return {

        loading: false,
        error: {},
        success: false,

        name: null,

        show_menu: true,

        show_edit: false


      }
    },
    watch: {

      // we refresh list, so if we don't close it on current vuetify version
      // it ends up being in wrong spot. can remove or change if that thing gets fixed
      attribute() {
        this.show_edit = false
      }

    },

    created() {

    },
    computed: {

    },
    methods: {

      // feels strange to have this here and NOT as part of the edit / update...

      api_attribute_archive: function (mode) {

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

            // WIP
            // TODO handle refreshing this
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
