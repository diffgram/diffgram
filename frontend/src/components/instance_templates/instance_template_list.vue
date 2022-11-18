<template>
  <v-container fluid class="pa-0">
    <v-alert type="success" :dismissible="true" v-model="show_success_alert">Instance template created successfully.
    </v-alert>
    <v-progress-linear indeterminate v-if="loading"></v-progress-linear>
    <v-card v-if="!loading" style="overflow-y:auto; max-height: 700px" elevation="0">
      <v-card-title>
        <v-btn icon color="primary" data-cy="new_instance_template" @click="open_instance_template_create_dialog">
          <v-icon size="36">mdi-plus</v-icon>
        </v-btn>

        <v-spacer></v-spacer>

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

            <standard_button
              tooltip_message="Edit"
              icon="edit"
              :close_by_button="true"
              @click="edit_instance_template(props.item)"
              :disabled="props.item.instance_list[0].type != 'keypoints'"
              color="primary"
              :icon_style="true"
            >
            </standard_button>


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

  </v-container>


</template>

<script lang="ts">

  import axios from '../../services/customInstance';
  import instance_template_creation_dialog from './instance_template_creation_dialog';
  import instance_template_creation_page from './instance_template_creation_page';

  import Vue from "vue";

  export default Vue.extend({
      name: 'instance_template_list',
      components: {
        instance_template_creation_page
      },
      props: {
        'project_string_id': {},
        'schema_id': {
          required: true
        },
      },
      watch: {
        schema_id: function(){
          this.fetch_instance_templates();
        }
      },
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
          // this.selected_instance_template = undefined;
          // this.$refs.instance_template_creation_dialog.open();
          this.$router.push(`/project/${this.$props.project_string_id}/schema/${this.schema_id}/create-template`)
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
            const response = await axios.post(`/api/v1/project/${this.$props.project_string_id}/instance-template/list`, {
              schema_id: this.schema_id
            });
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
