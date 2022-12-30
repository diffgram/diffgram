<template>
  <div v-cloak style="width: 400px" id="geo-add-tile">
    <h3>Render</h3>
    <v-switch
      label="Normalize"
      @change="$emit('on_geotiff_rendere_change', 'normalize', !normalize)"
    />
    <v-switch
      label="Interpolate"
      @change="$emit('on_geotiff_rendere_change', 'interpolate', !interpolate)"
    />
    <h3>Tiles</h3>
    <ul>
      <li
        v-for="tile in tiles"
        :key="tile.key"
      >
        <div style="display: flex; flex-direction: row; align-items: center; justify-content: space-between">
          <div style="width: 33%">
            {{ tile.name }}
          </div>
          <div style="width: 33%">
            <v-slider
              :hint="`Layer opacity ${tile.layer.getOpacity()}`"
              max="100"
              min="0"
              :value="tile.layer.getOpacity() * 100"
              @change="(e) => set_layer_opacity(tile.key, e)"
            />
          </div>
          <div style="display: flex; flex-direction: row; align-items: center; justify-content: space-between">
            <standard_button
              tooltip_message="Delete layer"
              icon="mdi-delete"
              :icon_style="true"
              :bottom="true"
              :disabled="!tile.removable"
              @click="() => remove_tile(tile.key)"
            />
            <standard_button
              tooltip_message="Hide/Show Layer"
              :icon="tile.hidden ? 'mdi-eye-off' : 'mdi-eye'"
              :icon_style="true"
              :bottom="true"
              @click="() => show_hide_layer(tile.key)"
            />
          </div>
        </div>
      </li>
    </ul>
    <br />
    <div>
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
    normalize: {
      type: Boolean,
      default: false
    },
    interpolate: {
      type: Boolean,
      default: false
    },
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
    set_layer_opacity: function(key, value) {
      this.$emit('set_layer_opacity', {key, value})
    },
    remove_tile: function(key) {
      this.$emit('remove_tile', key)
    },
    show_hide_layer: function(key) {
      this.$emit('show_hide_layer', key)
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