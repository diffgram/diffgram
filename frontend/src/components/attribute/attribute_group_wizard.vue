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

          <v-stepper-step
            editable
            :complete="step > 4"
            step="4"
          >
            Access
          </v-stepper-step>



          <v-divider></v-divider>

          <v-stepper-step
            editable
            :complete="step > 5"
            step="5">
           Triggers
          </v-stepper-step>

          <v-divider></v-divider>

          <v-stepper-step
            editable
            :complete="step > 6"
            step="6"
          >
            Values
          </v-stepper-step>

          <v-divider v-if="group.kind !== 'tree'"></v-divider>
          <v-stepper-step
            v-if="group.kind !== 'tree'"
            editable
            :complete="step > 7"
            step="7">
            Defaults
          </v-stepper-step>

        </v-stepper-header>


        <v-progress-linear
          color="secondary"
          striped
          :value="global_progress"
          :height="group.kind !== 'tree' ? 8 : 7"
        >
        </v-progress-linear>


        <v-stepper-items style="height: 100%; min-height: 300px; border-bottom: 1px solid #e0e0e0" class="pt-4">

          <v-stepper-content step="1" style="height: 100%" data-cy="attribute_wizard_step_1">

            <h1 class="pb-2">Kind</h1>

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

            <h1>Name</h1>

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

            <h1>Scope</h1>

            <p>
              Scope determines the Attribute's relation to Annotations, Files or Objects.
              <br>
              Learn more about
            <a href="https://diffgram.readme.io/docs/attribute-scope" target="_blank">
                Attribute Scope.
            </a>
            </p>

            <v-layout class="justify-center align-center">
              <v-btn-toggle color="secondary" v-model="toggle_global_attribute" @change="set_is_global($event, group)">
                <v-btn data-cy="instance-attribute-button">
                  <v-icon left color="primary" size="18">
                    mdi-brush
                  </v-icon>
                  Annotation
                </v-btn>

                <v-btn data-cy="global-attribute-button">
                  <v-icon left color="primary" size="18">
                    mdi-file
                  </v-icon>

                   File

                </v-btn>

                <v-btn data-cy="global-compound-attribute-button">
                  <v-icon class="pl-2 pr-2" left color="primary" size="18">
                    mdi-file-table-box-multiple
                  </v-icon>

                    Object

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

            <h1> Access Control </h1>

            <p>
              Control Access for this Attribute.
              <br>
              Learn more about
              <a href="https://diffgram.readme.io/docs/attribute-access-control" target="_blank">
                  Attribute Access Control.
              </a>
            </p>


            <h2> Read Only? </h2>

            <v-layout class="justify-center align-center">
              <v-checkbox
                clearable
                v-model="group.is_read_only"
                label="Read Only?"
                @change="$emit('change')"
              >
              </v-checkbox>

            </v-layout>

            <wizard_navigation
              @next="go_to_step(5)"
              @back="go_back_a_step()"
              :disabled_next="!group.prompt"
              :skip_visible="false"
            >
            </wizard_navigation>

          </v-stepper-content>

          <v-stepper-content step="5" style="height: 100%" data-cy="attribute_wizard_step_5">

            <h1 class="pb-2" >Triggers</h1>

            <div v-if="group.is_global" class="d-flex flex-column">
            <strong class="secondary--text">
              <v-icon color="secondary" size="85">mdi-check</v-icon>
              <p>
                Scope is set to Global which is always shown.
              </p>
              <p>
              Change Scope to Per Annotation to trigger conditional visibility.
              </p>
            </strong>
            </div>
            <label_select_only
              v-if="!group.is_global"
              :disabled="group.is_global"
              :schema_id="schema_id"
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
              @next="go_to_step(6)"
              @back="go_back_a_step()"
              :disabled_next="!group.kind"
              :skip_visible="false"
                               >
            </wizard_navigation>

          </v-stepper-content>

          <v-stepper-content step="6" style="height: 100%" data-cy="attribute_wizard_step_6">

          <h1 class="pb-2">
          Values
          </h1>

          <div v-if="group.kind == 'text'" >
            <strong class="secondary--text">
              <v-icon color="secondary" size="85">mdi-check</v-icon>
              <p>
                There are no values to set on Free Text.
              </p>
            </strong>
          </div>

          <div v-if="group.kind == 'slider'" >
            <strong class="secondary--text">
              <v-icon color="secondary" size="85">mdi-check</v-icon>
              <p>
                Use Defaults to set slider Defaults.
              </p>
            </strong>
          </div>

          <v-layout v-if="['select', 'multiple_select', 'radio'].includes(group.kind)" column>

            <v_error_multiple :error="error">
            </v_error_multiple>

            <div class="pa-2">
              <button_with_menu
                tooltip_message="New"
                button_text="New"
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
                    @attribute_updated="attribute_updated($event)"
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
                <template
                  v-for="item in group.attribute_template_list">

                  <attribute
                    :project_string_id="project_string_id"
                    :attribute="item"
                    :key="item.id"
                    @attribute_updated="attribute_updated($event)"
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

          <v-layout v-if="group.kind == 'tree'" column>
            <v_error_multiple :error="error" />

            <v-treeview
              :items="tree_items"
              :active="[]"
              activatable
              open-on-click
            >
              <template v-slot:label="{ item, open }">
                <v-layout v-if="item.name !== 'Add new'" class="pa-2" style="border: 1px solid #e0e0e0">
                  <input
                    style="width: 100%"
                    @click.stop.prevent=""
                    @change="(e) => change_tree_item_name(e, item.id)"
                    @focus="$store.commit('set_user_is_typing_or_menu_open', true)"
                    @blur="$store.commit('set_user_is_typing_or_menu_open', false)"
                    :value="item.name"
                  />
                  <standard_button
                    v-if="open"
                    color="primary"
                    icon="mdi-plus"
                    tooltip_message="Add child"
                    @click.stop.prevent="() => add_tree_item([item.id])"
                    :icon_style="true"
                    :bottom="true"
                  />
                  <standard_button
                    v-else
                    color="primary"
                    icon="mdi-plus"
                    tooltip_message="Add child"
                    @click="() => add_tree_item([item.id])"
                    :icon_style="true"
                    :bottom="true"
                  />
                  <button_with_confirm
                    @confirm_click="delete_tree_item(item.id)"
                    class="text-right pa-4"
                    icon="archive"
                    color="red"
                    :loading="loading"
                    :disabled="loading"
                    :icon_style="true"
                    tooltip_message="Archive"
                  >
                    <template slot="content">
                      <v-layout column>

                        <v-alert type="warning">
                            Are you sure? This will remove all the nested items too.
                        </v-alert>

                      </v-layout>
                    </template>
                  </button_with_confirm>
                  <v-chip class="ma-auto" x-small v-if="$store.state.user.settings.show_ids === true">
                    ID: {{ item.id }}
                  </v-chip>
                </v-layout>
                <v-layout @click="add_root_tree_item" v-else flexe>
                  Add new
                </v-layout>
              </template>
            </v-treeview>

          </v-layout>


            <wizard_navigation
              @next="go_to_step(7)"
              @back="go_back_a_step()"
              :disabled_next="!group.kind"
              :skip_visible="false"
                               >
            </wizard_navigation>

          </v-stepper-content>

          <v-stepper-content v-if="group.kind !== 'tree'" step="7" style="height: 100%" data-cy="attribute_wizard_step_7">

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
              @next="go_to_step(8)"
              @skip="go_to_step(7)"
              @back="go_back_a_step()"
                               >
            </wizard_navigation>

          </v-stepper-content>

          <v-stepper-content :step="group.kind !== 'tree' ? 8 : 7" data-cy="attribute_wizard_step_8">

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
import { v4 as uuidv4 } from "uuid";
import { TreeNode } from "../../helpers/tree_view/Node"
import { construct_tree, find_all_relatives } from "../../helpers/tree_view/construct_tree"
import { attribute_update_or_new } from "../../services/attributesService.ts"
import pLimit from 'p-limit';

