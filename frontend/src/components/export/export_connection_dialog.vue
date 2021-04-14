<template>
  <div>
    <v-dialog v-model="main_dialog" max-width="1000px" id="export-dialog">
      <v-card>
        <v-container>
          <v-card-title>
            <span class="headline">Export data to 3rd Party Vendor</span>
          </v-card-title>

          <v-card-subtitle>
            Please select the connection where you want to send your data to:
          </v-card-subtitle>

              <v-row>
                <v-col cols="12" class="pa-0">
                  <connection_select
                    :project_string_id="project_string_id"
                    display_mode="icons"
                    v-model="selected_connection"
                    :show_new="true"
                    ref="connection_selector"
                    @onChange="set_selected_connection"
                  >
                  </connection_select>
                </v-col>
              </v-row>
              <v-row>
                <v-col cols="12" class="pa-8 pt-0">
                  <connector_export_renderer
                    :project_string_id="project_string_id"
                    :connection="selected_connection"
                    :export_obj="export_obj"
                    :show_new="true"
                    :format="format"
                    ref="connector_export_renderer"
                    @export-success="on_export_success"
                    @folder-selected="on_folder_selected"
                  ></connector_export_renderer>
                </v-col>
              </v-row>

          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn color="blue darken-1" text @click="close_dialog">Close</v-btn>
            <v-btn color="blue darken-1" text @click="start_renderer_export" :disabled="!export_ready">Start Data Export</v-btn>
          </v-card-actions>
        </v-container>
      </v-card>
    </v-dialog>
    <v-dialog
      v-model="open_success"
      id="import-dialog"
      max-width="290"
    >
      <v-card>
        <v-card-title class="headline">Export Started Successfully</v-card-title>

        <v-card-text>
          <div>
            <p>Export sent successfully! Files have been sent to your 3rd party provider.</p>
            <br>
            <p class="align-center text-center">
              <v-icon right color="success" size="x-large" dark dense class="display-3"> mdi-check</v-icon>
            </p>
          </div>
        </v-card-text>

        <v-card-actions class="d-flex justify-center">
          <v-btn
            color="gray darken-1"
            text
            @click="close_success_dialog"
          >
            Close
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
  import Connector_export_renderer from "./connector_export_renderer";
  import connection_select from "../connection/connection_select";
  export default {
    components: {Connector_export_renderer, connection_select},
    props: {
      'open':{
        default: false
      },
      'export_obj':{
        default: {}
      },
      'project_string_id':{
        default: null
      },
      'format': {
        default: 'JSON'
      }
    },
    name: "export_connection_dialog",
    computed:{},
    data (){
      return {
        selected_connection: {},
        open_success: false,
        main_dialog: false,
        export_ready: false,
      }
    },
    methods: {
      on_folder_selected(selection){
        if(selection.length > 0){
          this.export_ready = true;
        }
        else{
          this.export_ready = false;
        }

      },
      open_export_dialog(){
        this.main_dialog = true;
      },
      close_dialog(){
        this.main_dialog = false
      },
      open_success_dialog(){
        this.open_success = true;
      },
      on_export_success(){
        this.close_dialog();
        this.open_success_dialog();
      },
      close_success_dialog(){
        this.open_success = false;
      },
      set_selected_connection(connection){
        this.selected_connection = connection;
      },
      async start_renderer_export(){
        const result = await this.$refs.connector_export_renderer.export_start();
        if(result.status && result.status === 200){
          this.close_dialog();
          this.open_success_dialog();
        }

      },
    },
    watch:{
      main_dialog(val){
        if(this.$refs.connection_selector){
          this.$refs.connection_selector.connection_list_api();
        }

      }
    }
  }
</script>

<style scoped>

</style>
