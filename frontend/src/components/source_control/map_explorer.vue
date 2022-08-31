<template>
    <div style="display:flex; flex-direction: row">
        <div class="pl-4 pt-2" style="width: 400px; border-top: 1px grey solid">
            <h3>Actions:</h3>
            <div>
                <v-btn>Show in area</v-btn>
            </div>
        </div>
        <div 
            id="map" 
            ref="map" 
            :style="`height: calc(100vh - 48px); z-index: 0; width: 100%;`"
        />
    </div>
</template>

<script>
import Vue from "vue";
import Map from 'ol/Map';
import TileLayer from 'ol/layer/WebGLTile';
import OSM from 'ol/source/OSM';
import View from 'ol/View';
import Feature from 'ol/Feature'
import Point from 'ol/geom/Point'
import VectorLayer from 'ol/layer/Vector'
import VectorSource from 'ol/source/Vector'
import { Circle as CircleStyle, Fill, Stroke, Style } from 'ol/style';

export default Vue.extend({
    name: 'map_explorer',
    props: {
        project_string_id: {
            type: String,
            required: true
        },
        full_screen: {
            type: Boolean,
            default: true
        },
        directory: {
            type: Number,
            required: true
        }
    },
    data() {
        return {
            map: null,
            render_source: null
        }
    },
    mounted() {
        this.render_source = new VectorSource({})
        const draw_layer = new VectorLayer({
            source: this.render_source
        })

        // WIP render some points on the map

        const styleSet = {
            fill: new Fill({
                color: `rgba(${0}, ${0}, ${0}, 0.5)`
            }),
            stroke: new Stroke({
                color: `rgba(${0}, ${0}, ${0}, 1)`
            })
        }
        
        const style = new Style({
            ...styleSet,
            image: new CircleStyle({
                radius: 5,
                ...styleSet
            })
        })

        const pointFeature = new Feature(new Point([-109.89, 45.02]));
        pointFeature.setStyle(style)
        this.render_source.addFeature(pointFeature)

        const map = new Map({
            target: 'map',
            view: new View({
                center: [0, 0],
                zoom: 1,
            }),
            layers: [
                new TileLayer({
                    source: new OSM(),
                }),
                draw_layer
            ]
        });

        this.map = map
    }
})
</script>