<template>
  <div id="3d-container">

  </div>

</template>

<script lang="ts">
  import * as THREE from 'three';
  import {WEBGL} from "./WebGL";
  import Vue from "vue";
  import * as THREE from "three";

  export default Vue.extend({
      name: 'canvas_3d',
      components: {

      },
      props: {

      },
      data() {
        return {

        }
      },

      mounted() {
        if ( WEBGL.isWebGLAvailable() ) {
          const scene = new THREE.Scene();
          const camera = new THREE.PerspectiveCamera( 75, window.innerWidth / window.innerHeight, 0.1, 1000 );
          const renderer = new THREE.WebGLRenderer();
          renderer.setSize( window.innerWidth, window.innerHeight );
          document.getElementById('3d-container').appendChild( renderer.domElement );
          const geometry = new THREE.BoxGeometry();
          const material = new THREE.MeshBasicMaterial( { color: 0x00ff00 } );
          const cube = new THREE.Mesh( geometry, material );
          scene.add( cube );

          camera.position.z = 5;
          function animate() {

            requestAnimationFrame( animate );
            cube.rotation.x += 0.01;
            cube.rotation.y += 0.01;
            renderer.render( scene, camera );
          }
          animate();

        } else {
          const warning = WEBGL.getWebGLErrorMessage();
          alert('WebGL is not available on this machine.')

        }
      },
      computed: {

      },
      methods: {


      }
    }
  ) </script>