export default Vue.extend( {
  name: 'NewAttributeGroupWizard',
  components:{
    label_select_only,
    attribute_new_or_update,
    draggable,
    attribute
  },
  model: {
    prop: 'group',
    event: 'change'
  },
  props: {
    'kind_list': {
      default: []
    },
    'schema_id':{
      required: true
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
    'group': {
      type: Object,
      default() {
        return {};
      }
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
      add_path: [],
      items: [],
      tree_items_list: []
    }
  },
  computed: {
    global_progress: function () {
      return 100 * (parseFloat(this.step) / 6);
    },
    tree_items: function() {
      const tree = construct_tree(this.tree_items_list)
      const add_too_root_item = {
        name: "Add new",
        id: uuidv4()
      }
      return [...tree, add_too_root_item]
    },
  },
  created() {

    if(!this.group){
      return
    }

    this.set_global_attribute()
    this.build_tree_data();

  },
  watch: {
    value: {
      handler: function (item) {
        this.group = item
        if(!this.group){
          return
        }
        this.set_global_attribute()
        this.build_tree_data();
      },
      deep: true
    }
  },
  methods: {

    attribute_updated: function (attribute_template){
      const attribute_template_existing = this.group.attribute_template_list.find(a => a.id === attribute_template.id)
      if (attribute_template_existing) {
        let index = this.group.attribute_template_list.indexOf(attribute_template_existing)
        this.group.attribute_template_list[index].name = attribute_template.name
      } else {
        this.group.attribute_template_list.push(attribute_template)
      }
    },

    set_global_attribute: function(){
      if(this.group.is_global){
        if(this.group.global_type === 'compound_file'){
          this.toggle_global_attribute = 2
        } else{
          this.toggle_global_attribute = 1
        }

      }
      else{
        this.toggle_global_attribute = 0
      }
    },
    build_tree_data: function(){

      if (this.group.kind != 'tree') { return }

      this.group.attribute_template_list.map(attr => {
        const new_node = new TreeNode(attr.group_id, attr.name)
        new_node.initialize_existing_node(attr.id, attr.parent_id)
        this.tree_items_list.push(new_node)
      })
    },
    set_is_global: function(value, group){
      if(value === 1){
        group.is_global = true
        group.global_type = 'file'
      } else if(value === 2){
        group.is_global = true
        group.global_type = 'compound_file'
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
      }
      this.step = step
    },
    on_change_step: function(){

    },
    go_back_a_step: function(){
      this.step -= 1
    },
    save_tree_item: async function(mode, item) {
      if (mode !== "ARCHIVE") {
        const { data: { attribute_template : { id }} } = await attribute_update_or_new(mode, this.project_string_id, item.get_API_data())
        item.set_id(id)
      } else {
        const limit = pLimit(25);
        const deletion_requests = item.map(to_delete => limit(() => attribute_update_or_new(mode, this.project_string_id, to_delete.get_API_data())))
        await Promise.all(deletion_requests);
      }
    },
    delete_tree_item: function(item_id) {
      const all_relatives = find_all_relatives(item_id, this.tree_items_list)
      let relative_node_ids = all_relatives.related_nodes.map(elm => elm.id)
      const list_copy = [...this.tree_items_list].filter(item => !relative_node_ids.includes(item.get_id()))
      const list_to_delete = [...this.tree_items_list].filter(item => relative_node_ids.includes(item.get_id()))
      this.tree_items_list = list_copy
      this.save_tree_item("ARCHIVE", list_to_delete)
    },
    change_tree_item_name: function(e, item_id) {
      const new_name = e.target.value
      const node_to_modify = this.tree_items_list.find(node => node.get_id() === item_id)
      node_to_modify.update_name(new_name)
      this.save_tree_item("UPDATE", node_to_modify)
    },
    add_tree_item: function(e) {
      if (e.length > 0) {
        const new_node = new TreeNode(this.group.id, `New item ${this.tree_items_list.length + 1}`)
        new_node.set_parent(e[0])
        this.tree_items_list.push(new_node)
        this.save_tree_item("NEW", new_node)
      }
    },
    add_root_tree_item: function() {
      const new_node = new TreeNode(this.group.id, `New item ${this.tree_items_list.length + 1}`)
      this.tree_items_list.push(new_node)
      this.save_tree_item("NEW", new_node)
    }
   }
}

)
</script>
