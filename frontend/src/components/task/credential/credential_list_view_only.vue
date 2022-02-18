<template>
  <div v-cloak>

  
    <v-container
            container--fluid
            grid-list-md
                 >
      <v-layout >

        <v-flex xs4 md4 v-for="(item, index) in credential_list_filtered_by_kind"
                :key="index">

          <v-card>
            <v-img v-if="item.image"
                   :src="item.image.url_signed_thumb"
                  width="100%"
                  height="100%" />

            {{ item.name }}
          </v-card>

        </v-flex>
      </v-layout>

    </v-container>

  </div>
</template>

<script lang="ts">

/* Idea of this being a component assumes
 * that generaly the presentation of both required and awards is similar
 * BUT if that changes in the future, can still use this as starting point
 * to have it in seperate component.
 */

import Vue from "vue"; export default Vue.extend( {
  name: 'credential_list_view',
  props: {
    'credential_list': {
      default: []
    },
    'kind': {  // awards, requires...
      default: null
    }
   },
  watch: {

  },
  data() {
    return {
      }
  },
  computed: {
    credential_list_filtered_by_kind() {
        return this.credential_list.filter(x => x.kind == this.kind)
    }
  },
  mounted() {


  },
  methods: {
    

  }
}

) </script>
