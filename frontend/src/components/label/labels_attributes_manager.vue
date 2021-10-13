<template>
  <v-layout class="pa-0 d-flex flex-column">

    <v-layout>
      <v-row>

        <v-col cols="6">
          <div class="d-flex align-center ">
            <h1 class="font-weight-medium text--primary flex-grow-1">Labels:</h1>
            <v-btn color="primary" icon @click="fetch_labels"><v-icon>mdi-refresh</v-icon></v-btn>
            <button_with_menu
              datacy="new_label_template"
              button_text="Create Label"
              tooltip_message="Create Label"
              small
              @click="$store.commit('set_user_is_typing_or_menu_open', true)"
              @update:return-value="$store.commit('set_user_is_typing_or_menu_open', false)"
              icon="add"
              icon_color="white"
              color="primary"
              offset="x"
            >

              <template slot="content">

                <v_labels_new @label_created="on_label_created">
                </v_labels_new>

              </template>

            </button_with_menu>
          </div>
          <v-list v-if="label_file_list.length > 0">
            <v-list-item class="label-row d-flex justify-start align-center" v-for="label_file in label_file_list">
              <v-icon :color="label_file.colour.hex" class="pr-2">mdi-flag</v-icon>
              <h2 class="font-weight-medium text--primary flex-grow-1"> {{label_file.label.name}}</h2>

              <button_with_menu
                :ref="`edit_button_label_${label_file.id}`"
                tooltip_message="Edit"
                icon="edit"
                :close_by_button="true"
                @update:return-value="$store.commit('set_user_is_typing_or_menu_open', false)"
                @click="$store.commit('set_user_is_typing_or_menu_open', true)"
                color="primary"
              >
                <template slot="content">

                  <v_labels_edit :project_string_id="project_string_id"
                                 :label_file_prop="label_file"
                                 :edit_label_menu="edit_label_menu"
                                 @label_updated="on_label_updated"
                                 :key="label_file.id">
                  </v_labels_edit>

                </template>

              </button_with_menu>
              <button_with_menu
                tooltip_message="Delete"
                icon="delete"
                :close_by_button="true"
                color="primary"
              >

                <template slot="content">
                  <v-layout column>

                    <v-alert type="warning"
                    >
                      Existing instances with this label
                      will not be effected.
                    </v-alert>
                    <!-- TODO option to delete all assoicated instances? -->

                    <v-btn @click="label_file_update('REMOVE', label_file)"
                           color="error"
                           :loading="labels_loading"
                           :disabled="labels_loading">
                      <v-icon>delete</v-icon>
                      Delete {{ label_file.label.name }}
                    </v-btn>

                  </v-layout>
                </template>

              </button_with_menu>

            </v-list-item>
          </v-list>
          <v-container v-else style="min-height: 500px" class="d-flex flex-column justify-center align-center">
            <h1 class="font-weight-medium text--primary text-center">No Labels Yet</h1>
            <v-icon color="secondary" size="128">mdi-flag</v-icon>
            <h4 class="font-weight-medium text--primary text-center">
              Create one by clicking the "Create Label Button"
            </h4>
          </v-container>
        </v-col>
        <v-col cols="6" style="border-left: 1px solid #b9d1ec" class="d-flex flex-column">
          <div class="d-flex align-center justify-space-between">
            <h1 class="font-weight-medium text--primary">Attributes:</h1>
            <button_with_menu
              datacy="new_label_attribute"
              button_text="Create Attribute"
              tooltip_message="Create Attribute"
              small
              @click="$store.commit('set_user_is_typing_or_menu_open', true)"
              @update:return-value="$store.commit('set_user_is_typing_or_menu_open', false)"
              icon="add"
              icon_color="white"
              color="primary"
              offset="x"
            >

              <template slot="content">
                <attribute_group_new :project_string_id="project_string_id">

                </attribute_group_new>

              </template>

            </button_with_menu>
          </div>
          <v-expansion-panels
            v-if="attribute_group_list.length > 0"
            v-model="openedPanel"
            :accordion="true"
            :popout="false"
            :inset="false"
            :multiple="false"
            :focusable="true"
            :disabled="false"
            :flat="false"
            :hover="false"
            :tile="true"

          >
            <v-expansion-panel
              v-for="group in attribute_group_list"
              :key="group.id"
            >
              <v-expansion-panel-header
                :data-cy="`attribute_group_header_${group.prompt}`"
                @click="update_url_with_current_group(group)"
                class="d-flex justify-start text-left">
                <h3 class="text-left d-flex align-center">
                  <attribute_kind_icons
                    class="pr-2"
                    :kind=" group.kind "
                  >
                  </attribute_kind_icons>

                  {{group.prompt}}

                  <div v-if="!group.prompt" :data-cy="`attribute_group_header_Untitled Attribute Group`">
                    Untitled Attribute Group
                  </div>

                </h3>

                <!-- TODO maybe, play with this more
                  eg maybe in edit mode show internal tag-->

              </v-expansion-panel-header>

              <v-expansion-panel-content>
                <attribute_group
                  :project_string_id="project_string_id"
                  :mode="mode"
                  :group="group"
                  :key="group.id"
                  @attribute_change="$emit('attribute_change', $event)"
                  :current_instance="current_instance"
                >
                </attribute_group>

                <div v-if="mode == 'edit'">
                  ID: {{group.id}}
                </div>
              </v-expansion-panel-content>

            </v-expansion-panel>

          </v-expansion-panels>
          <v-container v-else style="min-height: 500px" class="d-flex flex-column justify-center align-center">
            <h1 class="font-weight-medium text--primary text-center">No Attributes Yet</h1>
            <v-icon color="secondary" size="128">mdi-archive</v-icon>
            <h4 class="font-weight-medium text--primary text-center">
              Create one by clicking the "Create Attribute Button"
            </h4>
          </v-container>
        </v-col>
      </v-row>
    </v-layout>
    <v-btn small @click="go_to_step(3)" class="text-left ml-auto" color="secondary">

      <v-icon>mdi-debug-step-over</v-icon>
      Skip, I will create labels later
    </v-btn>
  </v-layout>

