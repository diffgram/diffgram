<template>

      <v-stepper v-model="step"
                 :non-linear="true"
                 style="height: 100%;"
                 @change="on_change_step">

        <v-stepper-header>
          <v-stepper-step
            editable
            :complete="step > 1"
            step="1"
          >
            Kind
          </v-stepper-step>

          <v-divider></v-divider>

          <v-stepper-step
            editable
            :complete="step > 2"
            step="2"
          >
            Name
          </v-stepper-step>

          <v-divider></v-divider>

          <v-stepper-step
            editable
            :complete="step > 3"
            step="3"
          >
            Scope
          </v-stepper-step>



          <v-divider></v-divider>

          <v-stepper-step
            editable
            :complete="step > 4"
            step="4">
           Visible When
          </v-stepper-step>

          <v-divider></v-divider>

          <v-stepper-step
            editable
            :complete="step > 5"
            step="5">
            Options
          </v-stepper-step>

          <v-divider></v-divider>
          <v-stepper-step
            editable
            :complete="step > 6"
            step="6">
            Defaults
          </v-stepper-step>

        </v-stepper-header>


        <v-progress-linear
          color="secondary"
          striped
          :value="global_progress"
          height="7"
        >
        </v-progress-linear>


        <v-stepper-items style="height: 100%" class="pt-4">

          <v-stepper-content step="1" style="height: 100%" data-cy="attribute_wizard_step_1">

            <h2 class="pb-2"> 1. What Kind of Question? </h2>

            <diffgram_select
              v-if="group"
              data_cy="attribute_kind_select"
              :item_list="kind_list"
              v-model="group.kind"
              label="Kind"
              :disabled="loading"
              @input="$emit('input', group)"
              @change="$emit('change')"
            >
            </diffgram_select>

            <wizard_navigation
              @next="go_to_step(2)"
              @back="go_back_a_step()"
              :disabled_next="!group.kind"
              :back_visible="false"
              :skip_visible="false"
                               >
            </wizard_navigation>

          </v-stepper-content>

          <v-stepper-content step="2" style="height: 100%" data-cy="attribute_wizard_step_2">

            <h2> 2. Name Your Question </h2>

            <v-layout>
              <v-text-field
                label="Prompt Shown"
                data-cy="attribute_prompt"
                v-model="group.prompt"
                @input="$emit('input', group)"
                @change="$emit('change')"
              >
              </v-text-field>


              <button_with_menu
                  tooltip_message="Optional Extra Reference"
                  icon="mdi-tag"
                  :close_by_button="true"
                  :small="true"
                  color="primary"
                      >

                  <template slot="content">
                    <v-layout column>

                      <h4 class="ma-0 mt-6">Optional Extra Reference:</h4>
                      <p class="text--secondary">Field not shown to Annotators.</p>
                      <v-text-field label="Reference"
                                    data-cy="attribute_tag"
                                    v-model="group.name"
                                    @input="$emit('input', group)"
                                    @change="$emit('change')"
                      >
                      </v-text-field>

                    </v-layout>
                  </template>

              </button_with_menu>
            </v-layout>

            <wizard_navigation
              @next="go_to_step(3)"
              @back="go_back_a_step()"
              :disabled_next="!group.prompt"
              :skip_visible="false"
                               >
            </wizard_navigation>

          </v-stepper-content>

          <v-stepper-content step="3" style="height: 100%" data-cy="attribute_wizard_step_3">

            <h2> 3. Per Annotation Or File? (Optional) </h2>

            <br>
            <p>
            The Default is per Annotation: each annotation instance - e.g. a box or entity - has different values.
            </p>
            <p>
            The Alternative is per File: each file - e.g. an image, video, text - has only one set of these values.
            </p>
            <br>

            <v-layout class="justify-center align-center">
              <v-btn-toggle color="secondary" v-model="toggle_global_attribute" @change="set_is_global($event, group)">
                <v-btn>
                  <v-icon left color="primary" size="18">
                    mdi-brush
                  </v-icon>
                  Per Annotation (Default)
                </v-btn>

                <v-btn>
                  <v-icon left color="primary" size="18">
                    mdi-file
                  </v-icon>

                   Per File  

                </v-btn>
              </v-btn-toggle>
            </v-layout>

            <wizard_navigation
              @next="go_to_step(4)"
              @back="go_back_a_step()"
              :disabled_next="!group.prompt"
              :skip_visible="false"
            >
            </wizard_navigation>

          </v-stepper-content>


          <v-stepper-content step="4" style="height: 100%" data-cy="attribute_wizard_step_4">

            <h2 class="pb-2" > 4. When Do You Want to Show This? </h2>

            <p v-if="group.is_global" class="d-flex flex-column">
              <v-icon color="secondary" size="85">mdi-pencil</v-icon>
              <strong class="secondary--text">
              Cannot select labels because attribute is a File Level
              Attribute. Change it to instance attribute to allow labels selection.
            </strong>
            </p>
            <label_select_only
              v-if="!group.is_global"
              :disabled="group.is_global"
              ref="label_selector"
              label_prompt="Visible on Annotation with these Labels:"
              datacy="label_select_attribute"
              :project_string_id="project_string_id"
              :mode=" 'multiple' "
              :attribute_group_id="group.id"
              @input="$emit('input', group)"
              @label_file="$emit('label_file', $event)"
            >
            </label_select_only>

            <wizard_navigation
              @next="go_to_step(5)"
              @back="go_back_a_step()"
              :disabled_next="!group.kind"
              :skip_visible="false"
                               >
            </wizard_navigation>

          </v-stepper-content>

          <v-stepper-content step="5" style="height: 100%" data-cy="attribute_wizard_step_5">

          <v-layout column>

            <v_error_multiple :error="error">
            </v_error_multiple>

            <h2 class="pb-2">
            5. Options:
            </h2>
            <div class="pa-2">
              <button_with_menu
                tooltip_message="New Option"
                button_text="New Option"
                datacy="new_attribute_option_button"
                datacyclose="close_button_new_attribute"
                v-if="group && group.kind != 'text' && group.kind != 'slider' "
                icon="add"
                :large="true"
                x-small=""
                color="primary"
                icon_color="white"
                :icon_style="false"
                :left="true"
                offset="x"
                :close_by_button="true"
              >
                <template slot="content"
                          slot-scope="props">

                  <attribute_new_or_update
                    :project_string_id="project_string_id"
                    :group_id="group.id"
                    :menu_open="props.menu_open"
                  >

                  </attribute_new_or_update>

                </template>

              </button_with_menu>
            </div>

            <v-container v-if="group.attribute_template_list.length > 0"
                         container--fluid grid-list-md>

              <draggable
                v-if="group && group.attribute_template_list.length > 0"
                v-model="group.attribute_template_list"
                draggable=false
              >
              <h4>Options List:</h4>
                <template
                  v-for="item in group.attribute_template_list">

                  <attribute
                    :project_string_id="project_string_id"
                    :attribute="item"
                    :key="item.id"
                  >
                  </attribute>

                </template>

              </draggable>



            </v-container>
            <div v-else class="d-flex flex-column justify-center align-center">
              <v-icon size="96" color="primary">mdi-archive</v-icon>
              <h4>No Options Yet.</h4>
              <p>Click "New Option" to add an option</p>

            </div>

          </v-layout>

            <wizard_navigation
              @next="go_to_step(6)"
              @back="go_back_a_step()"
              :disabled_next="!group.kind"
              :skip_visible="false"
                               >
            </wizard_navigation>

          </v-stepper-content>

          <v-stepper-content step="6" style="height: 100%" data-cy="attribute_wizard_step_6">

            <!-- Edit Default  default_id default_value -->
            <v-layout column>

              <h4 class="pa-2"> Default Option </h4>

              <v-col cols="12">

                <v-row v-if="group.kind === 'slider'">
                  <v-col cols="3">
                    <v-text-field v-model="group.min_value"
                                  @change="$emit('change')"
                                  @input="$emit('input', group)"
                                  type="number"
                                  data-cy="min_value"
                                  label="Min Value">

                    </v-text-field>
                  </v-col>
                  <v-col cols="3">
                    <v-text-field v-model="group.max_value"
                                  @change="$emit('change')"
                                  @input="$emit('input', group)"
                                  type="number"
                                  data-cy="max_value"
                                  label="Max Value">

                    </v-text-field>
                  </v-col>
                </v-row>

                <v-text-field
                  v-if="group.kind == 'text'"
                  v-model="group.default_value"
                  @input="$emit('input', group)"
                  label="Default"
                  :disabled="loading || view_only_mode"
                  @focus="$store.commit('set_user_is_typing_or_menu_open', true)"
                  @blur="$store.commit('set_user_is_typing_or_menu_open', false)"
                  @change="$emit('change')"
                  clearable

                >
                </v-text-field>

                <diffgram_select
                  v-if="['select', 'multiple_select', 'radio'].includes(group.kind)"
                  :item_list="select_format"
                  v-model="group.default_id"
                  @input="$emit('input', group)"
                  label="Default"
                  :disabled="loading || view_only_mode"
                  @change="$emit('change')"
                  :clearable="true"
                >
                </diffgram_select>

                <v-text-field
                  v-if="group.kind === 'slider'"
                  type="number"
                  v-model="group.default_value"
                  @input="$emit('input', group)"
                  label="Default"
                  :disabled="loading || view_only_mode"
                  @focus="$store.commit('set_user_is_typing_or_menu_open', true)"
                  @blur="$store.commit('set_user_is_typing_or_menu_open', false)"
                  @change="$emit('change')"
                  clearable

                >
                </v-text-field>
                <v-container v-if="group.kind === 'time'">
                  <p><strong>Default: </strong></p>
                  <p v-if="!group.default_value"> (None Yet)</p>
                  <v-time-picker
                    v-model="group.default_value"
                    @input="$emit('input', group)"
                    label="Default"
                    :disabled="loading || view_only_mode"
                    @focus="$store.commit('set_user_is_typing_or_menu_open', true)"
                    @blur="$store.commit('set_user_is_typing_or_menu_open', false)"
                    @change="$emit('change')"
                    clearable
                  >
                  </v-time-picker>
                </v-container>

                <div v-if="group.kind === 'date'">
                <p><strong>Default: </strong></p>
                <p v-if="!group.default_value"> (None Yet)</p>
                <v-date-picker
                  v-model="group.default_value"
                  @input="$emit('input', group)"
                  label="Default"
                  :disabled="loading || view_only_mode"
                  @focus="$store.commit('set_user_is_typing_or_menu_open', true)"
                  @blur="$store.commit('set_user_is_typing_or_menu_open', false)"
                  @change="$emit('change')"
                  clearable
                >
                </v-date-picker>
                </div>
              </v-col>
            </v-layout>


            <wizard_navigation
              @next="go_to_step(7)"
              @skip="go_to_step(6)"
              @back="go_back_a_step()"
                               >
            </wizard_navigation>

          </v-stepper-content>

          <v-stepper-content step="7" data-cy="attribute_wizard_step_7">

            <h2> Complete! Great work. </h2>

            <wizard_navigation
              @back="go_back_a_step()"
              :skip_visible="false"
              :next_visible="false"
                               >
            </wizard_navigation>

          </v-stepper-content>

        </v-stepper-items>

      </v-stepper>


