import { InstanceInterface } from "../../interfaces/InstanceData";
import { Command } from "../command";
import { transform } from 'ol/proj';

export default class UpdateInstanceGeoCoordinatesCommand extends Command {
    private bounds: Array<Array<number>>;
    private lonlat_bounds: Array<Array<number>>;
    private initial_instances: Array<InstanceInterface> = [];
    private radius: number;

    public set_new_geo_coords(bounds: Array<Array<number>>): void {
        this.lonlat_bounds = bounds.map(bound => transform(bound, 'EPSG:3857', 'EPSG:4326'))
        this.bounds = [...bounds];
    }

    public set_new_radius(radius: number): void {
        this.radius = radius
    }

    execute() {
        if (this.initial_instances.length === 0) this.initial_instances = this.instances.map(inst => this._copyInstance(inst))

        this.instances.forEach((_, index, instanceArray) => {
            if (instanceArray[index].type === 'geo_circle' || instanceArray[index].type === "geo_point") {
                instanceArray[index]["coords"] = this.bounds[0]
                instanceArray[index]["lonlat"] = this.lonlat_bounds[0]
                if (this.radius) {
                    instanceArray[index]["radius"] = this.radius
                }
            } else {
                instanceArray[index]["bounds"] = this.bounds
                instanceArray[index]["bounds_lonlat"] = this.lonlat_bounds
            }
        })

        this.instances.map((instance, index) => {
            this.instance_list.replace(instance, this.replacement_indexes[index])
        })
    }

    undo() {
        this.initial_instances.map((instance, index) => {
            const instance_to_modify = this.instance_list.get_all()[this.replacement_indexes[index]]
            if (instance.type === 'geo_circle' || instance.type === "geo_point") {
                instance_to_modify["coords"] = [...instance["coords"]]
                instance_to_modify["lonlat"] = [...instance["lonlat"]]
                if (instance.type === 'geo_circle') {
                    instance_to_modify["radius"] = instance["radius"]
                }
            } else {
                instance_to_modify["bounds"] = [...instance["bounds"]]
                instance_to_modify["bounds_lonlat"] = [...instance["bounds_lonlat"]]
            }
        })
    }
}