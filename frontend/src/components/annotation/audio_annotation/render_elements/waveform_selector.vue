<template>
  <div v-cloak style="width: 100%; padding: 20px" >
    <div id="waveform" data-cy="waveform" class="wave-form-container">
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

    <audio class="audio-controls" ref="audio" preload="auto" controls="controls"></audio>

  </div>
</template>

<script lang="ts">

import Vue from "vue";
import WaveSurfer from 'wavesurfer.js';
import Regions from 'wavesurfer.js/dist/plugins/regions.js'

export default Vue.extend({
  name: 'waveform_selector',
  props: {
    audio_file: {
      default: null,
    },
    current_label: {
      type: Object,
      default: null
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
      zoom: 0,
      regions: null,
      disableDragSelection: null,
      // NOTE: regionIdToIsCreatedMap is used to keep track of rendered regions
      regionIdToIsCreatedMap: {},
    }
  },
  watch:{
    zoom: function() {
      this.wavesurfer.zoom(this.zoom)
    },
    instance_list() {
      this.update_render()
    },
    force_watch_trigger: function() {
      this.update_render()
    },
    audio_file: function(new_file, old_file){
      this.load_audio();
    },
    current_label: function() {
      if (this.current_label) {
        const { r, g, b } = this.current_label.colour.rgba
        this.updateRegionColor(r, g, b)
      }
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
      media: this.$refs.audio
    });

    this.regions = this.wavesurfer.registerPlugin(Regions.create())

    this.regions.on('region-updated', this.on_region_update)
    this.regions.on('region-created', this.on_region_create)

    this.regions.on('region-clicked', (region, e) => {
      e.stopPropagation() // prevent triggering a click on the waveform
      region.play()
    })

    if (this.current_label) {
      const { r, g, b } = this.current_label.colour.rgba
      this.updateRegionColor(r, g, b)
    }

    this.load_audio();
    this.update_render()
  },
  unmounted () {
    if (typeof this.disableDragSelection === 'function') {
      this.disableDragSelection()
    }
  },
  methods: {
    update_render: function() {

      const regionsList = this.regions.regions
      // NOTE: initiall used this.regions.regions.map(({id}) => id) to keep track of ids for
      // regions that were added but this.regions.regions take too much time to update which
      // results in same regions get rendered more than once
      const regionsIds = Object.keys(this.regionIdToIsCreatedMap)

      // true if instance doesn't have audiosurfer_id set or has but it's not present
      const instances_to_add = this.instance_list.filter(inst => !inst.audiosurfer_id || !regionsIds.includes(inst.audiosurfer_id))

      instances_to_add.forEach(inst => {
        const { r, g, b } = inst.label_file.colour.rgba

        const added_region = this.regions.addRegion({
            id: inst.audiosurfer_id,
            start: inst.start_time,
            end: inst.end_time,
            color: `rgba(${r}, ${g}, ${b}, 0.5)`
          })

        this.regionIdToIsCreatedMap[added_region.id] = true

        this.$emit('asign_wavesurfer_id', inst.id, added_region.id)
      })

      regionsList.forEach((region, idx) => {
        const instance = this.instance_list.find(inst => inst.audiosurfer_id === region.id)

        if ( instance ) {
          const { start_time, end_time, label_file } = instance
          if (!this.invisible_labels.includes(label_file.id) && !instance.soft_delete ) {
            const { r, g, b } = instance.label_file.colour.rgba
            region.setOptions({
              color: `rgba(${r}, ${g}, ${b}, 0.5)`,
              start: start_time,
              end: end_time,
            })
          } else {
            delete this.regionIdToIsCreatedMap[region.id]
            region.remove()
          }
        } else {
            delete this.regionIdToIsCreatedMap[region.id]
            region.remove()
        }
      })
    },

    updateRegionColor(r, g, b) {
      if (typeof this.disableDragSelection === 'function') {
        this.disableDragSelection()
      }

      this.disableDragSelection = this.regions.enableDragSelection({
        color: `rgba(${r}, ${g}, ${b}, 0.5)`
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

    on_region_create: function(e) {
      const { id, start, end } = e

      this.regionIdToIsCreatedMap[id] = true
      this.$emit('instance_create', id, start, end)
    },

    on_region_update: function(e) {
      const { id, start, end } = e
      this.$emit('instance_update', id, start, end)
    },

    on_audio_ready: function(){
      this.loading_audio = false;
    },
    on_audio_error: function(error_str){
      console.error(error_str)
    }
  },
  beforeDestroy: function () {
    this.wavesurfer.destroy()
  }
})

</script>

<style scoped>

.wave-form-container{
  width: 100%;
}

.audio-controls {
  margin-top: 30px;
  width: 100%;
}

</style>
