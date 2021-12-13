import * as THREE from 'three';

export const getCenterPoint = function (mesh) {
  var middle = new THREE.Vector3();
  var geometry = mesh.geometry;

  geometry.computeBoundingBox();

  middle.x = (geometry.boundingBox.max.x + geometry.boundingBox.min.x) / 2;
  middle.y = (geometry.boundingBox.max.y + geometry.boundingBox.min.y) / 2;
  middle.z = (geometry.boundingBox.max.z + geometry.boundingBox.min.z) / 2;

  mesh.localToWorld(middle);
  return middle;
}
