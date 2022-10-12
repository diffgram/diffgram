<template>
  <div id="">
    <v-layout class="d-flex align-center">
      <div class="pl-4 pr-2">
        <v-select
          v-model="current_directory"
          return-object
          data-cy="directory_select"
          ref="diffgram_select"
          :items="dataset_list_filtered"
          :label="label"
          :item-value="null"
          :color="show_text_buttons ? 'white' : 'primary'"
          :disabled="view_only_mode"
          :clearable="clearable"
          :menu-props="{ auto: true }"
          :multiple="multiple"
          @focus="$emit('on_focus')"
          @blur="$emit('on_blur')"
          @change="change_dataset()"
        >
          <template v-slot:prepend-item>
            <div class="pl-2 pr-2">
              <div class=" d-flex  align-center pr-4" >
                <div>
                  <button_with_menu
                    v-if="!view_only_mode && show_new === true"
                    icon="mdi-plus"
                    offset="x"
                    menu_direction="left"
                    background="primary"
                    :tooltip_message="show_text_buttons ? undefined : 'Create Dataset'"
                    :button_text="show_text_buttons ? 'Create Dataset' : undefined"
                    :close_by_button="true"
                    :small="true"
                    :large="undefined"
                    :color="show_text_buttons ? 'white' : 'primary'"
                    :text_style="undefined"
                  >
                    <template slot="content">
                      <dataset_new 
                        :project_string_id="project_string_id"
                        @dataset_created="on_dataset_created" 
                      />
                    </template>
                  </button_with_menu>
                </div>
                <standard_button
                  icon="refresh"
                  color="primary"
                  tooltip_message="Refresh"
                  :icon_style="true"
                  @click="refresh_dataset_list"
                />
                <div class="mr-4">
                  <v-chip 
                    small
                    color="secondary" 
                  > 
                    Total: {{ dataset_list_filtered.length }}
                  </v-chip>
                </div>

                <v-text-field 
                  v-model="nickname"
                  clearable
                  label="Name"
                  style="width: 275px"
                  @change="refresh_dataset_list"
                />

                <date_picker
                  style="width: 450px;"
                  :with_spacer="false"
                  :initialize_empty="true"
                  @date="store_date_and_refresh($event)"
                />
              </div>

              <v-progress-linear
                v-if="loading_dataset_list"
                indeterminate
                rounded
                attach
                height="3"
              />

              <v_error_multiple :error="error_dataset_list" />
            </div>
          </template>

          <template v-slot:item="data">
            <v-skeleton-loader
              type="text"
              :loading="loading_dataset_list"
            >
              <div class="d-flex">
                <div style="width: 75px">
                  <v-chip 
                    v-if="is_super_admin"
                    x-small 
                  >
                    ID: {{ data.item.directory_id }}
                  </v-chip>
                </div>

                <v-icon left>
                  mdi-folder-network
                </v-icon>

                {{ data.item.nickname }}

                (<span>{{format_time_string(data.item.created_time)}}</span>)
              </div>
            </v-skeleton-loader>
          </template>

          <template v-slot:selection="data">
            <v-chip  
              v-if="is_super_admin"
              x-small 
            >
              ID: {{ data.item.directory_id }}
            </v-chip>

            <v-icon 
              left
              color="primary"
            >
              mdi-folder-network
            </v-icon>

            <span> 
              {{data.item.nickname}} 
            </span>
          </template>
        </v-select>
      </div>

      <button_with_menu
        v-if="!view_only_mode && show_update == true"
        icon="mdi-pencil-outline"
        tooltip_message="Update Dataset"
        color="primary"
        offset="x"
        background="white"
        menu_direction="left"
        :small="true"
        :large="undefined"
        :button_text="undefined"
        :close_by_button="true"
        :outlined="true"
      >
        <template slot="content">
          <dataset_update 
            :project_string_id="project_string_id"
            :current_directory_prop="current_directory"
          />
        </template>
      </button_with_menu>
    </v-layout>
  </div>
</template>

<script lang="ts">
import Vue from "vue";
import moment from "moment"
import dataset_new from "./dataset_new.vue"
import dataset_update from "./dataset_update.vue"
import date_picker from "../../regular/date_picker.vue"
import button_with_menu from "../../regular/button_with_menu.vue"
import { refresh_dataset_list } from "../../../services/datasetServices";

