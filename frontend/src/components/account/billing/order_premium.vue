<template>
  <div id="pricing">

    <v-container>

      <v-card>
        <h1 class="pa-4"> Order Premium Now </h1>
        <v-card-title>
          How many users?
        </v-card-title>

        <v-layout>
          <v-slider class="pt-4 pl-4 pr-4"
                    v-model="premium_plan_user_count"
                    min=1
                    :max=max_users
                    thumb-label="always"
                    step=1
                    label="Users">
          </v-slider>

        </v-layout>

        <v-alert type="info"
                 v-if="premium_plan_user_count > 14"
                 outlined
                 dismissible
        >
          Looking for more?
          Enterprise Subscriptions at $4,000/month.
          <a href="https://diffgram.com/contact"
             target="_blank">
            Book A Demo</a>
          or email sales@diffgram.com
        </v-alert>

        <v-layout>

          <v-checkbox class="pl-4 pr-4"
                      v-model="annual_pricing"
                      label="Annual Pricing">
          </v-checkbox>

          <v-checkbox v-model="show_ROI_calculator"
                      label="Show Return on Investment Calculator">
          </v-checkbox>

          <v-text-field class="pl-4 pr-4"
                        label="Promo Code (Optional)"
                        v-model="promo_code">
          </v-text-field>

        </v-layout>


        <v-alert type="success"
                 v-if="annual_pricing">
          Annual Pricing Applied! You saved {{$format_money(annual_savings)}}.
        </v-alert>

        <v-alert type="success"
                 v-if="promo_valid">
          Promo Applied! You saved {{$format_money(savings)}} {{monthly_or_annual}}
        </v-alert>

        <div v-if="show_ROI_calculator">
          <v-card-text class="text--primary">
            <h2 class='pb-4'>
              Estimated ROI {{ROI}} (Returns {{total_return}} {{monthly_or_annual}})
            </h2>

            <div class='pa-4'>
              <bar_chart
                :chart-data="format_chart_data"
                :options="bar_chart_options_non_time_series">
              </bar_chart>
            </div>

            <v-row justify="center" class="pb-4 d-flex justify-space-between ma-auto" style="width: 75%">

              <div>
                <button_with_menu
                  tooltip_message="Explain"
                  button_text="Productivity"
                  color="primary"
                  background="white--text"
                  :close_by_button="true"
                  menu_direction="top"
                  :max_width=500
                >

                  <template slot="content">
                    <v-card elevation=0>
                      <v-card-title>Productivity Benefits</v-card-title>
                      <v-card-text class="text--primary">

                        <ol>
                          <li>
                            <b> Get working faster. </b>
                            Teams start working instantly instead of waiting for each dataset to be ready. This directly
                            saves days off the monthly schedule.
                          </li>

                          <li>
                            <b> Keep working longer. </b>
                            The event driven system means once a pipeline is set up new fresh data is instantly
                            available to annotators. This evens out supervision cycles, making for more even monthly
                            work distribution, reducing daily bottlenecks by up to 40%.
                          <li>

                            <b> Work on the right thing. </b>
                            By focusing on improving existing models, adding new cases, and improving coverage of
                            scenarios. This makes the team more productive in the global sense of the word. Avoid weeks
                            of mistaken, or low value, supervision work!
                          </li>

                        </ol>

                        <br>

                        That’s the tip of the iceberg.
                        Diffgram has an array of features that help make your team more productive, from advanced
                        annotation UIs, to integrated communication on issues, to timely notifications and more.

                      </v-card-text>
                    </v-card>
                  </template>

                </button_with_menu>
              </div>

              <div>
                <button_with_menu
                  tooltip_message="Explain"
                  button_text="Engineering"
                  color="primary"
                  background="white--text"
                  :close_by_button="true"
                  menu_direction="top"
                  :max_width=500
                >

                  <template slot="content">
                    <v-card elevation=0>
                      <v-card-title>Engineering Benefits</v-card-title>
                      <v-card-text class="text--primary">

                        <ol>
                          <li>
                            <b> Less Data Engineering. </b>

                            Using integrations, pre-processing, and the SDK, there is less data engineering work when
                            using Diffgram. This affects both upfront setup costs, and especially ongoing costs for new
                            data. Save 10s of people hours of work every month.

                          <li>
                            <b> Bells and Whistles Included. </b>
                            The brunt of software work is maintenance. Instead of having engineering reinvent the wheel
                            (and the spoke), shift the burden to Diffgram. This helps save engineering focus and the
                            engineering roadmap.

                          <li>

                            <b> Less Engineering Risk. </b>
                            By having one central schema definition for resource definitions engineering reduces errors
                            and better tracks changes. This reduces the potential for major blunders, especially for
                            growing teams.
                          </li>

                        </ol>

                        <br>

                        Diffgram helps coordinate areas of responsibility for different team members. This reduces costs
                        of ad hoc engineering callouts and expensive cross-functional epics. Shift the engineering
                        conversation to how to get the most value out of the data, instead of the plumbing.

                      </v-card-text>
                    </v-card>
                  </template>

                </button_with_menu>
              </div>

              <div>
                <button_with_menu
                  tooltip_message="Explain"
                  button_text="Project"
                  color="primary"
                  background="white--text"
                  :close_by_button="true"
                  menu_direction="top"
                  :max_width=500
                >

                  <template slot="content">
                    <v-card elevation=0>
                      <v-card-title>Project Benefits</v-card-title>
                      <v-card-text class="text--primary">

                        <ol>
                          <li>
                            <b> More Revenue. </b>

                            The combination of productivity and engineering benefits, plus tools like reporting and
                            discussions, help you ship the best overall AI product. Collectively, this does more then
                            reduce costs - it results in a better overall sales and revenue.

                          <li>
                            <b> Less Management Costs.</b>
                            The bigger the projects, the more the people and process challenges. Diffgram provides the
                            blueprints to help organize the work - deeply integrated into every aspect of Diffgram. This
                            lowers leadership and planning costs.

                          </li>
                          <li>

                            <b> An Insurance Policy. </b>
                            Avoid data loss. It’s surprisingly common for data to be worked on, only to realize the
                            wrong labels (or assumptions) were used. People forget what sets contain what assumptions
                            and more. Reduce the risk of an event jeopardizing the entire project.

                          </li>

                        </ol>

                        <br>

                        AI projects are complex. With many moving parts, people, and data. Diffgram substantially
                        improves the overall quality of the AI product, reduces the management costs, and provides a
                        disaster insurance policy.
                      </v-card-text>
                    </v-card>
                  </template>


                </button_with_menu>
              </div>
            </v-row>

            <sub class="pl-4 pr-4">
              ROI Estimate and ROI Calculator are provided "AS IS" and
              are for general information only.
              Diffgram Inc does not promise any specific
              financial return and does NOT guarantee
              you will receive any returns.
            </sub>

          </v-card-text>
        </div>
      </v-card>

      <v-card v-if="show_ROI_calculator">

        <v-card-title> Your ROI Calculator

          <v-spacer></v-spacer>

          <tooltip_button @click="roi_reset"
                          icon="autorenew"
                          :icon_style="true"
                          tooltip_message="Reset">
          </tooltip_button>

        </v-card-title>


        <v-card-text class="text--primary">
          Adjust the sliders to calculate ROI based on
          your own numbers.
        </v-card-text>

        <v-slider class="pa-4"
                  color="primary"
                  label="Monthly Cost Per Fully Loaded Engineer"
                  v-model="monthly_engineering_cost"
                  min=3000
                  max=25000
                  :thumb-size="50"
                  thumb-label="always"
                  step=1000>
          <template v-slot:thumb-label="{ value }">
            {{ '$' + (value).toLocaleString('en-US', {
            maximumFractionDigits: 0,
            minimumFractionDigits: 0
            })
            }}
          </template>
        </v-slider>
        <v-slider class="pa-4"
                  color="primary"
                  label="Monthly Cost Per Supervisor"
                  v-model="monthly_supervisor_cost"
                  min=2000
                  max=10000
                  :thumb-size="50"
                  thumb-label="always"

                  step=500>
          <template v-slot:thumb-label="{ value }">
            {{ '$' + (value).toLocaleString('en-US', {
            maximumFractionDigits: 0,
            minimumFractionDigits: 0
            })
            }}
          </template>
        </v-slider>
        <v-slider class="pa-4"
                  label="Engineering Automation Benefit"
                  v-model="eng_automation_benefit"
                  color="primary"
                  min=.2
                  max=1.5
                  thumb-label="always"
                  step=.1>
        </v-slider>
        <v-slider class="pa-4"
                  label="Annotation Productivity Benefit"
                  v-model="annotation_productivity_benefit"
                  color="primary"
                  min=.1
                  max=2
                  thumb-label="always"
                  step=.1>
        </v-slider>
        <v-slider class="pa-4"
                  label="Annual Project Value"
                  v-model="project_value"
                  color="primary"
                  min=100000
                  max=5000000
                  :thumb-size="70"
                  thumb-label="always"
                  step=25000>
          <template v-slot:thumb-label="{ value }">
            {{ '$' + (value).toLocaleString('en-US', {
            maximumFractionDigits: 0,
            minimumFractionDigits: 0
            })
            }}
          </template>
        </v-slider>
        <v-slider class="pa-4"
                  label="Project Improvement"
                  v-model="project_quality_improvement"
                  color="primary"
                  min=.05
                  max=.5
                  thumb-label="always"
                  step=.025>
        </v-slider>

        <!--
        Total Workforce Cost: {{annotation_workforce_cost}}
        Productivity Value: {{productivity_benefit}}
        Engineering Automation: {{engineering_benefit}}
        Quality Benefit: {{project_quality_improvement_benefit}}
        Total Benefit: {{total_benefit}}
        Total Cost: {{total_whole_dollar_format}}
        Total Net Return: {{total_return}}
        ROI: {{ROI}}
        -->
        <v-checkbox v-model="show_ROI_calculator"
                    label="Show ROI Calculator">
        </v-checkbox>
        <br>
      </v-card>


      <v-card class="mt-5 mb-5">

        <div v-if="install_fingerprint && email">
          <v-card>

            <v-card-title>
              <v-icon size="48" color="primary">mdi-github</v-icon> Open Source Installation Detected:
            </v-card-title>
            <v-card-subtitle class="d-flex align-center">
              <h2 class="mr-2">Install ID:</h2>
              <v-chip color="secondary">{{install_fingerprint}}</v-chip>
              <h2 class="mr-2">Email:</h2>
              <v-chip color="secondary">{{email}}</v-chip>
            </v-card-subtitle>

            <!-- CREDIT CARD -->
            <credit_card show_account_info=false>
            </credit_card>

            <br>
            <br>
          </v-card>
        </div>

        <v-card class="mt-8 mb-4">
          <v-card-text class="text--primary">
            <h2 class="pt-4 pb-2">
              You will be charged {{$format_money(calculated_charge)}}
              USD
              {{monthly_or_annual}}
              for {{premium_plan_user_count}} users
              ({{$format_money(per_user_final)}} / user).
              Cancel anytime.
            </h2>
            <p>
              Questions? sales@diffgram.com

              <!-- Hide help until we update this page-->
              <!--
                <a color="primary"
                    dark
                    href="https://diffgram.readme.io/docs/billing-intro"
                    target="_blank">
                Help</a>
              -->
            </p>

            <sub class="pl-4 pr-4">
              Amounts paid are non-refundable.
              Terms and Conditions Apply.
              See <a href="/policies" targer="_blank"> Policies </a>
            </sub>

          </v-card-text>

          <v-card-actions>

            <v-btn v-if="($store.state.user.logged_in == true) || (install_fingerprint && email)  "
                   color="primary"
                   :disabled="loading"
                   @click="order()"
                   block
            >
              Order
            </v-btn>

          </v-card-actions>

          <v_error_multiple :error="error">
          </v_error_multiple>

        </v-card>

        <div v-if="$store.state.user.logged_in == true && !install_fingerprint && !email">
          <v-card>

            <v-card-title>
              Payment Method
            </v-card-title>

            <!-- CREDIT CARD -->
            <credit_card show_account_info=false>
            </credit_card>

            <br>
            <br>
          </v-card>
        </div>

        <div v-else-if="!$store.state.user.logged_in == true && !install_fingerprint && !email">
          <v-alert type="info"
                   prominent
          >

            Please <a style="color: white"
                      href="/user/login?redirect=%2Forder%2Fpremium"> login</a>
            to finish ordering.

          </v-alert>
        </div>

      </v-card>


      <br>
      <br>
      <br>
      <br>

    </v-container>


    <v-footer bottom><sub class="pa-4"> Terms and Conditions Apply.
      <a href="/policies" targer="_blank"> Policies </a>
      for more info.
      Diffgram uses
      <a href="https://stripe.com/docs/security/stripe" target="_blank">Stripe </a>
    </sub></v-footer>

  </div>
