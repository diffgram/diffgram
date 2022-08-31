<template>
    <div 
        id="map" 
        ref="map" 
        :style="`height: calc(100vh - 48px); z-index: 0; width: 100%;`"
    />
</template>

<script>
import Vue from "vue";
import Map from 'ol/Map';
import TileLayer from 'ol/layer/WebGLTile';
import OSM from 'ol/source/OSM';
import View from 'ol/View';

export default Vue.extend({
    name: 'map_explorer',
    data() {
        return {
            map: null
        }
    },
    mounted() {
        const map = new Map({
            target: 'map',
            view: new View({
                center: [0, 0],
                zoom: 1,
            }),
            layers: [
                new TileLayer({
                    source: new OSM(),
                })
            ]
        });

        this.map = map
    }
})
</script>