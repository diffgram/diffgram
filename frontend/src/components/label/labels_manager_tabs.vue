<template>
  <div>
    <v-tabs v-model="tab" color="secondary" :style="`height: 100%; width: ${width}`" >
      <v-tab class="d-flex justify-start"
             :data-cy="`tab__${item.name}`"
             v-for="item in header_items" :key="item.name"
             style="border: 1px solid #e0e0e0; border-bottom: none; width: 100%; text-transform: unset">
        <v-icon left>{{ item.icon }}</v-icon>
        <h2 class="font-weight-light"> {{ item.name }} </h2>
      </v-tab>
      <v-tabs-items v-model="tab">
        <v-tab-item>
          <v_labels_view
            v-if="current_schema"
            :schema_id="current_schema ? current_schema.id : undefined"
            :show_edit_templates="true"
            :show_create_samples="true"
            :show_attributes_table="true"
            :project_string_id="project_string_id">
          </v_labels_view>
        </v-tab-item>

        <v-tab-item>
          <attribute_home v-if="current_schema"
                          :schema_id="current_schema ? current_schema.id : undefined"
                          :project_string_id="project_string_id">

          </attribute_home>
        </v-tab-item>

        <v-tab-item>
          <instance_template_list
            v-if="current_schema"
            :schema_id="current_schema ? current_schema.id : undefined"
            :project_string_id="project_string_id"
          ></instance_template_list>
        </v-tab-item>
      </v-tabs-items>
    </v-tabs>
  </div>
</template>

<script>
import {get_schemas} from "@/services/labelServices";
import instance_template_list from '../instance_templates/instance_template_list'
import attribute_home from '../attribute/attribute_home'
export default {
  name: "labels_manager_tabs",
  components:{
    attribute_home,
    instance_template_list,
  },
  props:{
    project_string_id:{
      required: true
    },
    current_schema:{
      default: undefined
    },
    width:{
      default: '850px'
    }
  },
  data:function (){
    return{
      header_items: [
        {name: 'Labels', icon: 'mdi-star-circle'},
        {name: 'Attributes', icon: 'mdi-file-tree'},
        {name: 'Geometries', icon: 'mdi-vector-triangle'}
      ],
      tab: null,
    }
  },
  methods:{

  }
}
</script>

<style scoped>

</style>
