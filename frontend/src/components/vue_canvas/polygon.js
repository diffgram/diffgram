import * as math from 'mathjs';

export class Polygon {
  sortPoints(points) {
    // Compute centroid
    const centroid = {
      x: points.reduce((a, b) => a.x + b.x, 0) / points.length,
      y: points.reduce((a, b) => a.y + b.y, 0) / points.length,
    };

    // Sort by polar angle
    points.sort((a, b) => {
      const coords_a = math.atan2(a.y - centroid.y, a.x - centroid.x);
      const coords_b = math.atan2(b.y - centroid.y, b.x - centroid.x);

      if (coords_a < coords_b) {
        return -1;
      }
      if (coords_a > coords_b) {
        return 1;
      }

      return 0;
    });

    return points;
  }

  isInsidePolygon(point, polygon_points) {
    // Ray-casting algorithm based on
    // https://wrf.ecse.rpi.edu/Research/Short_Notes/pnpoly.html/pnpoly.html

    let x = point.x,
      y = point.y;

    let inside = false;
    for (let i = 0, j = polygon_points.length - 1; i < polygon_points.length; j = i++) {
      let xi = polygon_points[i].x,
        yi = polygon_points[i].y;
      let xj = polygon_points[j].x,
        yj = polygon_points[j].y;

      let intersect =
        ((yi > y) !== (yj > y)) &&
        x < ((xj - xi) * (y - yi) / (yj - yi) + xi);

      if (intersect) inside = !inside;
    }

    return inside;
  }
}
