<template>
  <div v-cloak id="geo-add-tile">
    <h3>Add XYZ Tile</h3>
    <v-text-field
      v-model="tile" 
      label="Link to the tile" 
    />
    <v-text-field
      v-model="opacity"
      label="Opacity"
      hide-details
      single-line
      type="number"
    />
    <br />
    <standard_button
      button_message="Add"
      button_color="primary"
      :icon="null"
      :bottom="true"
      :disabled="loading || save_loading"
      @click="add_tile"
    />
  </div>
</template>

<script lang="ts">

import Vue from "vue";

export default Vue.extend({
  name: 'geo_add_tile',
  data() {
    return {
      tile: null,
      opacity: null
    }
  },
  methods: {
    add_tile: function() {
      if (!this.tile) return
      
      this.$emit('add_tile', {
        tile: this.tile,
        opacity: this.opacity ? this.opacity / 100 : 1
      })

      this.tile = null
      this.opacity = null
    }
  }
}) 

</script>