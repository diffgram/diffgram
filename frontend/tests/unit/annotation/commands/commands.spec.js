import { CreateInstanceCommand } from "@/components/annotation/commands/create_instance_command";

describe("Instance creation class", () => {
  let instanceShape;
  let instance;

  beforeEach(() => {
    instanceShape = ["ann_core_ctx", "instance", "frame_number",  "created_instance_index"];
    instance = {
      initialized: false,
      type: "curve",
      points: []
    };
  });

  it("Instance should be null if points is not array", () => {
    instance.points = undefined;
    const newInstance = new CreateInstanceCommand(instance);
    expect(newInstance.instance).toBeNull();
  });

  it("Tests if curve instance has correct shape", () => {
    const newInstance = new CreateInstanceCommand(instance);
    const newInstanceShape = Object.keys(newInstance);
    expect(newInstanceShape).toEqual(instanceShape);
  });
});
