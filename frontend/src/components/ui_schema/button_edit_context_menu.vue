<template>
  <v-menu  persistent
           :close-on-click="false"
           :close-on-content-click="false"
           :offset-overflow="true"
           :position-x="150"
           :position-y="50"
           :right="true"
           offset-y
           v-if="button"
           v-model="open">
      <v-card class="pa-4">
        <v-card-text>
          <v-tabs
            v-model="tab"
            background-color="#f0f0f0"
          >
            <v-tabs-slider color="secondary"></v-tabs-slider>

            <v-tab
              style="border-bottom: 1px solid #e0e0e0"
              v-for="item in ['Style', 'Actions']"
              :key="item"
            >
              {{ item }}
            </v-tab>
            <v-tabs-items v-model="tab">
              <v-tab-item :key="1">
                <div class="d-flex flex-column">
                  <v-text-field class="custom-text-field" label="Button Title" v-model="button.display_name"></v-text-field>
                  <slider-picker class="mb-4" v-model="button_color" @change="change_color"/>
                </div>
              </v-tab-item>
              <v-tab-item :key="2">
                <h4 class="">Actions: </h4>

                <v-select return-object
                          item-text="name"
                          :items="actions_list" @change="set_action"></v-select>
              </v-tab-item>
            </v-tabs-items>
          </v-tabs>
        </v-card-text>


        <v-card-actions class="d-flex justify-end">
          <v-btn color="success" @click="save">
            Save
          </v-btn>
        </v-card-actions>
      </v-card>
  </v-menu>

</template>

<script lang="ts">

import Vue from 'vue';
import axios from '../../services/customInstance';
import {ActionCustomButton} from '../../types/ui_schema/Buttons'
import {types} from "sass";
import String = types.String;
export default Vue.extend({
  name: 'ButtonEditContextMenu',
  components: {

  },
  props: {
    'project_string_id': {type: String, required: true},
    'button': {
      required: true,

    }

  },
  data() {
    // move context menu off the page out of view when hidden
    return {
      button_color: {},
      tab: 0,
      actions_list: [
        {
          'name': 'Complete Task',
          'key': 'complete_task',
        },
        {
          'name': 'Set Attribute',
          'key': 'set_attribute',
        },

      ],
      open: false
    }
  },
  watch:{
    button_color: {
      deep: true,
      handler: function(val){
        this.button.color = val.hex
      }
    }
  },
  computed: {
  },
  methods: {
    set_action: function(){
      this.action = new ActionCustomButton();
    },
    open_menu: function(){
      this.open = true
    },
    close_menu: function(){
      this.open = false;
    },
    change_color: function(val){
      console.log('CHANGE COLOR', val)
      this.button.color = val
    },
    save: async function(){
      await this.$store.commit('update_custom_button', this.button.name, this.button)
      await this.update_ui_schema_with_servercall()
      this.open = false

    },
    get_ui_schema: function () {
      if (this.$store.state.ui_schema.current == undefined) {
        throw new Error("this.$store.state.ui_schema.current is undefined")
      }
      return this.$store.state.ui_schema.current
    },
    update_ui_schema_with_servercall: async function(){
      if (!this.get_ui_schema() || !this.get_ui_schema().id) {
        return
      }

      this.loading = true;
      this.error = {}

      try{
        const response = await axios.post(
          `/api/v1/project/${this.project_string_id}/ui_schema/update`,
          this.get_ui_schema()
        )
      }
      catch (error) {
        this.error = this.$route_api_errors(error)
        console.error(error)

      }
      finally {
        this.loading = false;
      }

    },
  }
});
</script>

<style>
.custom-text-field {
  font-size: 16px;
}
</style>
