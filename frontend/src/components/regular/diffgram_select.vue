<style>
  .v-menu__content {
    max-height: 600px !important
  }

  /*
    Careful! Any styles here are global for selectors.

    Why this is here:
    1) Vuetify forces a max-height ~300px randomly and we don't want it.
    2) Veutify has a "height" field in theory but it doesn't seem to work
    3) We don't want a generic min-height because otherwise all
    components have it, eg pushing a component more then we want

    4) It appears we can't just attach it as a style because it's actually part
    of the "inner" component, like inside v-select the v-menu component.
    So we have to identify the interior class it appears.
    5) !important to override the JS vuetify adds otherwise it doesn't work.
  */
</style>

<template>

  <!--
      @input is built right into vue js
     https://vuejs.org/v2/guide/components.html#Using-v-model-on-Components
    -->

  <v-select v-if="item_list"
            :items="item_list"
            v-model="item_internal"
            :label="label"
            :return-object="return_object"
            :item-value="key_to_seperate_objects"
            :disabled="disabled"
            :multiple="multiple"
            @input="$emit('input', $event)"
            @change="$emit('change', $event)"
            @focus="$emit('focus', $event)"
            :data-cy="`${data_cy}`"
            :clearable="clearable"
            >

    <!-- Menu OPEN -->
      <template v-slot:item="data">

        <v-layout class="d-flex align-center justify-start">

          <v-icon v-if="data.item.icon"
                  :color="data.item.color"
                  left
                  >
          {{data.item.icon}}
          </v-icon>
          <v-icon v-else-if="!data.item['image-icon']"
                  :color="default_icon_color"
                  left
                  >
            {{default_icon}}
          </v-icon>
          <img class="pr-2" width="30px" height="30px" :src="data.item['image-icon']" v-else/>

          <div v-if="name_key">
            {{data.item[name_key]}}
          </div>
          <div v-else>
            <div v-if="data.item.display_name">
              {{data.item.display_name}}
            </div>
            <div v-else>
              {{data.item.name}}
            </div>
          </div>

        </v-layout>

      </template>

    <!-- Menu CLOSED -->
      <template v-slot:selection="data">

        <v-layout class="mb-4">

          <v-icon v-if="data.item.icon"
                  :color="data.item.color"
                  left
                  >
          {{data.item.icon}}
          </v-icon>
          <v-icon v-else
                  :color="default_icon_color"
                  left
                  >
            {{default_icon}}
          </v-icon>

            <!-- Feb 27 2020
              For some reason the default padding when open
              looks fine but looks a bit funny when closed
              this helps level it with icon better
              -->

            <div class="pt-1">

              <div v-if="name_key">
                {{data.item[name_key]}}
              </div>
              <div v-else>
                <div v-if="data.item.display_name">
                  <div v-if="data.item.display_name.length >= 9">
                    {{ data.item.display_name.slice(0, 9) }}
                    ...
                  </div>
                  <div v-else>
                    {{ data.item.display_name }}
                  </div>
                </div>
                <div v-else>
                  {{data.item.name}}
                </div>
              </div>
            </div>

          </v-layout>

      </template>

  </v-select>

</template>

<script lang="ts">

/*
 *
 * Component is an ABSTRACT representation of a selector for use with other components.

Will do display_name if available otherwise name
Always uses name for key / return value,
but display name for case thing.

EXAMPLE (3 peices):
Put this stuff in the parent vue

1)
<diffgram_select
    :item_list="status_filters_list"
    v-model="status_filter"
    label="Status"
    :disabled="loading"
    @change="get_input_list"
    >
</diffgram_select>


2) Expects a list in the format:

status_filters_list: [
    {'name': 'success',
     'display_name': 'SUPER SUCCESS',
      'icon': 'check',
      'color': 'primary'
    },
    {'name': 'failed',
      'icon': 'error'
    },
    {'name': 'processing',
      'icon': ''
    }
  ],

3) and a v-model:
Sets starting value and recieves value from other thing
status_filter: "All"

v-model is the short hande for updating the parent
with the event
 https://vuejs.org/v2/guide/components.html#Using-v-model-on-Components

Basically we include an @input and a prop called "value"
for the "2 way" binding...

-> Context of this 3rd party UI libraries being unreliable,
and wanting a stronger abstraction of our own.
-> Specific context that this otherwise would
require a ton of "copy and paste" to show the icon stuff we want

Another example
      source_list: [
          { 'name': 'directory',
            'display_name': 'Directory',
            'icon': 'mdi-folder',
            'color': 'primary'
          },
          { 'name': 'job',
            'display_name': 'Job',
            'icon': 'mdi-inbox',
            'color': 'green'
          },
          { 'name': 'task',
            'display_name': 'Task',
            'icon': 'mdi-flash-circle',
            'color': 'purple'
          }
      ],


 */

import Vue from "vue";

export default Vue.extend( {

  // 'select' is a reserved name
  name: 'diffgram_select',
  props: {
    'item_list': {
      default: null,
      type: Array
    },
    'data_cy': {
      default: null,
      type: String
    },
    // built in vue js
    'value': {
      default: null
      //type: String || Array
      // type check is being silly, can be array if allow multiple selection.
    },
    'label': {
      default: null,
      type: String
    },
    'disabled' : {
      default: false,
      type: Boolean
    },
    'multiple' : {
      default: false,
      type: Boolean
    },
    'return_object' : {
      default: false,
      type: Boolean
    },
    'default_icon': {
      default: null,
      type: String
    },
    'clearable':{
      default: false,
      type: Boolean
    },
    'default_icon_color': {
      default: "primary",
      type: String
    },
    // TODO maybe this should default to 'display_name' to improve quality
    // BUT first need to check usage some assumptions around it handling the failover
    // from display_name to name.
    'name_key': {   // overrides default naming expecation.
      default: null,
      type: String
    },
    // for objects can set this to null
    // ie :key_to_seperate_objects="null"
    // reason for not default to null is some components assumed this is 'name' and break
    // careful, if the selected value is an object and a key is set here then the
    // key will be returned instead of the whole object
    'key_to_seperate_objects' : {
       default: "name",
       type: String
     }
  },
  data() {
    return {
      item_internal: null
    }
  },
  created(){
    this.item_internal = this.value
  },
  watch: {
    /*
     * If we just edit this directly
     * (ie at created), then it won't change nicely when
     * updated from server
     *
     * If we set it directly then it does the "prop doesn't mutate"
     * thing
     *
     * BUT we still do need to set it at created otherwise the
     * very first load isn't handled...
     *
     */
    value: function (item) {
      this.item_internal = item
    }
  }
}

) </script>
