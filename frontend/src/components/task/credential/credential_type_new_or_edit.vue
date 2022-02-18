<template>
  <div id="">

    <v-card>
      <v-container>

        <v-layout column>

          <v-card-title v-if="mode=='new'">
            New Award
          </v-card-title>

          <v-card-title v-if="mode=='edit'">
            Edit Award
          </v-card-title>

          <!-- Name / New -->
          <div v-if="mode=='edit'">

            <v-text-field label="Name"
                          v-model="name">
            </v-text-field>

          </div>

          <div v-if="mode=='new'
                    && !credential_type.id">

            <v-text-field label="Name"
                          v-model="name">
            </v-text-field>

             <v-btn v-if="mode=='new'"
                    data-cy="create-credential-button"
                   @click="new_credential_type_api"
                   :loading="loading"
                   :disabled="loading"
                   color="primary">
              Create
            </v-btn>
          </div>
          <!-- Name / New -->

          <!-- Image -->
          <div v-if='credential_type.id'>

            <h2> Upload an icon for {{name}} </h2>

          <vue-dropzone ref="credential"
                        id="dropzone"
                        :options="dropzoneOptions"
                        v-on:vdropzone-success="upload_success">
          </vue-dropzone>

          </div>
          <!-- Image -->

          <div v-if="mode=='edit'">

            <v-layout>
                <v-flex>
                  <v-btn @click="edit_credential_type_api('UPDATE')"
                         :loading="loading"
                         :disabled="loading"
                         color="primary">
                    Update
                  </v-btn>
                </v-flex>

                <v-spacer></v-spacer>

                <v-flex>
                  <!-- Archive button -->

                  <!--
                    not sure of fan of this being here should maybe be more from list
                    perspective? the api call is in this component
                    so just leaving it for now-->

                  <button_with_confirm
                    @confirm_click="edit_credential_type_api('ARCHIVE')"
                    color="warning"
                    icon="archive"
                    :icon_style="true"
                    tooltip_message="Archive"
                    confirm_message="Archive"
                    :loading="loading"
                    :disabled="loading"
                                        >
                  </button_with_confirm>
                  <!-- Archive button -->
                </v-flex>
              </v-layout>
            </div>
        </v-layout>
      </v-container>

      <v_error_multiple :error="error">
      </v_error_multiple>

      <v-alert type="success"

                v-if="show_success">
        Updated.
      </v-alert>

    </v-card>

  </div>
</template>

<script lang="ts">

  import axios from '../../../services/customAxiosInstance';
  import sillyname from 'sillyname';


  import Vue from "vue"; export default Vue.extend( {
    name: 'credential_new',
    props: {
      'project_string_id': {
        default: null
      },
      'credential_type_prop': {
        default: null
      },
      'mode': { // new, edit
        default: 'new',
        type: String
      }
    }
    ,

    data() {
      return {

        loading: false,

        credential_type: {},

        error: {},
        show_success: false,

        name: "",
        old_name: "",

        description_markdown: ""
        /*  hide description since not clear what need for it
           is and I think it makes the system see more complicated then
             needed. Could bring back in future
          */

      }
    },
    watch: {
      credential_type_prop(item) {
        this.description_markdown = item.description_markdown
        this.name = item.name
      }
    },
    mounted() {
      if (!this.project_string_id) {
        this.project_string_id = this.$store.state.project.current.project_string_id
      }
      if (!this.credential_type_prop) {
        this.name = sillyname().split(" ")[0]
        this.description_markdown = "default"
      } else {

        this.description_markdown = this.credential_type_prop.description_markdown
        this.name = this.credential_type_prop.name
        // TODO not clear which scheme we want to use here
        // since we were getting the id for the upload...
        this.credential_type = this.credential_type_prop
      }
    },
    beforeDestroy() {
      this.credential_type = {}
    },
    computed: {
      dropzoneOptions: function () {

        return {
          url: '/api/v1/project/' + this.project_string_id + '/credential/update/image',
          maxFiles: 1,
          parallelUploads: 1,
          thumbnailWidth: 150,
          maxFilesize: 30,
          dictDefaultMessage: "Drop icon here to upload. Small images work best.",
          headers: {
            "credential_type_id": this.credential_type.id
          }
        }
      }
    },
    methods: {
      reset: function(){
        this.credential_type = {};
        this.name = sillyname().split(" ")[0]
      },
      new_credential_type_api: function () {

        this.loading = true
        this.error = { }
        this.show_success = false

        axios.post(
          '/api/v1/project/' + this.project_string_id
        + '/credential/type/new',
          {
            name: this.name,
            description_markdown: this.description_markdown

          }).then(response => {

            if (response.data.log.success == true) {

              this.credential_type = response.data.credential_type

              this.show_success = true
              this.$emit('refresh_list')
              this.loading = false
            }

          }).catch(error => {
            this.error= error.response.data.log.error
            this.loading = false
            console.error(error)
          });

      },
      upload_success: function (file) {

        let response = JSON.parse(file.xhr.response)

        // TODO Not clear how we want to handle refreshing
        // this isn't quite working the way we want
        // making a second credential after this.
        // this.name = ""
        // this.description_markdown = ""
        /*
        var self = this
        setTimeout(function () {
          self.$emit('refresh_list')
        }, 2000)
        */

      },


      edit_credential_type_api: function (MODE) {

        this.loading = true
        this.error = { }
        this.show_success = false

        axios.post(
          '/api/v1/project/' + this.project_string_id
        + '/credential_type/edit',
          {
            name: this.name,
            description_markdown: this.description_markdown,
            id : this.credential_type.id,
            mode: MODE

          }).then(response => {

            this.credential_type = response.data.credential_type

            this.show_success = true
            this.$emit('edit_success')
            this.loading = false


          }).catch(error => {
            this.error= error.response.data.log.error
            this.loading = false
            console.error(error)
          });

      },

    }
  }
) </script>
