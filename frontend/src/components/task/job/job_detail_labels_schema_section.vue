<template>
  <v-layout>
    <label_select_only
      v-if="$store.state.job.current.label_dict && $store.state.job.current.label_dict.label_file_list_serialized"
      label_prompt="Locked Schema"
      :mode="'multiple'"
      :view_only_mode="label_select_view_only_mode"
      :label_file_list_prop="$store.state.job.current.label_dict.label_file_list_serialized"
      :load_selected_id_list="$store.state.job.current.label_dict.label_file_list"
      :request_refresh_from_project="request_refresh_labels"
      @label_file="$emit('update_label_file_list', $event)"
    >
    </label_select_only>

    <!-- Edit unlock -->
    <div class="pa-2">
      <tooltip_button
        v-if="label_select_view_only_mode == true"
        tooltip_message="Edit Locked Schema"
        @click="
                  (request_refresh_labels = Date.now()),
                    (label_select_view_only_mode = false)
                "
        icon="edit"
        :icon_style="true"
        color="primary"
      >
      </tooltip_button>
    </div>

    <!-- Save Edit -->

    <!-- In context of label updates
      but a bit more to think about here...
        wording could be a bit sensitive-->
    <button_with_confirm
      v-if="label_select_view_only_mode == false"
      @confirm_click="$emit('update_job')"
      color="primary"
      icon="save"
      :icon_style="true"
      :large="true"
      tooltip_message="Save & Update Tasks"
      confirm_message="Save & Update All Tasks"
      :loading="loading"
      :disabled="loading"
    >
    </button_with_confirm>
    <v-alert
      v-if="label_select_view_only_mode == false"
      type="info"
      icon="mdi-lock"
    >
      Schema is locked by default for each group of Tasks. To apply the
      new desired Schema to this set of tasks, select it here and then
      click save. Note Attributes follow labels, so if an attribute for a
      label has changed, simply click save directly.
      <a
        style="color: white"
        href="https://diffgram.readme.io/docs/updating-existing-tasks"
      >
        Docs
      </a>
    </v-alert>

    <v_error_multiple :error="error"> </v_error_multiple>

    <v_info_multiple :info="info"> </v_info_multiple>
  </v-layout>


</template>

<script>
export default {
  name: "job_detail_labels_schema_section",
  props: {
    'label_select_view_only_mode':{
      default: false
    },
    'request_refresh_labels':{
      default: null
    },
    'loading':{
      default: false
    },
    'error':{
      default: null
    },
    'info':{
      default: null
    }
  },
  data: function(){
    return{

    }
  },
  methods: {

  }
}
</script>

<style scoped>

</style>
