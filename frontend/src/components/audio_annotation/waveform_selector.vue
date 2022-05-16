<template>
  <div v-cloak style="width: 100%" >
    <div  id="waveform" class="wave-form-container">

    </div>
    <v-progress-linear indeterminate v-if="loading_audio"></v-progress-linear>
  </div>
</template>

<script lang="ts">

import Vue from "vue";
import WaveSurfer from 'wavesurfer.js';

export default Vue.extend({
  name: 'waveform_selector',
  props: {
    audio_file: {
      default: null,
    }
  },
  data: function(){
    return{
      loading_audio: false,
      wavesurfer: null
    }
  },
  watch:{
    audio_file: function(new_file, old_file){
      this.load_audio();
    }
  },
  mounted() {
    this.wavesurfer = WaveSurfer.create({
      container: '#waveform',
      fillParent: true,
      scrollParent: true,
      waveColor: 'violet',
      progressColor: 'purple',
      normalize: true,
      autoCenter: true,
      mediaControls: true,
      loading_audio: true,
      responsive: true,
      height: 500,
    });
    this.load_audio();
  },
  methods: {
    load_audio: function(){
      this.loading_audio = true
      console.log('trying to load')
      if(!this.audio_file || !this.audio_file.audio || !this.audio_file.audio.url_signed){
        return
      }

      console.log('loading...')
      this.wavesurfer.load(this.audio_file.audio.url_signed);
      this.wavesurfer.on('ready', this.on_audio_ready);
      this.wavesurfer.on('error', this.on_audio_error);

    },
    on_audio_ready: function(){
      this.loading_audio = false;
    },
    on_audio_error: function(error_str){
      console.error(error_str)
    }
  },
})

</script>

<style scoped>

.wave-form-container{
  width: 100%;
  height: 100%;

}

</style>
