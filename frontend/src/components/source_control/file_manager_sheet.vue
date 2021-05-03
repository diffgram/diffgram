<template>

  <div>
    <v-bottom-sheet scrollable
                    :retain-focus="false"
                    hide-overlay
                    class="media-core-container"
                    no-click-animation
                    v-if="!error_permissions.data"
                    :persistent="persistent_bottom_sheet"
                    v-model="media_sheet">
      <v-sheet class="text-right" style="position: relative">
        <v-btn
          style="position: absolute; top:0; right: 65px"
          data-cy="fullscreen-file-explorer-button"
          color="primary lighten-3"
          small
          @click="full_screen_sheet"
          fab
          right
          fixed
          v-on="on"
        >
          <v-icon> mdi-arrow-up </v-icon>
        </v-btn>
        <v-tooltip bottom>
          Minimize
          <template v-slot:activator="{ on }">
            <v-btn
              data-cy="minimize-file-explorer-button"
              color="primary"
              small
              @click="media_sheet = !media_sheet"
              fab
              right
              fixed
              v-on="on"
            >
              <v-icon> mdi-window-minimize </v-icon>
            </v-btn>
          </template>
        </v-tooltip>
        <v_media_core :project_string_id="project_string_id"
                      file_view_mode="annotation"
                      :task="task"
                      :view_only_mode="view_only"
                      :file_id_prop="file_id_prop"
                      :job_id="job_id"
                      :visible="media_sheet"
                      @height="media_core_height = $event"
                      @permissions_error="set_permissions_error"
                      ref="media_core"
        >
        </v_media_core>
      </v-sheet>
    </v-bottom-sheet>


    <!-- Open Bottom Sheet -->
    <v-tooltip v-if="media_sheet == false && !task"
               bottom>
      Open File Explorer
      <template v-slot:activator="{ on }">
        <v-btn
          style="position: absolute; bottom: 25px; right: 25px"
          color="primary"
          @click="media_sheet = !media_sheet"
          fab
          right
          absolute
          v-on="on"
        >
          <v-icon> mdi-folder-open </v-icon>
        </v-btn>
      </template>
    </v-tooltip>
  </div>
</template>

<script>
  import Vue from "vue";

  export default Vue.extend( {
    name: "file_manager_sheet",
    props: [
      'project_string_id',
      'persistent_bottom_sheet',
      'task',
      'view_only',
      'file_id_prop',
      'job_id',

    ],
    data: function(){
      return{
        media_sheet: true,
        persistent_bottom_sheet: true,
        media_core_height: 0,
        error_permissions: {},
      }
    },
    methods:{
      get_media: function(){
        return this.$refs.media_core.get_media();
      },
      set_file_list: function(){
        return this.$refs.media_core.set_file_list();
      },
      full_screen_sheet: function(){
        this.media_core_height = '800px';
      },
      set_permissions_error: function(new_error){
        this.error_permissions = new_error;
      },
    }

  })
</script>

<style scoped>

</style>
