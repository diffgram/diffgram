<template>
  <div id="">

    <!-- Careful with too much padding around
        here it can make it look funny with other things ie the media window-->
    <v-layout class="d-flex align-center">

      <button_with_menu
        :tooltip_message="show_text_buttons ? undefined : 'Create Dataset'"
        icon="add"
        :button_text="show_text_buttons ? 'Create Dataset' : undefined"
        :close_by_button="true"
        v-if="!view_only_mode && show_new === true"
        offset="x"
        :small="true"
        :large="undefined"
        :color="show_text_buttons ? 'white' : 'primary'"
        menu_direction="left"
        background="primary"
        :commit_menu_status="true"
        :text_style="undefined"
      >

        <template slot="content">

          <v_new_directory
            @directory_created="on_directory_created"
            :project_string_id="project_string_id">
          </v_new_directory>

        </template>

      </button_with_menu>

      <div class="pl-4 pr-2">

        <v-select
              data-cy="directory_select"
              :items="directory_list_filtered"
              v-model="current_directory"
              :label="label"
              :item-value="null"
              :color="show_text_buttons ? 'white' : 'primary'"
              ref="diffgram_select"
              return-object
              :disabled="view_only_mode"
              :clearable="clearable"
              @focus="$store.commit('set_user_is_typing_or_menu_open', true)"
              @blur="$store.commit('set_user_is_typing_or_menu_open', false)"
              @change="change_directory(), $store.commit('set_user_is_typing_or_menu_open', false)"
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
                    @click="refresh_directory_list"
                    icon="refresh"
                    :icon_style="true"
                    color="primary">
                </tooltip_button>
                 {{directory_list_filtered.length}}
              </div>
              <v-text-field label="Name"
                            v-model="nickname"
                            @change="refresh_directory_list"
                            clearable
              >
              </v-text-field>
              <date_picker
                    @date="store_date_and_refresh($event)"
                    :with_spacer="false"
                    :initialize_empty="true">
              </date_picker>
            </v-layout>

            <v-progress-linear
              v-if="loading_directory_list"
              indeterminate
              rounded
              height="3"
              attach
            ></v-progress-linear>

            <v_error_multiple :error="error_directory_list">
            </v_error_multiple>

          </v-container>

        </template>

         <template v-slot:item="data">

            <v-skeleton-loader
              :loading="loading_directory_list"
              type="text"
            >
              <v-chip x-small v-if="$store.state.user.current.is_super_admin == true">ID: {{ data.item.directory_id }}</v-chip>

              <v-icon left>
                mdi-folder-network
              </v-icon>

              {{data.item.nickname}}

               (<span>{{data.item.created_time | moment("ddd, MMM D h:mm:ss a")}} </span>)


            </v-skeleton-loader>

          </template>

          <template v-slot:selection="data">
            <v-chip x-small v-if="$store.state.user.current.is_super_admin == true">ID: {{ data.item.directory_id }}</v-chip>

            <v-icon left
                    color="primary">
              mdi-folder-network
            </v-icon>

           <span> {{data.item.nickname}} </span>

          </template>


        </v-select>

      </div>

      <button_with_menu
        tooltip_message="Update Dataset"
        icon="edit"
        :small="true"
        :large="undefined"
        :button_text="undefined"
        color="primary"
        :close_by_button="true"
        v-if="!view_only_mode && show_update == true"
        offset="x"
        :outlined="true"
        background="white"
        menu_direction="left"
        :commit_menu_status="true">

        <template slot="content">

          <v_update_directory :project_string_id="project_string_id"
                              :current_directory_prop="current_directory"
          >
          </v_update_directory>

        </template>

      </button_with_menu>

    </v-layout>

  </div>
</template>

