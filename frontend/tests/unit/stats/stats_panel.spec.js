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

    it("Renders right content", () => {
        const wrapper = shallowMount(stats_panel, props, localVue);
        console.log(wrapper.html())
    })
})