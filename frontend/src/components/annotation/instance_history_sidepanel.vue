<template>
  <v-card class="pa-4 pl-0">
    <v-card-title class="d-flex">
      <span class="flex-grow-1">Instance History</span>
      <v-btn @click="get_instance_history(instance)" icon color="primary"><v-icon>mdi-sync</v-icon></v-btn>
    </v-card-title>
    <v-card-text v-if="loading" class="d-flex justify-center">
      <v-progress-circular color="primary" indeterminate v-if="loading"></v-progress-circular>
    </v-card-text>
   <v-card-text v-if="!loading" 
             style="max-height: 400px;
                    overflow-y: auto">
     <v-list three-line
             dense>
       <template v-for="(item, index) in instance_history_list">
         <v-subheader
           v-if="item.header"
           :key="item.header"
           v-text="item.header"
         ></v-subheader>
         <v-list-item
           dense
           v-else
           :key="item.title"
           class="d-flex"
           @click="open_diff_dialog(index)"
         >
           <v-list-item-avatar>
             <v-chip color="primary">{{item.version}}</v-chip>
           </v-list-item-avatar>


           <v-list-item-content>

             <v-list-item-title v-if="item.action_type === 'edited'">

               <v-icon small v-if="item.action_type === 'edited'" color="warning">mdi-account-edit</v-icon>
               {{`[${item.id}] Instance Edited`}}
             </v-list-item-title>
             <v-list-item-title v-if="item.action_type === 'deleted'">
               <v-icon small v-if="item.action_type === 'deleted'" color="error">mdi-delete-sweep</v-icon>
              {{`[${item.id}] Instance Deleted`}}

             </v-list-item-title>
             <v-list-item-title v-if="item.action_type === 'undeleted'" >
               <v-icon small v-if="item.action_type === 'undeleted'" color="primary">mdi-delete-restore</v-icon>
              {{`[${item.id}] Instance Restored`}}
             </v-list-item-title>
             <v-list-item-title v-if="item.action_type === 'created'">

               <v-icon small v-if="item.action_type === 'created'" color="success">mdi-pencil-plus</v-icon>
                {{`[${item.id}] Instance Created`}}
             </v-list-item-title>

             <v-list-item-subtitle class="d-flex flex-row flex-wrap" style="display: flex">
               <div class="d-flex">
                 <v-chip v-if="item.change_source === 'ui_diffgram_frontend'" color="primary" x-small>UI/WebApp</v-chip>
                 <v-chip v-if="item.change_source === 'api'" color="warning" x-small>API/SDK</v-chip>
                 <v-chip x-small>{{item.created_time | moment("MM-DD-YYYY H:mm:ss a")}}</v-chip>
               </div>
               <div class="d-flex">
                 <span class="font-weight-bold text--primary" style="font-size: 10px">User: </span>
                 <v_user_icon
                              :show_full_name="true"
                              :size="25"
                              font-size="12px !important"
                              :user="item.member_created"></v_user_icon>
               </div>
             </v-list-item-subtitle>
           </v-list-item-content>
         </v-list-item>

         <v-divider
           v-else-if="item.divider"
           :key="index"
           :inset="item.inset"
         ></v-divider>
       </template>
     </v-list>
   </v-card-text>
    <v-card-actions class="d-flex justify-center">
      <v-btn @click="close" icon align="right"> <v-icon>mdi-close</v-icon>Close</v-btn>
    </v-card-actions>
    <instance_diff_dialog ref="diff_dialog" :old_instance="old_instance" :new_instance="new_instance"></instance_diff_dialog>
  </v-card>

</template>

<script>
  import Vue from 'vue';
  import axios from 'axios';
  import instance_diff_dialog from '../annotation/instance_diff_dialog'

  export default Vue.extend({
    name: "instance_history_sidepanel",
    components:{
      instance_diff_dialog
    },
    props: {
      'instance':{
        default: undefined
      },
      'project_string_id':{
        default: undefined
      }
    },
    data: function(){
      return{
        instance_history_list: [],
        new_instance: undefined,
        old_instance: undefined,
        loading: false
      }
    },
    watch:{
      instance: function(newVal, oldVal){
        if(newVal != undefined){
          this.get_instance_history(newVal);
        }
      }
    },
    methods: {
      open_diff_dialog: function(instance_index){
        if(instance_index === 0){
          this.new_instance = this.instance_history_list[instance_index];
          this.old_instance = undefined
        }
        else{
          this.new_instance = this.instance_history_list[instance_index];
          this.old_instance = this.instance_history_list[instance_index - 1];
        }
        this.$refs.diff_dialog.open();

      },
      close: function(){
        this.$emit('close_instance_history_panel');
      },
      get_instance_history: async function(instance){
        if(!instance){
          return
        }
        this.loading = true;
        try{
          const response = await axios.post(`/api/v1/project/${this.$props.project_string_id}/instance/${instance.id}/history`,
            {

            })
          if(response.status === 200){
            this.instance_history_list = response.data.instance_history;
          }
        }
        catch (error) {
          console.error(error)
        }
        finally {
          this.loading = false;
        }
      }
    }
  })
</script>

<style scoped>

</style>
