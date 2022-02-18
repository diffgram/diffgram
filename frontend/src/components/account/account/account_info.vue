<template>
  <div>

    <div v-if="show_account_info==true">
      <span class="nickname">{{ account.nickname }}</span>

      <span class="balance">{{ balance_new }}</span>

      <v-select :items="account_list"
                item-text="nickname"
                label="Accounts"
                v-model="account"
                return-object
                @change="change_account()"
                >

      </v-select>
    </div>

  </div>
</template>

<script lang="ts">


import axios from '../../../services/customInstance';


import Vue from "vue";
 export default Vue.extend( {
  name: 'account_info',
  props: {
      'show_account_info' : {
        default: true
      }
    },
  data() {
    return {

      account: {
        id: null,
        nickname: null,
        payment_method_on_file: false
      },

      loading: false,
      errors: null,

      balance_new: 0,

      account_list: []


    }
  },
  mounted() {

    this.account_report_info_api()

  },

  methods: {

    format_money(value) {
      return '$' + (value / 100).toLocaleString('en-US', {
        maximumFractionDigits: 2,
        minimumFractionDigits: 2
      })
    },

    account_report_info_api: function () {

      this.loading = true
      this.errors = null
      this.result = null

      axios.post(
        '/api/v1/account/list',
      {
        'mode_trainer_or_builder': this.$store.state.builder_or_trainer.mode

        }).then(response => {

          let log = response.data.log

          if (log.success == true) {

           if (response.data.account_list[0]) {
             this.account = response.data.account_list[0]

             this.change_account()

             this.account_list = response.data.account_list

            }
          }

        this.loading = false

      })
      .catch(error => {
        this.loading = false
      });
    },

    change_account: function () {

      this.emit_account()

      if (this.account.account_type == "billing") {
        this.balance_new = this.format_money(this.account.transaction_previous.balance_new)
      } else {
        this.balance_new = this.account.transaction_previous.balance_new
      }

    },

    emit_account: function () {
      this.$emit('account', this.account)
    }
  }
}

) </script>
