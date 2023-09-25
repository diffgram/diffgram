<template>
  <div>
    <v-progress-linear
      v-if="loading || loading_update_all_attributes"
      indeterminate
      class="mt-4"
      attach
    />
    <div
      style="overflow-y:auto"
    >
      <v-layout
        fill-height
        v-if="mode==='edit'"
        class="d-flex pa-4 align-center"
      >
        <!-- TODO trying to separate out this from the list layout
          since we have different goals for annotation vs
          admin thing here...-->
        <attribute_group_new
          :schema_id="schema_id"
          :project_string_id="project_string_id"
        />

        <v-btn
          text
          icon
          color="primary"
          href="https://diffgram.readme.io/docs/attributes-1"
          target="_blank"
        >
          <v-icon>help</v-icon>
        </v-btn>
      </v-layout>

      <!--  Caution     This is for  annotate mode too -->
      <v-layout
        column
        v-if="mode==='edit' || current_instance && current_instance.soft_delete != true || !current_instance"
      >
        <v_error_multiple :error="error"/>
        <!-- TODO use tree syntax from vue js -->
        <v-expansion-panels
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
          <draggable  @end="on_drag_end" v-if="draggable" v-bind="dragOptions" class="list-group" :disabled="loading_update_all_attributes">

            <transition-group type="transition" name="flip-list">
              <v-expansion-panel
                :ref="`attribute_group_${group.id}_panel`"
                class="list-group-item"
                v-for="(group, index) in attribute_group_list_computed"
                :key="group.id"
                :disabled="loading_update_all_attributes"
              >
                <v-expansion-panel-header
                  :ref="`attribute_group_${group.id}_header`"
                  :class="{'d-flex justify-start text-left': true}"
                  style="border: 1px solid #e0e0e0"
                  :data-cy="`attribute_group_header_${group.prompt}`"
                  @click="update_url_with_current_group(group)"
                >
                  <v-chip  small v-if="draggable" style="max-width: 30px" class="mr-2">
                    <h3>{{group.ordinal}}</h3>
                  </v-chip>
                  <h4 class="text-left d-flex align-center flex-grow-1">
                    <attribute_kind_icons
                      class="pr-2"
                      :kind=" group.kind "
                    />
                    {{ group.prompt }}
                    <div
                      v-if="!group.prompt"
                      :data-cy="`attribute_group_header_Untitled Attribute Group`"
                    >
                      Untitled Attribute Group
                    </div>

                    <v-spacer/>

                    <button_with_confirm
                      v-if="mode==='edit'"
                      icon="archive"
                      color="red"
                      tooltip_message="Archive Entire Attribute and All Options"
                      :loading="loading"
                      :disabled="loading || loading_update_all_attributes"
                      :icon_style="true"
                      @confirm_click="api_group_archive(group)"
                    >
                      <template slot="content">
                        <v-layout column>
                          <v-alert type="error">
                            Are you sure? This will remove all options too.
                          </v-alert>
                        </v-layout>
                      </template>
                    </button_with_confirm>
                    <v-chip v-if="show_ids && $store.state.user.settings.show_ids == true " x-small>ID {{ group.id }}</v-chip>
                  </h4>
                  <!-- Archive button -->
                  <!-- TODO maybe, play with this more
                    eg maybe in edit mode show internal tag-->
                </v-expansion-panel-header>

                <v-expansion-panel-content :eager="mode !== 'edit'">
                  <attribute_group

                    :ref="`attribute_group_${group.id}`"
                    :active_hotkeys="openedPanel === index"
                    :schema_id="schema_id"
                    :project_string_id="project_string_id"
                    :mode="mode"
                    :view_only_mode="view_only_mode"
                    :group="group"
                    :key="group.id"
                    :current_instance="current_instance"
                    @attribute_change="$emit('attribute_change', $event)"
                  />

                </v-expansion-panel-content>
              </v-expansion-panel>
            </transition-group>
          </draggable>
          <v-expansion-panel
            v-else
            v-for="(group, index) in attribute_group_list_computed"
            :key="group.id"
            :disabled="group.is_read_only"
          >
            <v-expansion-panel-header
              style="border: 1px solid #e0e0e0"
              :class="{'d-flex justify-start text-left': true, 'read-only': group.is_read_only}"
              :data-cy="`attribute_group_header_${group.prompt}`"
              @click="update_url_with_current_group(group)"
            >
              <h4 class="text-left d-flex align-center flex-grow-1">
                <attribute_kind_icons
                  class="pr-2"
                  :kind=" group.kind "
                />
                {{ group.prompt }}
                <div
                  v-if="!group.prompt"
                  :data-cy="`attribute_group_header_Untitled Attribute Group`"
                >
                  Untitled Attribute Group
                </div>



                <v-spacer/>

                <button_with_confirm
                  v-if="mode==='edit'"
                  icon="archive"
                  color="red"
                  tooltip_message="Archive Entire Attribute and All Options"
                  :loading="loading"
                  :disabled="loading"
                  :icon_style="true"
                  @confirm_click="api_group_archive(group)"
                >
                  <template slot="content">
                    <v-layout column>
                      <v-alert type="error">
                        Are you sure? This will remove all options too.
                      </v-alert>
                    </v-layout>
                  </template>
                </button_with_confirm>
                <div v-if="get_attribute_value(group.id)" class="mr-4">
                  <v-chip  x-small color="secondary lighten-5" text-color="primary lighten-1"  >
                   <p class="ma-0 pa-0" style="max-width: 135px;overflow: hidden; white-space: nowrap; text-overflow: ellipsis;"> {{get_attribute_value(group.id)}}</p>
                  </v-chip>
                </div>
                <v-chip v-if="show_ids && $store.state.user.settings.show_ids == true " x-small>ID {{ group.id }}</v-chip>
              </h4>
              <!-- Archive button -->
              <!-- TODO maybe, play with this more
                eg maybe in edit mode show internal tag-->
            </v-expansion-panel-header>

            <v-expansion-panel-content>
              <attribute_group
                :ref="`attribute_group_${group.id}`"
                :active_hotkeys="openedPanel === index"
                :schema_id="schema_id"
                :project_string_id="project_string_id"
                :mode="mode"
                :view_only_mode="view_only_mode"
                :group="group"
                :key="group.id"
                :current_instance="current_instance"
                :show_ids="show_ids"
                @attribute_change="$emit('attribute_change', $event)"
              />
              <div v-if="mode==='edit'">
                ID: {{ group.id }}
              </div>
            </v-expansion-panel-content>
          </v-expansion-panel>
        </v-expansion-panels>
      </v-layout>
    </div>
  </div>
