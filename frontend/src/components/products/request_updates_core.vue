<template>
  <div id="request_updates">
    <v-layout>
      <v-flex xs12>

        <v-card-title primary-title>
          <div>
            <h1 class="headline mb-0">Request {{ request_name }} </h1>
          </div>
        </v-card-title>


        <v-card>
          <v-container>

            <v-text-field label="Email"
                          v-model="email"
                          validate-on-blur
                          :rules="[rules.email]"
                          prepend-icon="email"
                          >
            </v-text-field>


            <v-card-actions>
              <v-btn color="primary"
                     class="mx-0"
                     @click="request_updates"
                     :loading="loading"
                     @click.native="loader = 'loading'"
                     :disabled="loading">
                Request {{ request_name }}
              </v-btn>
            </v-card-actions>

            <v-alert type="success"  v-if="show_success">
              Thanks!
            </v-alert>

          </v-container>

        </v-card>


      </v-flex>
    </v-layout>
  </div>
</template>

<script lang="ts">

  import axios from 'axios';

  import Vue from "vue"; export default Vue.extend( {
    name: 'request_updates_core',

    props: ['request_name'],

    data() {
      return {
        show_success: false,
        loading: false,
        email: null,
        rules: {
          required: (value) => !!value || 'Required.',
          email: (value) => {
            const pattern = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/
            return pattern.test(value) || 'Invalid e-mail.'
          }
        }
      }
    },
    created() {

    },
    methods: {
      request_updates: function () {

        this.loading = true;

        axios.post('/api/products/request_updates', {
          contact: {
            'request_name': this.request_name,
            'request_path_name': this.$route.path,
            'email': this.email
          }
        }).then(response => {
          if (response.data['success'] == true) {
            this.show_success = true
            this.email = null
          }
          this.loading = false
        })
          .catch(error => {
            console.log(error);
            this.loading = false
          });
      }
    }
  }
) </script>