export default Vue.extend({
  name: 'dataset_selector',
  props: {
    project_string_id: {
      type: String,
      required: true
    },
    clearable: {
      type: Boolean,
      default: false
    },
    dataset_blacklist: {
      type: Array,
      default: undefined
    },
    initial_dir_from_state: {
      type: Boolean,
      default: true
    },
    set_current_dir_on_change: {
      type: Boolean,
      default: true,
    },
    change_on_mount: {
      type: Boolean,
      default: true,
    },
    view_only_mode: {
      type: Boolean,
      default: false
    },
    multiple: {
      type: Boolean,
      default: false
    },
    show_text_buttons:{
      type: Boolean,
      default: false
    },
    update_from_state: {
      type: Boolean,
      default: true
    },
    show_new: {
      type: Boolean,
      default: false
    },
    show_update: {
      type: Boolean,
      default: false
    },
    set_from_id: {
      type: Number,
      default: null
    },
    label: {
      type: String,
      default: "Dataset"
    },
    is_super_admin: {
      type: Boolean,
      default: false
    },
    dataset_list: {
      type: Array,
      default: () => []
    }
  },
  components: {
    dataset_new,
    dataset_update,
    date_picker,
    button_with_menu
  },
  data() {
    return {
      new_directory_menu: false as boolean,
      update_directory_menu: false as boolean,
      current_directory: {} as boolean,
      loading_dataset_list: false as boolean,
      nickname: null as string,
      date: undefined as string,
      error_dataset_list: {} as object,
      internal_dataset_list: undefined as object
    }
  },
  mounted() {
    this.current_directory = this.multiple ? [] : {}

    if (this.dataset_list) {
      this.internal_dataset_list = this.dataset_list
    }

    if (this.set_from_id) {
      this.current_directory = this.dataset_list_filtered.find((dataset:any) => dataset.directory_id === this.set_from_id)
    }

    if(this.change_on_mount){
      this.$emit('change_dataset', this.current_directory)
    }
  },
  computed: {
    dataset_list_filtered(): Array<object> {
      if(!this.internal_dataset_list){
        return []
      }
      const workign_list = [...this.internal_dataset_list]

      let list: Array<object>;

      if (this.dataset_blacklist) {
        list = workign_list.filter(dataset => {
          this.dataset_blacklist.find((blacklisted_dataset: any) => blacklisted_dataset.id == dataset.id )
        })
      }
      else {
        list = workign_list
      }

      return list.sort((first_dataset, second_dataset) => {
        const result = new Date(second_dataset.created_time) - new Date(first_dataset.created_time)
        return result;
      });
    }
  },
  watch: {
    set_from_id(id: number): void {
      this.current_directory = this.get_dataset_object_from_directory_list_using_id(id)
      this.$emit('on_set_current_directory', this.current_directory)
    }
  },
  methods: {
    format_time_string(date: string): string {
      const date_bject = new Date(date)
      return moment(date_bject).format("ddd, MMM D h:mm a")
    },
    store_date_and_refresh(event: Event): void {
      this.date = event
      this.refresh_dataset_list()
    },
    on_dataset_created: function(directory: object): void {
      this.current_directory = directory;
      this.internal_dataset_list.push(directory)
      this.change_dataset();
    },
    get_dataset_object_from_directory_list_using_id(id: number) {
      if (!this.dataset_list_filtered) return null
      return this.dataset_list_filtered.find((dataset: any) => dataset.directory_id === id)
    },
    async refresh_dataset_list(): Promise<void> {
      this.loading_dataset_list = true;
      this.error_dataset_list = {}

      const payload = {
        date_from: this.date ? this.date.from : undefined,
        date_to: this.date ? this.date.to : undefined,
        nickname: this.nickname ? this.nickname : undefined
      }

       const [success, error] = await refresh_dataset_list(this.$props.project_string_id, payload)

      if (!error) {
        const dataset_list = success.directory_list.map((directory: any) => ({... directory, directory_id: directory.id }));
        this.internal_dataset_list = dataset_list
        this.$emit('on_refresh_dataset_list', dataset_list)
      } else {
        this.error_dataset_list = this.$route_api_errors(error)
      }

      this.loading_dataset_list = false;
    },
    change_dataset(): void {
      this.$emit('change_dataset', this.current_directory)
    },
    add_new_dataset(new_dataset: object): void {
      this.internal_dataset_list.push(new_dataset)
    }
  },
})
</script>


<style scoped>
.v-list {
  height: 500px;
  overflow-y: auto
}
</style>
