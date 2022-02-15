<template>
<div>
    <geo_toolbar />
    <div style="display: flex; flex-direction: row">
        <geo_sidebar />
        <div id="map" ref="map" @click="draw_instance" style="height: calc(100vh - 100px); z-index: 0; width: 100%" />
    </div>
</div>
</template>

<script>
import Vue from "vue"
import L from "leaflet"
import geo_toolbar from "./geo_toolbar.vue"
import geo_sidebar from "./geo_sidebar.vue"
import 'leaflet/dist/leaflet.css';

export default Vue.extend({
    name: "geo_annotation_core",
    components: {
        geo_toolbar,
        geo_sidebar
    },
    watch: {
        drawing_instance: function() {
            if (this.drawing_center) {
                const cal_radius = this.getDistance(this.drawing_center, this.drawing_latlng)
                const marker = L.circle(this.drawing_center, {radius: cal_radius})
                this.map_instance.addLayer(marker)
                this.draw_marker_instance = marker
            }
        },
        drawing_latlng: function() {
            if (this.drawing_center) {
                this.map_instance.removeLayer(this.draw_marker_instance)
                const cal_radius = this.getDistance(this.drawing_center, this.drawing_latlng)
                const marker = L.circle(this.drawing_center, {radius: cal_radius});
                this.map_instance.addLayer(marker)
                this.draw_marker_instance = marker
            }
        },
    },
    data () {
        return {
            drawing_instance: false,
            drawing_center: null,
            drawing_latlng: null,
            draw_marker_instance: null,
            map_instance: null,
            // EVERYTHING related to map
            url: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
            attribution:
                '&copy; <a target="_blank" href="http://osm.org/copyright">OpenStreetMap</a> contributors',
            zoom: 15,
            center: [51.505, -0.159],
            markerLatLng: [51.504, -0.159]
        };
    },
    mounted() {
        var map = L.map('map').setView([51.505, -0.09], 13);

        this.map_instance = map

        L.tileLayer(this.url, {
            attribution: this.attribution
        }).addTo(map);
    },
    methods: {
        draw_instance: function(e) {
            if (!this.drawing_instance) {
                this.drawing_instance = true
                const point = L.point(e.layerX, e.layerY)
                const unproject = this.map_instance.layerPointToLatLng(point)
                this.drawing_center = unproject
                this.drawing_latlng = unproject
                this.$refs.map.addEventListener('mousemove', this.move_mouse_listener)
                return
            }
            this.drawing_instance = false
            this.drawing_center = null
            this.drawing_latlng = null
            this.$refs.map.removeEventListener('mousemove', this.move_mouse_listener)
        },
        move_mouse_listener: function(e) {
            const point = L.point(e.layerX, e.layerY)
            const unproject = this.map_instance.layerPointToLatLng(point)
            this.drawing_latlng = unproject
        },
        getDistance: function(origin, destination) {
            // return distance in meters
            var lon1 = this.toRadian(origin.lng),
                lat1 = this.toRadian(origin.lat),
                lon2 = this.toRadian(destination.lng),
                lat2 = this.toRadian(destination.lat);

            var deltaLat = lat2 - lat1;
            var deltaLon = lon2 - lon1;

            var a = Math.pow(Math.sin(deltaLat/2), 2) + Math.cos(lat1) * Math.cos(lat2) * Math.pow(Math.sin(deltaLon/2), 2);
            var c = 2 * Math.asin(Math.sqrt(a));
            var EARTH_RADIUS = 6371;
            return c * EARTH_RADIUS * 1000;
        },
        toRadian: function (degree) {
            return degree*Math.PI/180;
        }
    }
})
</script>
