<template>
  <div v-cloak>
    <main_menu height="100">
      <template slot="third_row">
        <v-toolbar
          dense
          elevation="1"
          fixed
          height="50px"
        >
          <v-toolbar-items>
            <v-btn
              color="blue darken-1"
              dark
              @click="route_new_project"
            >
              <v-icon left>
                add
              </v-icon>
              New Project
            </v-btn>
          </v-toolbar-items>

          <tooltip_button
              tooltip_message="Create Sample Project"
              @click="open_confirm_dialog_sample_data"
              icon="mdi-apps-box"
              :icon_style="true"
              :bottom="true"
              color="primary">
          </tooltip_button>

        </v-toolbar>
      </template>
    </main_menu>
    <v-card>
      <v-card-title v-if="mode == 'user'">
        <h3 class="headline">
          Project Manager
        </h3>
      </v-card-title>

      <v-card-title v-if="mode == 'org'">
        <h3 class="headline">
          Projects in {{ $store.state.org.current.name }}
        </h3>
      </v-card-title>

      <div
        v-if="loading"
        class="skeleton"
      >
        <v-skeleton-loader
          :loading="loading"
          type="card@3"
        />
      </div>

      <template>
        <v-container v-if="!loading" class="pa-20">
          <v-row>
            <v-col

              v-for="(item, index) in project_list"
              :key="index"
            >
              <v-badge
                :value="item.project_string_id == $store.state.project.current.project_string_id"
              >
                <v-icon
                  slot="badge"
                  dark
                >
                  check
                </v-icon>
                <v-card
                  class="mx-auto"
                  width="400"
                  :accesskey="item.name"

                >
                  <div class="member-list">
                    <div
                      v-for="(member, i) in item.member_list.slice(0, 3)"
                      :key="i"
                      class="avatar"
                    >
                      <user_icon :user="member" />
                    </div>
                    <div
                      v-if="item.member_list.slice(3).length"
                      class="avatar count"
                    >
                      <user_icon :message="'+' + item.member_list.slice(3).length" />
                    </div>
                  </div>

                  <v-img
                    class="project-image white--text align-end"
                    height="200px"
                    :src="get_preview_url(item)"
                    :data-cy="`project-im-${item.project_string_id}`"
                    @click="change_project(item)"
                  />
                  <v-card-title
                    class="pb-0 project-title"
                    :data-cy="`project-title-${item.project_string_id}`"
                    @click="change_project(item)"
                  >
                    <div
                      v-if="item.project_string_id == $store.state.project.current.project_string_id"
                      style="display: flex; justify-content: flex-start; align-items: center;"
                    >
                      {{ item.name }}
                    </div>
                    <div v-else>
                      {{ item.name }}
                    </div>
                    <div v-if="mode == 'super_admin'">
                      {{ item.id }}
                    </div>
                  </v-card-title>

                  <v-card-text class="text--primary">
                    <div v-if="item.time_created">
                      <span>{{ item.time_created | moment("dddd, MMMM Do") }}</span>
                    </div>
                  </v-card-text>
                </v-card>
              </v-badge>
            </v-col>
          </v-row>
        </v-container>
      </template>
    </v-card>
    <v-dialog v-model="dialog_confirm_sample_data" max-width="450px">
      <v-card >
        <v-card-title class="headline">
          Create Sample Project
        </v-card-title>
        <v-card-text>
          Do you want to create a sample project?
          This will add 1 new project with sample data.
        </v-card-text>
        <v_error_multiple :error="error_sample_data">
        </v_error_multiple>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn
            color="primary darken-1"
            text
            @click="dialog_confirm_sample_data = false"
          >
            Cancel
          </v-btn>
          <v-btn
            color="success darken-1"
            text
            :loading="loading_create_sample_data"
            @click="create_sample_project"
          >
            Create Sample Data
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
    <v-snackbar
      v-model="snackbar_success"
      :timeout="3000"
      color="primary"
    >
      Sample project created successfully.
      <template v-slot:action="{ attrs }">
        <v-btn
          color="white"
          text
          v-bind="attrs"
          @click="snackbar_success = false"
        >
          Close
        </v-btn>
      </template>
    </v-snackbar>
  </div>
</template>
<script lang="ts">

import axios from 'axios';
import user_icon from '../user/user_icon.vue';

import Vue from "vue";
import {create_event} from "../event/create_event";

