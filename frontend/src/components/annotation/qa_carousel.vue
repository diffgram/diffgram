<template>
    <v-snackbar
        v-model="annotation_show_on"
        v-if="annotation_show_on"
        timeout="0"
        :bottom="true"
    >
        <template>
        <div class="d-flex justify-center align-center">
          <v-btn class="mr-4" v-if="is_paused" icon @click="play"><v-icon>mdi-play</v-icon></v-btn>
          <v-btn class="mr-4" v-else icon @click="pause"><v-icon>mdi-pause</v-icon></v-btn>
          <v-progress-linear
            :value="annotation_show_progress"
            height="25"
            color="green"
          >
            <div class="d-flex justify-center align-center">
              <strong data-cy="show-progress-bar ">
                {{
                  loading ?
                    "Loading..." :
                    `${Math.ceil(annotation_show_progress)} %`
                }}
              </strong>

              <span v-if="annotation_show_progress === 100">
                  <v-icon color="white" class="ml-2">mdi-check-circle-outline</v-icon>
              </span>
            </div>
          </v-progress-linear>
        </div>
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
                annotation_show_previous_instance: 0,
                annotation_show_current_instance: 0,
                annotation_show_timer: null,
                is_paused: false
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
            play: function(){
              this.is_paused = false;
              this.annotation_show()
            },
            pause: function(){
              console.log('PAUSE')
              this.is_paused = true;
              clearTimeout(this.annotation_show_timer)
            },
            annotation_show(instant_transition = false, backwards = false) {
                const {
                    loading,
                    instance_list,
                    annotation_show,
                    annotation_show_on,
                    annotation_show_timer,
                    annotation_show_duration,
                    annotation_show_current_instance,
                    } = this

                if(this.is_paused && !instant_transition){
                  return
                }
                if (!annotation_show_on) return
                if (instant_transition) clearTimeout(annotation_show_timer)
                if (loading) return annotation_show()

                let switch_instance = annotation_show_current_instance < instance_list.length ;
                if(backwards){
                  switch_instance = annotation_show_current_instance > 0;
                }
                if(backwards){
                  if (switch_instance) {
                    this.annotation_show_progress = (annotation_show_current_instance - 1) / instance_list.length * 100
                    this.annotation_show_previous_instance = annotation_show_current_instance;
                    this.annotation_show_current_instance = annotation_show_current_instance - 1
                    this.$emit('focus_instance',  this.annotation_show_current_instance)
                  } else {
                    this.annotation_show_current_instance = instance_list.length - 1
                    this.annotation_show_previous_instance = 0
                    this.annotation_show_progress = 0
                    this.$emit('change_item', "previous")
                  }
                }
                else{
                  if (switch_instance) {
                    this.annotation_show_progress = (annotation_show_current_instance + 1) / instance_list.length * 100

                    this.annotation_show_previous_instance = annotation_show_current_instance;
                    this.annotation_show_current_instance = annotation_show_current_instance + 1
                    this.$emit('focus_instance',  this.annotation_show_current_instance)
                  } else {
                    this.annotation_show_current_instance = 0
                    this.annotation_show_previous_instance = instance_list.length - 1
                    this.annotation_show_progress = 0
                    this.$emit('change_item', "next")
                  }
                }

                if(!this.is_paused){
                  this.annotation_show_timer = setTimeout(() => {
                    if(this.is_paused){
                      return
                    }
                    annotation_show()
                  }, annotation_show_duration)
                }

            },
            keyboard_events_global_down: function (event) {
                if (event.keyCode === 32 && this.annotation_show_on) {
                    if(!this.is_paused){
                      this.pause()
                    }
                    else{
                      this.play()
                    }

                }

                if (event.keyCode === 39 && this.annotation_show_on) {
                    this.annotation_show(true, false)
                    this.is_paused = true;
                }
                if (event.keyCode === 37 && this.annotation_show_on) {
                  this.annotation_show(true, true)
                  this.is_paused = true;
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
