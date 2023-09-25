<template>
  <div id="">

    <!--
      note for formatting we keep the "annotation" display separate
      from the "administration" thing, different formatting goals
      ie tight space conservation vs seperation for different groups.

      For context in earlier versions this was even more confusing because
      the prompt was part of a seperate group so was hard to tell what was
      changing

      now 2 seperate modes... much more clear.
      -->

    <v-card
        v-if="mode === 'annotate' "
        elevation="0">

      <v-container>

        <!-- Minimal padding here to free up screen real estate-->
        <v-layout>

          <!--  for veutify 2 moved the event @change to the group
            as didn't seem to be working as expected on v-radio  (event payload was undefined)
            found out after it not setting it MAY have been unrelated
            something to review later-->

          <!--
              v-model here returns an object  -->

          <v-radio-group
            class="pa-0"
            :data-cy="`${group.prompt}_value_radio_buttons`"
            :label="group.prompt"
            @change="attribute_change()"
            v-model="internal_selected"
            v-if="group.kind == 'radio'"
          >
            <v-radio
              :data-cy="`${group.prompt}_radio_${item.display_name}`"
              :disabled="view_only_mode"
              v-for="item in select_format"
              :key="item.name"
              :label="get_label(item)"
              :value="item"
            ></v-radio>
          </v-radio-group>


          <!-- FUTURE here we would declare if it
             pulls up a NESTED group or something
             otherwise assume it's the "value" being returned
             (kind is set at group level) -->

          <!--
              Text field limit to 1 for now, too many complications with allowing many here...
              Would probably want to abstract a "multiple textfield"
              into something else if we allowed this...
            -->

          <v-text-field
            v-if="group.kind == 'text'"
            :data-cy="`${group.prompt}_value_textfield`"
            v-model="internal_selected"
            :label="group.prompt"
            :disabled="loading || view_only_mode"
            @change="attribute_change"
            @keyup="attribute_change"
            @focus="$store.commit('set_user_is_typing_or_menu_open', true)"
            @blur="$store.commit('set_user_is_typing_or_menu_open', false)"

          >
          </v-text-field>


          <diffgram_select
            v-if="group.kind == 'multiple_select'"
            :data_cy="`${group.prompt}_value_multiple_select`"
            :item_list="select_format"
            :multiple="true"
            :return_object="true"
            v-model="internal_selected"
            :label="group.prompt"
            :disabled="loading || view_only_mode"
            @change="attribute_change()"
          >
          </diffgram_select>

          <!-- Single select

            return_object true becasue we want to be able to switch between
            the radio and select without hurting data

            Default if no kind (for migration)
            -->
          <diffgram_select
            v-if="group.kind == 'select' || !group.kind"
            :data_cy="`${group.prompt}_value_select`"
            :item_list="select_format"
            :return_object="true"
            :multiple="false"
            v-model="internal_selected"
            :label="group.prompt"
            :disabled="loading || view_only_mode"
            @change="attribute_change()"
          >
          </diffgram_select>

          <v-container  v-if="group.kind === 'slider' || !group.kind">
            <v-layout>
              <p></p>
              <v-slider
                :data-cy="`${group.prompt}_value_slider`"
                :min="group.min_value"
                :max="group.max_value"                
                :tick-size="group.max_value"
                thumb-label="always"
                v-model="internal_selected"
                :disabled="loading || view_only_mode"
                @change="attribute_change()"
              >
              </v-slider>
            </v-layout>
          </v-container>

          <v-time-picker
            v-if="group.kind === 'time' || !group.kind"
            v-model="internal_selected"
            :label="group.prompt"
            full-width
            :disabled="loading || view_only_mode"
            @change="attribute_change()"
            @focus="$store.commit('set_user_is_typing_or_menu_open', true)"
            @blur="$store.commit('set_user_is_typing_or_menu_open', false)"
            clearable
          >

          </v-time-picker>

          <v-date-picker
            v-if="group.kind === 'date' || !group.kind"
            v-model="internal_selected"
            :label="group.prompt"
            :disabled="loading || view_only_mode"
            @change="attribute_change()"
            @focus="$store.commit('set_user_is_typing_or_menu_open', true)"
            @blur="$store.commit('set_user_is_typing_or_menu_open', false)"
            clearable
          >
          </v-date-picker>

          <v-card
            width="100%"
            v-if="group.kind === 'tree'"
          >
            <div style="padding: 5px">
              <v-chip
                class="ma-1"
                x-small
                v-for="(name, index) in internal_selected_names"
                :key="`${name}_${index}`"
              >
                {{ name }}
              </v-chip>
            </div>
            <v-sheet class="pa-4 primary lighten-2">
              <v-text-field
                ref="treeview_search"
                v-model="search"
                label="Start by typing attribute name"
                dark
                flat
                solo-inverted
                hide-details
                clearable
                @focus="$store.commit('set_user_is_typing_or_menu_open', true)"
                @blur="$store.commit('set_user_is_typing_or_menu_open', false)"
              ></v-text-field>
            </v-sheet>
            <p v-if="tree_force_rerender">
              Searching...
            </p>
            <v-lazy
              v-else
              :options="{
                threshold: 0.3
              }"
            >
            <v-treeview
              ref="treeview"
              :items="tree_items"
              :load-children="load_clidren"
              :open-all="search ? true : false"
              selectionType="independent"
            >
              <template v-slot:prepend="{ item }">
                  <v-checkbox
                    :input-value="internal_selected.includes(item.id)"
                    @change="tree_input(item)"
                    style="margin-top: 0"
                    hide-details
                  />
              </template>
              <template v-slot:append="{item}">
                <v-chip v-if="show_ids && $store.state.user.settings.show_ids == true " x-small>
                  ID: {{ item.id }}
                </v-chip>
              </template>
            </v-treeview>
            </v-lazy>
          </v-card>

        </v-layout>

      </v-container>
    </v-card>


    <!-- EDIT  -->

    <div v-if="mode == 'edit' ">

      <attribute_group_wizard
        v-if="enable_wizard == true"
        ref="attribute_group_wizard"
        :schema_id="schema_id"
        :kind_list="kind_list"
        :error="error"
        :select_format="select_format"
        :group="group_internal"
        :loading="loading"
        @change="api_group_update('UPDATE')"
        :project_string_id="project_string_id"
        @label_file="recieve_label_file($event)"
                              >

      </attribute_group_wizard>

      <v-container v-if="enable_wizard == false"
                   class="pa-2">

          <v-layout>
            <!-- KIND -->
            <diffgram_select
              data_cy="attribute_kind_select_no_wizard"
              :item_list="kind_list"
              v-model="group.kind"
              label="Kind"
              :disabled="loading || !kind_warning_monitor(group.kind)"
              @change="api_group_update('UPDATE')"
            >
            </diffgram_select>
          </v-layout>

          <v-layout>
            <v-text-field label="Prompt Shown"
                          data-cy="attribute_prompt"
                          v-model="group.prompt"
                          @change="api_group_update('UPDATE')"
            >
            </v-text-field>
          </v-layout>

        <v-layout column>

          <h3 class="pb-2"> When Do You Want to Show This? </h3>

          <label_select_only
            ref="label_selector"
            label_prompt="Visible on Annotation with these Labels:"
            datacy="label_select_attribute"
            :project_string_id="project_string_id"
            :mode=" 'multiple' "
            :attribute_group_id="group.id"
            @label_file="recieve_label_file($event)"
          >
          </label_select_only>

        </v-layout>


        <v-layout column>

          <v_error_multiple :error="error">
          </v_error_multiple>

          <h2 class="pb-2">
          Options
          </h2>

          <div class="pa-2">
            <button_with_menu
              tooltip_message="New Option"
              button_text="New Option"
              data-cy="new_attribute_option_button"
              datacyclose="close_button_new_attribute"
              v-if="group && group.kind != 'text' && group.kind != 'slider' "
              icon="add"
              :large="true"
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
              v-if="group"
              v-model="group.attribute_template_list"
              draggable=false
            >

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


        </v-layout>

        <!-- Edit Default  default_id default_value -->
        <v-layout column>

          <h4 class="pa-2"> Default Option </h4>

          <v-row v-if="group.kind === 'slider'">
            <v-col cols="3">
              <v-text-field v-model="group.min_value"
                            @change="api_group_update('UPDATE')"
                            type="number"
                            data-cy="min_value"
                            label="Min Value">

              </v-text-field>
            </v-col>

            <v-col cols="3">
              <v-text-field v-model="group.max_value"
                            @change="api_group_update('UPDATE')"
                            type="number"
                            data-cy="max_value"
                            label="Max Value">

              </v-text-field>
              </v-col>
          </v-row>

        <v-row>
            <!-- Globals -->
          <div class="pt-0 ">
            <v-checkbox
              v-model="group.is_global"
              label="Show as Global Assessment of the File."
              :disabled="loading || view_only_mode"
              @change="api_group_update('UPDATE')"
            >
            </v-checkbox>
          </div>

        </v-row>

        <!-- Edit Default  default_id default_value -->
          <v-col cols="12">

            <v-text-field
              v-if="group.kind == 'text'"
              v-model="group.default_value"
              label="Default"
              :disabled="loading || view_only_mode"
              @focus="$store.commit('set_user_is_typing_or_menu_open', true)"
              @blur="$store.commit('set_user_is_typing_or_menu_open', false)"
              @change="api_group_update('UPDATE')"
              clearable

            >
            </v-text-field>

            <diffgram_select
              v-if="['select', 'multiple_select', 'radio'].includes(group.kind)"
              :item_list="select_format"
              v-model="group.default_id"
              label="Default"
              :disabled="loading || view_only_mode"
              @change="api_group_update('UPDATE')"
              :clearable="true"
            >
            </diffgram_select>

            <v-text-field
              v-if="group.kind === 'slider'"
              type="number"
              v-model="group.default_value"
              label="Default"
              :disabled="loading || view_only_mode"
              @focus="$store.commit('set_user_is_typing_or_menu_open', true)"
              @blur="$store.commit('set_user_is_typing_or_menu_open', false)"
              @change="api_group_update('UPDATE')"
              clearable

            >
            </v-text-field>
            <v-container v-if="group.kind === 'time'">
              <p><strong>Default: </strong></p>
              <p v-if="!group.default_value"> (None Yet)</p>
              <v-time-picker
                v-model="group.default_value"
                label="Default"
                :disabled="loading || view_only_mode"
                @focus="$store.commit('set_user_is_typing_or_menu_open', true)"
                @blur="$store.commit('set_user_is_typing_or_menu_open', false)"
                @change="api_group_update('UPDATE')"
                clearable
              >
              </v-time-picker>
            </v-container>

            <div v-if="group.kind === 'date'">
            <p><strong>Default: </strong></p>
            <p v-if="!group.default_value"> (None Yet)</p>
            <v-date-picker
              v-model="group.default_value"
              label="Default"
              :disabled="loading || view_only_mode"
              @focus="$store.commit('set_user_is_typing_or_menu_open', true)"
              @blur="$store.commit('set_user_is_typing_or_menu_open', false)"
              @change="api_group_update('UPDATE')"
              clearable
            >
            </v-date-picker>
            </div>
          </v-col>
        </v-layout>


        <v-layout column>

          <h2> Settings </h2>

          <v-text-field label="Internal Tag"
                        data-cy="attribute_tag"
                        v-model="group.name"
                        @change="api_group_update('UPDATE')"
          >
          </v-text-field>

          <!-- Archive button -->
          <button_with_confirm
            @confirm_click="api_group_update('ARCHIVE')"
            class="text-right pa-4"
            icon="archive"
            color="red"
            :loading="loading"
            :disabled="loading"
            :icon_style="true"
            tooltip_message="Archive Entire Attribute and All Options"
          >
            <template slot="content">
              <v-layout column>

                 <v-alert type="warning">
                    Are you sure? This will remove all options too.
                 </v-alert>

              </v-layout>
            </template>
          </button_with_confirm>

          <!-- Archive button -->


        </v-layout>

        <div class="d-flex justify-end">
          <v-chip class="ma-2" x-small color="secondary">ID: {{group.id}}</v-chip>
        </div>

      </v-container>

      <!-- On bottom so it doesn't bounce screen when fires -->
      <v-alert v-if="success"
               type="success"
               dismissible
               attach>
        Saved
      </v-alert>

    </div>

  </div>
