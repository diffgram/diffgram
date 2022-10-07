<template>
  <div>
    <v-tooltip 
      :top="top_actual" 
      :bottom="bottom_actual"
    >
      <template v-slot:activator="{ on }">
        <a 
          :href="href"
          :target="target"
          class="wrapper-link"
        >
          <v-btn  
            v-on="on"
            :width="width"
            :height="height"
            :loading="loading"
            :disabled="disabled"
            :x-small="xSmall"
            :x-large="xLarge"
            :left="left"
            :icon="icon_style"
            :text="text_style"
            :data-cy="datacy"
            :large="large"
            :small="small"
            :color=button_color
            @click="$emit('click', $event)"
          >
            <v-icon 
              :large="large"
              :class="active ? 'active' : ''"
              :size="iconSize"
              :color=color
              :left="left"
            >
              {{ icon }}
            </v-icon>
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
      type: Boolean,
      default: false
     },
    'xSmall':{
      type: Boolean,
      default: false
    },
    'xLarge':{
      type: Boolean,
      default: false
    },
    'small':{
      type: Boolean,
      default: false
    },
    'iconSize':{
      type: Number || String,
      default: undefined
    },
    'disabled': {
      type: Boolean,
      default: false
    },
    'href': {
      type: String,
      default: null
    },
    'color': {    // icon color
      type: String,
      default: null
    },
    'left':{
      type: Boolean,
      default: false
    },
    'button_color': {
      type: String,
      default: null
    },
    'icon': {
      type: String,
      default: 'mdi-lifebuoy'
    },
    'tooltip_message': {
      type: String,
      default: null
    },
    'icon_style': {
      type: Boolean,
      default: false
     },
    'text_style': {
      type: Boolean,
      default: false
    },
    'active': {
      type: Boolean,
      default: false
    },
    'bottom': {
      type: Boolean,
      default: false
    },
    'large': {
      type: Boolean,
      default: false
    },
    'button_message': {
      type: String,
      default: null
    },
    'width':{
      type: String || Number,
      default: undefined,
    },
    'height':{
      type: String || Number,
      default: undefined
    },
    'datacy':{
      type: String,
      default: 'tooltip-button'
     },
    'target': {
        type: String,
        default: '_self'
     },
  },
  computed: {
    bottom_actual(): boolean {
      return this.bottom
    },
    top_actual(): boolean {
      return !this.bottom
    }
  }
}

) 
</script>

<style scoped>
.active{
  border: 2px solid #2296f3;
  padding: 0.8rem;
  border-radius: 5px;
}

.wrapper-link {
  text-decoration: none;
}
</style>
