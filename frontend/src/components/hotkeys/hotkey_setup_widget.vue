<template>
  <div :class="{'active': pressed_key, 'pl-2 pr-2': true, 'value-set': pressed_key && !recording_active}" @click="toggle_recording_active">
    <h3 v-if="pressed_key">{{ key_display }}</h3>
    <div v-else-if="recording_active">
      <v-icon color="red">mdi-record-circle</v-icon>
    </div>
    <div v-else>
      <v-icon>mdi-keyboard</v-icon>
    </div>
  </div>
</template>

<script lang="ts">
import Vue from "vue";

export default Vue.extend({

  name: "hotkey_setup_widget",
  props: {},
  data() {
    return {
      pressed_key: null,
      recording_active: false
    }
  },

  mounted(): void {
  },
  methods: {
    set_recording_active: function(val){
      this.recording_active = val
      if(this.recording_active) {
        this.$store.commit('display_snackbar', {
          text: 'Press The Keys for the Hotkey',
          color: 'primary'
        })
        this.add_keydown_listener()
      } else {
        this.$emit('pressed_key', this.pressed_key)
        this.$store.commit('hide_snackbar', {
          text: 'Press The Keys for the Hotkey. Click The Icon Again to Save.',
          color: 'primary'
        })
        this.remove_keydown_listener()
      }
    },
    toggle_recording_active: function (event: MouseEvent): void {
      console.log('asdasdasd', event)
      event.stopPropagation();
      this.set_recording_active(!this.recording_active);
    },
    remove_keydown_listener: function (): void {
      document.removeEventListener("keydown", this.handle_keydown)
    },
    add_keydown_listener: function (): void {
      document.addEventListener("keydown", this.handle_keydown)
    },
    handle_keydown: function (event: KeyboardEvent): void {
      event.stopPropagation()
      if(this.pressed_key){
        this.pressed_key = {...this.pressed_key, key: event.key, shift: event.shiftKey, alt: event.altKey, ctrl: event.ctrlKey}
      } else{
        this.pressed_key = {key: event.key, shift: event.shiftKey, alt: event.altKey, ctrl: event.ctrlKey}
      }


    }
  },
  computed: {
    key_display: function(){
      if(this.pressed_key) {
        let result = this.pressed_key.key
        if(this.pressed_key.shift) {
          result = "Shift + " + result
        } else if(this.pressed_key.altKey){
          result = "Alt + " + result
        } else if(this.pressed_key.ctrlKey){
          result = "Ctrl + " + result
        }
        return result
      } else {
        return ""
      }
    },
  }
});
</script>

<style scoped>
.active {
  border: 3px solid #1565c0;
  background: #e0e0e0;
}
.value-set {
  border: 4px solid #f0f0f0;
  background: #e0e0e0;
}
</style>

