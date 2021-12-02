<template>
<div >
<v-col>
  <v-card>
    <v-card-title>
      AI Data Platform
    </v-card-title>
    <v-card-text class="black--text">
      For Data Science & Software Engineering.
      Bring your Team (SaaS or On-Prem). Optionally use The Fully Managed Pro Network
      <a class="pa-4"
          href="https://diffgram.readme.io/docs/create-tasks-for-pro-network"
          target="_blank">
          Learn More About the Pro Network
      </a>
    </v-card-text>
    <v-card-actions>
      <v-btn  color="primary"
              :loading="loading"
              large
              block
              @click="$router.push('/user/data_platform/new')"
              :disabled="loading">
        Data Platform
        <v-icon right> mdi-database </v-icon>
      </v-btn>
    </v-card-actions>
  </v-card>

  <div class="pa-4"> </div>

  <v-card>
    <v-card-title>
      Supervise AI
    </v-card-title>
    <v-card-text class="black--text">
      Supervise AI from home and earn with Diffgram.  
    </v-card-text>
    <v-card-actions>
      <v-btn  color="primary"
              :loading="loading"
              large
              block
              @click="$router.push('/user/pro/new')"
              :disabled="loading">
        For Pros
        <v-icon right> mdi-professional-hexagon </v-icon>
      </v-btn>
    </v-card-actions>
  </v-card>
</v-col>
</div>
</template>

<script lang="ts">

import Vue from "vue";

export default Vue.extend( {
  name: 'user_new_pro_or_data_platform_router',

  components: {
  },

  data () {
    return {
      loading: false
    }
  },
  created() {
    this.$store.commit('builder_or_trainer_clear')
  },
  methods: {

  }
}
) </script>

