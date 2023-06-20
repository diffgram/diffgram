<template>
  <div id="">

    <v-list-item dense elevation=0 style="border: 1px solid #e0e0e0" class="pa-0">
      <v-container class="pa-2">

        <v-layout row>

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
              @attribute_updated="$emit('attribute_updated', $event)"
                  >
            </attribute_new_or_update>

            </v-layout>
          </template>

        </button_with_menu>

        <standard_button
            tooltip_message="Archive"
            @click="api_attribute_archive('ARCHIVE')"
            icon="archive"
            :loading="loading"
            :disabled="loading"
            :icon_style="true"
            :bottom="true"
            color="red">
        </standard_button>


        </v-layout>
      </v-container>

    </v-list-item>


  </div>
</template>

<script lang="ts">

import attribute_new_or_update from './attribute_new_or_update.vue';
import { attribute_update_or_new } from "../../services/attributesService.ts"

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
        show_menu: true,

        show_edit: false


      }
    },
    watch: {

    },
    methods: {

      // feels strange to have this here and NOT as part of the edit / update...

      api_attribute_archive: async function (mode) {

        this.loading = true
        this.error = {}
        this.success = false

        const { status, error } = await attribute_update_or_new(mode, this.project_string_id, this.attribute)
        this.error = error

        if (status === 200) {
          this.$store.commit('attribute_refresh_group_list')
          this.success = true
        }

        this.loading = false
      }

    }
  }
) </script>
