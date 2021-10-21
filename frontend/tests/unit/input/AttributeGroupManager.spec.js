import AttributeGroupManager from "@/components/input/AttributeGroupManager.ts";

describe("footer.vue", () => {
  it("Render footer component", () => {
    const sampleAttributeGroupe = {
      name: "Sample",
      kind: "Test",
      prompt: "Prompt",
      label_file_list: []
    };
    const manager = new AttributeGroupManager();
    const listsEqual = manager.attributes_groups_are_equal(
      sampleAttributeGroupe,
      sampleAttributeGroupe
    );
    expect(listsEqual).toBeTruthy();
  });
});
