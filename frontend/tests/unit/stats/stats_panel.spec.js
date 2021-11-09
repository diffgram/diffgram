import Vuex from "vuex";
import { shallowMount, createLocalVue } from "@vue/test-utils";
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

    it("Renders stats panel when no localStorage variable is set", () => {
        const wrapper = shallowMount(stats_panel, props, localVue);
        expect(wrapper.text()).toContain("Hide statistics")
    })

    it("Checks local storage on creation", () => {
        jest.spyOn(window.localStorage.__proto__, 'getItem');
        window.localStorage.__proto__.getItem = jest.fn();
        shallowMount(stats_panel, props, localVue);
        expect(localStorage.getItem).toHaveBeenCalled();
    })

    it("Sets new local storage variable after clicking the button", async () => {
        jest.spyOn(window.localStorage.__proto__, 'setItem');
        window.localStorage.__proto__.setItem = jest.fn();
        const wrapper = shallowMount(stats_panel, props, localVue);
        await wrapper.find('v-btn').trigger('click')
        expect(localStorage.setItem).toHaveBeenCalled();
    })

    it("Renders show stats button when the stats is hidden", () => {
        const wrapper = shallowMount(stats_panel, {
          data: function() {
          return {
            stats_visibility: false,
            
          }
        },
        ...props
      }, localVue);

      expect(wrapper.text().toLowerCase()).toContain("show")
    })

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

      expect(wrapper.findAll('v-menu').length).toBe(1)
    })
})