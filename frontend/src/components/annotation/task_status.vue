<template>
  <div v-cloak>
      <v-layout>
          <v-flex>
              <v-card>
                <h3>Task status:</h3>
                <v-stepper
                    v-model="e6"
                    vertical
                    >
                    <v-stepper-step
                        :complete="e6 > 1"
                        step="1"
                        >
                            Pending
                    </v-stepper-step>
                    <v-stepper-step
                        :complete="e6 > 1"
                        step="2"
                    >
                        On review
                    </v-stepper-step>
                    <v-stepper-step
                        :complete="e6 > 1"
                        step="3"
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
}) 
</script>
