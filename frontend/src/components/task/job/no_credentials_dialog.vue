<template>
  <v-dialog v-model="is_open" id="no_credentials_dialog" persistent width="800px">
    <v-card elevation="1" class="pa-4" >
      <v-card-title class="d-flex justify-center flex-column">
        <img class="text-center mt-4 mb-4"
             height="150"
             width="400"
             src="https://github.com/diffgram/diffgram/raw/master/github_assets/DiffgramLogoVECTOR.svg" alt="">
        <h1 class="font-weight-medium">
          You don't have the credentials for this Task
        </h1>
      </v-card-title>
      <v-card-text class="d-flex align-center justify-center flex-column ">
        <h3 class="font-weight-light warning--text">
          You need the following credentials to be able to work:
        </h3>



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
export default {
  name: "no_credentials_dialog",
  props: {
    task_template:{
      default: null
    }
  },
  data: function(){
    return{
      is_open: false
    }
  },
  methods:{
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
