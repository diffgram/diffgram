<template>

  <v-card width="100%" class="d-flex justify-center flex-column align-center pa-4" elevation="0">
    <v-progress-circular
      :size="50"
      v-if="loading"
      color="primary"
      indeterminate
    ></v-progress-circular>

    <div style="width: 100%" class="graphContainer" ref="container" id="container" data-cy="mxgraphcontainer"></div>


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
    mxDivResizer,
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
  import axios from '../../services/customAxiosInstance';

  const outputIcon = './icon/output.png'
  const inputIcon = './icon/input.png'

  // export default hue1


  import Vue from "vue";

  export default Vue.extend({
      name: 'project_pipeline',
      props: ['job_id', 'job_object', 'initial_job_list'],
      components: {},

      data() {
        return {
          jobs: null,
          jobs_by_id: {},
          directories: null,
          directories_by_id: {},
          graph: undefined,
          loading: false,
          model: undefined,
        }
      },
      created() {
        this.populate_data();

      },
      watch: {},
      computed: {},
      methods: {
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
        get_cell_style_data: function () {
          // Gets the cell data depending on the object to be created (Dir, Task, Connection, etc..)
          const outputIcon = '../../../assets/mxgraph/public/icon'
          const styleobj = {
            fillColor: '#ececff',
            strokeColor: '#1b76d2',
            strokeWidth: '2',
            fontColor: '#535353',
            labelPadding: 80,
            sourcePerimeterSpacing: 500,
            fontStyle: 1,
            fontSize: 20,
            imageWidth: 80,
            imageHeight: 80,
            lineHeight: 6,
            [mxConstants.STYLE_SHAPE]: 'ellipse',
            STYLE_WHITE_SPACE: 'wrap',
            STYLE_ASPECT: 'fixed'
          };
          const style = Object.keys(styleobj).map((attr) => `${attr}=${styleobj[attr]}`).join(';')
          return style
        },
        fetch_dirs_from_jobs(jobs) {
          const result = [];
          for (const job of jobs) {
            if (job.attached_directories_dict && job.attached_directories_dict.attached_directories_list) {
              for (const dir of job.attached_directories_dict.attached_directories_list) {
                if (dir.directory_id) {
                  result.push(dir.directory_id)
                }
              }
            }
            if (job.completion_directory_id) {
              result.push(job.completion_directory_id)
            }
          }
          return [...new Set(result)]
        },
        populate_data: async function () {
          // Fetch all the job.
          this.loading = true;
          if(!this.$props.initial_job_list){

            await this.fetch_jobs();
          }
          else{
            this.jobs = this.initial_job_list;
          }
          this.jobs.map(job => {
            this.jobs_by_id[job.id] = {
              ...job
            }
          });
          // Grab all dir ids from output dirs and sync dirs.
          const directories_ids = this.fetch_dirs_from_jobs(this.jobs)
          await this.fetch_directories(directories_ids);
          if(this.directories){
            this.directories.map(dir => {
              this.directories_by_id[dir.id] = {
                ...dir
              }
            });
          }
          this.draw_pipeline(this.jobs);
          this.loading = false;
        },
        measureText(pText, pFontSize, pStyle) {
          // From https://stackoverflow.com/questions/118241/calculate-text-width-with-javascript
          var lDiv = document.createElement('div');

          document.body.appendChild(lDiv);

          lDiv.style.fontSize = "" + pFontSize + "px";
          lDiv.style.position = "absolute";
          lDiv.style.left = '-1000px';
          lDiv.style.top = '-1000px';

          lDiv.innerHTML = pText;

          var lResult = {
            width: lDiv.clientWidth,
            height: lDiv.clientHeight
          };

          document.body.removeChild(lDiv);
          lDiv = null;

          return lResult;
        },
        generate_job_html: function (job) {
          const textSize = 10;
          const dir_node_html = `<div class="d-flex flex-column justify-center  align-center ma-auto" style="padding: 0.5rem; border-radius: 50%; width: 50px; height: 50px; background-color:#d3ffe0; border: 2px solid #64bc47">` +
            `<p style="margin: 0"><i class="v-icon notranslate mdi mdi-brush" alt="" style="font-size: 30px; color: #64bc47;" ></i></p>` +
            `</div>` +
            `<p class="pl-1 ma-auto" style="font-size: ${textSize}px;  color:#535353; text-align: center">${job.name}</p>`;
          return dir_node_html

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
        draw_pipeline: async function (jobs) {
          // Checks if the browser is supported

          if (!mxClient.isBrowserSupported()) {
            // Displays an error message if the browser is not supported.
            mxUtils.error('Browser is not supported!', 200, false);
            alert('Mxgraph broweser not supported.')
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
            graph.setResizeContainer(false);
            graph.useScrollbarsForPanning = true;
            graph.recursiveResize = true;
            graph.autoSizeCellsOnAdd = true;
            // Adds cells to the model in a single step
            model.beginUpdate();
            //console.log(this.jobs, 'aaaaaa')
            try {
              // TODO: move this to a per component style function.
              const style = this.get_cell_style_data();
              const style_parent_job = this.get_parent_style_data('#64bc47');
              const style_parent_dir = this.get_parent_style_data();

              this.jobs.forEach((job, i) => {

                const job_node_html = this.generate_job_html(job)

                let vertx_job = graph.insertVertex(parent, null, job_node_html, 0, 0, 0, 0, style_parent_job);
                this.jobs_by_id[job.id].vertex = vertx_job
                // const style_vertx_job = vertx_job.getStylesheet();
                graph.updateCellSize(vertx_job);
                if(job.attached_directories_dict && job.attached_directories_dict.attached_directories_list){
                  const dir_list = job.attached_directories_dict.attached_directories_list;

                  dir_list.forEach((dir, i) => {
                    const dir_node_html = this.generate_dir_html(dir)
                    let vertx;
                    if(!this.directories_by_id[dir.directory_id].vertex){
                      vertx = graph.insertVertex(parent, null, dir_node_html, 0, 0, 0, 0, style_parent_dir);

                      this.directories_by_id[dir.directory_id].vertex = vertx
                    }
                    else{
                      vertx = this.directories_by_id[dir.directory_id].vertex;
                    }
                    let e1 = graph.insertEdge(parent, null, '', vertx, vertx_job);
                    graph.updateCellSize(e1)

                  })
                  // Add Output Dirs
                  const output_directory = this.directories_by_id[job.completion_directory_id]
                  if(output_directory){
                    const ouput_dir_node_html = this.generate_output_dir_html(output_directory)
                    let vertx_output;
                    if(!output_directory.vertex){
                      vertx_output = graph.insertVertex(parent, null, ouput_dir_node_html, 0, 0, 0, 0, style_parent_dir);
                    }
                    else{
                      vertx_output = output_directory.vertex;
                      this.directories_by_id[output_directory.id].vertex = vertx_output
                    }
                    graph.updateCellSize(vertx_output)
                    graph.insertEdge(parent, null, job.output_dir_action, vertx_job, vertx_output, 'defaultEdge;verticalAlign=top;verticalLabelPosition=bottom');

                  }


                }

              });

              let layout = new mxHierarchicalLayout(graph, 'west');
              layout.execute(parent);
            } finally {
              model.endUpdate();

            }
          }
        },
        fetch_directories: async function (directories_ids) {
          const project_string_id = this.$store.state.project.current.project_string_id;
          const username = this.$store.state.user.current.username;
          if (!directories_ids) {
            return false;
          }
          try {
            const response = await axios.get(`/api/project/${project_string_id}/user/${username}/working_dir/view`,
              {
                params: {
                  working_dir_ids: directories_ids
                },
              });

            if (response.data.success) {
              if(!Array.isArray(response.data.working_dir)){
                this.directories = [response.data.working_dir];
              }
              else{
                this.directories = response.data.working_dir;
              }

              return this.directories;
            }

            return false;
          } catch (error) {
            return error;
          }

        },
        fetch_jobs: async function () {
          const response = await axios.post(`/api/v1/job/list`, {
            metadata: {
              mode_data: 'job_detail',
              builder_or_trainer: {
                mode: 'builder'
              },
              project_string_id: this.$store.state.project.current.project_string_id,
              status: 'active'
            }
          });
          if (response.data.Job_list) {
            this.jobs = response.data.Job_list;
            return this.jobs;
          }

        },

      }
    }
  ) </script>
