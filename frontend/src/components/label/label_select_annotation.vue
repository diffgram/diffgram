<template>
  <div 
    id="label_select_annotation"
    ref="label_select_annotation"
    class="label_select_annotation"
  >
      <v-autocomplete 
        v-model="selected"
        return-object
        item-value="id"
        ref="label_select"
        :items="label_list_with_limit"
        :label="label_prompt"
        :data-cy="datacy"
        :disabled="label_refresh_loading"
        :filter="on_filter_labels"
        @change="emit_selected()"
        @focus="on_focus"
        @blur="on_blur"
      >
        <template v-slot:item="data">
          <v-icon 
            left
            :style="style_color(data.item.colour.hex)">
            mdi-flag
          </v-icon>

          <div 
            class="pl-4 pr-4"
            :data-cy="data.item.label.name"
          >
            {{data.item.label.name}}
           </div>
          <div v-if="show_visibility_toggle || data.item.is_visible === false">
            <v-layout>
              <div v-if="data.item.is_visible === true || data.item.is_visible === null">
                <standard_button
                  icon_style
                  bottom
                  color="grey lighten-1"
                  icon="remove_red_eye"
                  tooltip_message="Hide"
                  @click="toggle_label_visible(data.item)"
                />
              </div>

              <div v-if="data.item.is_visible === false">
                <standard_button
                  icon_style
                  bottom 
                  color="grey"
                  icon="mdi-eye-off"
                  tooltip_message="Show"
                  @click="toggle_label_visible(data.item)"
                />
              </div>
            </v-layout>
            </div>
        </template>

        <template v-slot:selection="data">
          <div>
            <v-icon
              left
              :style="style_color(data.item.colour.hex)"
            >
              mdi-flag
            </v-icon>
            {{ label_name_truncated(data.item.label.name) }}
          </div>
        </template>

        <template v-slot:no-data>
          <div class="d-flex flex-column align-center justify-center">
            No Labels Templates Created.
            <v-btn 
              color="primary" 
              small 
              @click="$router.push(`/project/${project_string_id}/labels`)"
            >
              <v-icon>
                mdi-plus
              </v-icon>
              Create New
            </v-btn>
          </div>
        </template>
      </v-autocomplete>
  </div>
</template>

<script lang="ts">
import Vue from "vue";
import { get_labels } from '../../services/labelServices';

export default Vue.extend({
  name: 'label_select_annotation',
  props: {
    project_string_id: {
      type: String,
      required: true
    },
    view_only_mode: {
      type: Boolean,
      default: false
    },
    datacy: {
      type: String,
      default: 'label_select_annotation'
    },
    default_hot_keys: {
      type: String,
      default: 'w'
    },
    request_refresh_from_project: {
      type: Boolean,
      default: false
    },
    label_prompt: {
      type: String,
      default: 'Label'
    },
    show_visibility_toggle: {
      type: Boolean,
      default: false
    },
    schema_id: {
      type: Number,
      default: undefined
    },
    select_this_id_at_load: {
      type: Number,
      default: undefined
    },
    is_typing_or_menu_open: {
      type: Boolean,
      default: false
    }
  },
  watch: {
    schema_id: function(): void {
      this.get_label_list_from_project()
    },
    request_refresh_from_project: function (): void {
      this.get_label_list_from_project()
    },
  },
  mounted() {
    if (this.label_file_list_prop) {
      this.label_list = this.label_file_list_prop
      this.selected = this.label_file_list_prop[0]
    } else {
      this.get_label_list_from_project()
    }

    if (this.select_this_id_at_load) {
      this.selected = this.label_list.find(
        (obj: Object): Object => obj["id"] === this.select_this_id_at_load
      )

      this.emit_selected()
    }

    window.addEventListener('keyup', this.keyboard_events_window);
  },
  beforeDestroy() {
    window.removeEventListener('keyup', this.keyboard_events_window)
  },
  computed: {
    label_list_with_limit: function (): Array<Object> {
      this.over_limit = false
      return this.label_list
    }
  },
  data() {
    return {
      label_refresh_loading: false as Boolean,
      error: null as Object,
      selected: {} as Object,
      label_list: [] as Array<Object>,
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
      } as Object,
    }
  },
  methods: {
    on_focus: function(): void {
      this.$emit('on_focus')
    },
    on_blur: function() :void {
      this.$emit('on_blur')
    },
    on_filter_labels: function(item: any, query_text: string): Array<any> {
      return item.label.name.toLocaleLowerCase().includes(query_text.toLocaleLowerCase())
    },
    label_name_truncated: function(name: string): string {
      let max_size = 23
      const default_selector_size = 290
      const selector_offset_width = this.$refs.label_select_annotation.offsetWidth
      
      if (selector_offset_width < default_selector_size) max_size = 5
          
      if (name.length > max_size) return name.slice(0, max_size) + '...'
      else return name
    },
    toggle_label_visible(label: any): void {
      if (typeof label.is_visible === "undefined") {
        label.is_visible = false
      } 
      else {
        label.is_visible = !label.is_visible
      }

      this.label_list.splice(this.label_list.indexOf(label), 1, label)
      this.$emit('update_label_file_visible', label)
    },
    get_label_list_from_project: async function(): Promise<void> {
      this.label_refresh_loading = true
      let [result, error] = await get_labels(this.project_string_id, this.$props.schema_id)
      if (error) {
        this.error = this.$route_api_errors(error)
      }
      
      if (result) {
        this.label_list = result.labels_out
        this.selected = this.label_list[0]
        this.emit_selected()
      }
      
      this.label_refresh_loading = false
    },
    toggle_label_menu: function(): void {
      this.$refs.label_select.isMenuActive = !this.$refs.label_select.isMenuActive;
    },
    style_color: function (hex: string): string {
      return "color:" + hex
    },
    emit_selected: function (): void {
      this.$emit('change', this.selected);
      this.$refs.label_select.blur()
    },
    keyboard_events_window: function (event: KeyboardEvent): void {
      if (this.is_typing_or_menu_open === true) return
      
      if (event.key === this.default_hot_keys) {
        this.toggle_label_menu()
        return
      }

      const hotkey = this.hotkey_dict[event.keyCode]
      if (hotkey !== null) {
        this.selected = this.label_list[hotkey]
        this.emit_selected()
      }
    }
  }
}) 
</script>

<style scoped>
.label_select_annotation {
  max-width: 300px;
}
</style>
