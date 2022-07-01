<template>
  <div>
      Here we go
  </div>
</template>

<script>
import { get_action_stat } from '../../../../services/actionService'

export default {
  name: "hf_zero_shot_report",
  props: {
    action:{
      required: true,
    },
    project_string_id: {
      required: true
    },
  },
  data (){
    return {}
  },
  async mounted() {
    const stats = await get_action_stat(this.project_string_id, this.action.id)
    console.log(stats)
  },
  methods: {}
}
</script>

<style scoped>

</style>

