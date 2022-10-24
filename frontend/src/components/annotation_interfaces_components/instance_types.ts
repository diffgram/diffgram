export interface InstanceType {
    name: string;
    display_name: string;
    icon: string;
}

const image_video: Array<InstanceType> = [
    { 
        name: "box", 
        display_name: "Box", 
        icon: "mdi-checkbox-blank" 
    },
    {
      name: "polygon",
      display_name: "Polygon",
      icon: "mdi-vector-polygon",
    },
    { 
        name: "tag", 
        display_name: "Tag", 
        icon: "mdi-tag" 
    },
    { 
        name: "point", 
        display_name: "Point", 
        icon: "mdi-circle-slice-8" 
    },
    { 
        name: "line", 
        display_name: "Fixed Line", 
        icon: "mdi-minus" 
    },
    { 
        name: "cuboid", 
        display_name: "Cuboid 2D", 
        icon: "mdi-cube-outline" 
    },
    {
      name: "ellipse",
      display_name: "Ellipse & Circle",
      icon: "mdi-ellipse-outline",
    },
    {
      name: "curve",
      display_name: "Curve Quadratic",
      icon: "mdi-chart-bell-curve-cumulative",
    },
]

export default {
    image_video
}