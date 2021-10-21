import { shallowMount } from "@vue/test-utils";
import footer from "@/components/footer/footer.vue";

describe("footer.vue", () => {
  it("Render footer component", () => {
    const shouldInclude = "Research Access";
    const wrapper = shallowMount(footer);
    expect(wrapper.text()).toContain(shouldInclude);
  });
});
