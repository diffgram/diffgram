<template>
  <!-- Display an image based on the presence of a logo object -->
  <div v-if="logo">
    <img :src="logo.url_signed"
         :height="height ? `${height}px` : undefined"
         :width="width ? `${width}px` : undefined"
    >
  </div>
  <div v-else>
    <!-- Default image source when logo object is not present -->
    <img src="https://storage.googleapis.com/diffgram-002/public/logo/diffgram_logo_word_only.png"
         :height="height ? `${height}px` : undefined"
         :width="width ? `${width}px` : undefined"
    />
  </div>
</template>

<script lang="ts">

import status from "../status" // Import the status component

import Vue from "vue";
import {get_system_logo} from "../../services/systemConfigs"; // Import the get_system_logo function

export default Vue.extend({

    name: 'Logo', // Set the name of the component
    components: { // Register the status component
      status
    },
    props: ['height', 'width'], // Accept height and width as props
    data() { // Define reactive data properties
      return {
        logo: undefined
      }
    },

    async created() { // Called when the component is created

      await this.get_system_configs() // Call the get_system_configs method
    },
    watch: { // Watch for changes in the component's properties
      logo_refresh: function(){
        this.get_system_configs() // Call the get_system_configs method when logo_refresh changes
      }
    },
    methods: { // Define methods for the component
      get_system_configs: async function () { // Method to fetch system configurations
        try {
          const [logo_data, err] = await get_system_logo() // Call the get_system_logo function
          if (err) {
            console.error(err) // Log any errors
            return
          }
          this.logo = logo_data // Set the logo data
        } catch (e) {
          console.error(e) // Log any errors
        }
      }
    },
    computed: { // Define computed properties for the component
      logo_refresh: function () { // Computed property to return the value of logo_refresh from the store
        return this.$store.state.system.logo_refresh;
      }
    }
  }
) </script>
