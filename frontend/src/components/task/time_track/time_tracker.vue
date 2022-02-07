<template>
  <v-container fluid class="d-flex justify-start align-center">
    <h2 class="font-weight-light">{{formatted_time}}</h2>
  </v-container>
</template>

<script>
export default {
  name: "time_tracker",
  props:{
    "task": {
      default: null
    }
  },
  data: function(){
    return{
      time: 0,
    }
  },
  mounted() {
    let has_time = false;
    this.set_task_tracking(this.$props.task)
    this.start();
  },
  watch: {
    task: function(new_value, old_value){
      console.log('watchhh', new_value)
      this.time = 0;
      clearTimeout(this.timer);
      this.set_task_tracking(new_value);
      this.start();
    }
  },
  computed: {
    formatted_time: function(){
      var date = new Date(0);
      date.setSeconds(this.time); // specify value for SECONDS here
      var timeString = date.toISOString().substr(11, 8);
      return timeString
    }
  },
  methods:{
    set_task_tracking: function(task){
      let current_user_id = this.$store.state.user.current.id;
      if(task && task.time_tracking){
        let record = task.time_tracking.find(elm => elm.user_id === current_user_id);
        if(record){
          this.time = record.time_spent;
        }
        else{
          task.time_tracking.push({
            user_id: current_user_id,
            time_spent: this.time
          })
        }
      }
    },
    start: function(){
      let current_user_id = this.$store.state.user.current.id;
      this.timer = setTimeout(() => {
          if ( document.visibilityState === "visible" && this.$props.task) {
            this.time += 1;
            let record = this.$props.task.time_tracking.find(elm => elm.user_id === current_user_id)
            record.time_spent = this.time;
          }

        this.start()
      }, 1000)
    },
    stop: function(){
      clearTimeout(this.timer);
    },
    set_time: function(){

    },
    save_time: async function(){

    }
  }
}
</script>

<style scoped>

</style>
