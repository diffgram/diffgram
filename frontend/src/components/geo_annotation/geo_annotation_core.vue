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
                @change_instance_type="change_instance_type"
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
            :label_list="label_list"
            :label_file_colour_map="label_file_colour_map"
            @delete_instance="delete_instance"
            @change_instance_label="change_instance_label"
        />
        <div 
            id="map" 
            ref="map" 
            @click="draw_instance" 
            @mouseup="change_center"
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
import { GeoPoly, GeoCircle, GeoPoint } from "../vue_canvas/instances/GeoInstance"
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
            if (this.draw_init) {
                const cal_radius = this.getDistance(this.draw_init, this.drawing_latlng)
                const marker = L.circle(this.draw_init, {radius: cal_radius, color: this.current_label.colour.hex})
                this.map_instance.addLayer(marker)
                this.draw_marker_instance = marker
            }
        },
        drawing_latlng: function() {
            if (this.draw_init) {
                this.map_instance.removeLayer(this.draw_marker_instance)
                let marker;
                if (this.current_instance_type === 'geo_circle') {
                    const cal_radius = this.getDistance(this.draw_init, this.drawing_latlng)
                    marker = L.circle(this.draw_init, {radius: cal_radius, color: this.current_label.colour.hex});
                }
                else if (this.current_instance_type === 'geo_box') {
                    marker = L.rectangle([[this.draw_init.lat, this.draw_init.lng], [this.drawing_latlng.lat, this.drawing_latlng.lng]], {color: this.current_label.colour.hex});
                }
                else if (this.current_instance_type === 'geo_polygon') {
                    marker = L.polygon([...this.drawing_poly_path, this.drawing_latlng], {color: this.current_label.colour.hex}).addTo(this.map_instance);
                }
                else if (this.current_instance_type === 'geo_polyline') {
                    marker = L.polyline([...this.drawing_poly_path, this.drawing_latlng], {color: this.current_label.colour.hex}).addTo(this.map_instance);
                }
                this.map_instance.addLayer(marker)
                this.draw_marker_instance = marker
            }
        },
        file: function() {
            this.existing_markers.map(marker => {
                this.map_instance.removeLayer(marker)
            })
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
                    if (instance.type === 'geo_circle') {
                        const already_exists = this.existing_markers.find(marker => 
                            marker._latlng && marker.options &&
                            marker.options.radius === instance.radius && 
                            marker._latlng.lat === instance.origin.lat &&
                            marker._latlng.lng === instance.origin.lng &&
                            marker.options.color === instance.label_file.colour.hex
                        )
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
                    }
                    else if (instance.type === 'geo_point') {
                        const already_exists = this.existing_markers.find(marker => 
                            marker._latlng &&
                            marker._latlng.lat === instance.origin.lat &&
                            marker._latlng.lng === instance.origin.lng &&
                            marker.options.color === instance.label_file.colour.hex
                        )
                        if (already_exists && instance.soft_delete) {
                            this.map_instance.removeLayer(already_exists)
                            const indexToRemove = this.existing_markers.indexOf(already_exists)
                            this.existing_markers.splice(indexToRemove, 1)
                        }
                        else if (!already_exists && !instance.soft_delete) {
                            const marker = L.circle(instance.origin, {radius: 1, color: instance.label_file.colour.hex})
                            this.existing_markers.push(marker)
                            this.map_instance.addLayer(marker)
                        }
                    }
                    else if (instance.type === 'geo_box') {
                        const already_exists = this.existing_markers.find(marker => 
                            marker._bounds && marker._bounds._northEast && marker._bounds._southWest &&
                            marker._bounds._northEast.lat === instance.bounds[0][0] &&
                            marker._bounds._northEast.lng === instance.bounds[1][1] &&
                            marker._bounds._southWest.lat === instance.bounds[1][0] &&
                            marker._bounds._southWest.lng === instance.bounds[0][1] &&
                            marker.options.color === instance.label_file.colour.hex
                        )
                        if (already_exists && instance.soft_delete) {
                            this.map_instance.removeLayer(already_exists)
                            const indexToRemove = this.existing_markers.indexOf(already_exists)
                            this.existing_markers.splice(indexToRemove, 1)
                        }
                        else if (!already_exists && !instance.soft_delete) {
                            const marker = L.rectangle(instance.bounds, {color: instance.label_file.colour.hex})
                            this.existing_markers.push(marker)
                            this.map_instance.addLayer(marker)
                        }
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
            drawing_poly_path: [],
            draw_init: null,
            drawing_latlng: null,
            draw_marker_instance: null,
            map_instance: null,
            // EVERYTHING related to map
            url: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
            attribution:
                '&copy; <a target="_blank" href="http://osm.org/copyright">OpenStreetMap</a> contributors',
            zoom: 13,
            initial_center: [51.505, -0.159],
            current_center: [51.505, -0.159],
            current_instance_type: "geo_circle",
            instance_type_list: [
                {
                    name: "geo_polygon",
                    display_name: "Polygon",
                    icon: "mdi-vector-polygon",
                },
                { name: "geo_box", display_name: "Box", icon: "mdi-checkbox-blank" },
                { name: "geo_point", display_name: "Point", icon: "mdi-circle-slice-8" },
                { name: "geo_polyline", display_name: "Polyine", icon: "mdi-minus" },
                {
                    name: "geo_circle",
                    display_name: "Circle",
                    icon: "mdi-checkbox-blank-circle-outline",
                },
            ],
        };
    },
    mounted() {
        this.on_mount()
        this.hot_key_listeners()
        const map = L.map('map').setView(this.initial_center, this.zoom);

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
        change_center: function(e) {
            const center = this.map_instance.getCenter()
            this.current_center = [center.lat, center.lng]
            this.map_instance.setView([center.lat, center.lng], this.zoom)
        },
        // Need to refactore this function because too many reoetiotions
        draw_instance: function(e) {
            if (!this.draw_mode) return;

            if (this.current_instance_type === 'geo_point') {
                const point = L.point(e.layerX, e.layerY)
                const unproject = this.map_instance.layerPointToLatLng(point)
                const deltas = [this.initial_center[0] - this.current_center[0], this.initial_center[1] - this.current_center[1]]
                const use_coords = {
                    lat: unproject.lat - deltas[0],
                    lng: unproject.lng - deltas[1]
                }
                const newPoint = new GeoPoint()
                newPoint.create_frontend_instance(
                    {lat: use_coords.lat, lng: use_coords.lng}, 
                    { ...this.current_label }
                )
                this.instance_list.push([newPoint])
                this.drawing_poly_path = []
                const command = new CreateInstanceCommand([newPoint], this.instance_list)
                this.command_manager.executeCommand(command)
                const marker = L.circle(use_coords, {radius: 1, color: this.current_label.colour.hex})
                this.existing_markers.push(marker)
                this.map_instance.addLayer(marker)
                return
            }

            if (!this.drawing_instance) {
                this.$refs.map.addEventListener('mousemove', this.move_mouse_listener)
                this.drawing_instance = true
                const point = L.point(e.layerX, e.layerY)
                const unproject = this.map_instance.layerPointToLatLng(point)
                const deltas = [this.initial_center[0] - this.current_center[0], this.initial_center[1] - this.current_center[1]]
                const use_coords = {
                    lat: unproject.lat - deltas[0],
                    lng: unproject.lng - deltas[1]
                }
                this.drawing_poly_path.push([use_coords.lat, use_coords.lng])
                this.draw_init = use_coords
                this.drawing_latlng = use_coords
                return
            }


            if (this.current_instance_type === 'geo_box') {
                const newBox = new GeoPoly("geo_box")
                newBox.create_frontend_instance(
                    [[this.draw_init.lat, this.draw_init.lng], [this.drawing_latlng.lat, this.drawing_latlng.lng]], 
                    { ...this.current_label }
                )
                this.instance_list.push([newBox])
                const command = new CreateInstanceCommand([newBox], this.instance_list)
                this.command_manager.executeCommand(command)

                this.drawing_instance = false
                this.draw_init = null
                this.drawing_latlng = null
                this.drawing_poly_path = []
                this.$refs.map.removeEventListener('mousemove', this.move_mouse_listener)
                this.existing_markers.push(this.draw_marker_instance)
                return
            }

            if (this.current_instance_type === 'geo_polygon' || this.current_instance_type === 'geo_polyline') {
                this.drawing_poly_path.push([this.drawing_latlng.lat, this.drawing_latlng.lng])
            }

            if (this.current_instance_type === 'geo_circle') {
                const newCircle = new GeoCircle()
                const radius = this.getDistance(this.draw_init, this.drawing_latlng)
                newCircle.create_frontend_instance(
                    {lat: this.draw_init.lat, lng: this.draw_init.lng}, 
                    radius, 
                    { ...this.current_label }
                )
                this.instance_list.push([newCircle])
                const command = new CreateInstanceCommand([newCircle], this.instance_list)
                this.command_manager.executeCommand(command)
    
                this.drawing_instance = false
                this.draw_init = null
                this.drawing_latlng = null
                this.drawing_poly_path = []
                this.$refs.map.removeEventListener('mousemove', this.move_mouse_listener)
                this.existing_markers.push(this.draw_marker_instance)
                return 
            }

        },
        move_mouse_listener: function(e) {
            const point = L.point(e.layerX, e.layerY)
            const unproject = this.map_instance.layerPointToLatLng(point)
            const deltas = [this.initial_center[0] - this.current_center[0], this.initial_center[1] - this.current_center[1]]
            const use_coords = {
                lat: unproject.lat - deltas[0],
                lng: unproject.lng - deltas[1]
            }
            this.drawing_latlng = use_coords
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
        delete_instance: async function(instance) {
            const delete_command = new DeleteInstanceCommand([instance], this.instance_list)
            this.command_manager.executeCommand(delete_command)
            this.has_changed = true
            this.draw_instances
        },
        change_instance_label: async function(event) {
            const { instance, label } = event
            const command = new UpdateInstanceLabelCommand([instance], this.instance_list)
            command.set_new_label(label)
            this.command_manager.executeCommand(command)
            this.has_changed = true
            this.draw_instances
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
        change_instance_type: function(instance_type) {
            this.current_instance_type = instance_type
        },
        hot_key_listeners: function() {
            window.removeEventListener("keydown", this.keydown_event_listeners)
            window.addEventListener("keydown", this.keydown_event_listeners)
        },
        keydown_event_listeners: async function(e) {
            if (e.keyCode === 27) {
                this.drawing_instance = false
                this.draw_init = null
                this.drawing_latlng = null
                this.map_instance.removeLayer(this.draw_marker_instance)
                this.$refs.map.removeEventListener('mousemove', this.move_mouse_listener)
            }

            if (e.keyCode === 13) {
                if (this.drawing_instance && (this.current_instance_type === 'geo_polygon' || this.current_instance_type === 'geo_polyline')) {
                    const newPoly = new GeoPoly(this.current_instance_type)
                    newPoly.create_frontend_instance(
                        [[this.draw_init.lat, this.draw_init.lng], [this.drawing_latlng.lat, this.drawing_latlng.lng]], 
                        { ...this.current_label }
                    )
                    this.instance_list.push([newPoly])
                    const command = new CreateInstanceCommand([newPoly], this.instance_list)
                    this.command_manager.executeCommand(command)
                    
                    this.drawing_instance = false
                    this.draw_init = null
                    this.drawing_latlng = null
                    this.drawing_poly_path = []
                    this.$refs.map.removeEventListener('mousemove', this.move_mouse_listener)
                    this.existing_markers.push(this.draw_marker_instance)
                }
            }
        }
    }
})
</script>
