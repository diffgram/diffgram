<template>
  <div style="padding: 0">
    <!-- v toolbar has drawer access button which interfaces
     with v navigation drawer. they are technically seperate components
     but are logically connected given this button so keeping together here
    -->
    <!--
  <v_annotation_trainer_job_info>

  </v_annotation_trainer_job_info>
  -->
    <v-snackbar v-model="$store.state.error.permission"
                top
                :timeout="5000"
                color="error">
      Invalid permission.
      <v-btn color="white"
             text
             @click="snackbar_warning = false">
        Close
      </v-btn>
    </v-snackbar>


    <!-- TODO use different snack bar color messages
        for different succces / error types -->

    <!-- TODO add a click to close like above
         Then put time out to 0?
          Or control timeout through succcess messaging
          with some kind of default
        -->
    <!-- TODO review success / info difference here-->
    <v-snackbar v-model="$store.state.alert.success_refresh"
                top
                color="info"
                :timeout="5000">

      <v_info_multiple :info="$store.state.alert.success">
      </v_info_multiple>

    </v-snackbar>


    <!-- TODO way to hide menu ie
       :value="$store.state.something

      Some other options to look at

      https://vuetifyjs.com/en/components/app-bars#app-bars

      hide-on-scroll
      or collapse-on-scroll

      could both help to hide this for extra screen real estate


      -->

    <!--
      Design doc for tool bar layout https://docs.google.com/document/d/1EVvPke7Ms25KsmDKpwrQcqB1k6pgB5SNs5WDbwGmLCo/edit#heading=h.wihzuap21ahi


      EXAMPLE

      Step 1)
        Hide default menu

        Go to router
          add  hide_default_menu: true

       ie
        {
            path: '/job/list',
            ...
            meta: {
              hide_default_menu: true
              }
          },


      Step 2)
        Add the menu to component

      <main_menu height="100">
        <template slot="second_row">

          <v-toolbar
            dense
            elevation="1"
            fixed
            height="50px">
            <v-toolbar-items>


            CONTENT CONTENT CONTENT


            </v-toolbar-items>
          </v-toolbar>
        </template>
      </main_menu>


      NOTE that selectors in the menu need a class like
      class="pl-3 pr-3 pt-4"



      -->


    <v-app-bar app
               style="padding: 0; background: white;"
               elevation="0"
               :height="height">

    <v-layout column>

      <v-layout >

      <!-- TODO would like to add  style="overflow: hidden"
           to toolbar but on marketing menu it causes
          it to go under the front card    so will have to review
        -->

      <v-toolbar height="50px"
                 padding="0"
                 class="pl-4 pr-4"
                 v-if="show_default_navigation == true"
                 >
      <ahref_seo_optimal :href="route_home">
        <v-toolbar-title class="ml-0 pt-2 pr-3 clickable"
                         @click.ctrl="route_home_new_tab">

          <img src="https://storage.googleapis.com/diffgram-002/public/logo/diffgram_logo_word_only.png"
                height="30px" />

        </v-toolbar-title>
      </ahref_seo_optimal>


      <div v-if="$store.state.user.logged_in == true ">


        <v-layout>


          <main_menu_project v-if=" $store.state.builder_or_trainer.mode == 'builder'">
          </main_menu_project>


          <v-btn v-if="$store.state.builder_or_trainer.mode == 'builder'"
                  :disabled="!$store.state.project.current.project_string_id"
                  text
                  @click="$router.push('/job/list')">
            <v-icon left>mdi-brush</v-icon>
            Tasks
          </v-btn>

          <v-btn v-if="$store.state.builder_or_trainer.mode == 'trainer'"
                  :disabled="$store.state.user.pro_account_approved != true"
                  text
                  @click="$router.push('/job/list')">
            <v-icon left>mdi-brush</v-icon>
            Tasks
          </v-btn>

          <!-- <v-icon right color="primary"> mdi-new-box </v-icon> -->

          <!-- Only show menu if a builder mode is enabled
      (new users have no mode enabled-->



          <!-- END action menu -->


        </v-layout>

      </div>

      <v-spacer></v-spacer>

      <div v-if="$store.state.builder_or_trainer.mode == 'trainer'">
        <h3 class="pr-3">
          <v-icon left
            color="primary">mdi-professional-hexagon</v-icon> Pro </h3>
      </div>

      <div v-if="$store.state.user.logged_in == true">

        <div v-if=" $store.state.builder_or_trainer.mode == 'builder'">

          <v-layout>
            <div v-if="$store.state.project.current">

              <!-- TODO make this a composable
              component so if we want truncated stuff
              for other areas (ie for Org) -->

            <v-tooltip bottom>

             Current Project: {{ $store.state.project.current.name }}

              <template v-slot:activator="{ on }">

                <h2 v-on="on" class="pa-3">

                  <!-- We seem to need this if we want
                  ... to be on one line with it.
                    I guess this depends on size of screen more then
                    length / is relative...

                    Truncating in the middle looks silly there...
                      {{ $store.state.project.current.name.slice(-6) }}
                    -->
                  <div v-if="$store.state.project.current.name
                       && $store.state.project.current.name.length >= 16">
                    {{ $store.state.project.current.name.slice(0, 15) }}
                    ...
                  </div>
                  <div v-else>
                    {{ $store.state.project.current.name }}
                  </div>
                </h2>

              </template>

            </v-tooltip>

            </div>

          </v-layout>

        </div>

      </div>


        <div v-if="$store.state.builder_or_trainer.mode == 'builder'"
             class="pa-2">
          <tooltip_icon
              color="primary"
              icon="mdi-database"
              tooltip_message="Data Platform"
              tooltip_direction="bottom"
              >
          </tooltip_icon>
        </div>


        <tooltip_button
          tooltip_message="View Pending File Operations"
          class="hidden-sm-and-down"
          @click="open_pending_files_dialog"
          color="primary"
          icon="mdi-file-clock"
          v-if="$store.state.builder_or_trainer.mode == 'builder'
                && $store.state.user.logged_in == true
                && $store.state.project.current.project_string_id"
          :icon_style="true"
          :bottom="true"
        >
        </tooltip_button>


      <pending_files_dialog
         ref="pending_files_dialog"
        :project_string_id="this.$store.state.project.current.project_string_id"
        :is_open="pending_files_dialog_is_open"
      ></pending_files_dialog>




      <div v-if="$store.state.user.logged_in == true
              && $store.state.builder_or_trainer.mode == 'builder'">
        <div v-if="$store.state.project.current">

          <!-- set_user_is_typing_or_menu_open  is lock for hotkeys!! -->

          <v-dialog :disabled="!$store.state.project.current.project_string_id"
                    @update:return-value="$store.commit('set_user_is_typing_or_menu_open', false)"
                    width="800">

            <template v-slot:activator="{ on }">
              <v-btn v-on="on"
                      :disabled="!$store.state.project.current.project_string_id"
                      @click="$store.commit('set_user_is_typing_or_menu_open', true)"
                      text
                      >
                Share
                <v-icon right>mdi-account-multiple-plus</v-icon>
              </v-btn>
            </template>

            <v_collaborate_new
                :project_string_id="this.$store.state.project.current.project_string_id">
            </v_collaborate_new>

          </v-dialog>
        </div>
      </div>

      <button_with_menu
            tooltip_message="Super Admin Menu"
            v-if="$store.state.user.current.is_super_admin == true"
            icon="mdi-account-supervisor"
            :close_by_button="true"
            color="primary"
                >

      <template slot="content">
        <v-layout column>

          <v-btn @click="builder_or_trainer_toggle()">
            Builder / Trainer Toggle
          </v-btn>

          <v-btn @click="toggle_super_admin_mode()">
            Super Admin Toggle
          </v-btn>

          <v-btn @click="$router.push('/admin/')">
            Projects
          </v-btn>

          <v-btn @click="$router.push('/admin/student')">
            Student Plan
          </v-btn>

        </v-layout>
      </template>

      </button_with_menu>


      <!-- Don't show for trainers, but do show even if not logged in.-->
      <!-- Docs -->
      <tooltip_button
          class="hidden-sm-and-down"
          href="https://diffgram.readme.io/docs"
          target="_blank"
          color="primary"
          icon="mdi-book-multiple"
          tooltip_message="Docs"
          :icon_style="true"
          :bottom="true"
          v-if="$store.state.builder_or_trainer.mode != 'trainer'"
          >
      </tooltip_button>



      <ahref_seo_optimal href="/user/new">
        <v-btn color="primary"
               outlined
               class="hidden-sm-and-down"
               v-if="$store.state.user.logged_in != true
               && !$store.state.builder_or_trainer.mode"
               >
          Sign Up
        </v-btn>
      </ahref_seo_optimal>


      <v_profile_in_menu class="hidden-xs-only">
      </v_profile_in_menu>

      </v-toolbar>
    </v-layout>

      <v-layout>
        <slot name="second_row"> </slot>
      </v-layout>

      <v-layout>
        <slot name="third_row"> </slot>
      </v-layout>

      <v-layout>
        <slot name="forth_row"> </slot>
      </v-layout>

    </v-layout>

    </v-app-bar>




  </div>

</template>

<script lang="ts">

import main_menu_project from './menu_project'
import pending_files_dialog from '../input/pending_files_dialog'


import Vue from "vue";

  export default Vue.extend( {
  name: 'main_menu',
  components: {
    main_menu_project,
    pending_files_dialog
  },
  props: {
    'height': {
      default: 50
     },
    'show_default_navigation': {
      default: true
    }
  },
  data() {
    return {

      title: "Diffgram",

      project_menu: false,

      project_manager_dialog: false,

      pending_files_dialog_is_open: false,

      brain_menu: false,

    }
  },

  computed: {

    items_super_admin: function () {


      var array =
        [
          {
            text: 'Annotation assignment', icon: 'edit',
            action: '/annotation_assignment/studio/annotate'
          },
          {
            text: 'New user', icon: 'add',
            action: '/user/new'
          },
          {
            text: 'Annotation assignment review', icon: 'verified_user',
            action: '/annotation_assignment/studio/review'
          }
        ]
      return this.items_logged_in.concat(array)
    },

    route_home: function () {
      if (this.$store.state.user.logged_in == true) {
        return('/home/dashboard')
      } else {
        return('/')
      }
    },
  },
  mounted() {


  },
  methods: {
    open_pending_files_dialog: function(){
      this.$refs.pending_files_dialog.open();
    },
    builder_or_trainer_toggle: function () {
      this.$store.commit('builder_or_trainer_toggle')
    },
    toggle_super_admin_mode: function () {
      this.$store.commit('super_admin_toggle')
    },
    route_home_new_tab: function () {
      if (this.$store.state.user.logged_in == true) {
        window.open('/home/dashboard')
      }
      else {
        window.open('/')
      }
    }

  }
}
) </script>
<style>
  .v-toolbar__content{
    padding: 0;
  }
</style>
