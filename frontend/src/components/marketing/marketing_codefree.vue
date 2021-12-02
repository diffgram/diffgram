<template>
<div id="home">

  <v-container>
    <v-card>
      <v-layout>
        <v-flex xs12>

          <v-card>

            <h1 class="green--text text--darken-1 text-center pt-4">
              Value from Deep Learning with No Code Required.
            </h1>

            <h2 class="blue--text text--darken-1 text-center pa-2">
              Easy to get started and flexible to scale.
            </h2>
           <h2 class="blue--text text--darken-1 text-center pb-2">
              If you can use a spreadsheet you can use Diffgram.
            </h2>

            
            <div>

              <div class="text-center pt-4 pb-2">

                  <v-btn large color="primary"
                          class="mx-0"
                          dark
                          @click="route_new_account()">
                    Create account
                  </v-btn>

              
                  <v-btn href="https://diffgram.readme.io/docs/actions-beta"
                          target="_blank">
                    <v-icon left>mdi-lifebuoy</v-icon>
                    Getting Started Guide
                  </v-btn>

                <!-- TODO Video Walkthrough -->

              </div>

              <div class="text-center pb-4">
                  Join over 1,100 people using Diffgram today!

              </div>

            </div>


            <img src="https://storage.googleapis.com/diffgram-002/public/marketing/codefree/process_via%20email.svg"
                  width="100%"
                  >

            <!-- See
            https://docs.google.com/document/d/1YFbfm-YCIbrzCch-Uzrqq9mv8-5nCSV6XrlCH_t4xDM/edit
                -->

            <h3 class="black--text text--darken-1 pa-4">

In this example we sent a contract to Diffgram and it returned which pages have not been signed. You can configure it to alert you to all documents that don’t (or do) have something visible. To use it, you and your team forward new contracts to the provided email, and get answers back via email (or can upload through the web interface).             </h3>

              <img src=""
                  width="100%"
                  >

              <img src="https://storage.googleapis.com/diffgram-002/public/marketing/codefree/RIMS%20-%20Raw%20data%20to%20processed%20image%20example%20-%20action%20overlay%20marketing.svg"
                  width="100%"
                  >

              <h3 class="black--text text--darken-1 pa-4">

With Diffgram you can overlay marketing images on top of detections. For example here, we label the type of rim. Then we setup an action that every time that rim is detected, we place the marketing image above it.
              </h3>



              <img src="https://storage.googleapis.com/diffgram-002/public/marketing/codefree/Pathology%20-%20Raw%20data%20to%20processed%20image%20example%20-%20action%20overlay%20marketing.svg"
                  width="100%"
                  >

             <h3 class="black--text text--darken-1 pa-4">

Are you an expert in your field? Apply your business, domain, subject matter knowledge. Create meaning that’s important to you. And embed more than just labels. Setup conditions such as counting examples, and then condition on it. You can use the web interface to record and share the results, and optionally get alerts via email.

             </h3>




            <h1 class="green--text text--darken-1 text-center pt-4">
               Scale with your software team.
            </h1>

            <h2 class="blue--text text--darken-1 text-center pa-2">
              Diffgram supports both your use case, and your software teams.            
            </h2>

             <h2 class="blue--text text--darken-1 text-center pb-2">
              See why software teams choose Diffgram:           
            </h2>


            <div class="text-center pa-4">

              <v-btn large color="primary"
                      class="mx-0"
                      dark
                      @click="route_diffgram_os()">
                Diffgram for Software Teams
              </v-btn>
                
            </div>

            
              <img src="https://storage.googleapis.com/diffgram-002/public/marketing/codefree/Emoji%20-%20Raw%20data%20to%20processed%20image%20example%20-%20action%20overlay%20marketing.svg"
                width="100%"
                >
            


          </v-card>
        </v-flex>

      </v-layout>

    </v-card>
  </v-container>


  <!-- More examples -->

  <marketing_examples>
  </marketing_examples>
    
   

  <v-card>
    <v-container>
      <v-layout>
        <v-flex xs9 md9>
          
          
          <br />
          <br />
          <br />


            <br />
            <br />
            Santa Clara, CA <br />
            Diffgram Inc, a Delaware corporation.

          <br />
          <br />

        </v-flex>
      </v-layout>
    </v-container>
  </v-card>



</div>
</template>

<script lang="ts">


import marketing_examples from './marketing_examples.vue'

import Vue from "vue"; export default Vue.extend( {
  name: 'marketing_code_free',

  components: {
    marketing_examples : marketing_examples
  },
  data () {
    return {

    }
  },
  created() {

  },
  mounted() {

  },

  methods: {
    route_diffgram_os: function () {
      this.$router.push('/marketing/os')
    },
    route_new_account: function () {
      this.$router.push('/user/new')

    }
  }
}
) </script>

