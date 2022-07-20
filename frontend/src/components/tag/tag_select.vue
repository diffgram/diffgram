<template>
  <div v-cloak>

    <v-autocomplete
              :items="tag_list_internal"
              v-model="item_internal"
              :label="label"
              :data-cy="datacy"
              item-value="id"
              :multiple="true"
              :disabled="loading || view_only"
              @input="$emit('input', $event)"
              @change="$emit('change', $event)"
              clearable
              return-object
    >

      <template v-slot:item="data">

        <v-layout :data-cy="`${datacy}__select-tag`">
            {{ data.item.name }}
        </v-layout>

      </template>

      <template v-slot:selection="data">
        <v-chip color="data.item.name" small>
          <template>

            <v-layout :data-cy="`${datacy}__select-tag`">
                {{ data.item.name }}
            </v-layout>

            <span  style="font-size: 10px">

            </span>

          </template>
        </v-chip>


      </template>

    </v-autocomplete>
  

  </div>
</template>

<!--

Example usage

<tag_select
    v-model="tag"
    :tag_list="$store.state.project.current.tag_list">
</tag_select>

Where is a dict in data() eg  tag: {}

-->

<script lang="ts">

  import Vue from "vue";

  export default Vue.extend({

      name: 'tag_select',

      props: {
        'value': {   // built in vue js
          default: null
        },
        'project_string_id': {
          type: String
        },
        'tag_list': {
          default: null,
          type: Array
        },
        'view_only': {
          default: false
        },
        'initial_value': {
          default: undefined,
        },
        'label': {
          default: 'Select Tags'
        },
        'datacy':{
          default: 'tag-select'
        }
      },

      watch: {

        value: function (item) {
          this.item_internal = item
        },
        tag_list: function(new_val, old_val){
            this.tag_list_internal = new_val;
        }

      },
      created() {
        this.item_internal = this.value
      },
      mounted(){
        if(this.$props.initial_value){
          this.item_internal = this.$props.initial_value;
        }
      },

      computed: {

      },
      data() {
        return {
          item_internal: null,
          loading: false,
          tag_list_internal: []
        }
      },

      methods: {

      }
    }
  )
</script>
