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
import {defaults as defaultControls} from 'ol/control';
import LineString from 'ol/geom/LineString';
import { getLength } from 'ol/sphere';
import { Circle as CircleStyle, Fill, Stroke, Style } from 'ol/style';
import 'ol/ol.css';

export default Vue.extend({
    name: "text_token_core",
    data() {
        return {
            instance_list: undefined,
            history: undefined,
            command_manager: undefined,
            map_instance: undefined
        }
    },
    components: {
        geo_toolbar,
        geo_sidebar
    },
    computed: {},
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

            // This is temporary, before backend is created
            const source = new GeoTIFF({
                sources: [
                    {
                        url: 'https://sentinel-cogs.s3.us-west-2.amazonaws.com/sentinel-s2-l2a-cogs/2020/S2A_36QWD_20200701_0_L2A/TCI.tif',
                    },
                ],
            });

            const map = new Map({
                controls: defaultControls().extend([mousePositionControl]),
                target: 'map',
                layers: [
                    new TileLayer({
                        source: new OSM(),
                    })
                ],
                view: new View(
                    {
                        center: [0, 0],
                        zoom: 2,
                    }
                ),
            });

            map.addLayer(new TileLayer({ source, opacity: 0.5 }))
            const view = await source.getView()
            const overlayView = new View({...view})
            map.setView(overlayView)
            map.on('pointermove', (evt) => {
                this.mouse_coords = evt.coordinate
            })

            this.map_instance = map
        },
        draw_instance: function() {
            //Start drawing instance depending on the current instance type
        },
        change_mode: function() {
            // Change between draw and annotate modes
        },
        delete_instance: function() {
            // Delete instance and remove from teh map
        },
        change_instance_label: function() {
            // change label of the instance
        },
        change_label_visibility: function() {
            // Changing visibility of the label
        },
        change_instance_type: function() {
            // Change current instance type
        },
        change_label_file: function() {
            //Chaging current label
        },
        undo: function() {
            // Undo function
        },
        redo: function() {
            // Redo fucntion
        },
        save: function() {
            // Save
        },
        on_mount_hotkeys: function() {
            // Setting howtkeys for the geo interface
        }
    }
})
</script>

