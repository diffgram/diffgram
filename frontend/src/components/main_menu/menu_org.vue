<template>
<div>

  <!-- Disabled flag is in case there isn't a project ...
       what was this comment??-->

  <!-- By making it != instead of == "trainer"
       it shows the org even on the Trainer signup thing.-->
  <div v-if="$store.state.builder_or_trainer.mode != 'builder'">
    <h2 class="pr-4"> {{ $store.state.org.current.name}} </h2>
  </div>

  <v-menu :disabled="!$store.state.org.current.id"
          v-model="org_menu"
          :nudge-width="100"
          offset-y
          >

    <template v-slot:activator="{ on }">
      <v-btn v-if="$store.state.builder_or_trainer.mode == 'builder'"
             v-on="on"
              color="primary"
              text
              :disabled="false">
      <!-- <v-icon left> mdi-domain </v-icon> -->
        <!-- Leave icon out till decide what todo with builder etc.-->
        {{ $store.state.org.current.name }}
      </v-btn>
    </template>

    <v-card>

      <v-layout column>

        <v-flex >

          <v-btn color="primary"
                  text
                  @click="$router.push('/org/' +
      $store.state.org.current.id
      + '/settings')">
            <v-icon left>mdi-settings</v-icon>
            Settings
          </v-btn>
            

        </v-flex>

        <v-flex>

          <!-- may add another button here -->

        </v-flex>
          

        <v-divider> </v-divider>

      </v-layout>
    </v-card>
  </v-menu>
</div>

</template>

<script lang="ts">


import Vue from "vue"; export default Vue.extend( {
  name: 'main_menu_org',

  components: {
  },

  data() {
    return {

      org_menu: false

    }
  },
  computed: {

  },
  methods: {
    route_my_flow_list() {
      this.$router.push("/project/" +
        this.$store.state.project.current.project_string_id
        + "/flow/list")
    }

  }
}
) </script>
