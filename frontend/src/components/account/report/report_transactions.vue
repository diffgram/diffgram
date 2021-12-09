<template>
  <div>

    <v-alert type="error" :value="errors">
      {{errors}}
    </v-alert>

    <v-btn @click="report_api">
      My transactions
    </v-btn>

    <v-btn color="primary"
            dark
            href="https://diffgram.readme.io/docs/billing-intro"
            target="_blank">
      Billing Help
      <v-icon right>mdi-book</v-icon>

    </v-btn>

    <date_picker @date="date = $event">
    </date_picker>


    <line_chart :chart-data="datacollection"
                  :options="options">
    </line_chart>


  </div>
</template>

<script lang="ts">


import axios from 'axios';


  import Vue from "vue"; export default Vue.extend( {
    name: 'report_transactions',
    props: {
      'account': {
        default: {
          id: null
        }
      }
    },
  data() {
    return {
      datacollection: null,

      labels: [],
      values: [],

      date: {},

      options: {
        responsive: true,

        maintainAspectRatio: false,
        scales: {

          xAxes: [{
            type: 'time',
            distribution: 'series',
            time: {
              unit: 'day',
              displayFormats: {
                'day': 'MMM DD'
              }
            },
          }],

          yAxes: [{
            ticks: {
              beginAtZero: true,
              callback: function (value, index, values) {

                // can't use vue js methods here apparently, hence repeating it
                // TODO this doesn't seem to be working / not updating when account changes
                if (this.account && this.account.account_type == "billing") {
                  return '$' + (value / 100).toLocaleString('en-US', {
                    maximumFractionDigits: 2,
                    minimumFractionDigits: 2
                  });
                } else {
                  return value
                }

              }
            }
          }]
        },

        tooltips: {
          callbacks: {
            label: function (tooltipItem, data) {

              let value = tooltipItem.yLabel

              // can't use vue js methods here apparently, hence repeating it
              if (this.account && this.account.account_type == "billing") {
                return '$' + (value / 100).toLocaleString('en-US', {
                  maximumFractionDigits: 2,
                  minimumFractionDigits: 2
                });
              } else {
                return value
              }

            }
          }
        }
      },

      count: 0,

      loading: false,
      errors: null,
      result: null,

      auth: {

      },
      show_auth: false,

      permission_level_list: ['Editor', 'Viewer'],
      permission_level: 'Editor',

    }
  },
  watch: {
    account: function () {
      this.report_api()
    }
  },
  mounted() {

    this.fillData()


  },
  methods: {

    format_money(value) {
      return '$' + (value / 100).toLocaleString('en-US', {
        maximumFractionDigits: 2,
        minimumFractionDigits: 2
      })
    },

    fillData() {
      this.datacollection = {
        labels: this.labels,
        datasets: [
          {
            label: "Value",
            backgroundColor: '#00c853',
            data: this.values
          },

        ]
      }
    },

    report_api: function () {

      this.loading = true
      this.errors = null
      this.result = null

      axios.post(
        '/api/v1/account/' + this.account.id +
        '/report/transactions',
      {
        'date_from': this.date.from,
        'date_to': this.date.to

      }).then(response => {
        let log = response.data.log
        if (log.success == true) {
          this.labels = response.data.labels
          this.values = response.data.values
          this.fillData()
        }
        this.loading = false

      })
      .catch(error => {
        this.loading = false
      });
    }
  }
}

) </script>
