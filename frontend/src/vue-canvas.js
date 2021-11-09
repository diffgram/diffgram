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
  let drawGrid = function (canvas) {
    var ctx = canvas.getContext('2d');
    var padding = 0;
    ctx.save()
    ctx.resetTransform();
    for (var x = 0; x <= canvas.width; x += 10) {
      ctx.moveTo( x + padding, padding);
      ctx.lineTo( x + padding, canvas.height + padding);
    }

    for (var x = 0; x <= canvas.height; x += 10) {
      ctx.moveTo(padding, x + padding);
      ctx.lineTo(canvas.width + padding, x + padding);
    }
    ctx.lineWidth = 1
    ctx.strokeStyle = "gray";
    ctx.stroke()
    ctx.restore();
  };
  Vue.directive('canvas', {
    bind: function (el, binding, vnode) {
      var canvas = el;
      var ctx = canvas.getContext('2d');
      if (!ctx.material_icons_loaded) {
        const material_font = new FontFace('material-icons',
          // pass the url to the file in CSS url() notation
          'url(https://fonts.gstatic.com/s/materialicons/v48/flUhRq6tzZclQEJ-Vdg-IuiaDsNcIhQ8tQ.woff2)');
        document.fonts.add(material_font); // add it to the document's FontFaceSet
        // wait the font loads
        material_font.load().then(() => {
          ctx.material_icons_loaded = true;
        }).catch(console.error);
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
