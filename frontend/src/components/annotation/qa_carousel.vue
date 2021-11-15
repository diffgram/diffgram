<template>
    <v-snackbar 
        v-model="annotation_show_on"
        v-if="annotation_show_on"
        timeout="0" 
        :bottom="true"
    >
        <template>
            <v-progress-linear
                :value="annotation_show_progress"
                height="25"
                color="green"
            >
                <strong data-cy="show-progress-bar">
                  {{ 
                    loading ? 
                    "Loading..." : 
                    `${Math.ceil(annotation_show_progress)} %` 
                  }}
                </strong>
            </v-progress-linear>
        </template>
    </v-snackbar>
</template>

<script>
    import Vue from "vue";
    
    export default Vue.extend({
        name: "qa_carousel",
        props: {
            loading: {
                type: Boolean,
                required: true
            },
            instance_list: {
                type: Array,
                required: true
            },
            annotation_show_duration: {
                type: Number,
                required: true
            },
            annotation_show_on: {
                type: Boolean,
                required: true
            }
        },
        data() {
            return {
                annotation_show_progress: 0,
                annotation_show_current_instance: 0,
                annotation_show_timer: null
            }
        },
        watch: {
            annotation_show_on: {
                handler(newVal){
                    if (newVal) setTimeout(() => this.annotation_show(), this.annotation_show_duration)
                },
            }
        },
        methods: {
            annotation_show(instant_transition = false) {
                const {
                    loading,
                    instance_list,
                    annotation_show,
                    annotation_show_on, 
                    annotation_show_timer,
                    annotation_show_duration,
                    annotation_show_current_instance,
                    } = this

                if (!annotation_show_on) return
                if (instant_transition) clearTimeout(annotation_show_timer)
                if (loading) return annotation_show()

                const switch_instance = annotation_show_current_instance < instance_list.length 

                if (switch_instance) {
                    this.annotation_show_progress = (annotation_show_current_instance + 1) / instance_list.length * 100
                    this.$emit('focus_instance', annotation_show_current_instance)
                    this.annotation_show_current_instance = annotation_show_current_instance + 1
                } else {
                    this.annotation_show_current_instance = 0
                    this.annotation_show_progress = 0
                    this.$emit('change_item')
                }

                this.annotation_show_timer = setTimeout(() => {
                    annotation_show()
                }, annotation_show_duration)
            },
            keyboard_events_global_down: function (event) {
                if (event.keyCode === 32 && this.annotation_show_on) {
                    this.$emit('stop_carousel', '')
                }

                if (event.keyCode === 39 && this.annotation_show_on) {
                    this.annotation_show(true)
                }
            },
            add_event_listeners() {
                window.addEventListener('keydown', this.keyboard_events_global_down);
            },
            remove_event_listeners() {
                window.removeEventListener('keydown', this.keyboard_events_global_down);
            }
        },
        mounted() {
            this.add_event_listeners()
        },
        beforeDestroy() {
            this.remove_event_listeners()
        }
    })
</script>
