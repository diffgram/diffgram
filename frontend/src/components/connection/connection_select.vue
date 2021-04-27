<template>
    <div v-if="connection_list.length > 0 || add_diffgram_default_option">
    <v-row v-if="display_mode==='select'"
           justify="start">

      <!--
       Use custom select (instead of Diffgram select)
        because we expect high degree of customization here

        Makes
         $store.state.connection.default
         available
         and also emits 'change' event on change

        Handles updating connection list in store if no
        connections are there yet

      CAUTION
        We don't want 'item-text' here, otherwise if the name is the same
        it will only show 1 and hide the rest. (And it's especially confusing
        as then it looks like list isn't working, but we see if we replace
        the veux with local list / watcher it works as expected.)
      -->

      <v-col cols="10">
        <v-select
          v-if="$store.state.connection.connection_list.length != 0 || add_diffgram_default_option"
          :items="connection_list"
          @change="change_connection($event)"
          v-model="connection_internal_value"
          :label="label"
          style="min-width: 300px"
          return-object
          item-value="id"
          :loading="loading || connection_list_loading"
          :disabled="disabled || connection_list_loading"
          clearable
          data-cy="connection-select-input"
        >

          <template v-slot:item="data">

        <span class="d-flex align-center">
          <icon_from_regular_list
            class="mr-1"
            :item_list="$store.state.connection.integration_spec_list"
            :value="data.item.integration_name"
          >
          </icon_from_regular_list>

          <span>{{data.item.name}}</span>
          <span v-if="data.item.time_created">
            ({{data.item.time_created | moment("MMM Do, YYYY") }})
           </span>
         </span>

          </template>

          <!-- Duplicate because veutify needs
            it - at least last time checked early 2020 -->

          <template v-slot:selection="data">

        <span>
          <icon_from_regular_list
            :item_list="$store.state.connection.integration_spec_list"
            :value="data.item.integration_name"
          >
          </icon_from_regular_list>

          {{data.item.name}}
          <span v-if="data.item.time_created">
            ({{data.item.time_created | moment("MMM Do, YYYY") }})
           </span>
         </span>

          </template>


        </v-select>
      </v-col>
      <v-col cols="1" class="pa-0 d-flex align-center">
        <button_with_menu
          tooltip_message="New Connection"
          icon="add"
          :close_by_button="true"
          v-if="!view_only_mode && show_new == true"
          offset="x"
          :large="false"
          color="primary"
          :commit_menu_status="true"
          font_size="small"
          ref="add_menu"
        >

          <template slot="content">
            <connection_form
              connection_id="new"
              :may_edit="true"
              :show_return_button="false"
              :buttons_size_large="false"
              form_width="500px"
              form_height="100%"
              :redirect_on_create="false"
              :reset_on_create="false"
              @connection-created="on_connection_created"
            >
            </connection_form>

          </template>

        </button_with_menu>
      </v-col>
      <v-col cols="1" class="pa-0 d-flex align-center">
        <button_with_menu
          tooltip_message="Edit Connection"
          :disabled="connection_internal_value_id === -1"
          icon="edit"
          :close_by_button="true"
          v-if="!view_only_mode
              && show_new === true
              && connection_internal_value
              && Object.keys(connection_internal_value).length > 0"
          offset="x"
          color="primary"
          :large="false"
          :commit_menu_status="true"
          font_size="small"
          ref="edit_menu"
        >

          <template slot="content">
            <connection_form
              :connection_id="connection_internal_value_id"
              :may_edit="true"
              :show_return_button="false"
              form_width="500px"
              form_height="100%"
              :buttons_size_large="false"
              font_size="small"
              :redirect_on_create="false"
              @connection-updated="on_connection_updated"
            >
            </connection_form>

          </template>

        </button_with_menu>
      </v-col>


    </v-row>
    <v-layout class="d-flex flex-column" v-if="display_mode==='icons'">
      <v-row>
        <v-col col="12" class="d-flex justify-end align-center">
          <h3>New Connection: </h3>
          <button_with_menu
            tooltip_message="New Connection"
            icon="add"
            :close_by_button="true"
            v-if="!view_only_mode && show_new == true"
            offset="x"
            color="primary"
            :commit_menu_status="true"
            font_size="small"
            ref="add_menu"
          >
            <template slot="content">
              <connection_form
                connection_id="new"
                :may_edit="true"
                :show_return_button="false"
                :buttons_size_large="false"
                form_width="500px"
                form_height="100%"
                :redirect_on_create="false"
                :reset_on_create="true"
                @connection-created="on_connection_created"
              >
              </connection_form>
            </template>

          </button_with_menu>
        </v-col>
      </v-row>
      <v-row justify="center">
        <v-col v-for="connection in $store.state.connection.connection_list" :key="connection.id" cols="3">
          <v-card
            v-bind:class="{'vendor-card': true, 'selected': connection_internal_value && (connection.id === connection_internal_value.id)}"
            elevation="4"
            :data-cy="`connection-box-${connection.name}`"
            @click="change_connection(connection)"
            min-height="250px"
            width="230px">
            <button_with_menu

              tooltip_message="Edit Connection"
              icon="edit"
              :close_by_button="true"
              v-if="!view_only_mode && show_new && connection && Object.keys(connection).length > 0"
              offset="x"
              color="primary"
              :commit_menu_status="true"
              font_size="small"
              ref="edit_menu"
            >

              <template slot="content">
                <connection_form
                  :connection_id="connection ? connection.id : ''"
                  :may_edit="true"
                  :show_return_button="false"
                  form_width="500px"
                  form_height="100%"
                  :buttons_size_large="false"
                  font_size="small"
                  :redirect_on_create="false"
                  @connection-updated="on_connection_updated"
                >
                </connection_form>

              </template>

            </button_with_menu>
            <v-card-text class="d-flex">
              <v-img :src="vendor_images[connection.integration_name].image" width="45" height="65px"></v-img>
            </v-card-text>
            <v-card-title class="text-center vendor-text d-flex justify-center align-center align-content-center">
              {{connection.name}}
            </v-card-title>
          </v-card>
        </v-col>
      </v-row>
    </v-layout>
  </div>
  <v-container v-else-if="connection_list.length === 0 && hide_if_empty"></v-container>
  <v-layout v-else class="empty-placeholder-container" column style="min-height: 120px">
    <v-row class="icons-container d-flex pb-0">
      <v-col cols="12" class="d-flex justify-center ">
        <div class="icon-container">
          <v-img class="ma-0" height="65" width="65"
                 src="https://cdn.iconscout.com/icon/free/png-512/google-cloud-2038785-1721675.png"></v-img>

        </div>
        <div class="icon-container">
          <v-img class="ma-0" height="65" width="75"
                 src="https://www.ntirety.com/wp-content/uploads/2019/09/aws.png"></v-img>
        </div>
        <div class="icon-container">
          <v-img class="ma-0" height="65" width="65"
                 src="https://image.flaticon.com/icons/png/512/873/873107.png"></v-img>
        </div>

      </v-col>
    </v-row>
    <v-row class="pt-0 pb-5">
      <v-col cols="12">
        <text_with_menu
          tooltip_message="Setup a new connection"
          tooltip_direction="left"
          menu_direction="top"
          :close_by_button="true"
          v-if="!view_only_mode && show_new == true"
          offset="x"
          color="primary"
          :commit_menu_status="true"
          font_size="small"
          ref="add_menu"
        >
          <template slot="content">
            <connection_form
              connection_id="new"
              :may_edit="true"
              :show_return_button="false"
              :buttons_size_large="false"
              form_width="500px"
              form_height="100%"
              :redirect_on_create="false"
              :reset_on_create="true"
              @connection-created="on_connection_created"
            >
            </connection_form>
          </template>

        </text_with_menu>

      </v-col>
    </v-row>

  </v-layout>
