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
                    :label_schema="label_schema"
                    :loading="rendering"
                    :save_loading="save_loading"
                    :map_layers="map_layers"
                    :normalize="normalize"
                    :interpolate="interpolate"
                    @on_geotiff_rendere_change="on_geotiff_rendere_change"
                    @change_label_schema="on_change_label_schema"
                    @edit_mode_toggle="change_mode" 
                    @change_instance_type="change_instance_type"
                    @change_label_file="change_label_file"
                    @change_label_visibility="change_label_visibility"
                    @change_file="change_file"
                    @change_task="trigger_task_change"
                    @add_xyz_layer="add_xyz_layer"
                    @remove_xyz_layer="remove_xyz_layer"
                    @reset_default_view="reset_default_view"
                    @on_task_annotation_complete_and_save="on_task_annotation_complete_and_save"
                    @show_hide_layer="show_hide_layer"
                    @set_layer_opacity="set_layer_opacity"
                    @save="save"
                    @undo="undo()"
                    @redo="redo()"
                />
            </template>
        </main_menu>
        <div style="display: flex; flex-direction: row">
            <geo_sidebar
                :project_string_id="project_string_id"
                :instance_list="instance_list ? instance_list.get() : []"
                :label_list="label_list"
                :label_file_colour_map="label_file_colour_map"
                :toolbar_height="`${!task ? '100px' : '50px'}`"
                :loading="rendering"
                :current_instance="current_instance"
                :schema_id="label_schema.id"
                :global_attribute_groups_list="global_attribute_groups_list"
                :per_instance_attribute_groups_list="per_instance_attribute_groups_list"
                :current_global_instance="instance_list && instance_list.get_global_instance() && instance_list.get_global_instance().get_instance_data()"
                @on_update_attribute="on_update_attribute"
                @delete_instance="delete_instance"
                @on_select_instance="on_select_instance"
                @change_instance_label="change_instance_label"
            />
            <v-progress-linear
                v-if="rendering"
                indeterminate 
            />
            <div
                :style="`display:flex; flex-direction: column; height: calc(100vh - ${!task ? '100px' : '50px'}); z-index: 0; width: 100%;`"
            >
                <v-progress-linear
                    v-if="rendering"
                    indeterminate 
                />
                <v_error_multiple 
                    v-if="tiff_source && tiff_source.error_ && !rendering" 
                    :error="['Error ocurred while rendering geotiff']" 
                />
                <div 
                    id="map" 
                    ref="map" 
                    v-if="!rendering"
                    @click="draw_instance" 
                    :style="`height: calc(100vh - ${!task ? '100px' : '50px'}); z-index: 0; width: 100%;`"
                />
            </div>
        </div>
    </div>
</template>

<script>
import Vue from "vue";
import geo_toolbar from "./geo_toolbar.vue"
import geo_sidebar from "./geo_sidebar.vue"
import CommandManager from "../../../helpers/command/command_manager"
import InstanceList from "../../../helpers/instance_list"
import { Instance } from "../../vue_canvas/instances/Instance"
import { GlobalAnnotationInstance } from "../../../components/vue_canvas/instances/GlobalInstance";
import History from "../../../helpers/history"
import { 
    CreateInstanceCommand, 
    DeleteInstanceCommand,
    UpdateInstanceLabelCommand,
    UpdateInstanceAttributeCommand,
    UpdateGlobalAttributeCommand,
    UpdateInstanceGeoCoordinatesCommand
} from "../../../helpers/command/available_commands"
import { GeoCircle, GeoPoint, GeoPoly } from "../../vue_canvas/instances/GeoInstance"
import { getInstanceList, postInstanceList } from "../../../services/instanceList";
import slugify from "slugify"
import { v4 as uuidv4 } from 'uuid'
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
import Polygon from 'ol/geom/Polygon'
import { transform } from 'ol/proj';
import MousePosition from 'ol/control/MousePosition';
import { createStringXY } from 'ol/coordinate';
import { defaults as defaultControls } from 'ol/control';
import LineString from 'ol/geom/LineString';
import { getLength } from 'ol/sphere';
import { Circle as CircleStyle, Fill, Stroke, Style } from 'ol/style';
import Transform from "ol-ext/interaction/Transform";
import XYZ from 'ol/source/XYZ';
import {finishTaskAnnotation, trackTimeTask} from "../../../services/tasksServices";
import 'ol/ol.css';

