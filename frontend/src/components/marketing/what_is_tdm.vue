<template>
<div >
   
  <v-container>
    <v-flex md8>
    <v-card>

      <!--

        Edit in google doc
        https://docs.google.com/document/d/12lwz-KzfKZ_8ERKUS5DbDNN9c-AVK_kwBrwRq8hN1ps/edit#heading=h.ffqtxvq7bvrv

      -->

      <v-container>

        <v-img
        class="white--text align-end"
        height="200px"
        src="https://storage.cloud.google.com/diffgram-002/public/marketing/diffgram_dot_com/path_resized.jpg"
      >
        <v-card-title>TDM 101: What is TDM?</v-card-title>
      </v-img>



       <v-card>
        <v-container>
          <h3 class="pa-2 pt-4"> A basic definition of TDM: </h3>

          <p> Training Data Management (TDM) is a technology for managing
            all of your company’s machine learning data, and people’s interactions
            with that data, and potential data. The goal is to continually
            improve the quality of your training data. A TDM system helps
            you stay connected to where your training data is at, upgrade
            the data, and improve profitability of your data. </p>

            <p>
          When people talk about TDM, they are referring to a TDM system,
                  a tool that helps you with data management, people management,
                  productivity, and more. </p>

                <p>
          A TDM solution helps you focus your organization's relationships with individual data sets - including annotation - throughout the lifecycle of the data, including new data ingestion, initial annotation, iterative annotation and upgrading, and use with machine learning products. 
                  </p>
          </v-container>
        </v-card>

        <v-card>
          <v-container>

            <call_to_action> </call_to_action>
              
          </v-container>
        </v-card>

       <v-card class="white--text" color="blue darken-3">
        <v-container>
          <h3 class="pa-2 pt-4"> Who is TDM for? </h3>

          <p>
          A TDM system gives everyone - from annotators (subject matter experts), software and data engineers, product managers, data scientists, project managers, executive leadership, and other line of business staff - a better way to manage the data that drives machine learning success. A TDM tool lets you store training data and annotation information, upgrade and annotate new data, resolve data issues, and manage data critical products, all in one central location. And makes information about the data available to everyone in your company who needs it.
          </p>

                 <p>
          With visibility and easy access to the data, it’s easier to collaborate and increase productivity. Everyone in the company, with the appropriate permissions, can see how data has been worked with, what needs to be improved, and so much more. TDM can help companies of all sizes drive business growth through machine learning.
          </p>


          <h3 class="pa-2 pt-4"> Here’s why TDM matters to your business. </h3>
          <p>
          Machine learning is as fundamental a change in how software is written as mobile and desktop. Machine learning gives computers the power to see. When you hear Tesla's providing full self-driving cars this is the new technology behind this. 
                </p>

         <p>
            If your business is going to last, you know that you need a strategy for the future. You have goals for your projects - but getting up to date reliable information on progress of machine learning projects can be difficult. How do you translate efforts by individual silos into actionable machine learning products? How do you manage mission critical data efforts that are continually changing, deeply integrated, and implemented across numerous teams?
        </p>

          <p>
          A TDM gives you a clear overview of your data. You can see it all in one place. Creating training data sets historically had been the domain of data science teams and is now becoming a core competency in all areas of the company to adopt. Tools of the past catered exclusively to data science teams, while a TDM is designed for your whole company.
          </p>
         </v-container>
      </v-card>


    <v-card>
      <v-container>
        <h3 class="pa-2 pt-4"> Running a business without TDM can cost you real money. </h3>

         <p>
        More administration means less time for everything else. A machine learning product needs a massive amount of data. Data that can be coming in from multiple sources in different time zones and different teams.
        </p>

        <p>
        Often this valuable information gets siloed into specific teams and formats they happen to be familiar with. Sometimes the relationship between annotations and raw data - the two core ingredients in training data - is never recorded anywhere, and only stored in someone’s mind. What if that person leaves the company?
        </p>

        <p>
        Details can get lost, the meaning of the data can get lost, and ultimately the training data is lost. Even if all of this can be put together, do you really want your highly paid software engineers providing status updates on annotations? Or doing repetitive administrative tasks? Or your subject matter experts bogged down trying to understand technical interfaces not designed for them? 
        </p>

      </v-container>
      </v-card>


    <v-card>
      <v-container>

        <call_to_action> </call_to_action>
              
      </v-container>
    </v-card>


    <v-card class="white--text" color="blue darken-3">
      <v-container>

            <h3 class="pa-2 pt-4">
        What does a TDM system do?
              </h3>

         <p>
        A Training Data Management (TDM) solution helps you discover what data needs to be upgraded, upgrade the data, and continually improve the quality of your data. This results in faster time to market on your machine learning efforts and better results.
        </p>

        <p>
        TDM systems start by collecting data - often images and videos - through drag and drop interfaces, spreadsheets, SDK integrations, and API endpoints. Project leaders work with subject matter experts (SMEs) to define meaningful categories, attributes, and other representations for the data.  SMEs work on the data, upgrading the raw data by adding annotations of it’s meaning. The software team accesses the upgraded data to build machine learning products. 
        </p>

        <h3 class="pa-2 pt-4">
        Work from anywhere
        </h3>

              <p>
        Cloud-based TDM systems such as Diffgram mean every user has the same information, all the time. Cloud computing revolution changed everything. Freed from the need to install software on hundreds or thousands of desktop computers and mobile devices, organizations worldwide are discovering the benefits of moving data, software, and services into a secure online environment.
        </p>

              <h3 class="pa-2 pt-4">
        A cloud based TDM system offers you:
              </h3>

        <ul>
          <li> Faster deployment </li>
        <li> Automatic updates </li>
         <li>  Cost-effectiveness and scalability </li>
         <li>  Increased collaboration </li>
         <li>  Central data storage </li>
        </ul>
      

        </v-container>
      </v-card>

      </v-container>
    </v-card>

   </v-flex>
  </v-container>

</div>
</template>

<script lang="ts">


import Vue from "vue";
import call_to_action from './call_to_action'

export default Vue.extend( {
  name: 'what_is_tdm',
  components: {
    call_to_action
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

  }
}
) </script>