</template>


<script lang="ts">
  import Vue from "vue";
  import axios from 'axios';
  import connection_form from './connection_form';

  export default Vue.extend({
      name: 'connection_select',
      props: {
        'value': {
          default: null
        },
        'add_diffgram_default_option': {
          default: false
        },
        'features_filters': {
          default: {}
        },
        'project_string_id': {
          default: null
        },
        'view_only_mode': {
          default: false
        },
        'show_new': {
          default: false
        },
        'show_edit': {
          default: false
        },
        'hide_if_empty': {
          default: false
        },
        'label': {
          default: "Connection",
          type: String
        },
        'disabled': {
          default: false,
          type: Boolean
        },
        'loading': {
          default: false,
          type: Boolean
        },
        'start_empty': {
          default: false,
          type: Boolean
        },
        'display_mode': {
          default: 'select',
          type: String
        }
      },
      components: {
        connection_form
      },
      data() {
        return {

          connection_internal_value: null,

          new_connection_menu: false,

          connection_list_loading: false,

          permission_scope: "project",
          vendor_images: {

            'amazon_aws': {
              'image': 'https://a0.awsstatic.com/libra-css/images/logos/aws_logo_smile_1200x630.png'
            },
            'google_gcp': {
              'image': 'https://cloud.google.com/images/social-icon-google-cloud-1200-630.png'
            },
            'microsoft_azure': {
              'image': 'https://dz2cdn1.dzone.com/storage/temp/12165862-azurelogo-1.png',
            }
          },
        }
      },
      mounted() {

        this.connection_list_api()

        if (this.value &&
          this.value.id &&
          this.$store.state.connection.connection_list) {

          const init_value = this.$store.state.connection.connection_list.find(
            x => {
              return x.id == this.value.id
            }
          )

          this.connection_internal_value = init_value;
          // Handle intial data updating
          this.change_connection(init_value)


        } else {
          if (!this.$props.start_empty) {
            this.connection_internal_value = this.$store.state.connection.default
            // Handle intial data updating
            this.change_connection(this.$store.state.connection.default)
          }
          if(this.$props.add_diffgram_default_option){
            const init_value = this.connection_list.find(
              x => {
                return x.integration_name == 'diffgram'
              }
            )
            this.connection_internal_value = init_value;
            this.change_connection(init_value)
          }

        }


      },
      computed: {
        connection_internal_value_id() {
          if (this.connection_internal_value) {
            return this.connection_internal_value.id
          }
          return undefined;
        },
        connection_list() {
          const conn_list = this.$store.state.connection.connection_list.filter(connection => {
            const filterRes = []
            for (const [key, value] of Object.entries(this.features_filters)) {
              filterRes.push(connection.supported_features[key] === value)
            }
            return filterRes.reduce((a, b) => a && b, true);
          });
          // For showing diffgram's default interface option.
          // Becuase the connection list is otherwise based on connections for a specific project
          // eg *not* generic. This is seperate from the icon.
          if (this.$props.add_diffgram_default_option){
            conn_list.push({
              name: "Diffgram (Default)",
              integration_name: 'diffgram',
              id: null,
            })
          }
          return conn_list;
        }
      },
      methods: {
        select_connection(connection) {
          this.connection_internal_value = connection;
        },

        connection_list_api() {

          this.connection_list_loading = true

          axios.post('/api/v1/connection/list', {

            permission_scope: this.permission_scope,
            project_string_id: this.project_string_id,
            org_id: null


          }).then(response => {

            this.$store.commit('set_connection_list', response.data.connection_list)
            this.connection_list_loading = false

          })
            .catch(error => {
              console.log(error);
              this.connection_list_loading = false

            });
        },

        change_connection(connection) {

          this.$store.commit('set_default_connection', connection)

          this.$emit('change', connection)
          this.$emit('input', connection);  // for standard v-model stuff

          if (this.display_mode === 'icons') {
            this.$emit('onChange', connection);
            this.select_connection(connection);
          }


        },
        on_connection_created(connection) {
          // this.select_connection(connection);
          // this.change_connection(connection);
          // this.$refs.add_menu.close_menu();

        },
        on_connection_updated(connection) {
          // I Refecth from API because connection might get archived and in that case it should disappear from dropdown.
          this.connection_list_api();
          // this.select_connection(connection);
          // this.change_connection(connection);
          // this.$refs.edit_menu.close_menu();
        }
      },

    }
  )
</script>
<style scoped>
  .vendor-text {
    font-size: 1rem;
    text-align: center;
  }

  .vendor-card.selected {
    border: 2px solid #bdbdbd;
  }

  .empty-placeholder-container {
    background: #f7f7f7;

  }


  .icons-container {
    padding: 2rem 6rem 2rem 6rem;
  }

  .icon-container {
    margin-right: 3rem;
  }
</style>
