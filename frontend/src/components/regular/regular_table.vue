<template>

    <v-card elevation="0">

      <!-- Not clear why headers are now showing up is not showing up
         May need to use that "template" thing for headers.
        -->

      <v-data-table :items="item_list"
                    :items-per-page="items_per_page"
                    :headers="headers_view"
                    :class="`elevation-${elevation}`"
                    :options.sync="options"
                    :data-cy="datacy"
                    v-model="selected_internal">

        <!-- appears to have to be item for vuetify syntax-->
        <template slot="item" slot-scope="props">

          <tr @mouseover="row_hover_index = props.index"
              @mouseleave="row_hover_index = -1"
              @click="$emit('rowclick', props.item)"
              >

            <!-- Feb 27, 2020 checkbox is WIP -->
            <!--
              <td>
                <v-checkbox v-model="props.isSelected"
                            @change="props.select($event),
                              $emit(selected_internal)"
                            primary>
                </v-checkbox>
              </td>
             -->

            <!--
             We don't need the show_column thing
              ASSUMING that the selection for columns is handled
              externally

            Not 100% sure on why the wordi ng needs to be this
              way / what's a 'magic' thing but this seems to be working.

             Not sure about how much data is getting processed
            BUT in theory if we are just passing the individual item should be reasoanble...
              alternatively could just pass the item.column but not
              sure if that would cause more issues or
              getting too abstract (like what if want to reference
              a comparison to some other value for example)

            -->

            <td v-for="column in column_list">


              <slot :name="column"
                    :item="props.item"
                    :index="props.index"
                    >
              </slot>            

            </td>

          </tr>
        </template>

        <div v-if="!loading">
          <v-alert slot="no-data"  color="error" icon="warning">
            No results found.
          </v-alert>
        </div>

      </v-data-table>
    </v-card>


</template>

<script lang="ts">

/*

Design Doc: https://docs.google.com/document/d/1FNl8L-gdhUAbJFC0iOMPyi9wg9bGXOW0IUwrXTwvH94/edit#heading=h.9sf9rgg8d3d1

column_list defines the order of the columns
so to re-order, change the the order of column_list

Zoom out context on this is:
1) We want to dynamically customize how the table looks
from a parent component. This can be cumbersome trying to
do it all in the base component

2) We want to standarize how some of this stuff renders since often
need new lists, but lots of customizations on base library

3) The reason we want to use templates
is so we can define logic that's relative IF that header is present
ie for xyz info we show something

One thing to be careful with is to get it to display need to have it "twice"
in the sense of the slot thing ie

      <template slot="name" slot-scope="props">
        {{props.item.name}}
      </template>

Some assumptions about the header names.




Feb 5, 2020 this is a WORK IN PROGRESS

Context that it would be good to abstract this anyway
 So a bit less reliant on library

And that for reporting we may want variable headers and
stuff here anyway


EXAMPLE (3 peices):
Put this stuff in the parent vue

1)
<regular_table
    :item_list="item_list"
    :column_list="column_list"
    v-model="selected"
    >


  <template slot="header_1_name">

  </template>

  <template slot="header_2_name">

  </template>

  <template slot="header_3_name">

  </template>

</regular_table>


2) Expects

  selected can be a empty array??

  a list of items:

TODO define example for item_list and header

TODO alignment between the "selected" column list and the header list.

Wording on "column" vs "header"...


ASSUMES a header_string_id is defined in the header_list....


 */

import Vue from "vue";

export default Vue.extend( {


  name: 'regular_table',

  props: {
    'item_list': {
      default: null,
      type: Array
    },
    'column_list': { // array of strings , the "selected" columns
      type: Array
    },
    'elevation':{
      type: Number,
      default: 1
    },
    'header_list': {  // array of dicts
      type: Array
    },
    // built in vue js
    // this assumes we want to propgate "selected" up this way???
    'value': {

    },
    'datacy':{
      default: 'regular_table'
    },

    'loading' : {
      default: false,
      type: Boolean
    },
    'items_per_page':{
      default: 25
    },
    // can you even disable a whole table?
    // apparently there is a 'loading' thing.
    'disabled' : {
      default: false,
      type: Boolean
    }
  },
  data() {
    return {

      row_hover_index: -1,

      selected_internal: [],

      // we may want this to be a prop
      // but need to think about a it a bit more.
      options : {
        'sortDesc': [true],
        'itemsPerPage': -1
      }

    }
  },

  computed: {
    headers_view: function () {
      let output_headers = []
      // careful we want the same sort order as the columns

      for (let column of this.column_list){
        const header = this.header_list.find(
              x => {
                return x.header_string_id == column
              }
            )
        if (header && header !== -1) {
           output_headers.push(header)
        }
      }
      // start legacy, push headers without a defined header_string_id 
      for (let header of this.header_list) {
        if (!header.header_string_id){
          output_headers.push(header)
        }
      }
      // end legacy

      return output_headers
    }
  },
  created(){
    this.selected_internal = this.value
  },

  watch: {
    row_hover_index: function (event) {
      this.$emit('row_hover_index', event)
    }
  },

  methods: {
    show_column(header_string_id){
      return this.column_list.includes(header_string_id)
    }
  }
}

) </script>
