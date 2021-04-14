<template>

  <v-tooltip :top="top_actual" :bottom="bottom_actual">

    <!-- Confirm menu -->
    <template v-slot:activator="{on : tooltip}">
      <v-menu v-model="menu_open"
              :close-on-content-click="close_content_on_click"
              >

        <!-- Button to launch confirm menu -->
        <template v-slot:activator="{ on : menu }">

          <v-btn  v-on="{ ...tooltip, ...menu }"
                  :loading="loading"
                  :disabled="disabled"
                  :icon="icon_style"
                  :text="text_style"
                  :large="large"
                  >
             <v-icon
                :color=color
                :large=large>
                {{icon}}
            </v-icon>

          </v-btn>
        </template>
       
          <v-card>

            <v-card-title>
              {{ confirm_message }}
            </v-card-title>

            <slot name="content"> </slot>

            <v-card-actions>

              <!-- menu_open control here is needed
                if we allow menu to stay open,
                ie by seting close_content_on_click to false.
              -->
              <v-btn color="primary"
                     @click="menu_open = false">
                Cancel
              </v-btn>

              <v-btn
                  color="warning"
                  @click="$emit('confirm_click', $event)">
                Confirm
              </v-btn>
            </v-card-actions>

          </v-card>

        </v-menu>
    </template>

       {{ tooltip_message }}

    </v-tooltip>


</template>

<script lang="ts">

/*
 *
 *  @confirm_click
 *
 *
 *  example
 *
 *  in input . vue
 *
<button_with_confirm
  @confirm_click="api_action_archive('ARCHIVE')"
  color="pink"
  icon="archive"
  :icon_style="true"
  tooltip_message="Archive"
  confirm_message="Archive"
  :loading="loading">
</button_with_confirm>


For more complex usage include a template ie:

  <template slot="content">
    <v-layout column>
          
         
    </v-layout>
  </template>

This can also be useful to explain side effects of an action

Named slot since we may add more slots later
so that way hopefully less existing stuff to change / more clear

For spacing issues check :icon_style="true" and text_style not enabled
 * 
 */

import Vue from "vue"; export default Vue.extend( {
  name: 'button_with_confirm',
  props: {
    'loading': {
      default: false
     },
    'disabled': {
      default: false
     },
    'color': {
      default: 'red'
    },
    'icon': {
      default: 'mdi-lifebuoy',
      type: String
    },
    'tooltip_message': {
      default: null,
      type: String
    },
    'icon_style': {
      default: false
     },
    'text_style': {
      default: false
    },
    'bottom': {
      default: true
    },
    'confirm_message': {
      default: "Are you sure?",
        type: String
    },
    /* This is a different pattern from
     * the other menue because
     * we already have a button     *
     */
    'close_content_on_click': {
      default: true
    },
    'large': {
      default: false
    }
  },
  data() {
    return {
      // because we can't override props
      // and rather have the interface be the "cleaner / shorter" thing
      top_actual: true,
      bottom_actual: false,

      menu_open: false,

    }
  },
  watch: {
    // We could also use v-model but maybe that confused more then helps?
    // esp if we just want read only?
    menu_open: function (state) {
      this.$emit('menu_open', state)
    }
  },
  created(){
    // defaults tp top, so setting bottom to true adds this?
    // not quite right but should work
    if (this.bottom == true) {
      this.bottom_actual = true
      this.top_actual = false
    }

  }
}

) </script>
