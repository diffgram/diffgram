<template>

  <v-tooltip
      :top="tooltip_direction_top"
      :bottom="tooltip_direction_bottom"
      :right="tooltip_direction_right"
      data-cy="text-with-menu-tooltip"
      :left="tooltip_direction_left">

    {{ tooltip_message }}

    <template ref='tooltip' v-slot:activator="{on : tooltip}">
      <v-menu
          v-model="menu_open"
          :close-on-content-click="close_content_on_click"
          :nudge-width="nudge_width"
          :offset-y="offset_y"
          :offset-x="!offset_y"
          ref="menu"
          data-cy="v-menu-component"
          @update:return-value="$emit('update:return-value', $event), update_return_value()"
          :attach="attach"
          :top="menu_direction_top"
          :bottom="menu_direction_bottom"
          :right="menu_direction_right"
          :left="menu_direction_left"
        >
        <!-- Default to offset y for now can fiddle with later -->

        <!-- TODO confirm we can scope the update return event like this-->

          <template v-slot:activator="{ on : menu }">
            <v-icon :large="large"
                    :color=color>{{icon}}</v-icon>
            <h4 ref="text" data-cy="clickable-text"class="main-clickable-text" v-on="{ ...tooltip, ...menu }"
                    @click="$emit('click', $event), click()"
                    >

                {{ tooltip_message}}
            </h4>

          </template>

        <!--  note how the template only wraps the activator,
              note the rest of the v-card -->

          <v-card data-cy="menu-card-component">
            <v-container>

              <!-- We can define a name but then need to
                  use that name with the template-->
              <!--

                  <slot name="content_unique_string"> </slot>
                  <template slot="content_unique_string"> </template>

                  -->

        <!-- Important, content gets injected here -->
              <slot name="content"> </slot>

            <!-- end content -->

              <div v-if="close_by_button === true">

                <!-- TODO consider putting this as option
                     in top right corner?
                     Some menus expecatation is can just click away... -->

                <v-divider></v-divider>

                <v-card-actions>
                  <v-btn data-cy="close-button" @click="menu_open = false"
                         text>
                    <v-icon left> {{ action_icon }} </v-icon>
                    {{ action_message }}
                  </v-btn>
                </v-card-actions>

              </div>

            </v-container>
          </v-card>



        </v-menu>
      </template>

    </v-tooltip>


</template>

<script lang="ts">
    // Jan 7, 2020, it's not liking new store references
  // @ts-nocheck


/*
 * Example
 *
 *

<button_with_menu
    tooltip_message="Hotkeys"
    icon="mdi-keyboard-settings"
    :close_by_button="true"
        >

    <template slot="content">
      <v-layout column>


      </v-layout>
    </template>

</button_with_menu>

 *  We normally style tooltip message first so it's easier to see what
 *  it's referring too
 *
 *  Questions / notes
 *  We could add a v-model if we wanted to be able trigging it from something else
 *
 *
vuetify 2, and @click on button is correct placement
if issue with lock check use actually has BOTH:

1) ie <button_with_menu> has:

Jan 7, 2020: OLD
@click="$store.commit('set_user_is_typing_or_menu_open', true)"
@update:return-value="$store.commit('set_user_is_typing_or_menu_open', false)"

NEW:, just bind this flag
:commit_menu_status="true"
Little things like the "commit menu" open can now be automatic in this shared setup!!!
But I think it's good to expose that too in case we want to do other things with the events


2) AND !!!! that whatever event expecting to not fire actually has the lock ie:
if (this.$store.state.user.is_typing_or_menu_open == true) {
  return
}
like in annotation_core , keyboard_events_global_up()

Keep in mind this is sort of a "hack" in the sense that we don't
always want to disble hotkeys when a menu comes up,
but if a menu has text we want to enter, then while we are entering the text
we want to disable the hotkeys, and if that's the main thing the menu has then it
seems like that's an ok work around? hmmm
An alternative we could have a wrapper around text entries or something?...
I guess in the future is it possible different hotkeys for different context menus?...

Perhaps the "set menu open" is still a valuable property to have for other reasons,
we just happen to be using it for hot keys now....


The "action" thing is in the context that sometimes we seem to need to
close a menu for updates to trigger nicely / propogate in vue
(maybe some better way to do this?)
And so it makes more sense to have this as say a "go" action
(that indireclty "goes" by closing it...) Not sure.

See sequence list for an example with the "change sequence number

The flip side is not clear if we want to always be trying to update "everything"
when a single menu like this is open.


 *
 */

import Vue from "vue";

export default Vue.extend( {
  name: 'text_with_menu',
  props: {
    'disabled': {
      default: false
     },
    'color': { // button color (not menu)
      default: 'red'
    },
    'icon': {
      default: undefined,
      type: String
    },
    'tooltip_message': {
      default: null,
      type: String
    },
    'icon_style': {
      default: true
     },
    'tooltip_direction': {      // left, right, bottom, top
      default: "bottom"
    },
    'menu_direction': {      // left, right, bottom, top
      default: "right"
    },
    'close_by_button': {
      default: false
    },
    'nudge_width' : {
      default: 200
    },
    'offset' : {    // == 'x', 'y'
       default: 'y'
    },
    'attach' : {
       default: false
    },
    'open-on-hover' : {
       default: false,
       type: Boolean
    },
    'commit_menu_status' : {
       default: false,
      type: Boolean
    },
    'large': {
      default: false,
      type: Boolean
    },
    'action_message': {
      default: 'close',
      type: String
    },
    'action_icon': {
      default: 'close',
      type: String
    }
  },

  data() {
    return {
      // tooltip direction
      // maybe in future could use for other stuff too...
      tooltip_direction_top: false,
      tooltip_direction_right: false,
      tooltip_direction_left: false,
      tooltip_direction_bottom: false,

      menu_direction_top: false,
      menu_direction_right: false,
      menu_direction_left: false,
      menu_direction_bottom: false,

      offset_y: true,
      offset_x: false,

      menu_open: false,

      // https://vuetifyjs.com/en/components/menus

      // Designates if menu should close when its content is clicked
      close_content_on_click: false

      // Designates if menu should close on outside-activator click
      //close_on_click: true

    }
  },
  created(){
    // defaults to bottom now since that's more common for menus?

    // vuetify has flags for each of these
    // so this just sets it to true assuming it was false before...
    this["tooltip_direction_" + this.tooltip_direction] = true
    this["menu_direction_" + this.menu_direction] = true

    if (this.close_by_button == true) {
      this.close_content_on_click = false
    }
    if (this.offset == 'x') {
      this.offset_y = !this.offset_y
      this.offset_x = !this.offset_x

    }

    // WIP not complete
    if (this.text_style == true) {
      this.icon_style = false
    }
  },
  methods: {
    close_menu: function(){
      this.menu_open = false;
    },
    update_return_value: function () {
      if (this.commit_menu_status == true) {
        this.$store.commit('set_user_is_typing_or_menu_open', false)
      }
    },
    click: function () {
      if (this.commit_menu_status == true) {
        this.$store.commit('set_user_is_typing_or_menu_open', true)
      }
    }

  }
}

) </script>
<style scoped>
  .main-clickable-text {
    color: #207ad4;
    font-weight: bold;
    text-decoration: underline;
    text-align: center;
    font-size: 1rem;
  }
  .main-clickable-text:hover{
    cursor: pointer;
  }
</style>
