<template>
  <div v-if="!do_not_show_menu" style="padding: 0">

    <v-snackbar
      v-model="$store.state.error.permission"
      top
      color="error"
    >
      Invalid permission.
      <v-btn color="white" text @click="$store.commit('clear_permission_error')">
        Close
      </v-btn>
    </v-snackbar>

    <v-snackbar
      v-model="$store.state.alert.success_refresh"
      top
      color="info"
      :timeout="5000"
    >
      <v_info_multiple :info="$store.state.alert.success"></v_info_multiple>
    </v-snackbar>

    <!--
      Design doc for tool bar layout https://docs.google.com/document/d/1EVvPke7Ms25KsmDKpwrQcqB1k6pgB5SNs5WDbwGmLCo/edit#heading=h.wihzuap21ahi

      -->


    <v-app-bar app
               style="padding: 0; background: white;"
               elevation="0"
               :height="height">

      <v-layout column>

        <v-layout>

          <v-toolbar height="50px"
                     padding="0"
                     class="pl-4 pr-4"
                     v-if="show_default_navigation == true"
          >
            <ahref_seo_optimal :href="route_home">
              <v-toolbar-title data-cy="navbar-logo" class="ml-0 pt-2 pr-3 clickable"
                               @click.ctrl="route_home_new_tab">

                <img src="https://storage.googleapis.com/diffgram-002/public/logo/diffgram_logo_word_only.png"
                     height="30px"/>

              </v-toolbar-title>
            </ahref_seo_optimal>


            <div class="hidden-sm-and-down"
                 v-if="$store.state.user.logged_in != true ">

              <menu_marketing>

              </menu_marketing>

            </div>
            <div v-if="$store.state.user.logged_in == true ">


              <v-layout>

                <v-btn text
                       data-cy="go-to-home-page"
                       @click="$router.push('/me')">
                  <v-icon left>mdi-home</v-icon>
                  Home
                </v-btn>

                <main_menu_project v-if=" $store.state.builder_or_trainer.mode == 'builder'">
                </main_menu_project>

                <menu_tasks v-if="$store.state.builder_or_trainer.mode === 'builder'"></menu_tasks>
                <menu_tasks v-else-if="$store.state.builder_or_trainer.mode === 'trainer'"></menu_tasks>

              </v-layout>

            </div>

            <v-spacer></v-spacer>

            <div v-if="$store.state.builder_or_trainer.mode == 'trainer'">
              <h3 class="pr-3">
                <v-icon left
                        color="primary">mdi-professional-hexagon
                </v-icon>
                Pro
              </h3>
            </div>

            <div v-if="$store.state.user.logged_in == true">
              <div v-if="$store.state.builder_or_trainer.mode == 'builder'">
                <v-layout>
                  <div v-if="display_projectName" id="project_name">

                    <v-menu offset-y>
                      <template
                        v-slot:activator="{ on, attrs }"
                        v-bind="attrs"
                        v-on="on"
                      >
                        <v-btn v-bind="attrs" v-on="on"
                               style="text-transform: none !important;"
                               text>
                          <h2 v-on="on" class="pa-3">
                            {{ display_projectName }}
                          </h2>
                        </v-btn>
                      </template>
                      <v-list
                        id="project_list"
                        v-if="$store.state.project_list &&
                              $store.state.project_list.user_projects_list &&
                              $store.state.project_list.user_projects_list.length > 1">
                        <v-list-item
                          class="project-option"
                          style="cursor: pointer"
                          v-for="project in user_project_list"
                          :key="project.id"
                        >
                          <v-list-item-title @click="change_project(project)">{{
                            project.name
                            }}
                          </v-list-item-title>
                        </v-list-item>
                      </v-list>
                    </v-menu>
                  </div>
                </v-layout>
              </div>
            </div>


            <tooltip_button
              tooltip_message="View Pending File Operations"
              class="hidden-sm-and-down"
              @click="open_pending_files_dialog"
              color="primary"
              icon="mdi-file-clock"
              v-if="$store.state.builder_or_trainer.mode == 'builder'
                    && $store.state.user.logged_in == true
                    && $store.state.project
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
              <div v-if="$store.state.project && $store.state.project.current">

                <!-- set_user_is_typing_or_menu_open  is lock for hotkeys!! -->

                <v-dialog :disabled="!$store.state.project || !$store.state.project.current.project_string_id"
                          @update:return-value="$store.commit('set_user_is_typing_or_menu_open', false)"
                          width="800">

                  <template v-slot:activator="{ on }">
                    <v-btn v-on="on"
                           :disabled="!$store.state.project || !$store.state.project.current.project_string_id"
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
              v-if="$store.state.user && $store.state.user.current.is_super_admin == true"
              icon="mdi-account-supervisor"
              :close_by_button="true"
              color="primary"
            >

              <template slot="content">
                <v-layout column>

                  <v-btn @click="$router.push('/admin/')">
                    Projects
                  </v-btn>

                  <v-btn @click="$router.push('/admin/install/info')">
                    Install Info
                  </v-btn>

                  <v-btn @click="$router.push('/admin/mock')">
                    Mock Data
                  </v-btn>

                  <v-btn @click="builder_or_trainer_toggle()">
                    Builder / Trainer Toggle
                  </v-btn>

                  <v-btn @click="toggle_super_admin_mode()">
                    Super Admin Toggle
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


            <ahref_seo_optimal href="/contact"
                               v-if="$store.state.org && !$store.state.org.current.id &&
                       $store.state.builder_or_trainer.mode == 'builder'"
            >
              <v-btn color="primary"
                     text
                     style="text-transform: none !important;"
              >
                Book A Demo
              </v-btn>
            </ahref_seo_optimal>

            <ahref_seo_optimal href="/user/data_platform/new">
              <v-btn color="primary"
                     outlined
                     class="hidden-sm-and-down"
                     style="text-transform: none !important;"
                     v-if="$store.state.user.logged_in != true"
              >
                Try Now
              </v-btn>
            </ahref_seo_optimal>
            <v-btn
              v-if="$store.state.user.logged_in == true
                   && $store.state.org && !$store.state.org.current.id"
              @click="go_to_order_page"
              outlined
              color="success">
              <v-icon left>mdi-star-shooting</v-icon>
              Upgrade
            </v-btn>

            <v_profile_in_menu class="hidden-xs-only">
            </v_profile_in_menu>

          </v-toolbar>
        </v-layout>

        <v-layout>
          <slot name="second_row"></slot>
        </v-layout>

        <v-layout>
          <slot name="third_row"></slot>
        </v-layout>

        <v-layout>
          <slot name="forth_row"></slot>
        </v-layout>

      </v-layout>

    </v-app-bar>
  </div>
