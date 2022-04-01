<template>
<div>
    <main_menu
        :height="`${!task ? '100px' : '50px'}`"
        :show_default_navigation="!task"
    >
        <template slot="second_row">
            <geo_toolbar 
                :instance_type_list="instance_type_list" 
                :draw_mode="draw_mode"
                :undo_disabled="undo_disabled"
                :redo_disabled="redo_disabled"
                :has_changed="has_changed"
                @edit_mode_toggle="change_mode" 

                :project_string_id="project_string_id"
                :label_list="label_list"
                :label_file_colour_map="label_file_colour_map"
                :task="task"
                :file="file"
                @change_label_file="change_label_file"
                @change_label_visibility="change_label_visibility"
                @change_file="change_file"
                @undo="undo()"
                @redo="redo()"
            />
        </template>
    </main_menu>
    <div style="display: flex; flex-direction: row">
        <geo_sidebar
            :instance_list="instance_list ? instance_list.get() : []"
        />
        <div 
            id="map" 
            ref="map" 
            @click="draw_instance" 
            :style="`height: calc(100vh - 100px); z-index: 0; width: 100%; cursor: ${cursor}`" 
        />
    </div>
</div>
</template>

<script>
import Vue from "vue"
import L from "leaflet"
import geo_toolbar from "./geo_toolbar.vue"
import geo_sidebar from "./geo_sidebar.vue"
import CommandManager from "../../helpers/command/command_manager"
import InstanceList from "../../helpers/instance_list"
import History from "../../helpers/history"
import { CreateInstanceCommand, DeleteInstanceCommand, UpdateInstanceLabelCommand } from "../../helpers/command/available_commands"
import { GeoCircle } from "../vue_canvas/instances/GeoInstance"
import 'leaflet/dist/leaflet.css';

export default Vue.extend({
    name: "geo_annotation_core",
    components: {
        geo_toolbar,
        geo_sidebar
    },
    props: {
        file: {
            type: Object,
            default: undefined
        },
        task: {
            type: Object,
            default: undefined
        },
        job_id: {
            type: Number,
            default: undefined
        },
        label_file_colour_map: {
            type: Object,
            requered: true
        },
        label_list: {
            type: Array,
            requered: true
        },
        project_string_id: {
            type: String,
            requered: true
        }
    },
    watch: {
        drawing_instance: function() {
            if (this.drawing_center) {
                const cal_radius = this.getDistance(this.drawing_center, this.drawing_latlng)
                const marker = L.circle(this.drawing_center, {radius: cal_radius, color: this.current_label.colour.hex})
                this.map_instance.addLayer(marker)
                this.draw_marker_instance = marker
            }
        },
        drawing_latlng: function() {
            if (this.drawing_center) {
                this.map_instance.removeLayer(this.draw_marker_instance)
                const cal_radius = this.getDistance(this.drawing_center, this.drawing_latlng)
                const marker = L.circle(this.drawing_center, {radius: cal_radius, color: this.current_label.colour.hex});
                this.map_instance.addLayer(marker)
                this.draw_marker_instance = marker
            }
        },
        file: function() {
            this.instance_list = [];
            this.command_manager = undefined;
            this.history = undefined;
            this.existing_markers = [];
            this.on_mount()
        },
    },
    computed: {
        cursor: function() {
            return this.draw_mode ? 'crosshair' : 'grab'
        },
        undo_disabled: function() {
            return !this.history || !this.history.undo_posible
        },
        redo_disabled: function() {
            return !this.history || !this.history.redo_posible
        },
        draw_instances: function() {
            if (this.instance_list) {
                this.instance_list.get_all().map(instance => {
                    const already_exists = this.existing_markers.find(marker => marker.options.radius === instance.radius && marker._latlng.lat === instance.origin.lat)
                    if (already_exists && instance.soft_delete) {
                        this.map_instance.removeLayer(already_exists)
                        const indexToRemove = this.existing_markers.indexOf(already_exists)
                        this.existing_markers.splice(indexToRemove, 1)
                    }
                    else if (!already_exists && !instance.soft_delete) {
                        const marker = L.circle(instance.origin, {radius: instance.radius, color: instance.label_file.colour.hex})
                        this.existing_markers.push(marker)
                        this.map_instance.addLayer(marker)
                    }
                })
            }
        }
    },
    data () {
        return {
            // Command pattern
            history: undefined,
            instance_list: undefined,
            command_manager: undefined,
            existing_markers: [],
            current_label: null,
            // Mode
            draw_mode: true,
            has_changed: false,
            //
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
            markerLatLng: [51.504, -0.159],
            instance_type_list: [
                {
                    name: "polygon",
                    display_name: "Polygon",
                    icon: "mdi-vector-polygon",
                },
                { name: "box", display_name: "Box", icon: "mdi-checkbox-blank" },
                { name: "tag", display_name: "Tag", icon: "mdi-tag" },
                { name: "point", display_name: "Point", icon: "mdi-circle-slice-8" },
                { name: "line", display_name: "Fixed Line", icon: "mdi-minus" },
                {
                    name: "circle",
                    display_name: "Circle",
                    icon: "mdi-checkbox-blank-circle-outline",
                },
            ],
        };
    },
    mounted() {
        this.on_mount()
        var map = L.map('map').setView([51.505, -0.09], 13);

        this.map_instance = map

        L.tileLayer(this.url, {
            attribution: this.attribution
        }).addTo(map);
    },
    methods: {
        on_mount: function() {
            this.history = new History();
            this.command_manager = new CommandManager(this.history)
            this.instance_list = new InstanceList()
        },
        draw_instance: function(e) {
            if (!this.draw_mode) return;
            if (!this.drawing_instance) {
                this.drawing_instance = true
                const point = L.point(e.layerX, e.layerY)
                const unproject = this.map_instance.layerPointToLatLng(point)
                this.drawing_center = unproject
                this.drawing_latlng = unproject
                this.$refs.map.addEventListener('mousemove', this.move_mouse_listener)
                return
            }
            const newCircle = new GeoCircle()
            const radius = this.getDistance(this.drawing_center, this.drawing_latlng)
            newCircle.create_frontend_instance(
                {lat: this.drawing_center.lat, lng: this.drawing_center.lng}, 
                radius, 
                { ...this.current_label }
            )
            this.instance_list.push([newCircle])
            const command = new CreateInstanceCommand([newCircle], this.instance_list)
            this.command_manager.executeCommand(command)

            this.drawing_instance = false
            this.drawing_center = null
            this.drawing_latlng = null
            this.$refs.map.removeEventListener('mousemove', this.move_mouse_listener)
            this.existing_markers.push(this.draw_marker_instance)
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
        },
        change_mode: function() {
            this.draw_mode = !this.draw_mode
        },
        undo: function () {
            if (!this.history.undo_posible) return;

            let undone = this.command_manager.undo();

            if (undone) this.has_changed = true;
            this.draw_instances
        },
        redo: function () {
            if (!this.history.redo_posible) return;

            let redone = this.command_manager.redo();
            
            if (redone) this.has_changed = true;
            this.draw_instances
        },
        change_file(direction, file) {
            if (direction == "next" || direction == "previous") {
                this.$emit("request_file_change", direction, file);
            }
        },
        change_label_file: function(event) {
            this.current_label = event
        },
        change_label_visibility: async function(label) {
            if (label.is_visible) {
                this.invisible_labels = this.invisible_labels.filter(label_id => label_id !== label.id)
            } else {
                this.invisible_labels.push(label.id)
            }
        },
    }
})
</script>
