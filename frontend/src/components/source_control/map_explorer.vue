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
        <div class="ol-popup" id="popup" ref="popup">
            <div v-if="active_file">
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
import OSM from 'ol/source/OSM';
import View from 'ol/View';
import Feature from 'ol/Feature'
import Point from 'ol/geom/Point'
import VectorLayer from 'ol/layer/Vector'
import VectorSource from 'ol/source/Vector'
import { Circle as CircleStyle, Fill, Stroke, Style } from 'ol/style';
import Overlay from 'ol/Overlay';
import { fromLonLat } from 'ol/proj';

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

        this.active_file = this.file_list[1]
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

            const getRandomNumber = function (min, ref) {
                return Math.random() * ref + min;
            }

            this.file_list.map(file => {                
                const pointFeature = new Feature(new Point(fromLonLat([-getRandomNumber(50, 50), getRandomNumber(10, 50)])));
                pointFeature.setStyle(style)
                this.render_source.addFeature(pointFeature)
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
            this.map.on('singleclick', function (evt) {
                const coordinate = evt.coordinate;

                overlay.setPosition(coordinate);
            });
        },
        fetch_file_list: async function(reload_all = true){
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
          console.error(error);
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