</template>

<script lang="ts">
  import menu_tasks from "./menu_tasks";
  import main_menu_project from "./menu_project";
  import pending_files_dialog from "../input/pending_files_dialog";
  import {getProjectList} from "../../services/projectServices";
  import menu_marketing from './menu_marketing'

  import Vue from "vue";

  export default Vue.extend({
    name: 'main_menu',
    components: {
      main_menu_project,
      menu_tasks,
      pending_files_dialog,
      menu_marketing
    },
    props: {
      'height': {
        default: 50
      },
      'show_default_navigation': {
        default: true
      },
    },
    data() {
      return {
        title: "Diffgram",
        project_menu: false,
        project_manager_dialog: false,
        pending_files_dialog_is_open: false,
        do_not_show_menu: false,
        routes_without_menu: [
          '/user/login/',
          '/user/new/',
          '/user/builder/signup'
        ]
      };
    },
    computed: {
      user_project_list: function () {
        let user_project_list = this.$store.state.project_list.user_projects_list;
        if (this.$store.state.project && this.$store.state.project.current) {
          user_project_list = user_project_list.filter(
            project => project.project_string_id != this.$store.state.project.current.project_string_id
          )
        }
        const new_project = {
          new_project: true,
          name: "New Project"
        }
        user_project_list.push(new_project)
        return user_project_list
      },
      display_projectName: function () {
        if (!this.$store.state.project || !this.$store.state.project.current) {
          return undefined
        }
        const project_name = this.$store.state.project.current.name;
        if (project_name && project_name.length >= 16)
          return `${project_name.slice(0, 15)}...`;
        return project_name;
      },
      route_home: function () {
        if (this.$store.state.user.logged_in == true) {
          return "/home/dashboard";
        } else {
          return "/";
        }
      },
    },
    watch: {
      '$store.state.user.logged_in': function (value) {
        if (value) this.get_avalible_projects()
      },  
      '$route.path': function(value) {
        const do_not_display = value !== "/" && this.routes_without_menu.some(route => {
          return route.includes(value)
        })
        if (do_not_display) {
          this.do_not_show_menu = true
        } else {
          this.do_not_show_menu = false
        }
      }
    },
    mounted() {
      if (
        !this.$store.state.project_list ||
        this.$store.state.project_list.user_projects_list ||
        (this.$store.state.project_list.user_projects_list &&
          this.$store.state.project_list.user_projects_list.length === 0)
      ) {
        this.get_avalible_projects()
      }
    },
    methods: {
      go_to_order_page: function(){
        if(window.location.host === 'diffgram.com'){
          window.open(`https://diffgram.com/order/premium`, '_blank')

        }
        else{
          window.open(`https://diffgram.com/order/premium?install_fingerprint=${this.$store.state.user.current.install_fingerprint}&email=${this.$store.state.user.current.email}`, '_blank')

        }
      },
      change_project(item) {
        if (item.new_project == true) {
          this.$router.push({path: "/a/project/new"});
          this.$emit("exit", true);
          return
        }
        if (item.is_public) {
          this.$store.commit("set_current_public_project", item);
        } else {
          this.$store.commit("set_current_public_project", {});
        }
        this.$store.commit("set_project", item);
        this.$router.push({path: "/home/dashboard"});
        this.$emit("exit", true);
        if (window.location.pathname === '/home/dashboard') this.$router.go()
      },
      open_pending_files_dialog: function () {
        this.$refs.pending_files_dialog.open();
      },
      builder_or_trainer_toggle: function () {
        this.$store.commit("builder_or_trainer_toggle");
      },
      toggle_super_admin_mode: function () {
        this.$store.commit("super_admin_toggle");
      },
      route_home_new_tab: function () {
        if (this.$store.state.user.logged_in == true) {
          window.open("/home/dashboard");
        } else {
          window.open("/");
        }
      },
      get_avalible_projects: async function () {
        const response = await getProjectList();
        const project_list = response.data.project_list;
        this.$store.commit("set_userProjects_list", project_list);
      }
    },
  });
</script>


<style>
  .v-toolbar__content {
    padding: 0;
  }
</style>