</template>

<script lang="ts">
  // @ts-nocheck

  import axios from '../../services/customInstance';
  import draggable from 'vuedraggable'
  import attribute from './attribute.vue';
  import attribute_new_or_update from './attribute_new_or_update.vue';
  import label_select_only from '../label/label_select_only.vue'
  import attribute_kind_icons from './attribute_kind_icons';
  import attribute_group_wizard from './attribute_group_wizard';
  import { construct_tree, tree_parents } from "../../helpers/tree_view/construct_tree"
  import { TreeNode } from "../../helpers/tree_view/Node"

  import Vue from "vue";
  import {attribute_group_update} from "../../services/attributesService";

  export default Vue.extend({

      name: 'attribute_group',

      components: {
        draggable,
        attribute,
        label_select_only,
        attribute_kind_icons,
        attribute_group_wizard

      },

      props: {

        'project_string_id': {
          default: null
        },
        'show_ids': {
          default: true,

        },
        'group': {
          default: {}
        },
        // edit, annotate,  ...
        'mode': {
          default: null
        },

        'current_instance': {
          default: null
        },

        'view_only_mode': {
          default: false
        },

        'enable_wizard': {
          default: true   // default back to false
        },
        'schema_id':{
          default: undefined
        },
        'active_hotkeys': {
          default: false
        }

      },

      data() {
        return {

          search: "",
          tree_force_rerender: false,
          tree_rerender_timeout: null,
          filtered_node_list: null,
          first_load: true,
          original_kind: null,
          loading_update: null,
          min_value: 1,
          max_value: 10,
          openIds: [],

          loading: false,
          error: {},
          success: false,

          internal_selected: [],
          internal_selected_names: [],

          kind_list: [

            {
              'display_name': 'Select',
              'name': 'select',
              'icon': 'mdi-selection',
              'color': 'primary'
            },
            {
              'display_name': 'Free Text',
              'name': 'text',
              'icon': 'mdi-card-text',
              'color': 'green'
            },
            {
              'display_name': 'Multiple Select',
              'name': 'multiple_select',
              'icon': 'mdi-select-multiple',
              'color': 'purple'
            },
            {
              'display_name': 'Radio Buttons',
              'name': 'radio',
              'icon': 'mdi-radiobox-marked',
              'color': 'pink'
            },
            {
              'display_name': 'Slider',
              'name': 'slider',
              'icon': 'mdi-video-input-component',
              'color': 'pink'
            },
            {
              'display_name': 'Time',
              'name': 'time',
              'icon': 'mdi-clock',
              'color': 'primary'
            },
            {
              'display_name': 'Date',
              'name': 'date',
              'icon': 'mdi-calendar',
              'color': 'primary'
            },
            {
              'display_name': 'Tree',
              'name': 'tree',
              'icon': 'mdi-file-tree',
              'color': 'primary'
            },

            // future
            /*
            {
              'display_name': 'Open nested selection to new group',
              'name': 'chidren',
              'icon': 'mdi-function-variant'
            }
            */

          ],
          hotkey_dict: {
            49: 0,
            50: 1,
            51: 2,
            52: 3,
            53: 4,
            54: 5,
            55: 6,
            56: 7,
            57: 8,
            58: 9
          },
          name: null,

          label_file_list: [],

          group_internal: {},
          tree_items_list: [],
          tree_items: []

        }
      },
      beforeDestroy() {
       this.remove_hotkey_listeners()
      },
      watch: {
        active_hotkeys: function(newValue){
          if(newValue){
            this.add_hotkey_listeners()
          } else{
            this.remove_hotkey_listeners()
          }
        },
        search: function(newValue) {
          clearTimeout(this.tree_rerender_timeout)
          this.tree_force_rerender = true
          this.tree_rerender_timeout = setTimeout(() => {
            this.tree_search(newValue)
            this.tree_force_rerender = false
          }, 400)
        },

        // not sure if this is right thing to watch
        current_instance() {

          this.set_existing_selected()
        },

        group() {

          // for "resesting" it.
          // we want a newly created group to be different
          // vue js being a bit fiddly here
          this.original_kind = this.group.kind

          this.group_internal = this.$props.group
        }

      },

      created() {

        this.set_existing_selected()

        this.original_kind = this.group.kind

        this.group_internal = this.$props.group

        if (this.group.kind === "tree") {
          this.group.attribute_template_list.filter(item => !item.parent_id).map(attr => {
            const new_node = new TreeNode(attr.group_id, attr.name)
            new_node.initialize_existing_node(attr.id, attr.parent_id)
            this.tree_items_list.push(new_node)
          })

          this.tree_items = construct_tree(this.tree_items_list)
        }
        if(this.active_hotkeys){
          this.add_hotkey_listeners()
        }
      },
      computed: {
        export_internal_selected: function() {
          if (this.group.kind !== "tree") return this.internal_selected

          const tree_array = this.internal_selected.map(item => {
            const item_node = this.tree_items_list.find(node_item => node_item.get_id() === item)
            if (item_node) {
              const { id, name } = item_node.get_API_data()
              return {[id]: { name, "selected": true}}
            }
          })

          const tree_post_items = {
            ...tree_array.reduce((a, v) => ({ ...a, ...v}), {})
          }

          return tree_post_items
        },

        select_format: function () {
          /* Convert a list of data base objects into form
           * diffgram_select wants
           *
           * also helps keep format we save it in uniform
           * in case a user switches between selector types
           *
           * and/or we change what we are sending from backend later
           */

          if (this.group.kind == "text") {
            return []
          }

          let attribute_template_list = []

          /*
           * Another option is we could just add
           * The display name and name to the existing object
           * advantage is if we do want to reduce what we store
           * here we can do that
           */

          if (!this.group.attribute_template_list){
            throw("Missing group.attribute_template_list. Check API.")
          }

          for (let x of this.group.attribute_template_list) {

            let attribute = {}
            attribute.display_name = x.name
            attribute.id = x.id
            attribute.name = x.id   // temp duplication thing, diffgram_select expects a name

            attribute_template_list.push(attribute)
          }

          return attribute_template_list

        }
      },
      methods: {
        set_radio_select_value_by_id: function(option_id){
          for(let option of this.select_format){
            if(option.id === option_id){
              this.internal_selected = option
              this.attribute_change()
            }
          }
        },
        get_label: function(item){

          let label = item.display_name
          if (this.$store.state.user.settings.show_ids == true) {
            label += " [" +  item.id + "]"
          }
          return label
        },

        set_attribute_value: function(value){
          if(['radio', 'select'].includes(this.group.kind)){
              // Assume value is the ID for this case
              this.set_radio_select_value_by_id(value)
          }
          // TODO: implement set method for rest of attributes.
        },
        add_hotkey_listeners: function(){
          window.addEventListener('keyup', this.attribute_keyup_handler);
          window.addEventListener('keydown', this.attribute_keydown_handler);
        },
        remove_hotkey_listeners: function(){
          window.removeEventListener('keyup', this.attribute_keyup_handler);
          window.removeEventListener('keydown', this.attribute_keydown_handler);
        },
        attribute_keyup_handler: function(){
          if(!['radio', 'select'].includes(this.group.kind)){
            return
          }

        },
        attribute_keydown_handler: function(event){
          if(!['radio', 'select'].includes(this.group.kind)){
            return
          }
          let index = this.hotkey_dict[event.keyCode]
          if(index != undefined){
            let item_to_select = this.select_format[index]
            if(item_to_select && item_to_select != this.internal_selected){
              this.internal_selected = item_to_select
              this.attribute_change()
            }
          }
        },
        tree_input: function(e) {
          const already_selected = this.internal_selected.includes(e.id)

          if (already_selected) {
            const index_to_delete = this.internal_selected.indexOf(e.id);
            this.internal_selected.splice(index_to_delete, 1);

            const index_to_delete_name = this.internal_selected_names.indexOf(e.name);
            this.internal_selected_names.splice(index_to_delete_name, 1);
          }
          else {
            this.internal_selected.push(e.id)
            this.internal_selected_names.push(e.name)
          }

          this.attribute_change()
        },
        load_clidren: function(e) {
          let template_list = this.group.attribute_template_list.filter(item => item.parent_id === e.id)

          this.set_tree(template_list)
        },
        tree_search: async function(e) {
          this.tree_items_list = []

          if (!this.search) {
            this.group.attribute_template_list.filter(item => !item.parent_id).map(attr => {
              const new_node = new TreeNode(attr.group_id, attr.name)
              new_node.initialize_existing_node(attr.id, attr.parent_id)
              this.tree_items_list.push(new_node)
            })
            this.tree_items = construct_tree(this.tree_items_list)
            return
          }

          const res = this.group.attribute_template_list.filter(item => item.name.toLowerCase().includes(e.toLowerCase()))

          const selected_nodes = res.map(item => {
            const new_node = new TreeNode(item.group_id, item.name)
            new_node.initialize_existing_node(item.id, item.parent_id)
            return new_node
          })

          const all_nodes = this.group.attribute_template_list.map(item => {
            const new_node = new TreeNode(item.group_id, item.name)
            new_node.initialize_existing_node(item.id, item.parent_id)
            return new_node
          })

          const local_nodes = []
          const global_tracker = []

          await selected_nodes.map(async node => {
            const result = await tree_parents(node.id, [...all_nodes], global_tracker)
            local_nodes.push(...result.nodes_to_return)
            global_tracker.push(...result.local_tracker)
          })

          this.tree_items_list = [...new Set(local_nodes.map(node => node))]
          this.tree_items = construct_tree(this.tree_items_list)
        },
        set_tree: function(to_tree) {
          to_tree.map(attr => {
            const new_node = new TreeNode(attr.group_id, attr.name)
            new_node.initialize_existing_node(attr.id, attr.parent_id)
            this.tree_items_list.push(new_node)
          })

          this.tree_items = construct_tree(this.tree_items_list)
        },
        update_label_files: function(new_label_list){
          if(!this.$props.enable_wizard){
            this.$refs.label_selector.set_label_list(new_label_list)
          }
          else{
            this.$refs.attribute_group_wizard.update_label_files(new_label_list)
          }

        },
        // group change
        attribute_change: function () {
          /*
           *
           * the theory here is mainly that it is maintaining the same format
           * so we are always setting a
           *
           * group_id :  actual group data

            Attribute group is responsible for loading it’s group of attributes,
            including existing data from a given Instance

            It emits an event that contains the group id, and the new “value”
            value could be one of [string, object, list, node (future)]

            Node could potentially be another group in the future

            Annotation core is responsible for saving a dict where the key
            is the group id and the value for that instance.

            More: https://docs.google.com/document/d/1bkq8ftciLqDtlmFRrm-dJmPGmIV5Cra8YnegSTXJJbc/edit#heading=h.51y9ufvnioeu

           *
           */

          this.$emit('attribute_change', [this.group, this.export_internal_selected])

        },

        get_default: function () {
          if (this.group.default_id){
            return this.group.default_id
          }
          if (this.group.default_value){
            return this.group.default_value
          }
        },

        format_default: function () {
          if ([null, "select", "radio"].includes(this.group.kind)) {
            let default_attribute = {}
            default_attribute.id = this.group.default_id
            return default_attribute
          }
          if (this.group.kind == 'multiple_select'){
            return [{id:this.group.default_id}]  // note array formatting, assumed to be single ID for now
          }
          if (this.group.kind == 'text'){
            return this.group.default_value
          }
          if(this.group.kind === 'slider'){
            return this.group.default_value;
          }
          if(this.group.kind === 'time'){
            return this.group.default_value;
          }
          if(this.group.kind === 'date'){
            return this.group.default_value;
          }

        },

        set_existing_selected: function () {
          /*
           * In context of annotation this component is focused
           * on displaying attributes and propogating selections
           * If an instance already has selections then we need to set it,
           * and since vue js seems to like component reuse (I think this was reason)
           * we need to reset it if the current_instance changes
           *
           * We are already in the context of a specific group
           * so here we are looking at the dict of groups in the current
           * instance and seeing if any
           * match the group id (this avoids a n^2 setup?)
           *
           * This was really more for the "single select" otherwise can just load from instance right?
           *
           */
          // reset
          this.internal_selected = []
          this.internal_selected_names = []

          if (this.group.kind === 'date') {
            this.internal_selected = ''
          }

          // set existing if applicable
          if (!this.current_instance) {
            return
          }
          if (!this.current_instance.attribute_groups) {
            return
          }

          let value = null    // shared with existing and default
          let existing_value = null
          let default_value = null
          if (this.current_instance.attribute_groups && this.current_instance.attribute_groups[this.group.id]) {
            existing_value = this.current_instance.attribute_groups[this.group.id]
          }
          else  {

            // If not existing value, check for default
            // We must be careful here, we don't want to "reset" to the default value
            // if there was an existing value. We only set default when it's null.
            default_value = this.get_default()
            if (!default_value) {
              // If no default and no exist_value to set so return
              return
            } else {
              value = this.format_default()
            }
          }
          // Populate existing value.
          if ((existing_value != null && this.group.kind != 'multiple_select' )
            || (this.group.kind === 'multiple_select' && existing_value && existing_value.length > 0)){
            value = existing_value
          }
          // Code below is for LOADING VALUES / formatting.
          // At this point we around know the value itself as ( existing_value )

          // We use id because the attributes may have been updated since they were selected

          /*  Radio buttons have bug in veutify that requires object selection
           *  BUT that's a primary reason, main thing is because we want to use
           *  IDs incase the "text" for the id changes
           */

          /* Caution we want to use "this.group" thing here since existing_value
           * will NOT have the kind (it ONLY has instance specific information)
           */

          if (!this.group.kind || this.group.kind == "select" || this.group.kind == "radio") {
            this.internal_selected = this.select_format.find(
              attribute => {
                return attribute.id == value.id
              })

          } else if(this.group.kind == "tree") {
            this.internal_selected = Object.keys(this.current_instance.attribute_groups[this.group.id]).map(key => parseInt(key))
            this.internal_selected_names = this.internal_selected.map(key => this.current_instance.attribute_groups[this.group.id][key]['name'])
          } else if (this.group.kind == "text") {
            // in this case nothing to change we are only storing text
            this.internal_selected = value

          } else if (this.group.kind == "multiple_select") {
            if(value && value.length > 0){
              this.internal_selected = []
            }
            // value is an array now
            for (let single_selected of value) {
              if(!single_selected){
                return
              }
              let selected_attr = this.select_format.find(
                attribute => {
                  return attribute.id == single_selected.id
                })
              this.internal_selected.push(selected_attr)
            }
          }
          else if(this.group.kind === 'slider'){
            this.internal_selected = parseInt(value, 10)
          }
          else if(this.group.kind === 'time'){
            this.internal_selected = value
          }
          else if(this.group.kind === 'date'){
            this.internal_selected = value
          }

          if (default_value) {
            // IF we added a default value, emit the change
            // The above setting is done automatically (not by user)
            // eg if it's existing, then there's no need to emit change
            this.attribute_change()
          }


        },


        kind_warning_monitor: function (value) {
          /* When a group is first created it can have a blank kind
           * So we want user to edit this freely
           * Then once it's set we warn
           *
           * In future could also do a hard restriction here...
           *
           * Allow swap between radio and select?
           *
           * Because we don't update original kind, the person
           *  can flip freely through newly created groups
           *  and this should only display if they come back to the page.
           *
           *  Consider:
           *  We also check that there must be at least one attribute
           *  or other things so it doesn't show up for new users
           *  (this wouldn't work for "text" type though)
           *
           *  Enforcing this
           *    We would need to run this first
           *    then run / not run the update request
           *    otherwise timing issue because it does the API call even
           *    if the group is set...
           *
           *    Also not really wanting to have such a hard "enforcement" here?
           *    Flip side is right now front end can look broken since it will show
           *    object...
           *
           *
           *  manual test case
           *    -> Reloading page I expect it to be locked (as long as labels present)
           *    -> New group I expect it to be availabe
           *    -> new group with labels (haven't gone off page) I still expect it to be available
           *
           *   At the moment if we remove labels it becomes available again...
           *    but I think that's something we can address later...
           */

          /* This allowed swap list was in a different context,
           * it was more of a "validation" rule, ie that
           * runs when it changes. Realized for now the bigger concern is more
           * disabling it in the first place.
           */

          /*
          let allowed_swap_list = ["select", "radio"]

          if (allowed_swap_list.includes(this.original_kind)
            && allowed_swap_list.includes(value)) {
            return true
          }
          */

          if (!this.original_kind) {
            return true
          }

          // we assume if no labels selected it's ok
          if (this.group_internal.label_file_list.length == 0) {
            return true
          }

          // default case if other things aren't true
          return false

        },

        recieve_label_file: function (label_file_list) {


          this.group_internal.label_file_list = label_file_list

          // this feels a bit hacky but at least should work for now...
          if (this.first_load == true) {
            this.first_load = false
          } else {

            this.api_group_update("UPDATE")
          }


        },


        api_group_update: async function (mode) {
          this.loading_update = true
          this.error = {}
          this.success = false

          let group

          if (this.group_internal) {
            group = this.group_internal
          } else {
            group = this.group
          }

          if (mode == 'ARCHIVE') {
            // backend validates that a kind exists
            // so doing this as a work around
            group.kind = "ARCHIVE"
          }
 
          if(group.kind === 'slider'){

            if(!this.group.min_value) {
              this.group.min_value=1;
            }
            if(!this.group.max_value) {
              this.group.max_value=10;
            }
          }

          try{
            let [data, error] = await attribute_group_update(this.project_string_id, mode, group)
            this.success = true
            this.loading_update = false
            if(error){
              if (error.response.status == 400) {
                this.error = error.response.data.log.error
              }
              this.loading_update = false
              console.error(error)
            }

            // careful mode is local, not this.mode
            if (mode == 'ARCHIVE') {

              // only refresh on archive?

              this.$store.commit('attribute_refresh_group_list')
            }
          }
          catch (error){
            this.loading_update = false
            console.error(error)
          } finally {
            this.loading_update = false
          }
        }

      }
    }
  ) </script>
