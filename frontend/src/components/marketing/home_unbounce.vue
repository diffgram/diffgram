<template>
<div v-if="!loading">


</div>
</template>

<script lang="ts">

import Vue from "vue";
import {is_open_source} from '../../services/configService'
export default Vue.extend( {
  name: 'home',

  components: {
  },

  data () {
    return {
      loading: false
    }
  },
  async created() {
    this.loading = true
    console.log(this.$route)
    let result = await is_open_source();
    console.log('is_open_source', result)
    if(this.$route.path === '/' && !result.is_open_source){
      window.location.href = 'https://diffgram.com/main/'
    }
    else{
      if(this.$store.state.user.logged_in == true){
        this.$router.push('/home/dashboard')
      }
      else{
        this.$router.push('/user/login')
      }

    }
    this.loading = false;
  },
  methods: {

  }
}
) </script>

