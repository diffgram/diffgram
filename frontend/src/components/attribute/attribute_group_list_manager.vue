<template>
  <div>
    <attribute_group_new
      :project_string_id="project_string_id">

    </attribute_group_new>

    <v-spacer></v-spacer>
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
      <v-expansion-panel v-for="group in attribute_group_list" :key="group.id">
        <v-expansion-panel-header
          :data-cy="`attribute_group_header_${group.prompt}`"
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
        </v-expansion-panel-header>

        <v-expansion-panel-content>

          <attribute_group
            :ref="`attribute_group_${group.id}`"
            :project_string_id="project_string_id"
            mode="edit"
            :view_only_mode="false"
            :group="group"
            :key="group.id"
            @attribute_change="$emit('attribute_change', $event)"
          >
          </attribute_group>


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
  </div>
</template>

<script lang="ts">


  import axios from '../../services/customInstance';
  import draggable from 'vuedraggable'

  import attribute_group from './attribute_group.vue';
  import attribute_kind_icons from './attribute_kind_icons.vue';
  import attribute_group_new from './attribute_group_new'


  import Vue from "vue";

  export default Vue.extend({
      name: 'attribute_group_list_manager',
      components: {
        draggable: draggable,
        attribute_group: attribute_group,
        attribute_kind_icons: attribute_kind_icons,
        attribute_group_new: attribute_group_new

      },
      props: {
        'project_string_id': {
          default: null
        },
        'attribute_group_list_prop': {
          default: null
        },
      },

      data() {
        return {
          loading: false,
          error: {},
          success: false,
          name: null,
          attribute_group_list: [],
          openedPanel: null
        }
      },

      watch: {
        attribute_template_group_id() {
          this.api_attribute_group_list()
        },

        attribute_group_list_prop() {
          this.attribute_group_list = this.attribute_group_list_prop
        }

      },

      async mounted() {
        await this.api_attribute_group_list("from_project")
        var self = this
        this.refresh_watcher = this.$store.watch((state) => {
            return this.$store.state.attribute.refresh_group_list
          },
          (new_val, old_val) => {
            self.api_attribute_group_list("from_project")
          },
        )
      },
      destroyed() {
        this.refresh_watcher() // destroy
      },
      computed: {},
      methods: {
        update_label_file_list_for_all_attributes: function(new_label_file_list){
          for(const group of this.attribute_group_list){
            let component = this.$refs[`attribute_group_${group.id}`][0]
            component.update_label_files(new_label_file_list)
          }
        },
        open_panel_by_id(id: number) {
          if (!this.attribute_group_list) {
            return
          }
          this.openedPanel = this.attribute_group_list.findIndex(x => {
            return x.id == id
          })
        },

        auto_open_new_group: function () {

          let last_element = this.attribute_group_list.at(-1)
          if (last_element) {
                this.open_panel_by_id(last_element.id)
            }
        },

        api_attribute_group_list: async function (mode) {

          this.loading = true
          this.error = {}
          this.success = false
          try{
            const response = await axios.post(
              `/api/v1/project/${this.project_string_id}/attribute/template/list`,
              {
                group_id: this.attribute_template_group_id,
                mode: mode

              })
            this.attribute_group_list = response.data.attribute_group_list

            this.auto_open_new_group()

            this.success = true

          }
          catch(error){
            if (error.response.status == 400) {
              this.error = error.response.data.log.error
            }
            console.error(error)
          }
          finally{
            this.loading = false
          }


        }


      }
    }
  ) </script>
