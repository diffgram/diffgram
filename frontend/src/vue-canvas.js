import Vue from 'vue'

(function () {


  var drawFuncs = {};

  var VueCanvas = {
    draw: function (ctx, vnode, done) {

      var uid = vnode.context._uid;

      var children = vnode.children;

      if (!drawFuncs[uid]) {
        var children = children.filter(function (child) {

          return child.componentOptions !== undefined && child.componentInstance !== undefined;
        });

        children.sort(function (child1, child2) {
          return (parseInt(child1.componentOptions.propsData.ord) || 9999) - (parseInt(child2.componentOptions.propsData.ord) || 9999);
        });

        drawFuncs[uid] = children.map(function (child) {
          return child.componentInstance.draw;
        });
      }
      // else{
      //   var children = children.filter(function (child) {
      //
      //     return child.componentOptions !== undefined && child.componentInstance !== undefined;
      //   });
      //
      //   console.log('      var children = vnode.children;', vnode.children)
      //   console.log('childdd', children)
      //   console.log('uid[uid]', uid)
      //   console.log('drawFuncs[uid]', drawFuncs[uid])
      //
      // }

      var promises = drawFuncs[uid].map(function (draw) {
        return function () {
          return new Promise(function (resolve) {
            draw(ctx, resolve);
          });
        };

      });

      var promise = promises[0]();
      for (var i = 1; i < promises.length; i++) {
        promise = promise.then(promises[i]);
      }
      promise.then(done);
    }
  };

  Vue.directive('canvas', {
    bind: function (el, binding, vnode) {
      var canvas = el;
      var ctx = canvas.getContext('2d');
      if(!ctx.material_icons_loaded){
        const material_font = new FontFace( 'material-icons',
          // pass the url to the file in CSS url() notation
          'url(https://fonts.gstatic.com/s/materialicons/v48/flUhRq6tzZclQEJ-Vdg-IuiaDsNcIhQ8tQ.woff2)' );
        document.fonts.add( material_font ); // add it to the document's FontFaceSet
        // wait the font loads
        material_font.load().then( () => {
          ctx.material_icons_loaded = true;
        }).catch( console.error );
      }
      let canvas_transform = vnode.data.attrs.canvas_transform
      // TODO not clear if this is needed / performance differences
      ctx.clearRect(0, 0, canvas.width , canvas.height);
      ctx.save()

      // using set transform to prevent that double scaling (where it scales image twice)
      // not sure if that's a heavy operation or not but seems to be needed.


      ctx.setTransform(1, 0, 0, 1, 0, 0);
      if(canvas_transform){

        ctx.translate(canvas_transform['translate_previous']['x'], canvas_transform['translate_previous']['y'])
        ctx.scale(canvas_transform['zoom'], canvas_transform['zoom'])
        ctx.translate(-canvas_transform['translate']['x'], -canvas_transform['translate']['y'])

        // maybe skip if scale is == 1?
        if(canvas_transform.canvas_scale_global_x && canvas_transform.canvas_scale_global_y){
          ctx.scale(canvas_transform['canvas_scale_global_x'], canvas_transform['canvas_scale_global_y'])

        }
        else{
          ctx.scale(canvas_transform['canvas_scale_global'], canvas_transform['canvas_scale_global'])

        }

      }


      vnode.children.forEach(function (c) {

        if (c.tag && c.componentInstance && c.elm.localName == "v-canvas-wrapper") {
          var instance = c.componentInstance;
          instance.draw = function (ctx, done) {

            var onRendered = instance.onRendered;
            if (onRendered) {
              done = function () {
                onRendered(ctx, done);
              }
            }
            VueCanvas.draw(ctx, c.componentInstance._vnode, done);
          }
        }

      });

      VueCanvas.draw(ctx, vnode, function () {
        binding.value ? binding.value(ctx) : null;
      });

    },

    update: function (el, binding, vnode) {
      var bind = binding.def.bind;
      bind(el, binding, vnode);
    }
  });

})();