</template>

<script lang="ts">


import Vue from "vue";
import draggable from 'vuedraggable'
import attribute from './attribute.vue';
import label_select_only from '../label/label_select_only.vue'
import attribute_new_or_update from './attribute_new_or_update.vue';

export default Vue.extend( {
  name: 'NewAttributeGroupWizard',
  components:{
    label_select_only,
    attribute_new_or_update,
    draggable,
    attribute
  },
  props: {

    'value': {
      default: null
    },
    'kind_list': {
      default: []
    },
    'loading': {
      default: false
    },
    'error': {
      default: false
    },
    'project_string_id': {
      default: false
    },
    'view_only_mode': {
      default : false
    },
    'select_format' : {
      default: []
    }
  },
  data() {
    return {
      step: 1,
      member_invited: false,
      toggle_global_attribute: 0,
      group: {}
    }
  },
  computed: {
    global_progress: function () {
      return 100 * (parseFloat(this.step) / 6);
    },
  },
  created() {
    this.group = this.value
    if(this.group.is_global){
      this.toggle_global_attribute = 1
    }
    else{
      this.toggle_global_attribute = 0
    }
  },
  watch: {
    value: function (item) {
      this.group = item
    }
  },
  methods: {
    set_is_global: function(value, group){
      if(value === 1){
        group.is_global = true
      }
      else{
        group.is_global = false
      }
      this.$emit('change')
    },
    update_label_files: function(new_label_file_list){
      this.$refs.label_selector.set_label_list(new_label_file_list)

    },
    go_to_step: function(step){
      if(step === 4 && this.group.is_global){
        step = step + 1
        console.log('www', step)
      }
      console.log('aaa', step)
      this.step = step
    },
    on_change_step: function(){

    },
    go_back_a_step: function(){
      this.step -= 1
    },

  }
}

) </script>
