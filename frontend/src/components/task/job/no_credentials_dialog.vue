<template>
  <v-dialog v-model="is_open" id="no_credentials_dialog" persistent width="800px">
    <v-card elevation="1" class="pa-4" >
      <v-card-title class="d-flex justify-center flex-column">
        <h1 class="font-weight-medium text-center">
          You don't have the credentials for this Task
        </h1>
      </v-card-title>
      <v-card-text class="d-flex align-center justify-center flex-column ">
        <h3 class="font-weight-light warning--text">
          You need the following credentials to be able to work:
        </h3>
        <div class="d-flex flex-wrap justify-center align-center">
          <credential_badge v-for="credential in missing_credentials" :credential="credential">

          </credential_badge>

        </div>


        <v-btn

          @click="go_to_exams"
          outlined
          x-large
          class="mt-4"
          color="secondary">
          <v-icon left>mdi-test-tube</v-icon>
          Go to Exams
        </v-btn>

      </v-card-text>
    </v-card>
  </v-dialog>

</template>

<script>
import credential_badge from '../credential/credential_badge'
export default {
  name: "no_credentials_dialog",
  components:{
    credential_badge
  },
  props: {
    missing_credentials:{
      default: null
    }
  },
  data: function(){
    return{
      is_open: false
    }
  },
  methods:{
    go_to_exams: function(){
      this.$router.push(`/job/list/?type=exam_template`)
    },
    close(){
      this.input = undefined;
      this.is_open = false;
    },
    open() {
      this.is_open = true;
    },
  }
}
</script>

<style scoped>

</style>
