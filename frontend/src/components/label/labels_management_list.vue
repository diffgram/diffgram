<template>
  <div>
    <v-list class="mt-4" v-if="label_file_list.length > 0">
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
  </div>


</template>

<script lang="ts">

import axios from 'axios';

import Vue from "vue"; export default Vue.extend( {
  name: 'labels_management_list',
  props: {
    'label_file_list':{
      default: [],
    },
    'project_string_id':{
      default: null,
    }
  },
  data() {
    return {
      labels_loading: false,
      edit_label_menu: false,
    }
  },
  computed: {
  },
  created() {

  },
  methods: {

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
    on_label_updated: function(label_file){

      let old = this.label_file_list.find(elm => elm.id === label_file.id);
      if(old){
        let index = this.label_file_list.indexOf(old);
        this.label_file_list[index] = label_file;
        this.label_file_list[index].label = {...label_file.label};
      }

      let button = this.$refs[`edit_button_label_${label_file.id}`][0];
      button.close_menu();

      this.$emit('label_file_list_updated', this.label_file_list.map(elm => elm));

    },
  }
}

) </script>
