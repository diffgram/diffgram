<template>
  <div v-cloak>
      <v-layout>
          <v-flex>
              <v-card>
                <h3>Task status:</h3>
                <v-stepper
                    v-model="step"
                    vertical
                    >
                    <v-stepper-step
                        step="1"
                        :color="color"
                        :complete="step > 1"
                        complete-icon="mdi-check-circle"
                    >
                        In progress
                    </v-stepper-step>
                    <v-stepper-step
                        v-if="!need_changes"
                        step="2"
                        :color="color"
                        :complete="step > 2"
                        complete-icon="mdi-check-circle"
                    >
                        On review
                    </v-stepper-step>
                    <v-stepper-step
                        v-else
                        step="2"
                        :rules="[() => false]"
                    >
                        Changes required
                    </v-stepper-step>
                    <v-stepper-step
                        step="3"
                        :color="color"
                        :complete="step > 2"
                    >
                        Completed
                    </v-stepper-step>
                </v-stepper>
              </v-card>
          </v-flex>
      </v-layout>
  </div>
</template>

<script lang="ts">

import Vue from "vue";

  export default Vue.extend( {
    name: 'task_status',
    props: {
        task_status: {
            type: Boolean,
            required: true
        }
    },
    computed: {
        step() {
            if (this.task_status === 'review_requested' || this.task_status === "requires_changes") return 2
            if (this.task_status === "complete") return 3
            return 1
        },
        need_changes() {
            if (this.task_status === "requires_changes") return true
            return false
        },
        color() {
            if (this.task_status === "complete") return 'green'
            return 'primary'
        }
    }
}) 
</script>
