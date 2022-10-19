<template>
  <div
    class="compound-file-container"
    @mouseenter="() => {hovered = true}"
    @mouseleave="() => {hovered = false}"
  >

    <file_preview_details_card
      v-if="show_preview_details"
      :file="file"
      :child_files="child_files"
      :file_preview_height="file_preview_height"
      :file_preview_width="file_preview_width"
    ></file_preview_details_card>
    <drawable_canvas

      v-if="child_files.length > 0 && image_bg"
      ref="drawable_canvas"
      :allow_zoom="false"
      :image_bg="image_bg"
      :canvas_height="file_preview_height"
      :canvas_width="file_preview_width"
      :editable="false"
      :auto_scale_bg="true"
      :refresh="refresh"
      :canvas_wrapper_id="`canvas_wrapper__${file.id}__${file_preview_width}__${file_preview_height}`"
      :canvas_id="`canvas__${file.id}__${file_preview_width}__${file_preview_height}`"
    >

      <instance_list
        slot-scope="props"
        :instance_list="filtered_instance_list"
        :vertex_size="3"
        :refresh="refresh"
        :video_mode="false"
        :label_settings="label_settings"
        :show_annotations="true"
        :draw_mode="false"
        :canvas_transform="props.canvas_transform"
        slot="instance_drawer"
      />

    </drawable_canvas>

  </div>

</template>

<script>
  import Vue from "vue";

  import instance_list from "../vue_canvas/instance_list";
  import drawable_canvas from "../vue_canvas/drawable_canvas";
  import {InstanceContext} from "../vue_canvas/instances/InstanceContext";
  import {get_child_files} from "@/services/fileServices";
  import {filter_global_instance_list} from "@/components/source_control/dataset_explorer_instance_filtering";
  import file_preview_details_card from "./file_preview_details_card";

  export default Vue.extend({
    name: "compound_file_preview",
    components: {
      drawable_canvas,
      file_preview_details_card,
      instance_list
    },
    props: {
      'project_string_id': {
        default: undefined
      },
      'show_preview_details':{
        default: true
      },
      'file': {
        default: undefined
      },
      'file_preview_width': {
        default: 440
      },
      'file_preview_height': {
        default: 325
      },
      'base_model_run': {
        default: null
      },
      'compare_to_model_run_list': {
        default: null
      },
      'show_ground_truth':{
        default: true
      },
      show_video_nav_bar:{
        default: true
      },
      'video':{
        default: null
      },
      'enable_go_to_file_on_click':{
        default: true
      }
    },
    data: function () {
      return {
        image_bg: undefined,
        refresh: null,
        interval: null,
        hovered: false,
        filtered_instance_list: [],
        child_files: [],
        instance_context: new InstanceContext(),
        compare_to_instance_list_set: [],
        file_index: 0,
        label_settings: {
          font_size: 20,
          show_removed_instances: false,
          spatial_line_size: 2,
          show_text: false,
          show_label_text: false,

        }
      }
    },
    created() {
      this.prepare_filtered_instance_list();
    },

    async mounted() {
      await this.fetch_child_files()
      let file = this.child_files[this.file_index]
      if (file) {
        this.set_bg(file)
      }
      this.start_file_thumb_rotation()

    },
    watch: {
      hovered: function(new_val, old_val){
        console.log(
          new_val, 'aksjdlkasjdk'
        )
        if(new_val){
          this.start_file_thumb_rotation()
        }
      },
      file: {
        deep: true,
        handler: async function(new_val, old_val){
          await this.set_bg(new_val);
          this.prepare_filtered_instance_list();
        }
      },
      base_model_run: function () {

        this.prepare_filtered_instance_list();
      },
      compare_to_model_run_list: function () {
        this.prepare_filtered_instance_list();
      },
      show_ground_truth: function(){
        this.prepare_filtered_instance_list();
      }
    },
    methods: {
      prepare_filtered_instance_list: function () {
        this.filtered_instance_list = []
        this.filtered_instance_list = filter_global_instance_list(
          this.filtered_instance_list,
          this.global_instance_list,
          this.$props.base_model_run,
          this.$props.compare_to_model_run_list,
          this.$props.show_ground_truth
        )
      },
      fetch_child_files: async function(){
        let [child_files, err] = await get_child_files(this.project_string_id, this.file.id)
        if (err){
          console.error(err)
          return
        }
        this.child_files = child_files
      },
      start_file_thumb_rotation: async function(){
        if(!this.child_files){
          return
        }
        this.file_index = 0;
        let vm = this;

        while(this.hovered){
          let file = vm.child_files[vm.file_index]
          if (!file) {
            await new Promise((resolve) => setTimeout(resolve, 700));
            continue
          }
          vm.set_bg(file)
          await new Promise((resolve) => setTimeout(resolve, 700));
          vm.file_index += 1
          if(vm.file_index > vm.child_files.length - 1){
            vm.file_index = 0

          }

          await new Promise((resolve) => setTimeout(resolve, 700));
        }


      },
      set_bg: async function (newFile) {
        return new Promise((resolve, reject) => {
          if (!newFile) {
            console.log('NO NEW FILE',newFile)
            this.image_bg = undefined;
            this.refresh = new Date();
            resolve();
          }
          else {
            console.log('NO NEW FILE',newFile)
            if (newFile.image && newFile.image.url_signed) {
              console.log('newFile.image.url_signed',newFile.image.url_signed)
              if(!newFile.html_image){
                const image = new Image();
                image.onload = () => {
                  this.image_bg = image;
                  this.refresh = new Date();
                  console.log('RESOLVE', image)
                  image.onload = () => resolve(image)
                }
                image.src = newFile.image.url_signed;
                image.onerror = reject
              }
              else{
                console.log('image_bg', this.image_bg)
                this.image_bg = newFile.html_image;
                this.refresh = new Date();
                resolve(newFile.html_image);
              }

            }
            else{
              resolve();
            }

          }
        })

      },

    },
    computed:{
    },
  });
</script>

<style>
.drawable-wrapper:hover{
  cursor: pointer;
}
.compound-file-container{
  position: relative;
}
.fade-box{
  background: rgba(0,0,0,0.4) !important;



}

</style>
