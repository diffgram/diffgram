<template>
  <div class="d-flex justify-space-between align-center mb-6">
    <h1 class="pa-2">
      <v-layout>
        <div
          class="font-weight-light clickable"
          @click="$router.push('/job/list')"
        >
          {{ $store.state.project.current.name }} /
          <span class="secondary--text">
              <strong>
              <v-icon color="secondary">mdi-test-tube</v-icon>
              <span v-if="$store.state.job.parent_id">Exams</span>
              <span v-else>{{object_name}}</span>
              </strong>
            </span>
          /
        </div>

        <div
          v-if="edit_name != true && allow_edit"
          class="font-weight-normal pl-2 d-flex align-center"
          @dblclick="edit_name = true"
        >
          {{ exam.name }}
          <tooltip_button
            v-if="edit_name == false && allow_edit"
            tooltip_message="Edit Name"
            tooltip_direction="bottom"
            @click="edit_name = true"
            icon="edit"
            :icon_style="true"
            color="primary"
          >
          </tooltip_button>
        </div>
        <div
          v-if="edit_name != true && !allow_edit"
          class="font-weight-light pl-2 d-flex align-center"
          @dblclick="edit_name = true"
        >
          {{ exam.name }}
        </div>

        <v-text-field
          v-if="edit_name == true"
          v-model="exam.name"
          @input="has_changes = true"
          @keyup.enter="(edit_name = false), $emit('name_updated')"
          solo
          flat
          style="font-size: 22pt; border: 1px solid grey; height: 55px"
          color="blue"
        >
        </v-text-field>

        <div>
          <button_with_confirm
            v-if="edit_name == true"
            @confirm_click="$emit('name_updated'); edit_name = false"
            color="primary"
            icon="save"
            :icon_style="true"
            tooltip_message="Save Name Updates"
            confirm_message="Confirm"
            :loading="loading"
            :disabled="loading"
          >
          </button_with_confirm>
        </div>

        <tooltip_button
          v-if="edit_name == true"
          tooltip_message="Cancel Name Edit"
          datacy="cancel_edit_name"
          @click="edit_name = false"
          icon="mdi-cancel"
          :icon_style="true"
          color="primary"
          :disabled="loading"
        >
        </tooltip_button>
      </v-layout>
    </h1>
    <v-btn
      v-if="show_apply_button"
      @click="$emit('apply_clicked')"
      color="success"
      :loading="loading"
      large
    >
      <v-icon>mdi-shield-star</v-icon>
      Apply For Exam
    </v-btn>
  </div>
</template>

<script>
export default {
  name: "exam_detail_header",
  props: {
    'loading': {
      default: false
    },
    'exam':{
      default: null
    },
    'show_apply_button':{
      default: true
    },
    'object_name':{
      default: 'Exams Templates'
    },
    'allow_edit':{
      default: false
    }
  },
  data: function(){
    return {
      edit_name: false,
      has_changes: false,
    }
  }

}
</script>

<style scoped>

</style>
