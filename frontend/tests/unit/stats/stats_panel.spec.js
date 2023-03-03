import Vuex from "vuex";
import { shallowMount, createLocalVue, mount } from "@vue/test-utils";
import stats_panel from "@/components/stats/stats_panel.vue";

const localVue = createLocalVue();
localVue.use(Vuex);

describe("Test stats panel component", () => {
    let props;

    beforeEach(() => {
        props = {
          mocks: {
            $route: {
                params: {
                    job_id: 1
                }
            },
            $store: {
              state: {
                user: {
                  current: {
                      id: 1
                  }
                },
                project: {
                  current: {
                    member_list: []
                  }
                }
              },
            }
          }
        };
      });

    it("Should render all the headers of the stats elements correctly", () => {
      const wrapper = shallowMount(stats_panel, props, localVue);

      const wrapper_text = wrapper.text().toLowerCase()
      expect(wrapper_text).toContain('job progress')
      expect(wrapper_text).toContain('my progress')
    })

    it("Should render two pie charts and user stats", () => {
      const wrapper = shallowMount(stats_panel, {
          data: function() {
          return {
            job_data_fetched: true,
          }
        },
        ...props
      }, localVue);

      expect(wrapper.findAll('pie-chart-stub').length).toBe(2)
    })

    it("Should render user list if data is fetched", () => {
      const wrapper = shallowMount(stats_panel, {
          data: function() {
          return {
            job_data_fetched: true,
          }
        },
        ...props
      }, localVue);

      expect(wrapper.findAll('#member_select').length).toBe(1)
    })
})