</template>

<script lang="ts">

  import axios from 'axios';
  import Vue from "vue";
  import v_labels_edit from '../annotation/labels_edit'
  import attribute_group_new from '../attribute/attribute_group_new'

  export default Vue.extend({
      name: 'labels_attributes_manager',
      components:{
        attribute_group_new,
        v_labels_edit,
      },
      props: {
        'project_string_id': {},
      },
      watch: {},
      async mounted() {
        await this.fetch_labels();

      },
      data() {
        return {
          labels_loading: false,
          openedPanel: false,
          edit_label_menu: false,
          selected_label: null,
          label_file_list: [],
          attribute_group_list: [],
          label_file_colour_map: {}
        }
      },

      methods: {
        on_label_updated: function(label_file){

          let old = this.label_file_list.find(elm => elm.id === label_file.id);
          if(old){
            let index = this.label_file_list.indexOf(old);
            this.label_file_list[index] = label_file;
            this.label_file_list[index].label = {...label_file.label};
          }

          let button = this.$refs[`edit_button_label_${label_file.id}`][0];
          console.log('qweqwe', button)
          button.close_menu();

          console.log('label_file', old)
          this.label_file_list = this.label_file_list.map(elm => elm);

        },
        on_label_created: function(label_file){
          this.label_file_list.push(label_file)
        },
        go_to_step: function(step){
          this.$emit('skip', step)
        },
        fetch_labels: async function(){

          if (this.$props.project_string_id == null) {
            return
          }

          try{
            var url = `/api/project/${this.project_string_id}/labels/refresh`
            this.labels_loading = true

            const response = await axios.get(url, {})
            this.label_file_list = response.data.labels_out

            this.label_file_colour_map = response.data.label_file_colour_map

            this.label_refresh_loading = false
            this.$emit('labels_fetched', this.label_file_list)


          }
          catch (e) {
            console.error(e)
          }
          finally {
            this.labels_loading = false
          }
        },

        open_panel_by_id(id: number){
          if (!this.attribute_group_list) {return }
          this.openedPanel = this.attribute_group_list.findIndex(x => {
            return x.id == id
          })
        },

        async label_file_update(mode, label) {

          this.labels_loading = true
          this.info = {}  // reset
          try{
            const response = await axios.post(`/api/v1/project/${this.project_string_id}/file/update`,
              {
                'file_list': [label],
                'mode': mode
              })
            this.info = response.data.log.info

            if (mode == "REMOVE") {
              let label_file = this.label_file_list.find(elm => elm.id === label.id)
              let index = this.label_file_list.indexOf(label_file);
              this.label_file_list.splice(index, 1);

            }

          }
          catch (e) {
            console.error(e)
          }
          finally {
            this.labels_loading = false
          }


        },
      }
    }
  ) </script>

<style scoped>
  .label-row{
    border: 1px solid #e0e0e0;
    border-radius: 5px;
  }
  .skip-title{
    color: #1565c0 !important;
  }
  .skip-title:hover{
    cursor: pointer;
  }
</style>
