import * as THREE from "three";


export const create_test_mesh = function () {
  let geometry = new THREE.BoxGeometry(2, 2, 2);
  let material = new THREE.MeshBasicMaterial({
    color: new THREE.Color('red'),
    opacity: 1,
    transparent: true,
  });
  let mesh = new THREE.Mesh(geometry, material);
  return mesh
}
