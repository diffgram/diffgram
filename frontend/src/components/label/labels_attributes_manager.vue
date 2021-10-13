<template>
  <v-layout class="pa-0 d-flex flex-column" style="min-height: 600px">
    <v-btn x-small @click="go_to_step(3)" class="text-left ml-auto mb-6" color="secondary">

      <v-icon>mdi-debug-step-over</v-icon>
      Skip, I will create labels later
    </v-btn>
    <v-layout>
      <v-row>

        <v-col cols="6">
          <div class="d-flex align-center ">
            <h2 class="font-weight-medium text--primary flex-grow-1">Labels:</h2>
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

          <labels_management_list
            :project_string_id="project_string_id"
            :label_file_list="label_file_list"
            @label_file_list_updated="on_label_file_list_updated"
          >
          </labels_management_list>

        </v-col>
        <v-col cols="6" style="border-left: 1px solid #b9d1ec" class="d-flex flex-column">
          <attribute_group_list_manager
            v-if="project_string_id"
            ref="attribute_group_list_manager"
            :show_borders="true"
            :project_string_id="project_string_id"
            :mode = "'edit'"
            :show_empty_placeholder="true"
            @attribute_group_list_updated="on_attribute_group_list_updated"
          >
          </attribute_group_list_manager>

        </v-col>
      </v-row>

    </v-layout>
    <v-btn :disabled="label_file_list.length == 0 && attribute_group_list.length === 0" x-large @click="go_to_step(3)" class="text-left ml-auto mb-6" color="success">
      Continue
    </v-btn>
  </v-layout>

</template>

<script lang="ts">

  import axios from 'axios';
  import Vue from "vue";
  import v_labels_edit from '../annotation/labels_edit'
  import attribute_group_new from '../attribute/attribute_group_new'
  import attribute_group_list_manager from '../attribute/attribute_group_list_manager'
  import labels_management_list from '../label/labels_management_list'

  export default Vue.extend({
      name: 'labels_attributes_manager',
      components:{
        attribute_group_list_manager,
        labels_management_list,
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

          openedPanel: false,
          label_file_list: [],
          attribute_group_list: [],
          label_file_colour_map: {}
        }
      },

      methods: {
        on_attribute_group_list_updated: function(new_attr_list){
          this.attribute_group_list = new_attr_list;
        },
        update_attributes_label_file_list: function(new_label_file_list){
          this.$refs.attribute_group_list_manager.update_label_file_list_for_all_attributes(new_label_file_list)
        },
        on_label_file_list_updated: function(new_label_file_list){
          this.label_file_list = new_label_file_list;
          this.update_attributes_label_file_list(new_label_file_list)
        },
        on_label_created: function(label_file){
          this.label_file_list.push(label_file);
          this.update_attributes_label_file_list(this.label_file_list)
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

      }
    }
  ) </script>

<style scoped>

  .skip-title{
    color: #1565c0 !important;
  }
  .skip-title:hover{
    cursor: pointer;
  }
</style>
