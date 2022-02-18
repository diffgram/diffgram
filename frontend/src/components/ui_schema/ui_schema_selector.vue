<template>
<div>
<v-select
      class="pt-0 pb-0"
      data-cy="ui_schema_select"
      ref="ui_schema_select"
      :items="ui_schema_list_computed"
      v-model="current_ui_schema"
      :label="label"
      :item-value="null"
      return-object
      :disabled="disabled"
      :clearable="clearable"
      @focus="$store.commit('set_user_is_typing_or_menu_open', true)"
      @update:return-value="$store.commit('set_user_is_typing_or_menu_open', false)"
      @blur="$store.commit('set_user_is_typing_or_menu_open', false)"
      @change="$emit('change', $event)"
      :menu-props="{ auto: true }"
          >
    <!-- For :menu-props="{ auto: true }" see
      https://github.com/vuetifyjs/vuetify/issues/10750 (which leads to ->)
      https://github.com/vuetifyjs/vuetify/issues/2660
      -->

<template v-slot:prepend-item v-slot:no-data>
  <v-container>
    <v-layout>
      <div class="pt-4 pr-4">

        <tooltip_button
            tooltip_message="Refresh"
            @click="refresh"
            icon="refresh"
            :icon_style="true"
            color="primary">
        </tooltip_button>

          {{ui_schema_list_computed.length}}

      </div>

      <v-text-field label="Name"
                    v-model="name_search"
                    @change="refresh()"
                    clearable
      >
      </v-text-field>

      <date_picker
            @date="store_date_and_refresh($event)"
            :with_spacer="false"
            :initialize_empty="true">
      </date_picker>

      <v-checkbox v-model="archived_search"
                  @change="refresh()"
                  label="Show Archived">
      </v-checkbox>

    </v-layout>

    <v-progress-linear
      v-if="loading"
      indeterminate
      rounded
      height="3"
      attach
    ></v-progress-linear>

    <v_error_multiple :error="error">
    </v_error_multiple>

  </v-container>

</template>

  <template v-slot:item="data">

    <v-skeleton-loader
      :loading="loading"
      type="text"
    >
      <v-icon left>
        mdi-page-layout-body
      </v-icon>

      <b>
      {{data.item.name}}
      </b>

      (<span>{{data.item.created_time | moment("from")}} </span>)

      ID: {{ data.item.id }}

      <v-icon
              v-if="data.item.is_public"
              right>
        mdi-earth
      </v-icon>
      <span v-if="data.item.is_public">
        Public Example
      </span>

    </v-skeleton-loader>

  </template>

  <template v-slot:selection="data">

    <v-icon left>
      mdi-page-layout-body
    </v-icon>

    <v-icon left
            color="primary">
      language-javascript
    </v-icon>

    <span> {{data.item.name}} </span>


    <v-icon v-if="data.item.is_public"
            class="pl-2 pr-2">
      mdi-earth
    </v-icon>
    <span v-if="data.item.is_public">
      Public Example
    </span>

  </template>


</v-select>

</div>
</template>

<script lang="ts">

import axios from '../../services/customInstance';
import Vue from "vue";

export default Vue.extend({
  name: 'ui_schema_selector',
  props: {
    'project_string_id': {
      default: null
    },
    'show_default_option': {
      default: false
    },
    'clearable': {
      default: null
    },
    'blocklist': {
      default: undefined
    },
    'disabled': {
      default: false
    },
    'label': {
      default: "Select a Schema"
    },
    'current_ui_schema_prop': {  //eg for when external thing creates a new one
      default: null
    }
  },
  components: {

  },
  data() {
    return {
      current_ui_schema: {},
      default_ui_schema: {id: undefined, name: 'Diffgram Default UI'},
      date: undefined,
      name_search: undefined,
      archived_search: false,

      error: {},
      internal_ui_schema_list: [],
      loading: false

    }
  },
  created() {

  },
  mounted() {
    this.refresh()
  },
  computed: {
    ui_schema_list_computed() {

      let list = this.internal_ui_schema_list.slice() // note slice, not reference

      if (this.blocklist){
        for (let i=0; i < list.length; i++){
            if (this.blocklist.find( x => {
                  return x.id == list[i].id}))
            {
            list.splice(i, 1)
          }
        }
      }
      //console.debug(list)
      return list
    },
    computed_project_string_id: function () {
      if (this.$props.project_string_id) {
        return this.$props.project_string_id;
      }
      return this.$store.state.project.current.project_string_id;
    },
  },

  watch: {
    current_ui_schema_prop (ui_schema) {
      this.internal_ui_schema_list.splice(0, 0, ui_schema)
      this.current_ui_schema = ui_schema
    }
  },

  methods: {
    async refresh(){

      this.loading = true;
      this.error = {}

      try {
        const result = await axios.post(
          `/api/v1/project/${this.computed_project_string_id}`+
          `/ui_schema/list`, {

          'date_from': this.date ? this.date.from : undefined,
          'date_to': this.date ? this.date.to : undefined,
          'name': this.name_search ? this.name_search : undefined,
          'archived': this.archived_search ? this.archived_search : undefined

        })
        if (result.status === 200) {
          this.internal_ui_schema_list = result.data.ui_schema_list
          if(this.$props.show_default_option){
            this.internal_ui_schema_list.unshift(this.default_ui_schema)
            this.current_ui_schema = this.default_ui_schema
          }
        }
      } catch (error) {
        this.error = this.$route_api_errors(error)

      } finally {
        this.loading = false;
      }
    },

    store_date_and_refresh(event) {
      this.date = event
      this.refresh()
    },

  },
  beforeDestroy() {
  }
})
</script>


<style scoped>

  .v-list {
    height: 500px;
    overflow-y: auto
  }

</style>