</template>

<script lang="ts">

  import axios from '../../../services/customAxiosInstance';
  import credit_card from './credit_card'

  import Vue from "vue";

  export default Vue.extend({
      name: 'order_premium',
      components: {credit_card},
      data() {
        return {

          show_ROI_calculator: false,
          premium_plan_user_count: 5,
          annual_pricing: false,
          max_users: 20,
          promo_code: '',
          promo_valid: false,
          plan_rate: 12900,  // as integer
          error: {},
          success: false,
          loading: false,
          per_user_final: 0,
          savings: 0,
          annual_savings: 0,
          total: 0,     // cents

          // ROI stuff
          monthly_engineering_cost: 12000,
          monthly_supervisor_cost: 3000,
          eng_automation_benefit: .5,
          annotation_productivity_benefit: .4,
          project_value: 500000,  // annual
          project_quality_improvement: .1,

          marketing_promo_rate_found: null,
          install_fingerprint: null,
          email: null,
          promo_map: {
            'switch': .20,
            'holiday': .30
          },

          bar_chart_options_non_time_series: {
            legend: {
              display: false
            },
            responsive: true,
            maintainAspectRatio: false,
            scales: {
              xAxes: [{
                ticks: {
                  beginAtZero: true
                }
              }],

              yAxes: [{
                ticks: {
                  beginAtZero: true
                }
              }]
            }
          }
        }
      },
      created() {
        if (this.$store.state.user.logged_in == true) {
          this.show_ROI_calculator = true
          // keep focus on ordering
        }
        if (this.$route.query.install_fingerprint) {
          this.install_fingerprint = this.$route.query.install_fingerprint;
        }
        if (this.$route.query.email) {
          this.email = this.$route.query.email;
        }
      },
      computed: {
        calculated_charge() {

          this.plan_rate = 12900
          let savings_rate = 0

          if (this.annual_pricing) {
            this.plan_rate = this.plan_rate * 12
          }

          this.marketing_promo_rate_found = this.promo_map[this.promo_code.toLowerCase()]
          if (this.marketing_promo_rate_found) {
            savings_rate += this.marketing_promo_rate_found
            this.promo_valid = true
          } else {
            this.promo_valid = false
          }

          this.total = this.plan_rate * this.premium_plan_user_count
          // want to keep annual seperate from other promos
          if (this.annual_pricing) {
            this.annual_savings = this.total * .10
            this.total = this.total - this.annual_savings
          }

          this.savings = this.total * savings_rate
          this.total = this.total - this.savings

          this.per_user_final = this.total / this.premium_plan_user_count

          return this.total
        },
        monthly_or_annual() {
          if (this.annual_pricing) {
            return "Annually"
          } else {
            return "Monthly"
          }
        },

        annotation_workforce_cost() {
          let result = this.monthly_supervisor_cost * this.premium_plan_user_count
          return result
        },
        productivity_benefit() {
          let result = this.annotation_workforce_cost * this.annotation_productivity_benefit
          if (this.annual_pricing) {
            result = result * 12
          }
          return result
        },
        engineering_benefit() {
          let result = this.monthly_engineering_cost * this.eng_automation_benefit *
            (.12 * this.premium_plan_user_count)
          if (this.annual_pricing) {
            result = result * 12
          }
          return result
        },
        project_quality_improvement_benefit() {
          let result = (this.project_value / 12) * this.project_quality_improvement *
            (.25 * this.premium_plan_user_count)
          if (this.annual_pricing) {
            result = result * 12
          }
          return result
        },
        total_benefit() {
          let result = this.productivity_benefit + this.engineering_benefit + this.project_quality_improvement_benefit
          // note we don't do annual pricing multipler here becuase we already did it for
          // earlier calculations
          result = Math.round(result)
          return result
        },
        total_whole_dollar_format() {
          return this.total / 100
        },
        total_return() {
          let result = this.total_benefit - this.total_whole_dollar_format
          let formatted_result = '$' + result.toLocaleString('en-US', {
            maximumFractionDigits: 0,
            minimumFractionDigits: 0
          })
          return formatted_result
        },
        ROI() {
          let result = this.total_benefit / this.total_whole_dollar_format
          let formatted_result = result.toLocaleString('en-US', {
            maximumFractionDigits: 0,
            minimumFractionDigits: 0
          }) + "x"
          return formatted_result
        },
        format_chart_data() {
          return {
            labels: [
              "Productivity Benefit",
              "Engineering Benefit",
              "Project Benefit"],
            datasets: [
              {
                //label: "Benefits",
                data: [
                  this.productivity_benefit,
                  this.engineering_benefit,
                  Math.round(this.project_quality_improvement_benefit)],
                backgroundColor: ["green", "blue", "orange"]
              }
            ]
          }
        }

      },
      methods: {

        roi_reset: function () {
          this.monthly_engineering_cost = 12000
          this.monthly_supervisor_cost = 3000
          this.eng_automation_benefit = .5
          this.annotation_productivity_benefit = .4
          this.project_value = 500000  // annual
          this.project_quality_improvement = .1
        },

        order: function () {

          this.loading = true
          this.error = {}

          axios.post('/api/v1/project/'
            + this.$store.state.project.current.project_string_id
            + '/account/plan/new', {

            premium_plan_user_count: this.premium_plan_user_count,
            calculated_charge: this.calculated_charge,
            annual_pricing: this.annual_pricing,
            per_user_final: this.per_user_final,
            email_opensource: this.email,
            install_fingerprint: this.install_fingerprint,

            plan_template_public_name: 'premium',

            promo_code: this.promo_code,
            promo_rate_found: this.promo_rate_found,
            plan_rate: this.plan_rate,
            savings: this.savings,

            roi_monthly_engineering_cost: this.monthly_engineering_cost,
            roi_monthly_supervisor_cost: this.monthly_supervisor_cost,
            roi_project_value: this.project_value,
            roi_eng_automation_benefit: this.eng_automation_benefit,
            roi_annotation_productivity_benefit: this.annotation_productivity_benefit,
            roi_project_quality_improvement: this.project_quality_improvement,

            roi_total_benefit: this.total_benefit,
            roi_multiple: this.multiple

          })
            .then(response => {

              this.success = true
              this.$router.push('/order/success')

            })
            .catch(error => {
              this.loading = false
              this.error = this.$route_api_errors(error)
            });

        }
      }
    }
  ) </script>

