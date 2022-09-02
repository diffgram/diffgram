<template>
    <div style="display:flex; flex-direction: row">
        <div class="pl-4 pt-2" style="width: 400px; border-top: 1px grey solid">
            <h3>Select area:</h3>
            <v-btn-toggle v-model="toggle_exclusive">
              <v-btn>
                <v-icon>mdi-rectangle-outline</v-icon>
              </v-btn>
              <v-btn>
                <v-icon>mdi-circle-outline</v-icon>
              </v-btn>
              <v-btn>
                <v-icon>mdi-vector-polygon-variant</v-icon>
              </v-btn>
            </v-btn-toggle>
            <br />
            <br />
            <h3>Set view coordinates:</h3>
            <div style="display: flex; flex-direction: row">
              <v-text-field
                hide-details
                single-line
                label="Max latitude"
                type="number"
                style="max-width: 125px"
              />
              <div style="width: 25px" />
              <v-text-field
                hide-details
                single-line
                label="Max longitude"
                type="number"
                style="max-width: 125px"
              />
            </div>
            <div style="display: flex; flex-direction: row">
              <v-text-field
                hide-details
                single-line
                label="Min latitude"
                type="number"
                style="max-width: 125px"
              />
              <div style="width: 25px" />
              <v-text-field
                hide-details
                single-line
                label="Min longitude"
                type="number"
                style="max-width: 125px"
              />
            </div>
        </div>
        <div 
            id="map" 
            ref="map" 
            :style="`height: calc(100vh - 48px); z-index: 0; width: 100%;`"
        />
        <div class="ol-popup" id="popup" ref="popup">
            <div v-if="active_file">
                <p>{{ active_file.original_filename }}</p>
                <file_preview
                    class="file-preview"
                    :key="active_file.id"
                    :project_string_id="project_string_id"
                    :file="active_file"
                    :instance_list="active_file.instance_list"
                    :show_ground_truth="true"
                />
            </div>
        </div>
    </div>
</template>

<script>
import Vue from "vue";
import axios from "axios";
import file_preview from "./file_preview"

import Map from 'ol/Map';
import TileLayer from 'ol/layer/WebGLTile';
import Select from 'ol/interaction/Select';
import OSM from 'ol/source/OSM';
import View from 'ol/View';
import Feature from 'ol/Feature'
import Point from 'ol/geom/Point'
import VectorLayer from 'ol/layer/Vector'
import VectorSource from 'ol/source/Vector'
import { Circle as CircleStyle, Fill, Stroke, Style } from 'ol/style';
import Overlay from 'ol/Overlay';
import { fromLonLat } from 'ol/proj';
import { click } from 'ol/events/condition';

export default Vue.extend({
    name: 'map_explorer',
    components: {
        file_preview
    },
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
            render_source: null,
            overlay: null,
            file_list: [],
            active_file: null,
            metadata: {
                'directory_id': undefined,
                'limit': 28,
                'media_type': this.filter_media_type_setting,
                'page': 1,
                'query_menu_open' : false,
                'file_view_mode': 'explorer',
                'previous': undefined,
                'search_term': this.search_term
                }
        }
    },
    async mounted() {
        this.initialize_map()
        await this.fetch_file_list()
        this.place_items_on_map()

        this.remove_event_listeners()
        this.set_event_listeners()
    },
    unmounted() {
      this.remove_event_listeners()
    },
    methods: {
        initialize_map: function() {
            this.render_source = new VectorSource({})
                const draw_layer = new VectorLayer({
                source: this.render_source
            })

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
            this.handle_popup_open()
        },
        place_items_on_map: function() {
            // WIP: this function should get data from the backend and place it to the map
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

            // This is temporarty to seimulate coordinates on the file
            const getRandomNumber = function (min, ref) {
                return Math.random() * ref + min;
            }

            this.file_list = this.file_list.map(file => {                
                const pointFeature = new Feature(new Point(fromLonLat([-getRandomNumber(85, 30), getRandomNumber(35, 10)])));
                pointFeature.setStyle(style)
                this.render_source.addFeature(pointFeature)
                
                file.feature_id = pointFeature.ol_uid
                return file
            })

        },
        handle_popup_open: function() {
            const container = document.getElementById('popup');

            const overlay = new Overlay({
                element: container,
                autoPan: {
                    animation: {
                    duration: 250,
                    },
                },
            });

            this.map.addOverlay(overlay)

            const select = new Select({
              condition: click
            });

            select.on('select', (evt) => {
              if (evt.selected[0]) {
                const feature = evt.selected[0]

                this.active_file = this.file_list.find(file => file.feature_id === feature.ol_uid)

                const coordinate = feature.getGeometry().getCoordinates();
                overlay.setPosition(coordinate);
              } else {
                overlay.setPosition(undefined)
              }
            });

            this.map.addInteraction(select);

            this.map.on("pointermove", function (evt) {
                const hit = this.forEachFeatureAtPixel(evt.pixel, () => true); 
                this.getTargetElement().style.cursor = hit ? 'pointer' : ''
            });
        },
        set_event_listeners: function() {
          window.addEventListener("keyup", this.keyup_listener)
        },
        remove_event_listeners: function() {
          window.removeEventListener("keyup", this.keyup_listener)
        },
        keyup_listener: function() {
          window.addEventListener("keyup", (evt) => {
            if (evt.keyCode === 27) {
              this.active_file = null
              this.map.overlays_.array_[0].setPosition(undefined)
            }
          })
        },
        fetch_file_list: async function(reload_all = true) {
          if(reload_all){
            this.metadata.page = 1;
            this.loading = true
          }
          else{
            this.infinite_scroll_loading = true;
          }
          try{
            this.none_found = undefined
            const response = await axios.post('/api/project/' + String(this.$props.project_string_id) +
              '/user/' + this.$store.state.user.current.username + '/file/list', {
              'metadata': {
                ...this.metadata,
                query: this.query,
                previous: this.metadata_previous
              },
              'project_string_id': this.$props.project_string_id

            })
            if (response.data['file_list'] == false) {
              this.none_found = true
            }
            else {
              if(reload_all){
                this.file_list = response.data.file_list;
              }
              else{

                for(const file in response.data.file_list){
                  if(!this.file_list.find(f => f.id === file.id)){
                    this.file_list.push(file);
                  }
                }
                this.file_list = this.file_list.concat(response.data.file_list);
              }

            }
            this.metadata_previous = response.data.metadata;
          }
          catch (error) {
            this.query_error = this.$route_api_errors(error)
          }
          finally {
            if(reload_all){
              this.loading = false;
            }
            else{
              this.infinite_scroll_loading = false;
            }

          }
      },
    }
})
</script>

<style scoped>
      .ol-popup {
        position: absolute;
        background-color: white;
        box-shadow: 0 1px 4px rgba(0,0,0,0.2);
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #cccccc;
        bottom: 12px;
        left: -50px;
        min-width: 280px;
      }
      .ol-popup:after, .ol-popup:before {
        top: 100%;
        border: solid transparent;
        content: " ";
        height: 0;
        width: 0;
        position: absolute;
        pointer-events: none;
      }
      .ol-popup:after {
        border-top-color: white;
        border-width: 10px;
        left: 48px;
        margin-left: -10px;
      }
      .ol-popup:before {
        border-top-color: #cccccc;
        border-width: 11px;
        left: 48px;
        margin-left: -11px;
      }
      .ol-popup-closer {
        text-decoration: none;
        position: absolute;
        top: 2px;
        right: 8px;
      }
      .ol-popup-closer:after {
        content: "✖";
      }
</style>