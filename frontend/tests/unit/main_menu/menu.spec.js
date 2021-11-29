import Vuex from "vuex";
import { shallowMount, createLocalVue } from "@vue/test-utils";
import menu from "@/components/main_menu/menu.vue";

const localVue = createLocalVue();
localVue.use(Vuex);

describe("Test project dropdown", () => {
    let mockedStore;

    beforeEach(() => {
        mockedStore = {
              $store: {
                state: {
                  user: {
                    logged_in: true,
                    current: {
                        is_super_admin: false
                    }
                  },
                  error: {
                    permission: null
                  },
                  alert: {},
                  builder_or_trainer: { 
                      mode: 'builder'
                    },
                  project: {
                      current: {
                        project_string_id: 0,
                        name: 'Test project'
                      }
                  },
                  project_list: {
                    user_projects_list: [
                        {
                            id: 2,
                            name: 'Test project 1'
                        },
                        {
                            id: 2,
                            name: 'Test project 2'
                        },
                    ]
                  }
                }
              }
            }
    })

    it("Should not render project list if the user is not logged in", () => {
        mockedStore.$store.state.user.logged_in = false
        const wrapper = shallowMount(menu, {
            mocks: mockedStore,
            localVue
          })
        expect(wrapper.html()).not.toContain('Test project')
    })

    it("Should have dropdown in the component", () => {
        const wrapper = shallowMount(menu, {
            mocks: mockedStore,
            localVue
          })
        expect(wrapper.html()).toContain('Test project')
        expect(wrapper.findAll('v-list-item').length).toBe(2)
    })
})