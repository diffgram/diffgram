<template>
<div>
  <v-card>
    <v-card-title>
    Add External Scripts
    </v-card-title>

    <v-card-text>
      Any URL's added here will be added as script tags
      in order, and run before the JavaScript in the editor.
    </v-card-text>


    <v-list-item
      v-for="(source, i) in userscript.external_src_list">
      <v-list-item-title class="pl-2">
        {{source}}
      </v-list-item-title>

      <tooltip_button
        tooltip_message="Remove"
        @click="$emit('remove', i)"
        icon="delete"
        :icon_style="true"
        color="primary"
                    >
      </tooltip_button>

    </v-list-item>

    <v-card-text>
      <v-layout>
        <v-text-field
            v-model="newly_desired_source"
            flat
            label="New External Script"
            style="max-width: 800px"
            @focus="$store.commit('set_user_is_typing_or_menu_open', true)"
            @blur="$store.commit('set_user_is_typing_or_menu_open', false)"
            >
        </v-text-field>

        <tooltip_button
          tooltip_message="Add"
          @click="$emit('add', newly_desired_source), newly_desired_source = null"
          icon="add"
          :icon_style="true"
          :disabled="!newly_desired_source"
          color="primary"
          :large="true"
                      >
        </tooltip_button>
      </v-layout>

    </v-card-text>
  </v-card>
</div>
</template>

<script lang="ts">


import Vue from "vue";

export default Vue.extend({
  name: 'userscript_sources_selector',
  props: {
    'project_string_id': {
      default: null
    },
    'userscript': {
      default: null
    },
    'disabled': {
      default: false
    },
    'label': {
      default: null
    }
  },
  components: {

  },
  data() {
    return {

      newly_desired_source: null,

      internal_userscript: {},
      internal_userscript_list: [],
      loading: false

    }
  },
  created() {

  },
  mounted() {

  },
  computed: {
  },
  watch: {
  },
  methods: {

      
  },
  beforeDestroy() {
  }
})
</script>


