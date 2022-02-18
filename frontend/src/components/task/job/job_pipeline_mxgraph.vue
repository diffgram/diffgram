<template>

  <v-card width="100%" class="d-flex justify-center flex-column align-center pa-4" elevation="0">

    <v-progress-circular
      :size="50"
      v-if="loading"
      color="primary"
      indeterminate
    ></v-progress-circular>

    <div class="graphContainer" ref="container" id="container" data-cy="mxgraphcontainer"></div>


  </v-card>
</template>

<script lang="ts">
  // noinspection TypeScriptCheckImport
  import * as mxgraph from 'mxgraph';

  const {
    mxClient,
    mxStackLayout,
    mxGraph,
    mxRubberband,
    mxUtils,
    mxFastOrganicLayout,
    mxSwimlaneLayout,
    mxEvent,
    mxGraphModel,
    mxConstants,
    mxHierarchicalLayout,
    mxSwimlaneManager
  } = mxgraph();
  // noinspection TypeScriptCheckImport
  import {
    mxConstants as MxConstants
  } from 'mxgraph/javascript/mxClient.js'
  import axios from '../../../services/customAxiosInstance';

  const outputIcon = './icon/output.png'
  const inputIcon = './icon/input.png'

  // export default hue1


  import Vue from "vue";

  export default Vue.extend({
      name: 'job_pipeline_mxgraph',
      props: ['job_id', 'job_object', 'show_output_jobs'],
      components: {},

      data() {
        return {
          job: null,
          output_dir: null,
          output_jobs: [],
          graph: undefined,
          loading: undefined,
          model: undefined,
        }
      },
      created() {
        if (this.$props.job_id || this.$props.job_object) {
          this.populate_data();
        }
      },
      watch: {
        job_object: {
          deep: true,
          async handler(newval, oldval) {
            await this.redraw();
          }
        }
      },
      computed: {},
      methods: {
        redraw: async function(){
          if (this.graph) {
            this.graph.getModel().beginUpdate();
            this.graph.removeCells(this.graph.getChildVertices(this.graph.getDefaultParent()));
            this.graph.getModel().endUpdate();
          }
          this.loading = true;
          this.job = this.$props.job_object;
          await this.get_directory();
          this.draw_pipeline(this.job, this.output_dir)
          this.loading = false;
        },
        populate_data: async function () {
          if (this.$props.job_object) {
            this.job = this.$props.job_object;
          } else {
            await this.fetch_job();
          }
          await this.get_directory();
          if (this.$props.show_output_jobs) {
            await this.get_output_jobs();
          }
          this.draw_pipeline(this.job, this.output_dir);
        },
        get_output_jobs: async function () {
          if(!this.output_dir){
            return false;
          }
          let output_jobs = this.output_dir.jobs_to_sync;
          if (!output_jobs) {
            return false;
          }
          output_jobs = output_jobs.job_ids;
          try {
            const response = await axios.post(`/api/v1/job/list`, {
              metadata: {
                mode_data: 'job_detail',
                builder_or_trainer: {
                  mode: 'builder'
                },
                job_ids: output_jobs,
                project_string_id: this.$store.state.project.current.project_string_id,
                status: 'active'
              }
            });
            this.output_jobs = response.data.Job_list;

            return this.output_jobs;
          } catch (error) {
            return error;
          }

        },
        get_directory: async function () {
          const project_string_id = this.$store.state.project.current.project_string_id;
          const username = this.$store.state.user.current.username;
          const dir_id = this.job.completion_directory_id;
          if (!dir_id) {
            this.output_dir = undefined;
            return false;
          }
          try {
            const response = await axios.get(`/api/project/${project_string_id}/user/${username}/working_dir/view`,
              {
                params: {
                  working_dir_id: dir_id
                }
              });
            if (response.data.success) {
              this.output_dir = response.data.working_dir
              return response.data.working_dir;
            }

            return false;
          } catch (error) {
            return error;
          }

        },
        get_parent_style_data: function (strokeColor = '#1b76d2') {
          // Gets the cell data depending on the object to be created (Dir, Task, Connection, etc..)
          const outputIcon = '../../../assets/mxgraph/public/icon'
          const styleobj = {
            fillColor: '#ffffff',
            strokeColor: '#1b76d2',
            strokeWidth: '1',
            fontColor: '#535353',
            labelPadding: 80,
            sourcePerimeterSpacing: 500,
            fontStyle: 1,
            fontSize: 20,
            lineHeight: 6,
            STYLE_WHITE_SPACE: 'wrap',
            STYLE_ASPECT: 'fixed'
          };
          const style = Object.keys(styleobj).map((attr) => `${attr}=${styleobj[attr]}`).join(';')
          return style
        },
        get_cell_style_data: function (fillColor = '#1776d2') {
          // Gets the cell data depending on the object to be created (Dir, Task, Connection, etc..)
          const outputIcon = '../../../assets/mxgraph/public/icon'
          const styleobj = {
            fillColor: fillColor,
            strokeColor: '#ffffff',
            strokeWidth: '2',
            fontColor: 'white',
            labelPadding: 80,
            sourcePerimeterSpacing: 80,
            fontStyle: 1,
            image: 'https://api.iconify.design/mdi-folder.svg?height=24',
            fontSize: 20,
            imageWidth: 20,
            imageHeight: 20,
            lineHeight: 6,
          };
          const style = Object.keys(styleobj).map((attr) => `${attr}=${styleobj[attr]}`).join(';')
          return style
        },
        generate_job_html: function (job) {
          const textSize = 10;
          const job_node_html = `<div class="d-flex flex-column justify-center  align-center ma-auto" style="padding: 0.5rem; border-radius: 50%; width: 50px; height: 50px; background-color: #d3ffe0; border: 2px solid #64bc47">` +
            `<p style="margin: 0"><i class="v-icon notranslate mdi mdi-brush" alt="" style="font-size: 30px; color: #64bc47;" ></i></p>` +
            `</div>` +
            `<p class="pl-1 ma-auto" style="font-size: ${textSize}px;  color:#535353; text-align: center">${job.name}</p>`;
          return job_node_html

        },
        generate_dir_html: function (dir) {
          const textSize = 10;
          const dir_node_html = `<div class="d-flex flex-column justify-center  align-center ma-auto" style="padding: 0.5rem; border-radius: 50%; width: 50px; height: 50px; background-color: #ececff; border: 2px solid #1b76d2">` +
            `<p style="margin: 0"><i class="v-icon notranslate mdi mdi-folder-sync" alt="" style="font-size: 30px; color: #1b76d2;" ></i></p>` +
            `</div>` +
            `<p class="pl-1 ma-auto" style="font-size: ${textSize}px;  color:#535353; text-align: center">${dir.nickname}</p>`;
          return dir_node_html
        },
        generate_output_dir_html: function (dir) {
          const textSize = 10;
          const dir_node_html = `<div class="d-flex flex-column justify-center  align-center ma-auto" style="padding: 0.5rem; border-radius: 50%; width: 50px; height: 50px; background-color: #ececff; border: 2px solid #1b76d2">` +
            `<p style="margin: 0"><i class="v-icon notranslate mdi mdi-folder-table" alt="" style="font-size: 30px; color: #1b76d2;" ></i></p>` +
            `</div>` +
            `<p class="pl-1 ma-auto" style="font-size: ${textSize}px;  color:#535353; text-align: center">${dir.nickname}</p>`;
          return dir_node_html
        },
        draw_pipeline: async function (job, output_directory) {
          // Checks if the browser is supported
          if (!mxClient.isBrowserSupported()) {
            // Displays an error message if the browser is not supported.
            mxUtils.error('Browser is not supported!', 200, false);
          } else {
            let model = this.model;
            if (!this.model) {
              model = new mxGraphModel();
              this.model = model;
            }
            let node = document.getElementById('container');
            let graph = this.graph;
            if (!this.graph) {
              graph = new mxGraph(node, model);
              this.graph = graph;
            }

            // First clear everything.
            graph.getModel().beginUpdate();
            graph.removeCells(graph.getChildVertices(graph.getDefaultParent()));
            graph.getModel().endUpdate();

            let style = graph.getStylesheet().getDefaultEdgeStyle();
            style[mxConstants.STYLE_CURVED] = '1';
            style[mxConstants.STYLE_EDGE] = mxConstants.EDGESTYLE_ENTITY_RELATION;
            // style.put(mxConstants.STYLE_EDGE, mxConstants.EDGESTYLE_ENTITY_RELATION);
            let parent = graph.getDefaultParent();
            graph.setAutoSizeCells(true);
            graph.setCellsEditable(false);
            graph.setHtmlLabels(true);
            // graph.setCellsMovable(false);
            graph.setCellsResizable(false);
            graph.setCellsSelectable(false);
            // Adds cells to the model in a single step

            // Swimlanes config
            graph.setDropEnabled(true);
            graph.setSplitEnabled(false);

            model.beginUpdate();

            const dir_list = job.attached_directories_dict.attached_directories_list;
            try {
              // TODO: move this to a per component style function.
              const style = this.get_parent_style_data();
              const dirs_vertex = [];

              dir_list.forEach((dir, i) => {
                const dir_node_html = this.generate_dir_html(dir)
                let vertx = graph.insertVertex(parent, null, dir_node_html, 0, 0, 0, 0, style);
                dirs_vertex.push(vertx);
              });

              const job_node_html = this.generate_job_html(job)
              const style_job = this.get_parent_style_data('64bc47');
              let vertx_job = graph.insertVertex(parent, null, job_node_html, 0, 0, 0, 0, style_job);
              graph.updateCellSize(vertx_job)
              vertx_job.geometry.grow(10);

              // Draw edges from sync dirs to job
              dirs_vertex.forEach((v, i) => {
                let e1 = graph.insertEdge(parent, null, '', v, vertx_job);
                graph.updateCellSize(v)
                graph.updateCellSize(e1)
                v.geometry.grow(10)
              })

              // Add Output dir vertex
              if (output_directory) {
                const ouput_dir_node_html = this.generate_output_dir_html(output_directory)
                let vertx_output = graph.insertVertex(parent, null, ouput_dir_node_html, 0, 0, 0, 0, style);
                graph.updateCellSize(vertx_output)
                vertx_output.geometry.grow(10);
                graph.insertEdge(parent, null, this.job.output_dir_action, vertx_job, vertx_output, 'defaultEdge;verticalAlign=top;verticalLabelPosition=bottom');
              }
              // This layout helps put the graph in a pipeline manner. From left to right.
              let layout = new mxHierarchicalLayout(graph, 'west');
              layout.execute(parent);
            } finally {
              // Updates the display
              model.endUpdate();
            }
          }
        },
        fetch_job: async function () {
          const response = await axios.post(
            `/api/v1/job/${this.$props.job_id}/builder/info`, {
            mode_data: 'job_detail',
            refresh_stats: false
          });
          if (response.data.job && response.data.job.attached_directories_dict
            && response.data.job.attached_directories_dict.attached_directories_list) {
            this.data = response.data.job.attached_directories_dict.attached_directories_list.map((dir, i) => {
              return {
                id: dir.directory_id,
                name: dir.nickname,
                status: 'succeed',
                next: [
                  {
                    index: 1 + response.data.job.attached_directories_dict.attached_directories_list.length
                  }
                ]
              }
            })
            this.job = response.data.job;
            return this.job;
          }

        },

      }
    }
  ) </script>
