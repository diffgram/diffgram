<template>

  <div @mouseover="mouseover"
       @mouseleave="mouseleave"
       v-if="visible"
       >
    <v-tooltip :top="top_actual" :bottom="bottom_actual">

      <template v-slot:activator="{ on }">

      <a :href="href"
         @click="preventdefault($event)"
         :target="target"
         style="text-decoration: none;">

        <v-btn  v-on="on"
                :width="width"
                :height="height"
                :loading="loading"
                :disabled="disabled"
                :x-small="xSmall"
                :x-large="xLarge"
                data-cy="data_cy"
                :left="left"
                :icon="icon_style"
                :text="text_style"
                :data-cy="datacy"
                @click="$emit('click', $event)"
                :large="large"
                :small="small"
                :color=button_color
               >

          <v-icon :large="large"
                  :class="active ? 'active' : ''"
                  :size="iconSize"
                  :color=color
                  :left="left"
                  >{{icon}}</v-icon>

          {{ button_message }}

        </v-btn>
      </a>

      </template>

      {{ tooltip_message }}


    </v-tooltip>
  </div>
</template>

<script lang="ts">

/*
 *  Context of them switching v-slot to be
 * nested inside template (in addition to different syntax)
 * and it just feeling reallly unwiedly for such a "basic" component
 * not to mention more difficult to test.
 *
 * We expect can just add classes needed right on this component
 *
 * Very much a WIP
 * Assumes wanting to do an href link, mostly in context of "little" links
 * core UI stuff still maybe just have to repeat code maybe
 *
 *  TODOs
 *  Support for large icons?
 *  Merging with other stuff / more slot usage
 *
 *   Maybe could have a generic "tool_tip" type thing
 *   with slot for templates (but somehow include activator for tooltip?...)
 *
 *
 *  EXAMPLE USAGE:
 *

<tooltip_button
    tooltip_message="Help"
    @click="move_frame"
    icon="help"
    :text_style="true"
    color="primary">
</tooltip_button>


// Too enable the normal "open in new tab" on links (not always relevant,
since often we don't want to go anywhere). include the :href.

eg
        <tooltip_button
          :href="'/project/' + project_string + '/job/new'"
          @click="$router.push('/project/' + project_string + '/job/new')">
        </tooltip_button>

That way a direct push will still use the router, but an "open in new tab"
will work too.

can use either @click or href    href is null by default
href="https://diffgram.readme.io/docs"

 */

import Vue from "vue";

export default Vue.extend( {
  name: 'tool_tip_button',
  props: {
    'loading': {
      default: false
     },
    'xSmall':{
      default: false
    },
    'xLarge':{
      default: false
    },
    'small':{
      default: false
    },
    'iconSize':{
      default: undefined
    },
    'disabled': {
      default: false
     },
    'href': {
      default: null
    },
    'color': {    // icon color
      default: null
    },
    'left':{
      default: false,
      type: Boolean
    },
    'button_color': {
      default: null
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
    'data_cy': {
      default: false
    },
    'text_style': {
      default: false
    },
    'active': {
      default: false
    },

    // TODO maybe change this to like "direction" or something so
    // can support bottom, right, left etc...
    // ie it gets that as string and transfers prop to menu?...
    'bottom': {
      default: false
    },
    'large': {
      default: false
    },
    'button_message': {
      default: null,
      type: String
    },
    'width':{
      default: undefined,
      type: String,
    },
    'height':{
      default: undefined,
      type: String,
    },
    'datacy':{
      default: 'tooltip-button'
     },
    'target': {
        type: String,
        default: '_self'
     },
    'ui_schema_name': {
        type: String,
        default: undefined
     }
  },
  data() {
    return {
      // because we can't override props
      // and rather have the interface be the "cleaner / shorter" thing
      top_actual: true,
      bottom_actual: false,
      visible: true
    }
  },
  created(){
    // defaults tp top, so setting bottom to true adds this?
    // not quite right but should work
    if (this.bottom == true) {
      this.bottom_actual = true
      this.top_actual = false
    }
    this.refresh_button_state_from_ui_schema()
  },
  mounted(){
    this.show_ui_schema_refresh = this.$store.watch((state) => {
        return this.$store.state.ui_schema.refresh
      },
      (new_val, old_val) => {
        this.refresh_button_state_from_ui_schema()
      },
    )
  },
  beforeDestroy() {
    this.show_ui_schema_refresh()
  },
  methods: {
    refresh_button_state_from_ui_schema(){
      if (this.$props.ui_schema_name == undefined) { return true }
      this.visible = this.$store.getters.get_ui_schema(this.$props.ui_schema_name, 'visible')
    },
    preventdefault(event) {
      // we don't assume this will go anywhere unless opened in new tab
      // in which case the event will follow the default. In the future
      // could offer an "open in new tab" specific new

      if (this.target != '_self'){ return } // eg '_blank' we want default opening in new tab
      event.preventDefault();
    },
    mouseover(event) {
      //console.log(this.ui_schema_name, event)
      this.$store.commit('set_ui_schema_event', [this.ui_schema_name, event])
    },
    mouseleave(event) {
      //this.$store.commit('clear_ui_schema_event')
    }
  }
}

) </script>
<style scoped>
.active{
  border: 2px solid #2296f3;
  padding: 0.8rem;
  border-radius: 5px;
}
</style>
