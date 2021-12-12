<template>
<div class="status-button">
    <button_with_menu
          :tooltip_message="display_status.title"
          v-if="view_only_mode != true"
          :color="task_status === 'requires_changes' ? 'red' : color"
          :icon="display_status.icon"
          :close_by_button="true"
          :icon_style="false"
          :text_style="true"
        >
        <template slot="content">
            <v-stepper v-model="step">
                <v-stepper-header>
                    <v-stepper-step :complete="step > 1" step="1">
                        In progress
                    </v-stepper-step>

                    <v-stepper-step v-if="!need_changes" :complete="step > 2" step="2">
                        In review
                    </v-stepper-step>

                    <v-stepper-step :rules="[() => false]" v-else step="2">
                        Requires changes
                    </v-stepper-step>

                    <v-stepper-step :complete="step > 2" step="3">
                        Completed
                    </v-stepper-step>
                </v-stepper-header>
            </v-stepper>
        </template>
    </button_with_menu>
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
        display_status() {
            if (this.task_status === 'review_requested') return { icon: "mdi-archive-eye-outline", title: "In review" }
            if (this.task_status === "requires_changes") return { icon: "mdi-clipboard-alert-outline", title: "Requires changes" }
            if (this.task_status === "complete") return { icon: "mdi-check-circle", title: "Completed" }
            return { icon: "mdi-account-clock-outline", title: "In progress" }
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

<style scoped>
.status-button {
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
}
</style>
