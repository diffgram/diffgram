<template>
  <div v-cloak style="width: 100%" >
    <div  id="waveform" class="wave-form-container">
    </div>

    <v-progress-linear 
      :playtime-line-width="0.8" 
      indeterminate 
      v-if="loading_audio"
    />

  </div>
</template>

<script lang="ts">

import Vue from "vue";
import WaveSurfer from 'wavesurfer.js';
import RegionPlugin from 'wavesurfer.js/dist/plugin/wavesurfer.regions.min.js';

export default Vue.extend({
  name: 'waveform_selector',
  props: {
    audio_file: {
      default: null,
    },
    current_label: {
      type: Object,
      required: true
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
    },
    current_label: function() {
      this.wavesurfer.disableDragSelection()

      const { r, g, b } = this.current_label.colour.rgba
      this.wavesurfer.enableDragSelection({
        color: `rgba(${r}, ${g}, ${b}, 0.5)`
      })
    }
  },
  mounted() {
    this.wavesurfer = WaveSurfer.create({
      container: '#waveform',
      fillParent: true,
      scrollParent: true,
      waveColor: 'grey',
      progressColor: 'grey',
      normalize: true,
      autoCenter: true,
      mediaControls: true,
      loading_audio: true,
      responsive: true,
      height: 200,
      plugins: [
        RegionPlugin.create()
      ]
    });

    const { r, g, b } = this.current_label.colour.rgba

    this.wavesurfer.enableDragSelection({
      color: `rgba(${r}, ${g}, ${b}, 0.5)`
    })

    this.wavesurfer.on('region-update-end', this.on_annotate)

    this.load_audio();
  },
  methods: {
    load_audio: function(){
      this.loading_audio = true
      if(!this.audio_file || !this.audio_file.audio || !this.audio_file.audio.url_signed){
        return
      }

      this.wavesurfer.load(this.audio_file.audio.url_signed);
      this.wavesurfer.on('ready', this.on_audio_ready);
      this.wavesurfer.on('error', this.on_audio_error);

    },
    on_annotate: function(e) {
      const { id, start, end } = e
      this.$emit('instance_create_update', id, start, end)
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