export default Vue.extend( {
  name: 'ProjectManager',
  components: {
    user_icon,
  },
  props: {
      'project_manager_dialog' : {
        type: Boolean,
        default: null
      },
      'org_id' : {
        type: Number,
        default: null
      },
      'mode' : {
        type: String,
        default: "user"   // user, org, or?
      }
  },
  data() {
    return {
      dialog_confirm_sample_data: false,
      loading_create_sample_data: false,
      snackbar_success: false,
      error_sample_data: {},
      project_list: [],

      limit: 25,

      loading: true

    }
  },
  computed: {
  },
  watch: {
    project_manager_dialog(bool) {
      if (bool == true) {
        this.refresh()
      }
    }
  },
  created() {

    this.refresh()

  },
  mounted(){
    this.add_visit_history_event();
  },
  methods: {
    add_visit_history_event: async function(){
      await create_event(this.$store.state.project.current.project_string_id, {
        page_name: 'project_manager',
        object_type: 'page',
        user_visit: 'user_visit',
      })
    },

    get_preview_url(project) {
      // example of getting a single one.

      if (project == undefined) {return false}

      if (project.preview_file_list && project.preview_file_list[0]) {
        let preview_file = project.preview_file_list[0]

        return this.get_preview_url_from_file(preview_file)
      } else {
        return 'https://storage.googleapis.com/diffgram_public/app/Empty_state_card.svg';
      }
    },

    get_preview_url_from_file(file) {
      // Relevant for single or multiple

      if (file.image) {
        // thumb is actually kind of low res so this may be better, not huge files normally
        return file.image.url_signed
      }
      else if (file.video) {
        return file.video.preview_image_url_thumb
      }
    },


    change_project(item) {
      if(item.is_public){
        this.$store.commit('set_current_public_project', item);
      }
      else{
        this.$store.commit('set_current_public_project', {});
      }
      this.$store.commit('set_project', item)

      this.$router.push({ path: '/home/dashboard'})

      this.$emit('exit', true)
    },

    refresh: function () {

      this.loading = true

      if (this.mode == "user"){
        this.refresh_from_user()
      }
      else if (this.mode == "org"){
        this.refresh_from_org()
      }
      else if (this.mode == "super_admin"){
        this.refresh_super_admin()
      }


    },

    refresh_from_user: function () {

      axios.post('/api/v1/project/list', {

      }
      ).then(response => {

        this.loading = false
        this.$store.commit('set_user_projects', response.data.project_list)
        this.project_list = response.data.project_list

      })
      .catch(error => {
        console.log(error);
      });

    },

    refresh_from_org: function () {

      axios.post('/api/v1/org/'
        + this.org_id +
        '/project/list', {
      }
      ).then(response => {

        this.loading = false

        this.project_list = response.data.project_list

      })
      .catch(error => {
        console.log(error);
      });

    },

    refresh_super_admin: function () {

      axios.post('/api/v1/admin/project/list', {
        limit: this.limit
      }
      ).then(response => {

        this.loading = false
        // note we don't set users projects here as assumed to be super admin?
        // or should we cache it somwhere

        this.project_list = response.data.project_list

      })
      .catch(error => {
        console.log(error);
      });

    },
    create_sample_project: async function(){
      this.loading_create_sample_data = true;
      try{
        const response = await axios.post('/api/walrus/v1/gen-data', {
          data_type: 'project',
        })
        if(response.status === 200){
          this.refresh();
          this.dialog_confirm_sample_data = false;
          this.snackbar_success = true;
        }
      }
      catch (error) {
        this.error_sample_data = this.$route_api_errors(error);
      }
      finally {
        this.loading_create_sample_data = false;
      }
    },
    open_confirm_dialog_sample_data: function(){
      this.dialog_confirm_sample_data = true;
    },
    route_new_project() {
      this.$router.push("/a/project/new")
      this.$emit('exit', true)
    }
  }
}

)
</script>

<style>
.member-list {
  display: flex;
  position: absolute;
  justify-content: flex-end;
  align-items: flex-end;
  top: 145px;
  right: 10px;
  z-index: 10;
}

.member-list .avatar {
  margin: 0 -.5rem;
  border: 3px solid white;
  border-radius: 50rem;
  padding: 0;
}

.member-list .avatar:nth-child(4) {
  z-index: -4;
}
.member-list .avatar:nth-child(3) {
  z-index: -3;
}
.member-list .avatar:nth-child(2) {
  z-index: -2;
}
.member-list .avatar:nth-child(1) {
  z-index: -1;
}

.member-list .avatar:last-child {
  margin: 0;
}

.project-image, .project-title {
  cursor: pointer;
}

.skeleton {
  margin-top: 100px;
}

.skeleton > .v-skeleton-loader {
  display: flex;
  flex-direction: row;
  justify-content: space-around;
  align-items: flex-start;
  margin: 0 auto;
  flex-wrap: wrap;
}
.skeleton > .v-skeleton-loader > .v-skeleton-loader__card {
  width: 400px;
}

</style>
