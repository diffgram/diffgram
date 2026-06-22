<template>
  <div>

    <!-- Date picker for selecting a start date -->
    <v-layout >
      <v-flex xs12 sm6 md6>
        <v-menu ref="menu_from"
                v-model="menu_from"
                :close-on-content-click="false"
                :nudge-right="40"
                :return-value.sync="date_from"
                transition="scale-transition"
                offset-y
                min-width="290px">

          <!-- Activator slot for displaying the input field and clear button -->
          <template v-slot:activator="{ on }">
            <v-text-field v-on="on"
                          v-model="date_from"
                          label="From"
                          :clearable="true"
                          @click:clear="on_clear_from"
                          prepend-icon="mdi-calendar"
                          readonly>
            </v-text-field>
          </template>

          <!-- Date picker panel for selecting a date -->
          <v-date-picker v-model="date_from" no-title scrollable>
            <v-spacer></v-spacer>

            <!-- Cancel button for closing the date picker panel -->
            <v-btn text color="primary" @click="menu_from = false">Cancel</v-btn>

            <!-- OK button for saving the selected date and emitting an event -->
            <v-btn text color="primary"
                   @click="$refs.menu_from.save(date_from),  emit_date()">OK</v-btn>

          </v-date-picker>
        </v-menu>
      </v-flex>
      <!-- Spacer between the two date pickers -->
      <v-spacer v-if="with_spacer"></v-spacer>

      <!-- Date picker for selecting an end date -->
      <v-flex xs12 sm6 md6>
        <v-menu ref="menu_to"
                v-model="menu_to"
                :close-on-content-click="false"
                :nudge-right="40"
                :return-value.sync="date_to"
                transition="scale-transition"
                offset-y
                min-width="290px">

          <!-- Activator slot for displaying the input field and clear button -->
          <template v-slot:activator="{ on }">
            <v-text-field v-on="on"
                          v-model="date_to"
                          label="To"
                          prepend-icon="mdi-calendar"
                          @click:clear="on_clear_to"
                          :clearable="true"
                          readonly></v-text-field>
          </template>
          <!-- Date picker panel for selecting a date -->
          <v-date-picker v-model="date_to" no-title scrollable>
            <v-spacer></v-spacer>
            <!-- Cancel button for closing the date picker panel -->
            <v-btn text color="primary" @click="menu_to = false">Cancel</v-btn>
            <!-- OK button for saving the selected date and emitting an event -->
            <v-btn text color="primary"
                   @click="$refs.menu_to.save(date_to),
                              emit_date()">
              OK</v-btn>
          </v-date-picker>
        </v-menu>
      </v-flex>
    </v-layout>

  </div>
</template>

<script lang="ts">


import Vue from "vue"; export default Vue.extend( {
  name: 'date_picker',
  props: {
    // Whether to display a spacer between the two date pickers
    with_spacer: {
      default: true,
      type: Boolean
    },
    // Whether to initialize the date pickers with empty values
    initialize_empty:{
      default: false,
      type: Boolean
    }
  },
  data() {
    return {
      // The start date selected in the date picker
      date_from: undefined,
      // Whether the start date picker is open
      menu_from: false,
      // The end date selected in the date picker
      date_to: undefined,
      // Whether the end date picker is open
      menu_to: false

    }
  },
  mounted() {
    // If the date pickers should not be initialized with empty values,
    // set the start and end dates to the current date and the day before,
    // respectively.
    if(!this.$props.initialize_empty){
      this.date_from = new Date(new Date().getTime() - 3*24*60*60*1000).toISOString().substr(0, 10);
      this.date_to = new Date().toISOString().substr(0, 10);
      this.emit_date()
    }

  },
  computed: {
    // An object containing the start and end dates
    date: function () {

      return {
        'from': this.date_from,
        'to': this.date_to
      }

    }
  },
  methods: {
    // Clear the start date and emit an event
    on_clear_from: function(){
      this.date_from = undefined;
      this.emit_date();
    },
    // Clear the end date and emit an event
    on_clear_to: function(){
      this.date_to = undefined;
      this.emit_date();
    },
    // Emit an event with the selected start and end dates
    emit_date: function () {
      this.$emit('date', this.date)
    }
  },


}

) </script>
