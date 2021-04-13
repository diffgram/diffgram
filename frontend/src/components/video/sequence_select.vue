<template>
  <div v-cloak>

    <v-select :items="sequence_list_internal"
              v-model="selected"
              :label="label"
              return-object
              :item-value="null"
              :disabled="view_only_mode"
              @change="$emit('change', $event)"
              :attach="attach"
              >

      <template v-slot:item="data">

        <v-chip :color="$get_sequence_color(data.item.id)"
                text-color="white"
                @click="change_current_sequence(data.item)"
                >
          {{data.item.number}}
        </v-chip>

        <div v-if="data.item.instance_preview != undefined
                  && data.item.instance_preview.preview_image_url">

            <img class="image_clickable"                           
                  style="max-height: 50px; max-width: 50px"
                  :src="data.item.instance_preview.preview_image_url"
                  width="100%"
                  height="100%"
                  >
          </div>

          <!-- Fallback -->
          <div v-else>
            <v-icon large>
              mdi-transition
            </v-icon>
          </div>
      </template>

      <template v-slot:selection="data">

        <v-chip :color="$get_sequence_color(data.item.id)"
                text-color="white"
                >
          {{data.item.number}}
        </v-chip>

        <div v-if="data.item.instance_preview != undefined
                  && data.item.instance_preview.preview_image_url">

            <img class="image_clickable"                           
                  style="max-height: 50px; max-width: 50px"
                  :src="data.item.instance_preview.preview_image_url"
                  width="100%"
                  height="100%"
                  >
          </div>

          <!-- Fallback -->
          <div v-else>
            <v-icon large>
              mdi-transition
            </v-icon>
          </div>

      </template>


    </v-select>

  </div>
</template>

<!--

  Example usage

    <sequence_select
      :sequence_list="sequence_list"
      @change="selected = $event"
                        >
    </sequence_select>

  NOT GLOBALLY available
  so import ie:

  import sequence_select from '../video/sequence_select.vue'

    components: {
    sequence_select
  },

-->

<script lang="ts">

import Vue from "vue";

export default Vue.extend({

    name: 'sequence_select',

    props: {
      'sequence_list': {},
      'view_only_mode': {},
      'label': {
        default: "Sequence"
      },
      'attach': {
        default: false // Must set to True if need to
        // attach to parent element, eg for context menu
        // Veutify docs suggest this to be a string but bool works
      },
      'select_this_id': {
      }
    },

    watch: {

      sequence_list: function (event) {
        this.sequence_list_internal = event
      },
      select_this_id: function (event){
        this.update_from_select_this_id(event)
      }

    },
    created() {
      this.sequence_list_internal = this.$props.sequence_list
      this.update_from_select_this_id(this.$props.select_this_id)
    },
    computed: {
    },
    data() {
      return {

        sequence_list_internal: [],
        selected: null,
      }
    },

    methods: {
      update_from_select_this_id(event) {
        this.selected = this.sequence_list_internal.find(
          x=> {return x.id == event})
      } 
    }
  }
)
</script>