</template>

<script lang="ts">
import draggable from 'vuedraggable'
import attribute_group from './attribute_group.vue'
import {attribute_group_list, archive_attribute_group, attribute_group_update} from '../../services/attributesService.ts'
import attribute_kind_icons from './attribute_kind_icons.vue'
import attribute_group_new from './attribute_group_new.vue'
import pLimit from 'p-limit';
import Vue from "vue"


export default Vue.extend({
    name: 'attribute_group_list',
    components: {
      draggable: draggable,
      attribute_group: attribute_group,
      attribute_kind_icons: attribute_kind_icons,
      attribute_group_new: attribute_group_new
    },
    props: {
      project_string_id: {type: String, default: null},
      schema_id: {type: Number || String, required: true},
      mode: {type: String, default: null},
      attribute_group_list_prop: {type: Array, default: null},
      current_instance: {type: Object, default: null},
      view_only_mode: {type: Boolean, default: false},
      attribute_list: {type: Array, default: null},
      draggable: {type: Boolean, default: false}
    },
    data() {
      return {
        loading: false as Boolean,
        error: {} as Object,
        success: false as Boolean,
        name: null as String,
        attribute_group_list: [] as Array<any>,
        out_of_schema_attributes: [] as Array<any>,
        openedPanel: null as Number,
        loading_update_all_attributes: false as Boolean,
        hotkey_dict: {
          38: 'previous',
          40: 'next',
        },
      }
    },
    watch: {
      schema_id: function (new_val, old_val) {
        this.api_attribute_group_list("from_project")
      },
      attribute_template_group_id(new_val, old_val) {
        this.api_attribute_group_list("from_project")
      },
      attribute_group_list_prop() {
        this.attribute_group_list = this.attribute_group_list_prop
        this.attribute_group_list = this.attribute_group_list_prop.sort((a, b) => a.ordinal - b.ordinal);
        this.attribute_group_list_computed
        if (this.attribute_group_list.length > 0 && this.openedPanel == undefined) {
          this.openedPanel = 0
        }
      },
      current_instance() {
        this.fetch_current_instance_missing_attributes("from_project")
      },
      attribute_list: function (new_value) {
        this.attribute_group_list = new_value
      }
    },
    created() {
      // is edit right name? or "from_project" as seperate context / mode here too
      if (this.mode == 'edit') {
        this.api_attribute_group_list("from_project")
      }
      if (this.mode == 'annotate') {
        this.attribute_group_list = this.attribute_group_list_prop
        this.fetch_current_instance_missing_attributes("from_project")
      }
    },
    mounted() {
      // ie triggered by  this.$store.commit('attribute_refresh_group_list')
      // defined in store.js action
      var self = this
      this.refresh_watcher = this.$store.watch((state) => {
          return this.$store.state.attribute.refresh_group_list
        },
        (new_val, old_val) => {
          self.api_attribute_group_list("from_project")
        },
      )

      if (this.$route.query.attribute_group) {
        this.open_panel_by_id(this.$route.query.attribute_group)
      }
      if (this.attribute_group_list.length > 0 && this.openedPanel == undefined) {
        this.openedPanel = 0
      }
      window.addEventListener('keydown', this.manage_key_down)
      window.addEventListener('keyup', this.manage_key_up)
    },
    destroyed() {
      window.removeEventListener('keydown', this.manage_key_down)
      window.removeEventListener('keyup', this.manage_key_up)
      this.refresh_watcher() // destroy
    },
    computed: {
      show_for_user_role: function(){
        if(!this.$store.state.user){
          return false
        }
        if(!this.$store.state.user.current){
          return false
        }
        if(this.$store.state.user.current.is_super_admin){
          return true
        }
        const member_id = this.$store.state.user.current.member_id
        const result = this.$store.getters.member_in_roles(member_id, ['admin', 'editor'])
        return result
      },
      show_ids: function(){
        return this.show_for_user_role
      },
      dragOptions() {
        return {
          animation: 200,
          group: "description",
          disabled: false,
          ghostClass: "ghost"
        };
      },
      attribute_group_list_computed: function () {
        if (!this.current_instance) {
          return this.attribute_group_list
        }
        let all_attributes = this.attribute_group_list.concat(this.out_of_schema_attributes);
        let result = [];
        for (let attr of all_attributes) {
          if (this.current_instance.type === 'global') {
            result.push(attr)
            continue
          }
          if (!attr.label_file_list && this.current_instance.type !== 'global') {
            continue
          }
          let id_list = attr.label_file_list.map(elm => elm.id);
          if (id_list.includes(this.current_instance.label_file_id)) {
            result.push(attr)
          }
        }
        return result
      }
    },
    methods: {
      open_panel_for_attribute_id: async function(attr_id){
        for(let i =0; i< this.attribute_group_list_computed.length; i++){
          if(attr_id === this.attribute_group_list_computed[i].id){
            this.openedPanel = i;
          }
        }
        await this.$nextTick()
      },
      manage_key_up: function(event){
        const shiftKey = 16;
        if (event.keyCode === shiftKey) {
          this.shift_key = false;
        }

      },
      change_open_attribute: async function(direction){
        if(isNaN(this.openedPanel)){
          this.openedPanel = 0
        }

        if (direction === 'next' && this.shift_key){
          this.openedPanel += 1
          if(this.openedPanel === this.attribute_group_list_computed.length - 1){
            this.openedPanel = 0
          }
        } else if(direction === 'previous' && this.shift_key){
          this.openedPanel -= 1
          if(this.openedPanel < 0){
            this.openedPanel = this.attribute_group_list_computed.length - 1
          }
        }
        await this.$nextTick()
        const attr = this.attribute_group_list_computed[this.openedPanel]
        if(attr && attr.kind === 'tree'){
          const attrRef = this.$refs[`attribute_group_${attr.id}`]
          if(attrRef && attrRef.length > 0){
            const treeInput = attrRef[0].$refs.treeview_search
            if(treeInput){
              await this.$nextTick()
              setTimeout(() => {
                treeInput.focus()
                // treeInput.$el.focus()
              }, 0)
            }
          }


        }
      },
      manage_key_down: async function(event){
        const shiftKey = 16;
        if (event.keyCode === shiftKey) {
          this.shift_key = true;
        }

        let direction = this.hotkey_dict[event.keyCode]
        if(direction){
          await this.change_open_attribute(direction)
        }
      },
      get_attribute_value: function(attribute_group_id: number){
        if(!attribute_group_id){
          return
        }
        if(!this.current_instance){
          return
        }

        let attr_values = this.current_instance.attribute_groups
        if(!attr_values){
          return
        }
        let attribute_value = attr_values[attribute_group_id]
        let attribute_group = this.attribute_group_list.find(group => group.id === attribute_group_id)
        if(!attribute_value || !attribute_group){
          return
        }
        if(['slider', 'date', 'time', 'text'].includes(attribute_group.kind)){
          return attribute_value
        } else if(['multiple_select'].includes(attribute_group.kind)){
          return attribute_value.map(elm => elm.display_name).toString()
        } else if(['select', 'radio'].includes(attribute_group.kind)){
          return attribute_value.display_name
        } else if(['tree'].includes(attribute_group.kind)){
          let result = ""
          for (let key of Object.keys(attribute_value)){
            let tree_val = attribute_value[key].name
            result += `${tree_val},`
          }
          result = result.substring(0, result.length - 1)
          return result
        }


      },
      on_drag_end: function(e){
        let old_index = e.oldIndex + 1
        let new_index = e.newIndex + 1
        let move_one = false
        for (let attr of this.attribute_group_list){
          if(attr.ordinal === old_index){
            attr.ordinal = new_index
            continue
          }
          // Move rest of items
          if(new_index > old_index){

            if(attr.ordinal <= new_index && attr.ordinal > old_index){
              if(attr.ordinal > 1){
                attr.ordinal -= 1
              }
            }
          } else if( new_index < old_index){
            if(attr.ordinal >=  new_index && attr.ordinal < old_index){
              if(attr.ordinal + 1 <= this.attribute_group_list.length){
                attr.ordinal += 1
              }
            }
          }
        }
        this.update_all_attributes()
      },
      update_all_attributes: async function(){
        if (this.loading_update_all_attributes == true ) {return}
        const limit = pLimit(3); // Max concurrent request.
        this.loading_update_all_attributes = true
        const promises = this.attribute_group_list.map(attribute_group => {
            return limit(() => attribute_group_update(this.project_string_id, 'UPDATE', attribute_group))
        });
        const result = await Promise.all(promises);
        this.loading_update_all_attributes = false
        return result
      },
      api_group_archive: async function (group: any) {
        this.loading = true
        this.error = {}
        this.success = false

        const [result, error] = await archive_attribute_group(this.project_string_id, group)

        if (result) {
          this.success = true
          this.$store.commit('attribute_refresh_group_list')
        } else {
          if (error.response.status == 400) {
            this.error = error.response.data.log.error
          }
        }
        this.loading = false
      },
      open_panel_by_id(id: number) {
        if (!this.attribute_group_list) {
          return
        }
        this.openedPanel = this.attribute_group_list.findIndex(x => {
          return x.id == id
        })
      },

      update_url_with_current_group(group) {
        if(group.is_read_only){
          return
        }
        this.$addQueriesToLocation({'attribute_group': group.id})
      },
      fetch_current_instance_missing_attributes: async function (mode) {
        /*
        * Fetches any attributes that are not on the current schema. This is useful when a user
        * changed the schema of a task template and it already had attributes from prev schema.
        * */

        if (!this.current_instance) {
          return
        }
        let attr_dict = this.current_instance.attribute_groups;
        if (!attr_dict) {
          return
        }
        let attribute_group_id_list = Object.keys(attr_dict).map(elm => parseInt(elm, 10));
        let existing_attribute_id_list = this.attribute_group_list.map(elm => elm.id);
        let missing_id_list = [];
        for (let id of attribute_group_id_list) {
          if (!existing_attribute_id_list.includes(id)) {
            missing_id_list.push(id)
          }
        }
        if (missing_id_list.length === 0) {
          return
        }

        let attr_data, error;

        if (!this.attribute_list && this.project_string_id) {
          [attr_data, error] = await attribute_group_list(
            this.project_string_id,
            undefined,
            undefined,
            mode,
            missing_id_list,
            true
          )
        } else {
          attr_data = this.attribute_list
        }

        if (error) {
          if (error.response.status == 400) {
            this.error = error.response.data.log.error
          }
          this.error = this.$route_api_errors(error)
          this.loading = false
          return
        }
        if (attr_data) {
          let attribute_group_list = attr_data.attribute_group_list
          this.out_of_schema_attributes = attribute_group_list

        }

      },
      api_attribute_group_list: async function (mode) {
        if (!this.project_string_id) {
          return
        }
        this.loading = true
        this.error = {}
        this.success = false
        let [attr_data, error] = await attribute_group_list(
          this.project_string_id,
          this.attribute_template_group_id,
          this.schema_id,
          mode,
          undefined,
          true
        )
        if (error) {
          if (error.response.status == 400) {
            this.error = error.response.data.log.error
          }
          this.error = this.$route_api_errors(error)
          this.loading = false
          return
        }
        if (attr_data) {
          let attribute_group_list = attr_data.attribute_group_list
          attribute_group_list = attribute_group_list.sort((a, b) => a.ordinal - b.ordinal);
          this.attribute_group_list = attribute_group_list.map((elm, index) => {
            elm.ordinal = index + 1
            return elm
          })
          this.attribute_group_list = attribute_group_list.sort((a, b) => a.ordinal - b.ordinal);
          await this.fetch_current_instance_missing_attributes(mode)
          this.success = true
          this.loading = false

        }
      }


    }
  }
)
</script>

<style>
.button {
  margin-top: 35px;
}

.flip-list-move {
  transition: transform 0.5s !important;
}

.no-move {
  transition: transform 0s !important;
}

.ghost {
  opacity: 0.5;
  background: #c8ebfb;
}

.list-group {
  min-height: 20px;
  width: 100%;
}

.list-group-item {
  cursor: move;
}

.list-group-item i {
  cursor: pointer;
}
.read-only{

}
</style>
