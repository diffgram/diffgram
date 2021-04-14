<template>

  <span>
    <tooltip_icon
      v-if="item && item.icon"
      :tooltip_message="item.display_name"
      :icon="item.icon"
      :color="item.color"
      :tooltip_direction=tooltip_direction
    >
    </tooltip_icon>
    <img v-if="item && item['image-icon']" :src="item['image-icon']" height="25px" width="25px"/>
  </span>

</template>

<script lang="ts">

/*
 *

Context of wanting to reuse same list as select,
but not wanting a triplicate of find functions

Follows same pattern as diffgram select

1) Same item_list   (that way it can be used for both)
item_list : [
  {
    'display_name': 'Chart',
    'name': 'chart',
    'icon': 'mdi-chart-bar',
    'color': 'green'
    },
    {
    'display_name': 'Count',
    'name': 'count',
    'icon': 'mdi-numeric',
    'color': 'blue'
  }
]

2) value == 'name'

Then will automatically set
1) display_name
2) icon
3) color


<icon_from_regular_list
    :item_list="item_list"
    :value="help">
</icon_from_regular_list>

 */

import Vue from "vue";
export default Vue.extend( {
  name: 'icon_from_regular_list',
  props: {
    'item_list': {
      type: Array
    },
    'value': {
      type: String
    },
    'tooltip_direction': {      // left, right, bottom, top
      default: "bottom",
      type: String
    },
    'icon_size': {
      default: null
    },
    'icon_style': {
      default: null
    },
    'large': { // not quite sure how well this works with 'icon_size' may be a conflict
      default: false,
      type: Boolean
    }

  },
  computed: {

    item: function () {
      return this.item_list.find(x => {return x.name == this.value})
    }

    },
  data() {
    return {
      top: false,
      right: false,
      left: false,
      bottom: false
    }
  },
  created(){
    this[this.tooltip_direction] = true
  }
}

) </script>
