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
                    :project_string_id="project_string_id"
                    :label_list="label_list"
                    :label_file_colour_map="label_file_colour_map"
                    :task="task"
                    :file="file"
                    @edit_mode_toggle="change_mode" 
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
                :style="`height: calc(100vh - 100px); z-index: 0; width: 100%; cursor: ${cursor}`"
            />
        </div>
    </div>
</template>

<script>
import Vue from "vue";
import geo_toolbar from "./geo_toolbar.vue"
import geo_sidebar from "./geo_sidebar.vue"
import CommandManager from "../../helpers/command/command_manager"
import InstanceList from "../../helpers/instance_list"
import History from "../../helpers/history"
import { 
    CreateInstanceCommand, 
    DeleteInstanceCommand,
    UpdateInstanceLabelCommand
} from "../../helpers/command/available_commands"
import { GeoPoint } from "../vue_canvas/instances/GeoInstance"
// Imports from OpenLayers
import GeoTIFF from 'ol/source/GeoTIFF';
import Map from 'ol/Map';
import TileLayer from 'ol/layer/WebGLTile';
import OSM from 'ol/source/OSM';
import View from 'ol/View';
import Feature from 'ol/Feature'
import VectorLayer from 'ol/layer/Vector'
import VectorSource from 'ol/source/Vector'
import Point from 'ol/geom/Point'
import Circle from 'ol/geom/Circle'
import { transform } from 'ol/proj';
import MousePosition from 'ol/control/MousePosition';
import {createStringXY} from 'ol/coordinate';
import { defaults as defaultControls } from 'ol/control';
import LineString from 'ol/geom/LineString';
import { getLength } from 'ol/sphere';
import { Circle as CircleStyle, Fill, Stroke, Style } from 'ol/style';
import 'ol/ol.css';

export default Vue.extend({
    name: "text_token_core",
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
    data() {
        return {
            // Instance management
            instance_list: undefined,
            history: undefined,
            command_manager: undefined,
            invisible_labels: [],
            // map management
            map_instance: undefined,
            annotation_layer: undefined,
            mouse_coords: undefined,
            feature_list: [],
            // Others
            current_label: undefined,
            draw_mode: true,
            has_changed: false,
            current_instance_type: 'geo_circle',
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
        }
    },
    components: {
        geo_toolbar,
        geo_sidebar
    },
    computed: {
        current_style: function() {
            return this.create_style(this.current_label)
        },
        undo_disabled: function() {
            return !this.history || !this.history.undo_posible
        },
        redo_disabled: function() {
            return !this.history || !this.history.redo_posible
        },
        draw_instances: function() {
            if (!this.instance_list) return

            this.instance_list.get_all().map(instance => {
                const already_exists = this.feature_list.find(feature => feature.ol_uid === instance.ol_id)
                if ((already_exists && instance.soft_delete) || this.invisible_labels.find(label => label.id === instance.label_id)) {
                    this.annotation_source.removeFeature(already_exists)
                    const index_to_remove = this.feature_list.indexOf(already_exists)
                    this.feature_list.splice(index_to_remove, 1)
                    return
                }

                let feature;
                const style = this.create_style(instance.label_file)

                if (!already_exists && !instance.soft_delete && instance.type === 'geo_point') {
                    feature = new Feature(new Point(instance.coords));
                }

                if (feature) {
                    feature.setStyle(style)
                    this.annotation_source.addFeature(feature)
                    this.feature_list.push(feature)
                    instance.ol_id = feature.ol_uid
                }

            })
        }
    },
    watch: {},
    mounted() {
        this.instance_list = new InstanceList()
        this.history = new History()
        this.command_manager = new CommandManager(this.history)

        this.initialize_map()
        this.initialize_interface()
        this.on_mount_hotkeys()
    },
    methods: {
        initialize_interface_data: function() {
            // Get instances from teh backend and render them
        },
        initialize_map: async function() {
            const mousePositionControl = new MousePosition({
                coordinateFormat: createStringXY(4),
                projection: 'EPSG:4326',
            });

            // This is temporary, before backend is wired up
            const source = new GeoTIFF({
                sources: [
                    {
                        url: 'https://sentinel-cogs.s3.us-west-2.amazonaws.com/sentinel-s2-l2a-cogs/2020/S2A_36QWD_20200701_0_L2A/TCI.tif',
                    },
                ],
            });


            this.annotation_source = new VectorSource({})

            const map = new Map({
                controls: defaultControls().extend([mousePositionControl]),
                target: 'map',
                layers: [
                    new TileLayer({
                        source: new OSM(),
                    }),
                    new TileLayer({
                        source,
                        opacity: 0.5
                    }),
                    new VectorLayer({
                        source: this.annotation_source
                    })
                ]
            });

            const view = await source.getView()
            const overlayView = new View({...view})
            map.setView(overlayView)

            // This  is event listener for mouse move within the map, and return coordinates of the map
            map.on('pointermove', (evt) => {
                this.mouse_coords = evt.coordinate
            })

            this.map_instance = map
        },
        draw_instance: function() {
            //Start drawing instance depending on the current instance type
            if (!this.draw_mode) return;
            
            if (this.current_instance_type === 'geo_point') {
                const lonlat = transform(this.mouse_coords, 'EPSG:3857', 'EPSG:4326');
                const pointFeature = new Feature(new Point(this.mouse_coords));
                pointFeature.setStyle(this.current_style)

                this.annotation_source.addFeature(pointFeature)
                this.feature_list.push(pointFeature)
                
                const newPoint = new GeoPoint()
                newPoint.create_frontend_instance(
                    lonlat,
                    this.mouse_coords, 
                    { ...this.current_label },
                    pointFeature.ol_uid
                )
                this.instance_list.push([newPoint])

                const command = new CreateInstanceCommand([newPoint], this.instance_list)
                this.command_manager.executeCommand(command)
                return
            }
        },
        change_mode: function() {
            // Change between draw and annotate modes
        },
        delete_instance: function(instance) {
            const delete_command = new DeleteInstanceCommand([instance], this.instance_list)
            this.command_manager.executeCommand(delete_command)
            this.has_changed = true;
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
        change_label_visibility: async function(label) {
            if (label.is_visible) {
                this.invisible_labels = this.invisible_labels.filter(label_id => label_id !== label.id)
            } else {
                this.invisible_labels.push(label.id)
            }
            this.draw_instances
        },
        change_instance_type: function(instance_type) {
            this.current_instance_type = instance_type
        },
        change_label_file: function(event) {
            this.current_label = event
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
        save: function() {
            // Save
        },
        change_file(direction, file) {
            if (direction == "next" || direction == "previous") {
                this.$emit("request_file_change", direction, file);
            }
        },
        on_mount_hotkeys: function() {
            // Setting howtkeys for the geo interface
        },
        create_style: function(label_file) {
            const { r, g, b } = label_file.colour.rgba;
            const styleSet = {
                fill: new Fill({
                    color: `rgba(${r}, ${g}, ${b}, 0.5)`
                }),
                stroke: new Stroke({
                    color: `rgba(${r}, ${g}, ${b}, 1)`
                })
            }
            const style = new Style({
                ...styleSet,
                image: new CircleStyle({
                    radius: 1,
                    ...styleSet
                })
            })
            
            return style
        }
    }
})
</script>

