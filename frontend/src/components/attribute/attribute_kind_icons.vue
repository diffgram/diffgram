<template>
<div>

  <tooltip_icon
      v-if="kind === 'select'"
      tooltip_message="Select"
      icon="mdi-selection"
      color="primary"
      :large="large"
      :icon_size="icon_size"
                >
  </tooltip_icon>

  <tooltip_icon
      v-if="kind === 'text'"
      tooltip_message="Text"
      icon="mdi-card-text"
      color="green"
      :large="large"
      :icon_size="icon_size"
                >
  </tooltip_icon>

  <tooltip_icon
      v-if="kind === 'multiple_select'"
      tooltip_message="Multiple Select"
      icon="mdi-select-multiple"
      color="purple"
      :large="large"
      :icon_size="icon_size"
                >
  </tooltip_icon>

  <tooltip_icon
      v-if="kind === 'radio'"
      tooltip_message="Radio Buttons"
      icon="mdi-radiobox-marked"
      color="pink"
      :large="large"
      :icon_size="icon_size"
                >
  </tooltip_icon>

  <tooltip_icon
    v-if="kind === 'slider'"
    tooltip_message="Slider"
    icon="mdi-video-input-component"
    color="pink"
    :large="large"
    :icon_size="icon_size"
  >
  </tooltip_icon>

  <tooltip_icon
    v-if="kind === 'time'"
    tooltip_message="Time"
    icon="mdi-clock"
    color="primary"
    :large="large"
    :icon_size="icon_size"
  >
  </tooltip_icon>
  <tooltip_icon
    v-if="kind === 'date'"
    tooltip_message="Date"
    icon="mdi-calendar"
    color="primary"
    :large="large"
    :icon_size="icon_size"
  >
  </tooltip_icon>



</div>
</template>

<script lang="ts">

/*
 *
 *  ie example usage:
 *
 *  1) Define in component

<attribute_kind_icons
    :kind="kind"
    :disabled="loading">
</attribute_kind_icons>

 *
 */

import Vue from "vue";

export default Vue.extend( {

  name: 'attribute_kind_icons',

  props: {
    // built in vue js
    'kind': {
      default: null,
      type: String
    },
    'disabled' : {
      default: false,
      type: Boolean
    },
    'large' : {
      default: false,
      type: Boolean
    },
    'icon_size':{
      default: 16
    }
  },
  data() {
    return {
    }
  },
  created(){
  }
}

) </script>
