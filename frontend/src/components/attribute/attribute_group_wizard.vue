<template>
  <v-card elevation="0">
    <v-card-text>
      <v-stepper v-model="step" :non-linear="true" style="height: 100%;" @change="on_change_step">
        <v-stepper-header class="ma-0 pl-8 pr-8">
          <v-stepper-step
            editable
            :complete="step > 1"
            step="1"
          >
            Name
          </v-stepper-step>

          <v-divider></v-divider>

          <v-stepper-step
            editable
            :complete="step > 2"
            step="2"
          >
            Label Schema
          </v-stepper-step>

          <v-divider></v-divider>

          <v-stepper-step
            editable
            :complete="step > 3"
            step="3">
            Upload
          </v-stepper-step>

          <v-divider></v-divider>

          <v-stepper-step
            editable
            :complete="step > 4"
            step="4">
            Invite Team
          </v-stepper-step>

          <v-divider></v-divider>
          <v-stepper-step
            editable
            :complete="step > 5"
            step="5">
            Tasks
          </v-stepper-step>

        </v-stepper-header>


        <v-progress-linear
          color="secondary"
          striped
          :value="global_progress"
          height="12"
        >
        </v-progress-linear>


        <v-stepper-items style="height: 100%">

          <v-stepper-content step="1" style="height: 100%">

            <diffgram_select
              v-if="group"
              data_cy="attribute_kind_select"
              :item_list="kind_list"
              v-model="group.kind"
              label="Kind"
              :disabled="loading"
              @input="$emit('input', group)"
              @change="$emit('change')"
            >
            </diffgram_select>

          </v-stepper-content>

          <v-stepper-content step="2" style="height: 100%">

          </v-stepper-content>

          <v-stepper-content step="3" style="height: 100%">

          </v-stepper-content>

          <v-stepper-content step="4" style="height: 100%">
          
          </v-stepper-content>

          <v-stepper-content step="5" style="height: 100%">

          </v-stepper-content>

        </v-stepper-items>

      </v-stepper>

    </v-card-text>
  </v-card>
</template>

<script lang="ts">


import Vue from "vue";

export default Vue.extend( {
  name: 'NewAttributeGroupWizard',
  components:{

  },
  props: {

    'value': {
      default: null
    },
    'kind_list': {
      default: []
    },
    'loading': {
      default: false
    }
  },
  data() {
    return {
      step: 1,
      global_progress: 0,
      project_string_id: null,
      member_invited: false,

      group: {}
    }
  },
  computed: {

  },
  created() {
    this.group = this.value
  },
  watch: {
    value: function (item) {
      this.group = item
    }
  },
  methods: {
    go_to_step: function(step){
      this.step = step
    },
    on_change_step: function(){

    }

  }
}

) </script>
