<template>
  <div>

    <v-card>

      <v-card>
        <v-container>

          <v-card-title>
            {{$store.state.user.current.first_name}}, welcome to {{$store.state.project.current.name}}
          </v-card-title>

          <v-card-subtitle>
            Key Concept 101: Task Template
          </v-card-subtitle>

          <v-card-text>
          A Task Template watches Datasets and outputs to a single Dataset.
          Multiple Task Templates may be strung together to create non-linear Data Pipelines.
          This can be done in advance and on demand as the need arises, such as changing Label Templates.
          </v-card-text>

          <div class="pa-4" >
            <v-btn
                   @click="$router.push('/project/' +
        String($store.state.project.current.project_string_id) +
                   '/job/new')"
                   large
                   color="primary">
              Create Task Template
            </v-btn>
          </div>

          <div class="pa-4" >
           <v-btn  href="https://diffgram.readme.io/docs/tasks-introduction"
                   target="_blank"
                   color="primary">
              Guide Me
             <v-icon right> mdi-open-in-new </v-icon>
            </v-btn>
          </div>

          <!-- Would be nice to embed docs here but apparently
            can't -->

        </v-container>
      </v-card>


    </v-card>

  </div>
</template>


<script lang="ts">

import axios from 'axios';


import Vue from "vue"; export default Vue.extend( {
  name: 'welcome_builder',
  props: {

  },

  data () {
    return {


    }
  },
  watch: {

  },
  created() {
  },
  computed: {

  },
  methods: {

  }
}
) </script>
