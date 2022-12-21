<template>
  <div v-cloak id="geo-add-tile">
    <h3>Tiles</h3>
    <ul>
      <li
        v-for="tile in tiles"
        :key="tile.key"
      >
        <div style="display: flex; flex-direction: row; align-items: center; justify-content: space-between">
          {{ tile.name }}
          <standard_button
            tooltip_message="Delete layer"
            icon="mdi-close"
            :icon_style="true"
            :bottom="true"
            :disabled="!tile.removable"
            @click="() => remove_tile(tile.key)"
          />
        </div>
      </li>
    </ul>
    <br />
    <div v-if="allow_add_tiles">
      <h3>Add XYZ Tile</h3>
      <v-text-field
        v-model="name" 
        label="Layer name" 
      />
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
  </div>
</template>

<script lang="ts">

import Vue from "vue";

export default Vue.extend({
  name: 'geo_tile',
  props: {
    map_layers: {
      type: Object,
      default: {}
    },
    allow_add_tiles: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      tile: null,
      name: null,
      opacity: null
    }
  },
  computed: {
    tiles: function() {
      const tile_keys = Object.keys(this.map_layers)
      const tile_list = []

      tile_keys.map(key => {
        const current_tile = this.map_layers[key]
        if (current_tile) {
          tile_list.push({...current_tile, key})
        }
      })

      return tile_list.sort((a, b) => {
        if (a.layer.values_.zIndex < b.layer.values_.zIndex) return -1;
        if (a.layer.values_.zIndex > b.layer.values_.zIndex) return 1;
        return 0;
      });
    }
  },
  methods: {
    tiles: function() {
      const tile_keys = Object.keys(this.map_layers)
      const tile_list = []

      tile_keys.map(key => {
        const current_tile = this.map_layers[key]
        if (current_tile) {
          tile_list.push({...current_tile, key})
        }
      })

      return tile_list.sort((a, b) => {
        if (a.layer.values_.zIndex < b.layer.values_.zIndex) return -1;
        if (a.layer.values_.zIndex > b.layer.values_.zIndex) return 1;
        return 0;
      });
    },
    remove_tile: function(key) {
      this.$emit('remove_tile', key)
    },
    add_tile: function() {
      if (!this.tile || !this.name) return
      
      this.$emit('add_tile', {
        tile: this.tile,
        name: this.name,
        opacity: this.opacity ? this.opacity / 100 : 1
      })

      this.tile = null
      this.opacity = null
      this.name = null
    }
  }
}) 

</script>