<script lang="ts">

  // TODO combine directory list elements into single component
  // look at props for passing some of stuff...

  // TODO pass loading or?

  import axios from '../../services/customInstance';
  import v_new_directory from './directory_new'
  import v_update_directory from './directory_update'
  import Vue from "vue";

  export default Vue.extend({
    name: 'directory_selector',
    props: {
      'project_string_id': {
        default: null
      },
      'clearable': {
        default: null
      },
      'directory_blacklist': {
        default: undefined
      },
      'initial_dir_from_state': {
        default: true
      },
      'set_current_dir_on_change': {
        default: true,
      },
      'change_on_mount': {
        default: true,
      },
      'view_only_mode': {
        default: false
      },
      'show_text_buttons':{
        default: false
      },
      'update_from_state': {
        default: true
      },
      'show_new': {
        default: false
      },
      'show_update': {
        default: false
      },
      'set_from_id': {
        default: null,
        type: Number
      },
      'label': {
        default: "Dataset",
        type: String
      }
    },
    components: {
      v_new_directory,
      v_update_directory
    },
    data() {
      return {
        new_directory_menu: false,
        update_directory_menu: false,
        current_directory: {},

        nickname: null,

        date: undefined,
        error_directory_list: {},
        internal_directory_list: undefined,
        loading_directory_list: false

      }
    },
    created() {

    },
    mounted() {
      if (this.set_from_id && this.$store.state.project.current.directory_list_filtered) {
        this.current_directory = this.directory_list_filtered.find(
          x => {return x.directory_id == this.set_from_id});
        if(this.change_on_mount){

          this.$emit('change_directory', this.current_directory)
        }
      } else {
        if(this.$props.initial_dir_from_state){
          this.current_directory = this.$store.state.project.current_directory;
        }
        if(this.change_on_mount){

          this.$emit('change_directory', this.current_directory)
        }
        // there can be a timing issue where this won't get set
        // could have a watcher or something but not quite sure.
      }


      this.create_patch_watcher()
      this.create_current_dir_watcher()

    },
    computed: {
      directory_list_filtered() {
        if (!this.internal_directory_list) {
          this.internal_directory_list = this.$store.state.project.current.directory_list
        }
        if(!this.internal_directory_list){
          return []
        }
        let list = this.internal_directory_list.slice() // note slice, not reference

        if (this.directory_blacklist){
          for (let i=0; i < list.length; i++){
              if (this.directory_blacklist.find( x => {
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
      set_from_id(id) {
        this.current_directory = this.get_dataset_object_from_directory_list_using_id(id)
        this.$store.commit('set_current_directory', this.current_directory)
        // for now doesn't emit change
        // eg use case of loading from query string in annotation
        // and just want to get the dir updated but not reload it
      }
    },
    methods: {
      store_date_and_refresh(event) {
        this.date = event
        this.refresh_directory_list()
      },
      on_directory_created: function(directory){
        this.patch(directory)
        //console.log(directory)
        this.current_directory = directory;
        this.change_directory();
      },
      get_dataset_object_from_directory_list_using_id(id: number) {

       if (!this.directory_list_filtered) {
         return null
       }

       return this.directory_list_filtered.find( x => {return x.directory_id == id})
      },

      async refresh_directory_list(){

        this.loading_directory_list = true;
        this.error_directory_list = {}

        try {
          const result = await axios.post(
            `/api/v1/project/${this.$props.project_string_id}`+
            `/directory/list`, {

            'date_from': this.date ? this.date.from : undefined,
            'date_to': this.date ? this.date.to : undefined,
            'nickname': this.nickname ? this.nickname : undefined
            // limit not implemented

          })
          if (result.status === 200) {

            const directory_list = result.data.directory_list;

            // Temp hack until we go back to just straight .id everywhere
            for (let i=0; i < directory_list.length; i++){
              directory_list[i].directory_id = directory_list[i].id
            }
            //console.log(directory_list)

            this.internal_directory_list = directory_list

            this.patch_update_potential_new_directory(directory_list)

          }

        } catch (error) {
          this.error_directory_list = this.$route_api_errors(error)
          console.log(this.error_directory_list)

        } finally {
          this.loading_directory_list = false;

        }

      },

      patch_update_potential_new_directory(new_directory_list){
        /* Test case
         * 1) Create a directory in seperate window
         * 2) Do a refresh
         * 3) Assert one dir added to store
         *
         * Test 2) Assume inverse, eg that refreshing without changes won't push new
         *
         * Assumption
         * We only want to "add" new ones, but if say the user creates a
         * filter list of single x directory, we don't want that to effect the
         * "master" copy. We can't do a straight replacement
         * since the serached list may be different.
         *
         * Must consider that state is beyond length, eg nickname, or other properties in
         * future may change
         */

        if (new_directory_list == this.$store.state.project.current.directory_list) {
          return
        }

        for (let directory of new_directory_list) {

          let directory_in_existing = this.$store.state.project.current.directory_list.find(
              x => {return x.directory_id === directory.id});
          // For some strange reason, it's directory_id instead of just id on Store
          // something to fix at some point...

          if (!directory_in_existing) {
            this.$store.commit('patch_single_directory', directory)
          }
        }

      },

      change_directory() {
        if (this.$props.set_current_dir_on_change) {
          this.$store.commit('set_current_directory', this.current_directory)
        }
        // TODO change type?
        // ie if just rename may handle differently...
        this.$emit('change_directory', this.current_directory)

      },

      create_patch_watcher() {
        // if another components patches a dir, eg template context multiple components
        // seperate from current, as someone may switch, does not imply a patch is needed
        // may wish to think about a better "matching" concept here...

        this.patch_dir_watcher = this.$store.watch(() => {
          return this.$store.state.project.current.last_patched_directory
        },
        (new_val, old_val) => {
            this.patch(new_val)

          }
        )
      },

      patch(new_directory) {

        // it seems like because of timing we need the splice still?
        let directory_in_existing = this.internal_directory_list.find(
            x => {return x.id === new_directory.id});

        if (!directory_in_existing) {
          this.internal_directory_list.splice(0, 0, new_directory)
        }
      },

      create_current_dir_watcher() {
        /* Why:
         *    When it changes after mount ie in case of {first login + first load} to studio
         *    feels nicer to watch it, rather then just set a timeout and hope it makes it
         *
         * Comment on stronger "project change" concept.
         *    in that case, this may not be needed, however it is nice for super admins / support
         *    where we may be jumping between projects.
         *
         * TODOS
         *   Support multiple directories more smoothly -> https://diffgram.teamwork.com/#/tasks/20232123
         *
         *  May see multiple console logs here becuase multiple components on screen
         *
         */

        this.current_dir_watcher = this.$store.watch(() => {

            return this.$store.state.project.current_directory   // we assume this the key 'current_directory' will exist here
          },
          (new_val, old_val) => {
            // No update required case:
            if (!new_val ||
              !this.current_directory ||
              new_val.directories_by_id === this.current_directory.directories_by_id) {
              // console.log("[current_dir_watcher] No update required")
              return
            }
            // Update required case:
            this.current_directory = new_val
            if (this.$props.update_from_state) {
              this.change_directory()
            }

          }
        )

      }

    },
    beforeDestroy() {
      this.current_dir_watcher()
      this.patch_dir_watcher()
    }
  })
</script>


<style scoped>

  .v-list {
    height: 500px;
    overflow-y: auto
  }

</style>
