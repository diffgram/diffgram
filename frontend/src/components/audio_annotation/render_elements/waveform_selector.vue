<template>
  <div v-cloak style="width: 100%; padding: 20px" >
    <div id="waveform" class="wave-form-container">
      <v-subheader>Zoom</v-subheader>
      <v-slider
        v-model="zoom"
        hint="Drag to change display scale"
        max="1000"
        min="0"
        append-icon="mdi-magnify-plus-outline"
        prepend-icon="mdi-magnify-minus-outline"
      />
    </div>

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
    },
    instance_list: {
      type: Array,
      required: true
    },
    force_watch_trigger: {
      type: Number,
      required: true
    },
    invisible_labels: {
      type: Array,
      default: []
    }
  },
  data: function(){
    return{
      loading_audio: false,
      wavesurfer: null,
      zoom: 0
    }
  },
  watch:{
    zoom: function() {
      this.wavesurfer.zoom(this.zoom)
    },
    force_watch_trigger: function() {
      this.update_render()
    },
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
      progressColor: '#595959',
      normalize: true,
      autoCenter: true,
      mediaControls: true,
      loading_audio: true,
      responsive: true,
      height: 300,
      backend: 'MediaElement',
      plugins: [
        RegionPlugin.create()
      ]
    });

    const { r, g, b } = this.current_label.colour.rgba

    this.wavesurfer.enableDragSelection({
      color: `rgba(${r}, ${g}, ${b}, 0.5)`
    })

    this.wavesurfer.on('region-update-end', this.on_annotate)

    this.wavesurfer.on('region-click', function(region, e) {
        e.stopPropagation();
        region.wavesurfer.play(region.start, region.end);
    });

    this.load_audio();
    this.update_render()
  },
  methods: {
    update_render: function() {
      const region_keys = Object.keys(this.wavesurfer.regions.list)
      const instances_to_add = this.instance_list.filter(inst => !inst.audiosurfer_id || !region_keys.includes(inst.audiosurfer_id))

      instances_to_add.map(inst => {
        const { r, g, b } = inst.label_file.colour.rgba

        const added_region = this.wavesurfer.addRegion({
            id: inst.audiosurfer_id,
            start: inst.start_time,
            end: inst.end_time,
            color: `rgba(${r}, ${g}, ${b}, 0.5)`
          })
        this.$emit('asign_wavesurfer_id', inst.id, added_region.id)
      })

      region_keys.map(key => {
        const instance = this.instance_list.find(inst => inst.audiosurfer_id === key)
        if (instance) {
          const { start_time, end_time, label_file } = instance
          if (!this.invisible_labels.includes(label_file.id)) {
            const { r, g, b } = instance.label_file.colour.rgba
            const region_to_update = this.wavesurfer.regions.list[key]
            region_to_update.color = `rgba(${r}, ${g}, ${b}, 0.5)`
            region_to_update.start = start_time
            region_to_update.end = end_time
            region_to_update.updateRender()
          } else {
            this.wavesurfer.regions.list[key].remove()
          }
        } else {
          this.wavesurfer.regions.list[key].remove()
        }
      })
    },
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
}

</style>
