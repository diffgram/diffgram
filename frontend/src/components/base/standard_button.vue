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
import Vue from "vue";

export default Vue.extend( {
  name: 'standard_button',
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
      type: [Number, String],
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
    'color': {
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
      type: [String, Number],
      default: undefined,
    },
    'height':{
      type: [String, Number],
      default: undefined
    },
    'datacy':{
      type: String,
      default: 'standard-button'
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
