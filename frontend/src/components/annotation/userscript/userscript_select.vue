<template>
<div>
<v-select
      class="pt-0 pb-0"
      data-cy="userscript_select"
      ref="userscript_select"
      :items="userscript_list_computed"
      v-model="current_userscript"
      :label="label"
      :item-value="null"
      return-object
      :disabled="disabled"
      :clearable="clearable"
      @focus="$store.commit('set_user_is_typing_or_menu_open', true)"
      @update:return-value="$store.commit('set_user_is_typing_or_menu_open', false)"
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

          {{userscript_list_computed.length}}

      </div>

      <v-text-field label="Name"
                    v-model="name_search"
                    @change="refresh"
                    clearable
      >
      </v-text-field>

      <date_picker
            @date="store_date_and_refresh($event)"
            :with_spacer="false"
            :initialize_empty="true">
      </date_picker>

      <v-checkbox v-model="archived_search"
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
        mdi-language-javascript
      </v-icon>

      <b>
      {{data.item.name}}
      </b>

      (<span>{{data.item.time_created | moment("dd, MM D h:mm:ss a")}} </span>)

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
      mdi-language-javascript
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

import axios from 'axios';
import Vue from "vue";

export default Vue.extend({
  name: 'userscript_selector',
  props: {
    'project_string_id': {
      default: null
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
      default: null
    },
    'current_userscript_prop': {  //eg for when external thing creates a new one
      default: null
    }
  },
  components: {

  },
  data() {
    return {
      current_userscript: {},

      date: undefined,
      name_search: undefined,
      archived_search: false,

      error: {},
      internal_userscript_list: [],
      loading: false

    }
  },
  created() {

  },
  mounted() {
    this.refresh()
  },
  computed: {
    userscript_list_computed() {

      let list = this.internal_userscript_list.slice() // note slice, not reference

      if (this.blocklist){
        for (let i=0; i < list.length; i++){
            if (this.blocklist.find( x => {
                  return x.id == list[i].id}))
            {
            //console.log("Found", list[i])
            list.splice(i, 1)
          }
        }
      }
      //console.debug(list)
      return list
    }
  },

  watch: {
    current_userscript_prop (userscript) {
      this.internal_userscript_list.splice(0, 0, userscript)
      this.current_userscript = userscript
    }
  },

  methods: {
    async refresh(){

      this.loading = true;
      this.error = {}

      try {
        const result = await axios.post(
          `/api/v1/project/${this.$props.project_string_id}`+
          `/userscript/list`, {

          'date_from': this.date ? this.date.from : undefined,
          'date_to': this.date ? this.date.to : undefined,
          'name': this.name_search ? this.name_search : undefined,
          'archived': this.archived_search ? this.archived_search : undefined

        })
        if (result.status === 200) {
          this.internal_userscript_list = result.data.userscript_list

          if (this.internal_userscript_list &&
            this.internal_userscript_list[0]) {

            // temp disable because swapping doesn't clear as expected
            //this.current_userscript = this.internal_userscript_list[0]
            //this.$emit('change', this.current_userscript)
           
          }
        }

      } catch (error) {
        this.error = this.$route_api_errors(error)
        console.log(this.error)

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
