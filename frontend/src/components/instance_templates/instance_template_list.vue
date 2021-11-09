<template>


  <v-container class="pa-0 mt-8">
    <v-alert type="success" :dismissible="true" v-model="show_success_alert">Instance template created successfully.
    </v-alert>
    <v-card style="overflow-y:auto; max-height: 700px" elevation="3" class="pr-4">
      <v-card-title>
        Instance Templates
        <v-btn icon color="primary" data-cy="new_instance_template" @click="open_instance_template_create_dialog">
          <v-icon size="36">mdi-plus</v-icon>
        </v-btn>
        <v-btn icon color="primary" @click="fetch_instance_templates">
          <v-icon size="36">mdi-refresh</v-icon>
        </v-btn>
      </v-card-title>
      <regular_table
        :loading="loading"
        :header_list="header_list"
        :column_list="column_list"
        :item_list="instance_template_list"
        :elevation="0"
        @row_hover_index="table_row_hover_index = $event"
      >
        <template slot="name" slot-scope="props">
          <h3>{{props.item.name}}</h3>
        </template>
        <template slot="actions" slot-scope="props">

          <v-layout>

            <!-- menu left ?-->

            <tooltip_button
              tooltip_message="Edit"
              icon="edit"
              :close_by_button="true"
              @click="edit_instance_template(props.item)"
              :disabled="props.item.instance_list[0].type != 'keypoints'"
              color="primary"
              :icon_style="true"
            >
            </tooltip_button>


            <button_with_menu
              tooltip_message="Archive"
              icon="delete"
              :close_by_button="true"
              color="error"
            >

              <template slot="content">
                <v-layout column>

                  <v-alert type="warning"
                  >
                    You will no longer be able to use this instance template.
                  </v-alert>
                  <!-- TODO option to delete all assoicated instances? -->

                  <v-btn @click="archive_instance_template(props.item)"
                         color="error"
                         :loading="loading"
                         :disabled="loading">
                    <v-icon>delete</v-icon>
                    Archive {{ props.item.name }}
                  </v-btn>

                </v-layout>
              </template>

            </button_with_menu>

          </v-layout>
        </template>

      </regular_table>


    </v-card>
    <instance_template_creation_dialog
      :project_string_id="project_string_id"
      :instance_template="selected_instance_template"
      ref="instance_template_creation_dialog"
      @instance_template_create_success="instance_template_create_success"
    ></instance_template_creation_dialog>
  </v-container>


</template>

<script lang="ts">

  import axios from 'axios';
  import instance_template_creation_dialog from './instance_template_creation_dialog';

  import Vue from "vue";

  export default Vue.extend({
      name: 'instance_template_list',
      components: {
        instance_template_creation_dialog
      },
      props: {
        'project_string_id': {},
      },
      watch: {},
      mounted() {
        this.fetch_instance_templates();
      },
      data() {
        return {
          show_success_alert: false,
          search: null,
          is_open: false,
          loading: false,
          instance_template_dialog_open: false,
          selected_instance_template: undefined,
          table_row_hover_index: -1,

          instance_template_list: [],
          header_list: [
            {
              text: "Name",
              align: 'left',
              value: 'name'
            },
            {
              text: "Actions",
              align: 'left',
              value: undefined
            },
          ],
          column_list: [
            'name',
            'actions'
          ]

        }
      },

      methods: {
        archive_instance_template: async function(instance_template){
          try{
            if(!this.$props.project_string_id){
              return
            }
            const response = await axios.post(`/api/v1/project/${this.$props.project_string_id}/instance-template/${instance_template.id}`,
              {
                status: 'archive'
              })
            if (response.status === 200) {
              this.instance_template_list = this.instance_template_list.filter(it => it.id != instance_template.id)
            }
          }
          catch(error){

          }
          finally {

          }

        },
        edit_instance_template: function(instance_template){
          this.selected_instance_template = instance_template;
          this.$refs.instance_template_creation_dialog.open();
        },
        open_instance_template_create_dialog: function () {
          this.selected_instance_template = undefined;
          this.$refs.instance_template_creation_dialog.open();
        },
        instance_template_create_success: function(){
          this.show_success_alert = true;
          this.fetch_instance_templates()
        },
        fetch_instance_templates: async function () {

          if (this.project_string_id == null) {
            return
          }
          try {
            this.loading = true;
            const response = await axios.post(`/api/v1/project/${this.$props.project_string_id}/instance-template/list`, {});
            if (response.data.instance_template_list) {
              this.instance_template_list = response.data.instance_template_list;
            }

          } catch (error) {

          }
          finally {
            this.loading = false;
          }

        },


      }
    }
  ) </script>
