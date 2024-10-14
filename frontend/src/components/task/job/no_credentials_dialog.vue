<template>
  <!-- A dialog component that is displayed when the user doesn't have the required credentials for a task -->
  <v-dialog v-model="is_open" id="no_credentials_dialog" persistent width="800px">
    <v-card elevation="1" class="pa-4" >
      <!-- The title of the dialog -->
      <v-card-title class="d-flex justify-center flex-column">
        <h1 class="font-weight-medium text-center">
          You don't have the credentials for this Task
        </h1>
      </v-card-title>
      <!-- The content of the dialog -->
      <v-card-text class="d-flex align-center justify-center flex-column ">
        <!-- A warning message that lists the required credentials -->
        <h3 class="font-weight-light warning--text">
          You need the following credentials to be able to work:
        </h3>
        <!-- A list of badges that represent the required credentials -->
        <div class="d-flex flex-wrap justify-center align-center">
          <credential_badge v-for="credential in missing_credentials" :credential="credential">
          </credential_badge>
        </div>

        <!-- A button that directs the user to the exams page where they can obtain the required credentials -->
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
// Import the credential badge component
import credential_badge from '../credential/credential_badge'

export default {
  name: "no_credentials_dialog",
  // Register the credential badge component
  components:{
    credential_badge
  },
  // Define the props that this component accepts
  props: {
    missing_credentials:{
      // The missing credentials can be an array of objects or null
      default: null
    }
  },
  // Define the data properties for this component
  data: function(){
    return{
      is_open: false
    }
  },
  // Define the methods for this component
  methods:{
    go_to_exams: function(){
      // Navigate to the exams page
      this.$router.push(`/job/list/?type=exam_template`)
    },
    close(){
      // Reset the input and close the dialog
      this.input = undefined;
      this.is_open = false;
    },
    open() {
      // Open the dialog
      this.is_open = true;
    },
  }
}
</script>

<style scoped>

</style>

