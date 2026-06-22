<template>
  <!-- Display a success alert upon enabling the builder API -->
  <v-container>
    <v-alert type="success" v-if="builder_api_enabled_success"
      >Success! The first step to get started is to create a project.</v-alert
    >
    <!-- A card for creating a new project -->
    <v-card elevation="0">
      <v-card-title>
        <h1 class="headline">Name Your New Project</h1>
      </v-card-title>

      <v-card-text
        >A project is a big deal. It has many Datasets, Users, Tasks, Schema and
        more.</v-card-text
      >

      <!-- Container for the form fields -->
      <v-container>
        <!-- Project name input field -->
        <v-text-field
          label="Name"
          data-cy="project_name"
          v-model="name"
          :rules="[rules.required, rules.name]"
        >
        </v-text-field>

        <!-- Project goal input field -->
        <v-text-field
          label="Goal"
          data-cy="project_goal"
          v-model="goal"
          placeholder="What are you trying to achieve?"
          hint="ie training data for xyz, or build a brain to detect zyx"
        >
        </v-text-field>

        <!-- Organization input field (read-only) -->
        <v-text-field
          v-if="$store.state.org.current.id"
          data-cy="organization"
          label="Org"
          disabled
          v-model="$store.state.org.current.name"
        >
        </v-text-field>

        <!-- Display the project ID -->
        <v-card-text>
          {{ project_string_id_text }}
        </v-card-text>

        <!-- Create project button -->
        <v-btn
          color="success"
          data-cy="create_project_button"
          :loading="loading"
          x-large
          @click.native="loader = 'loading'"
          @click="new_project"
          :disabled="loading"
          >Create</v-btn
        >

        <!-- Error display component -->
        <v_error_multiple :error="error"></v_error_multiple>
      </v-container>
    </v-card>

    <!-- Verify email alert -->
    <div class="pt-2">
      <v-card>
        <v-alert type="info" data-cy="verify_email_alert" outlined
          >Please verify your email.</v-alert
        >
      </v-card>
    </div>
  </v-container>
</template>

<script lang="ts">
import axios from "../../services/customInstance";
import sillyname from "sillyname";
import { getProjectList } from "../../services/projectServices";

import Vue from "vue"; export default Vue.extend({
  name: 'new_project',
  data() {
    return {
      loading: false, // Loading state for the create project button

      name: sillyname().split(" ")[0], // Project name
      goal: null, // Project goal

      builder_api_enabled_success: false, // Success state for enabling the builder API

      error: {}, // Error object for displaying errors

      rules: { // Validation rules for form fields
        required: (value) => !!value || 'Required.',
        name: (value) => {
          const pattern = new RegExp("^[a-zA-Z0-9_ ]{4,30}$")
          return pattern.test(value) || 'No special characters. Between 4 - 30 characters.'
        }
      }
    }
  },
  computed: {
    project_string_id: function () { // Generate a string ID from the project name
      return this.name.replace(/\s+/g, '-').toLowerCase()
    },
    project_string_id_text: function () { // Display the generated string ID
      if (this.name != null) {
        return "Your project ID will be: " + this.project_string_id
      } else {
        return ""
      }
    }
  },
  created() {
    this.builder_api_enabled_success = (this.$route.query["builder_api_enabled_success"] == 'true')
  },
  methods: {
    new_project: function () { // Create a new project

      this.loading = true; // Set loading state to true

      this.error = {} // Reset error object

      axios.post('/api/project/new',
        {

        'project_name': this.name,
        'goal': this.goal,
        'project_string_id': this.project_string_id,
        'org_id': this.$store.state.org.current.id

      }).then(async response => {
        if (response.data.log.success == true) {

          this.$store.commit('set_project', response.data.project) // Set the