export default Vue.extend({
    name: "geo_annotation_core",
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
            required: true
        },
        label_list: {
            type: Array,
            required: true
        },
        project_string_id: {
            type: String,
            required: true
        },
        global_attribute_groups_list: {
            type: Array,
            required: true
        },
        per_instance_attribute_groups_list: {
            type: Array,
            required: true
        },
        label_schema: {
            type: Object,
            required: true
        }
    },
    data() {
        return {
            // Instance management
            instance_list: undefined,
            history: undefined,
            command_manager: undefined,
            invisible_labels: [],
            active_instance: null,
            // map management
            map_instance: undefined,
            annotation_layer: undefined,
            mouse_coords: undefined,
            feature_list: [],
            drawing_feature: undefined,
            transform_interaction: null,
            map_layers: {},
            tiff_source: null,
            normalize: true,
            interpolate: true,
            // Others
            save_loading: false,
            selected: null,
            rendering: false,
            current_label: undefined,
            drawing_instance: false,
            draw_init: undefined,
            drawing_coords: undefined,
            drawing_poly: [],
            draw_mode: true,
            has_changed: false,
            moving: false,
            current_instance: null,
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
        selected_style: function() {
            const styleSet = {
                fill: new Fill({
                    color: 'rgba(255, 255, 255, 0.5)',
                }),
                stroke: new Stroke({
                    color: 'rgba(255, 255, 255, 1)',
                    width: 2,
                })
            }
            const style = new Style({
                ...styleSet,
                image: new CircleStyle({
                    radius: 5,
                    ...styleSet
                })
            })

            return style
        },
        draw_instances: function(e) {
            if (!this.instance_list) return

            this.feature_list.map(feature => {
                const feature_to_remove = this.instance_list.get().find(inst => feature.ol_uid === inst.ol_id)
                if (!feature_to_remove) {
                    this.annotation_source.removeFeature(feature)
                }
            })

            this.instance_list.get_all().map(instance => {
                const already_exists = this.feature_list.find(feature => feature.ol_uid === instance.ol_id)
                if ((already_exists && instance.soft_delete) || this.invisible_labels.find(label => label === instance.label_file_id)) {
                    this.annotation_source.removeFeature(already_exists)
                    return
                }

                let feature;
                let style = this.create_style(instance.label_file)
 
                if (this.current_instance && this.current_instance.id === instance.id) {
                    style = this.activate_instance()
                }

                if (!instance.soft_delete && instance.type === 'geo_point') {
                    feature = new Feature(new Point(instance.coords));
                }

                else if (!instance.soft_delete && instance.type === 'geo_circle') {
                    feature = new Feature(new Circle(instance.coords, instance.radius));
                }

                else if (!instance.soft_delete && instance.type === 'geo_polyline') {
                    feature = new Feature(new LineString(instance.bounds));
                }

                else if (!instance.soft_delete && (instance.type === 'geo_polygon' || instance.type === 'geo_box')) {
                    feature = new Feature(new Polygon([instance.bounds]));
                }

                if (feature) {
                    this.annotation_source.removeFeature(already_exists)
                    feature.setStyle(style)
                    this.annotation_source.addFeature(feature)
                    this.feature_list.push(feature)
                    instance.ol_id = feature.ol_uid
                }

            })
        }
    },
    watch: {
        draw_mode: function() {
            if (!this.draw_mode) {
                this.map_instance.addInteraction(this.transform_interaction)
            } else {
                this.map_instance.removeInteraction(this.transform_interaction)
            }
        },
        file: async function() {
            this.rendering = true;
            this.map_instance = null
            this.instance_list = new InstanceList()
            this.history = new History()
            this.command_manager = new CommandManager(this.history)

            setTimeout(() => {
                this.rendering = false

                setTimeout(() => {
                    this.initialize_interface_data()
                    this.initialize_map()
                }, 100)
            }, 100)
        },
        task: function() {
            this.rendering = true;
            this.map_instance = null
            this.instance_list = new InstanceList()
            this.history = new History()
            this.command_manager = new CommandManager(this.history)

            setTimeout(() => {
                this.rendering = false

                setTimeout(() => {
                    this.initialize_interface_data()
                    this.initialize_map()
                }, 100)
            }, 100)
        },
        mouse_coords: function() {
            if (!this.drawing_instance) return;

            if (this.current_instance_type === 'geo_circle') {
                this.annotation_source.removeFeature(this.drawing_feature)
                const line = new LineString([this.draw_init, this.mouse_coords]);
                const radius = getLength(line); 
                const circleFeature = new Feature(new Circle(this.draw_init, radius));
                circleFeature.setStyle(this.current_style)
                this.annotation_source.addFeature(circleFeature)
                this.drawing_feature = circleFeature
            }

            if (this.current_instance_type === 'geo_polyline') {
                this.annotation_source.removeFeature(this.drawing_feature)
                const polylineFeature = new Feature(new LineString([this.draw_init, ...this.drawing_poly, this.mouse_coords]));
                polylineFeature.setStyle(this.current_style)
                this.annotation_source.addFeature(polylineFeature)
                this.drawing_feature = polylineFeature
            }

            if (this.current_instance_type === 'geo_polygon') {
                this.annotation_source.removeFeature(this.drawing_feature)
                const polygoneFeature = new Feature(new Polygon([[this.draw_init, ...this.drawing_poly, this.mouse_coords]]));
                polygoneFeature.setStyle(this.current_style)
                this.annotation_source.addFeature(polygoneFeature)
                this.drawing_feature = polygoneFeature
            }

            if (this.current_instance_type === 'geo_box') {
                this.annotation_source.removeFeature(this.drawing_feature)
                const polygoneFeature = new Feature(new Polygon([[this.draw_init, [this.draw_init[0], this.mouse_coords[1]], this.mouse_coords, [this.mouse_coords[0], this.draw_init[1]], this.draw_init]]));
                polygoneFeature.setStyle(this.current_style)
                this.annotation_source.addFeature(polygoneFeature)
                this.drawing_feature = polygoneFeature
            }
        }
    },
    mounted() {
        this.instance_list = new InstanceList()
        this.history = new History()
        this.command_manager = new CommandManager(this.history)

        this.hot_key_listeners()
        this.initialize_interface_data()
        this.initialize_map()
        this.start_autosave()
    },
    methods: {
        on_geotiff_rendere_change: function(name, value) {
            this[name] = value

            this.map_instance.removeLayer(this.map_layers.file_layer.layer)

            const geotiff_layer = new TileLayer({
                source: this.generate_geotif_source(),
                opacity: this.map_layers.file_layer.layer.getOpacity(),
                zIndex: 1000
            })

            this.map_layers.file_layer = {
                name: "GeoTiff layer",
                layer: geotiff_layer,
                hidden: false
            }

            this.map_instance.addLayer(geotiff_layer)
        },
        on_select_instance: function(instance) {
            this.current_instance = instance
            this.draw_instances
        },
        generate_geotif_source: function() {
            const source = new GeoTIFF({
                sources: [
                    {
                        url: this.task ? this.task.file.geospatial.layers[0].url_signed : this.file.geospatial.layers[0].url_signed,
                    },
                ],
                interpolate: this.normalize,
                normalize: this.interpolate,
            });

            this.tiff_source = source

            return source
        },
        on_update_attribute: function(event, is_global) {
            const attribute = event
            let command
            if (is_global) {
                command = new UpdateGlobalAttributeCommand([this.instance_list.get_global_instance()], this.instance_list, true)
            } else {
                command = new UpdateInstanceAttributeCommand([this.instance_list.get().find(inst => inst.creation_ref_id === this.current_instance.creation_ref_id)], this.instance_list)
            }
            let attribute_to_pass = Array.isArray(attribute[1]) ? [...attribute[1]] : {...attribute[1]}

            if (["slider", "text", "time", "date"].includes(attribute[0].kind)) attribute_to_pass = attribute[1]

            command.set_new_attribute(attribute[0].id, attribute_to_pass)
            this.command_manager.executeCommand(command)
            this.has_changed = true
        },
        on_task_annotation_complete_and_save: async function () {
            await this.save(false);
            const response = await finishTaskAnnotation(this.task.id);
            const new_status = response.data.task.status;
            this.task.status = new_status;
            if (new_status !== "complete") {
                this.submitted_to_review = true;
            }
            if (this.$props.task && this.$props.task.id) {
                this.save_loading_image = false;
                this.trigger_task_change("next", this.$props.task, true);
            }
        },
        get_and_set_global_instance: function (instance_list) {            
            let existing_global_instance = instance_list.find(inst => inst && inst.type === 'global');
            
            if(!existing_global_instance) {
                existing_global_instance = this.new_global_instance();
            }

            const { id, creation_ref_id, attribute_groups } = existing_global_instance

            const global_instance = new GlobalAnnotationInstance()
            global_instance.create_instance(id, creation_ref_id, attribute_groups)

            this.instance_list.set_global_instance(global_instance)
        },
        new_global_instance: function () {
            let new_instance = new Instance();
            new_instance.type = 'global'
            new_instance.creation_ref_id = uuidv4();
            return new_instance
        },
        initialize_interface_data: async function() {
            let url;
            let payload;
            if (this.task && this.task.id) {
                url = `/api/v1/task/${this.task.id}/annotation/list`;
                payload = {
                    directory_id: this.$store.state.project.current_directory.directory_id,
                    job_id: this.job_id,
                    attached_to_job: this.task.file.attached_to_job,
                }
            } else {
                url = `/api/project/${this.$props.project_string_id}/file/${this.$props.file.id}/annotation/list`;
                payload = {}
            }
            const instance_list = await getInstanceList(url, payload)
            // Get instances from teh backend and render them
            let initial_instances = instance_list.map(instance_object => {
                let instance;
                const { id, type, bounds, bounds_lonlat, creation_ref_id, radius, lonlat, coords, label_file, attribute_groups } = instance_object
                if (type === 'geo_circle') {
                    instance = new GeoCircle();
                    instance.create_instance(id, creation_ref_id, lonlat, coords, radius, label_file, attribute_groups)
                } 

                if (type === 'geo_point') {
                    instance = new GeoPoint();
                    instance.create_instance(id, creation_ref_id, lonlat, coords, label_file, attribute_groups)
                }

                if (type === 'geo_polygon' || type === 'geo_polyline' || type === 'geo_box') {
                    instance = new GeoPoly(type);
                    instance.create_instance(id, creation_ref_id, bounds, bounds_lonlat, label_file, attribute_groups)
                }
                return instance
            }).filter(inst => inst)

            this.instance_list.push(initial_instances)

            this.get_and_set_global_instance(instance_list)

            this.draw_instances
        },
        initialize_map: async function() {
            if (!this.file && !this.task) return
            const mousePositionControl = new MousePosition({
                coordinateFormat: createStringXY(4),
                projection: 'EPSG:4326',
            });

            const source = this.generate_geotif_source()
            this.annotation_source = new VectorSource({})

            const draw_layer = new VectorLayer({
                source: this.annotation_source,
                zIndex: 1001
            })

            const OSM_layer = new TileLayer({
                source: new OSM(),
                zIndex: 0
            })
            
            const geotiff_layer = new TileLayer({
                source,
                opacity: 0.5,
                zIndex: 1000
            })

            this.map_layers = {
                'base_layer': {
                    name: "Base layer",
                    layer: OSM_layer,
                    hidden: false
                },
                'file_layer': {
                    name: "GeoTiff layer",
                    layer: geotiff_layer,
                    hidden: false
                },
                'annotation_layer': {
                    name: "Annotation layer",
                    layer: draw_layer,
                    hidden: false
                }
            }

            const map = new Map({
                controls: defaultControls().extend([mousePositionControl]),
                target: 'map',
                layers: [
                    this.map_layers['base_layer'].layer, 
                    this.map_layers['file_layer'].layer, 
                    this.map_layers['annotation_layer'].layer
                ]
            });

            this.map_instance = map

            this.transform_interaction = new Transform({
                layers: [draw_layer],
            })

            this.transform_interaction.on('translateend', this.transform_interraction_handler)
            this.transform_interaction.on('rotateend', this.transform_interraction_handler)
            this.transform_interaction.on('scaleend', this.transform_interraction_handler)

            await this.reset_default_view()

            // This  is event listener for mouse move within the map, and return coordinates of the map
            this.map_instance.on('pointermove', (evt) => {
                this.mouse_coords = evt.coordinate
            })
            this.map_instance.on('movestart', (evt) => {
                this.moving = true
            })
            this.map_instance.on('moveend', (evt) => {
                this.moving = false
            })
        },
        reset_default_view: async function() {
            const sourceView = await this.tiff_source.getView()
            
            let view = new View({
                center: sourceView.center,
                resolutions: sourceView.resolutions,
                zoom: sourceView.zoom
            })

            this.map_instance.setView(view)
        },
        show_hide_layer: function(e) {
            const layer = this.map_layers[e]
            if (layer) {
                if (!layer.hidden) {
                    this.map_instance.removeLayer(layer.layer)
                    this.map_layers[e].hidden = true
                }
                else {
                    this.map_instance.addLayer(layer.layer)
                    this.map_layers[e].hidden = false
                }
            }
        },
        remove_xyz_layer: function(e) {
            const layer_to_remove = this.map_layers[e]
            if (layer_to_remove) {
                this.map_instance.removeLayer(layer_to_remove.layer)
    
                this.map_layers[e] = null
            }
        },
        add_xyz_layer: function(e) {
            const layer = new TileLayer({
                source: new XYZ({
                    url: e.tile
                }),
                opacity: e.opacity,
                zIndex: Object.keys(this.map_layers).length - 1
            })

            const new_layer = {
                name: e.name,
                removable: true,
                layer
            }

            const layer_key = slugify(e.name, '_')

            this.map_layers = {
                ...this.map_layers,
                [layer_key]: new_layer
            }

            this.map_instance.addLayer(this.map_layers[layer_key].layer)
        },
        set_layer_opacity: function(e) {
            this.map_layers[e.key].layer.setOpacity(e.value/100)
        },
        transform_interraction_handler: function(e) {
            const { ol_uid } = e.feature
            const instance = this.instance_list.get().find(inst => inst.ol_id === ol_uid)
            if (!instance) return;

            if (instance.type === 'geo_polygon' || instance.type === 'geo_polyline' || instance.type === 'geo_box') {
                let bounds = e.feature.getGeometry().getCoordinates()
                if (instance.type === 'geo_polygon' || instance.type === 'geo_box') bounds = bounds[0]
                let command = new UpdateInstanceGeoCoordinatesCommand([instance], this.instance_list)
                command.set_new_geo_coords(bounds)
                this.command_manager.executeCommand(command)
                this.has_changed = true
            }
            else if (instance.type === 'geo_circle') {
                const center = e.feature.getGeometry().getCenter()
                const radius = e.feature.getGeometry().getRadius()
                let command = new UpdateInstanceGeoCoordinatesCommand([instance], this.instance_list)
                command.set_new_geo_coords([center])
                command.set_new_radius(radius)
                this.command_manager.executeCommand(command)
                this.has_changed = true
            }
            else if (instance.type === 'geo_point') {
                const new_coordinates = e.feature.getGeometry().getCoordinates()
                const command = new UpdateInstanceGeoCoordinatesCommand([instance], this.instance_list)
                command.set_new_geo_coords([new_coordinates])
                this.command_manager.executeCommand(command)
                this.has_changed = true
            }
        },
        draw_instance: function(e) {
            if (!this.draw_mode) return;
            if (e.srcElement.tagName.toLowerCase() !== "canvas") return
            if (this.moving) return
            this.current_instance = null
            this.draw_instances
            
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
                this.has_changed = true
                return
            }

            if (!this.drawing_instance) {
                const pointFeature = new Feature(new Point(this.mouse_coords));
                pointFeature.setStyle(this.current_style)

                this.annotation_source.addFeature(pointFeature)
                this.drawing_feature = pointFeature
                
                this.drawing_instance = true
                this.draw_init = this.mouse_coords
                this.drawing_coords = this.mouse_coords
                return
            }

            if (this.current_instance_type === 'geo_circle') {
                const lonlat = transform(this.draw_init, 'EPSG:3857', 'EPSG:4326');
                const line = new LineString([this.draw_init, this.mouse_coords]);
                const radius = getLength(line); 

                const newCircle = new GeoCircle()
                newCircle.create_frontend_instance(
                    lonlat,
                    this.draw_init,
                    radius,
                    { ...this.current_label },
                    this.drawing_feature.ol_uid
                )

                this.instance_list.push([newCircle])

                const command = new CreateInstanceCommand([newCircle], this.instance_list)
                this.command_manager.executeCommand(command)
            }

            if (this.current_instance_type === 'geo_polyline' || this.current_instance_type === 'geo_polygon') {
                this.drawing_poly.push(this.mouse_coords)
                return
            }

            if (this.current_instance_type === 'geo_box') {
                const newBox = new GeoPoly('geo_box')
                const bounds = [this.draw_init, [this.draw_init[0], this.mouse_coords[1]], this.mouse_coords, [this.mouse_coords[0], this.draw_init[1]], this.draw_init]
                const lonlat_bounds = bounds.map(bound => transform(bound, 'EPSG:3857', 'EPSG:4326'))
                newBox.create_frontend_instance(
                    [this.draw_init, [this.draw_init[0], this.mouse_coords[1]], this.mouse_coords, [this.mouse_coords[0], this.draw_init[1]], this.draw_init],
                    lonlat_bounds,
                    { ...this.current_label },
                    this.drawing_feature.ol_uid
                )

                this.instance_list.push([newBox])
                const command = new CreateInstanceCommand([newBox], this.instance_list)
                this.command_manager.executeCommand(command)
            }

            this.drawing_instance = false;
            this.feature_list.push(this.drawing_feature);
            this.drawing_feature = undefined;
            this.draw_init = undefined;
            this.drawing_coords = undefined;
            this.has_changed = true;
        },
        activate_instance: function() {
            this.selected_style.getFill()
            return this.selected_style;
        },
        save_time_tracking: async function () {
            if (!this.task) return

            const current_user_id = this.$store.state.user.current.id;
            const record = this.task.time_tracking.find(elm => elm.user_id === current_user_id)
            const [result, error] = await trackTimeTask(
                record.time_spent,
                this.task.id,
                this.task.status,
                this.task.job.id,
                this.task.file.id,
                null
            )

            if (result) {
                record.id = result.id;
                record.task_id = result.task_id;
                record.job_id = result.job_id;
            }
        },
        change_mode: function() {
            this.draw_mode = !this.draw_mode
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
        save: async function() {
            this.has_changed = false
            this.save_loading = true
            let url;
            if (this.task && this.task.id) {
                url = `/api/v1/task/${this.task.id}/annotation/update`;
            } else {
                url = `/api/project/${this.project_string_id}/file/${this.file.id}/annotation/update`
            }
            if (!this.drawing_instance) {
                const res = await postInstanceList(url, this.instance_list.get_for_save())
                const { added_instances } = res
                this.instance_list.get_all().map(instance => {
                    const instance_uuid = instance.creation_ref_id
                    const updated_instance = added_instances.find(added_instance => added_instance.creation_ref_id === instance_uuid)
                    if (updated_instance) {
                        instance.id = updated_instance.id
                    }
                })
            }
            if (this.task) {
                await this.save_time_tracking();
            }
            this.save_loading = false
        },
        change_file: async function(direction, file) {
            await this.save()
            if (direction == "next" || direction == "previous") {
                this.$emit("request_file_change", direction, file);
            }
        },
        hot_key_listeners: function() {
            window.removeEventListener("keydown", this.keydown_event_listeners)
            window.addEventListener("keydown", this.keydown_event_listeners)
        },
        keydown_event_listeners: async function(e) {
            if (e.keyCode === 13) {
                if (this.drawing_instance) {
                    this.create_poly_instance()
                }
            }

            if (e.keyCode === 27) {
                this.drawing_instance = false
                this.current_instance = null
                this.annotation_source.removeFeature(this.drawing_feature)
                this.drawing_poly = []
                this.draw_instances
            }

            if (e.keyCode === 83) {
                await this.save()
            }
        },
        start_autosave: function () {
            this.interval_autosave = setInterval(
                this.detect_is_ok_to_save,
                15 * 1000
            );
        },
        detect_is_ok_to_save: async function () {
            if (this.has_changed && !this.drawing_instance) {
                await this.save();
            }
        },
        create_style: function(label_file) {
            if (!label_file) return

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
                    radius: 5,
                    ...styleSet
                })
            })
            
            return style
        },
        trigger_task_change: async function (direction, assign_to_user = false) {
            await this.save();
            this.$emit("request_new_task", direction, this.task, assign_to_user);
        },
        create_poly_instance: function() {
            this.annotation_source.removeFeature(this.drawing_feature)
            let polyFeature;
            
            if (this.current_instance_type === 'geo_polyline') {
                polyFeature = new Feature(new LineString([this.draw_init, ...this.drawing_poly]))
            } else if (this.current_instance_type === 'geo_polygon') {
                polyFeature = new Feature(new Polygon([[this.draw_init, ...this.drawing_poly]]))
            }
            polyFeature.setStyle(this.current_style)
            this.annotation_source.addFeature(polyFeature)

            const bounds = [this.draw_init, ...this.drawing_poly]
            const lonlat_bounds = bounds.map(bound => transform(bound, 'EPSG:3857', 'EPSG:4326'))

            const newPoly = new GeoPoly(this.current_instance_type)
            newPoly.create_frontend_instance(
                bounds,
                lonlat_bounds,
                { ...this.current_label },
                polyFeature.ol_uid
            )

            this.instance_list.push([newPoly])
            const command = new CreateInstanceCommand([newPoly], this.instance_list)
            this.command_manager.executeCommand(command)

            this.has_changed = true
            this.drawing_instance = false;
            this.feature_list.push(polyFeature);
            this.drawing_feature = undefined;
            this.drawing_poly = []
            this.draw_init = undefined;
            this.drawing_coords = undefined;
        },
        on_change_label_schema: function(schema){
            this.$emit('change_label_schema', schema)
        },
    }
})
</script>

