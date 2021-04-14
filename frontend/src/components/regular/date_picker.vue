<template>
  <div>

    <v-layout >
      <v-flex xs12 sm6 md6>
        <v-menu ref="menu_from"
                :close-on-content-click="false"
                v-model="menu_from"
                :nudge-right="40"
                :return-value.sync="date_from"

                transition="scale-transition"
                offset-y
                min-width="290px">

          <template v-slot:activator="{ on }">
            <v-text-field v-on="on"
                          v-model="date_from"
                          label="From"
                          :clearable="true"
                          @click:clear="on_clear_from"
                          prepend-icon="event"
                          readonly>
            </v-text-field>
          </template>

          <v-date-picker v-model="date_from" no-title scrollable>
            <v-spacer></v-spacer>

            <v-btn text color="primary" @click="menu_from = false">Cancel</v-btn>

            <v-btn text color="primary"
                   @click="$refs.menu_from.save(date_from),  emit_date()">OK</v-btn>

          </v-date-picker>
        </v-menu>
      </v-flex>
      <v-spacer v-if="with_spacer"></v-spacer>
      <v-flex xs12 sm6 md6>
        <v-menu ref="menu_to"
                :close-on-content-click="false"
                v-model="menu_to"
                :nudge-right="40"
                :return-value.sync="date_to"

                transition="scale-transition"
                offset-y
                min-width="290px">

          <template v-slot:activator="{ on }">
            <v-text-field v-on="on"
                          v-model="date_to"
                          label="To"
                          prepend-icon="event"
                          @click:clear="on_clear_to"
                          :clearable="true"
                          readonly></v-text-field>
          </template>
          <v-date-picker v-model="date_to" no-title scrollable>
            <v-spacer></v-spacer>
            <v-btn text color="primary" @click="menu_to = false">Cancel</v-btn>
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
    with_spacer: {
      default: true,
      type: Boolean
    },
    initialize_empty:{
      default: false,
      type: Boolean
    }
  },
  data() {
    return {

      // 3 is 3 days before
      // see second answer https://stackoverflow.com/questions/10599148/how-do-i-get-the-current-time-only-in-javascript
      date_from: undefined,
      menu_from: false,


      date_to: undefined,
      menu_to: false

    }
  },
  mounted() {

    // we may want to set a default date based on some other paremter.
    if(!this.$props.initialize_empty){
      this.date_from = new Date(new Date().getTime() - 3*24*60*60*1000).toISOString().substr(0, 10);
      this.date_to = new Date().toISOString().substr(0, 10);
      this.emit_date()
    }


  },
  computed: {

    date: function () {

      return {
        'from': this.date_from,
        'to': this.date_to
      }

    },
  },
  methods: {
    on_clear_from: function(){
      this.date_from = undefined;
      this.emit_date();
    },
    on_clear_to: function(){
      this.date_to = undefined;
      this.emit_date();
    },
    emit_date: function () {
      this.$emit('date', this.date)
    }
  },


}

) </script>
