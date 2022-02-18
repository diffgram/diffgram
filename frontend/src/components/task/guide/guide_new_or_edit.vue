<template>
  <div id="">

    <v-card>
      <v-container>

        <v-layout column>

          <v-card-title v-if="mode=='new'">
            New Guide
          </v-card-title>

          <v-card-title v-if="mode=='edit'">
            Edit Guide
          </v-card-title>

          <v_error_multiple :error="error">
          </v_error_multiple>

          <v-alert type="success"

                   v-if="success">
            Updated.
          </v-alert>

          <v-text-field label="Name"
                        v-model="name">
          </v-text-field>

          <v-textarea label="Markdown description"
                      v-model="description_markdown">
          </v-textarea>
          Preview
          <VueMarkDown :source="description_markdown">
          </VueMarkDown>

          <!--
          TODO Add examples from completed files:

          (Specify correct or not? how to add incorrect ones)

          Should this offer a viewer right here?
          Or better to have in core interface, and then can select to attach them here?
          Maybe just default to ones already marked as "samples"? "sample example or counter exampple"

          TODO add or update here
          -->

          <v-btn v-if="mode=='new'"
                 @click="guide_new_api"
                 :loading="loading"
                 :disabled="loading"
                 color="primary">
            Create
          </v-btn>

          <div v-if="mode=='edit'">
            <v-layout>
              <v-flex>
                <v-btn @click="guide_edit_api('UPDATE')"
                       :loading="loading"
                       :disabled="loading"
                       color="primary">
                  Update
                </v-btn>
              </v-flex>

              <v-spacer></v-spacer>

              <v-flex>
                <!-- Archive button -->
                <button_with_confirm
                  @confirm_click="guide_edit_api('ARCHIVE')"
                  color="red"
                  icon="archive"
                  :icon_style="true"
                  tooltip_message="Archive"
                  confirm_message="Archive"
                  :loading="loading">
                </button_with_confirm>
                <!-- Archive button -->

              </v-flex>
            </v-layout>
          </div>

        </v-layout>
      </v-container>

    </v-card>

  </div>
</template>

<script lang="ts">

  import axios from '../../../services/customInstance';
  import sillyname from 'sillyname';


  import Vue from "vue"; export default Vue.extend( {
    name: 'task_guide_new',

    props: {
      'project_string_id': {
        default: null
      },
      'guide': {
        default: null
      },
      'mode': { // new, edit
        default: null
      }
    },

    data() {
      return {

        loading: false,
        error: {},
        success: false,

        description_markdown: null,
        name: null,


      }
    },

    watch: {
      guide(item) {
        this.description_markdown = item.description_markdown
        this.name = item.name
      }
    },
    computed: {
    },
    created() {

      if (!this.guide) {
        this.name = sillyname().split(" ")[0]
        this.description_markdown = "# Markdown supported <3"
      } else {
        // This seeems to be needed for the first pass was watcher doesn't detect it...
        this.description_markdown = this.guide.description_markdown
        this.name = this.guide.name
      }

    },
    methods: {

      guide_new_api: function () {

        this.loading = true
        this.error = {}
        this.success = false

        axios.post(
          '/api/v1/project/' + this.project_string_id +
          '/guide/new',
          {
            name: this.name,
            description_markdown: this.description_markdown

          }).then(response => {

            if (response.data.log.success == true) {
              this.success = true

              this.$emit('guide_new_success', response.data.guide)
            }
            this.loading = false

          }).catch(error => {

            if (error.response.status == 400) {
              this.error = error.response.data.log.error
            }
            this.loading = false
            console.error(error)
          });

      },

      guide_edit_api: function (MODE) {

        this.loading = true
        this.error = {}
        this.success = false

        axios.post(
          '/api/v1/project/' + this.project_string_id +
          '/guide/edit',
          {
            name: this.name,
            description_markdown: this.description_markdown,
            id : this.guide.id,
            mode: MODE

          }).then(response => {

            this.$emit('edit_guide_success')
            this.loading = false

          }).catch(error => {

            if (error.response.status == 400) {
              this.error = error.response.data.log.error
            }
            this.loading = false
            console.error(error)
          });

      }

    }
  }
) </script>
