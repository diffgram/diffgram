Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.isCssColor = isCssColor;
exports.classToHex = classToHex;
exports.intToHex = intToHex;
exports.HSVAtoRGBA = HSVAtoRGBA;
exports.RGBAtoHSVA = RGBAtoHSVA;
exports.HSVAtoHSLA = HSVAtoHSLA;
exports.HSLAtoHSVA = HSLAtoHSVA;
exports.RGBAtoCSS = RGBAtoCSS;
exports.RGBtoCSS = RGBtoCSS;
exports.RGBAtoHex = RGBAtoHex;
exports.HexToRGBA = HexToRGBA;
exports.HexToHSVA = HexToHSVA;
exports.HSVAtoHex = HSVAtoHex;
exports.parseHex = parseHex;
exports.parseGradient = parseGradient;
exports.RGBtoInt = RGBtoInt;


function padEnd(str, length) {
  var char = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : '0';
  return str + char.repeat(Math.max(0, length - str.length));
}

export function get_random_color(){
  const color = '#'+(Math.random()*0xFFFFFF<<0).toString(16);
  return color
}

function chunk(str) {
  var size = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : 1;
  var chunked = [];
  var index = 0;

  while (index < str.length) {
    chunked.push(str.substr(index, size));
    index += size;
  }

  return chunked;
}


function ownKeys(object, enumerableOnly) { var keys = Object.keys(object); if (Object.getOwnPropertySymbols) { var symbols = Object.getOwnPropertySymbols(object); if (enumerableOnly) symbols = symbols.filter(function (sym) { return Object.getOwnPropertyDescriptor(object, sym).enumerable; }); keys.push.apply(keys, symbols); } return keys; }

function _objectSpread(target) { for (var i = 1; i < arguments.length; i++) { var source = arguments[i] != null ? arguments[i] : {}; if (i % 2) { ownKeys(source, true).forEach(function (key) { _defineProperty(target, key, source[key]); }); } else if (Object.getOwnPropertyDescriptors) { Object.defineProperties(target, Object.getOwnPropertyDescriptors(source)); } else { ownKeys(source).forEach(function (key) { Object.defineProperty(target, key, Object.getOwnPropertyDescriptor(source, key)); }); } } return target; }

function _defineProperty(obj, key, value) { if (key in obj) { Object.defineProperty(obj, key, { value: value, enumerable: true, configurable: true, writable: true }); } else { obj[key] = value; } return obj; }

function _slicedToArray(arr, i) { return _arrayWithHoles(arr) || _iterableToArrayLimit(arr, i) || _nonIterableRest(); }

function _nonIterableRest() { throw new TypeError("Invalid attempt to destructure non-iterable instance"); }

function _iterableToArrayLimit(arr, i) { var _arr = []; var _n = true; var _d = false; var _e = undefined; try { for (var _i = arr[Symbol.iterator](), _s; !(_n = (_s = _i.next()).done); _n = true) { _arr.push(_s.value); if (i && _arr.length === i) break; } } catch (err) { _d = true; _e = err; } finally { try { if (!_n && _i["return"] != null) _i["return"](); } finally { if (_d) throw _e; } } return _arr; }

function _arrayWithHoles(arr) { if (Array.isArray(arr)) return arr; }

function isCssColor(color) {
  return !!color && !!color.match(/^(#|var\(--|(rgb|hsl)a?\()/);
}



function classToHex(color, colors, currentTheme) {
  var _color$toString$trim$ = color.toString().trim().replace('-', '').split(' ', 2),
    _color$toString$trim$2 = _slicedToArray(_color$toString$trim$, 2),
    colorName = _color$toString$trim$2[0],
    colorModifier = _color$toString$trim$2[1];

  var hexColor = '';

  if (colorName && colorName in colors) {
    if (colorModifier && colorModifier in colors[colorName]) {
      hexColor = colors[colorName][colorModifier];
    } else if ('base' in colors[colorName]) {
      hexColor = colors[colorName].base;
    }
  } else if (colorName && colorName in currentTheme) {
    hexColor = currentTheme[colorName];
  }

  return hexColor;
}

function intToHex(color) {
  var hexColor = color.toString(16);
  if (hexColor.length < 6) hexColor = '0'.repeat(6 - hexColor.length) + hexColor;
  return '#' + hexColor;
}

/**
 * Converts HSVA to RGBA. Based on formula from https://en.wikipedia.org/wiki/HSL_and_HSV
 *
 * @param color HSVA color as an array [0-360, 0-1, 0-1, 0-1]
 */


function HSVAtoRGBA(hsva) {
  var h = hsva.h,
    s = hsva.s,
    v = hsva.v,
    a = hsva.a;

  var f = function f(n) {
    var k = (n + h / 60) % 6;
    return v - v * s * Math.max(Math.min(k, 4 - k, 1), 0);
  };

  var rgb = [f(5), f(3), f(1)].map(function (v) {
    return Math.round(v * 255);
  });
  return {
    r: rgb[0],
    g: rgb[1],
    b: rgb[2],
    a: a
  };
}
/**
 * Converts RGBA to HSVA. Based on formula from https://en.wikipedia.org/wiki/HSL_and_HSV
 *
 * @param color RGBA color as an array [0-255, 0-255, 0-255, 0-1]
 */


function RGBAtoHSVA(rgba) {
  if (!rgba) return {
    h: 0,
    s: 1,
    v: 1,
    a: 1
  };
  var r = rgba.r / 255;
  var g = rgba.g / 255;
  var b = rgba.b / 255;
  var max = Math.max(r, g, b);
  var min = Math.min(r, g, b);
  var h = 0;

  if (max !== min) {
    if (max === r) {
      h = 60 * (0 + (g - b) / (max - min));
    } else if (max === g) {
      h = 60 * (2 + (b - r) / (max - min));
    } else if (max === b) {
      h = 60 * (4 + (r - g) / (max - min));
    }
  }

  if (h < 0) h = h + 360;
  var s = max === 0 ? 0 : (max - min) / max;
  var hsv = [h, s, max];
  return {
    h: hsv[0],
    s: hsv[1],
    v: hsv[2],
    a: rgba.a
  };
}

function HSVAtoHSLA(hsva) {
  var h = hsva.h,
    s = hsva.s,
    v = hsva.v,
    a = hsva.a;
  var l = v - v * s / 2;
  var sprime = l === 1 || l === 0 ? 0 : (v - l) / Math.min(l, 1 - l);
  return {
    h: h,
    s: sprime,
    l: l,
    a: a
  };
}

function HSLAtoHSVA(hsl) {
  var h = hsl.h,
    s = hsl.s,
    l = hsl.l,
    a = hsl.a;
  var v = l + s * Math.min(l, 1 - l);
  var sprime = v === 0 ? 0 : 2 - 2 * l / v;
  return {
    h: h,
    s: sprime,
    v: v,
    a: a
  };
}

function RGBAtoCSS(rgba) {
  return "rgba(".concat(rgba.r, ", ").concat(rgba.g, ", ").concat(rgba.b, ", ").concat(rgba.a, ")");
}

function RGBtoCSS(rgba) {
  return RGBAtoCSS(_objectSpread({}, rgba, {
    a: 1
  }));
}

function RGBAtoHex(rgba) {
  var toHex = function toHex(v) {
    var h = Math.round(v).toString(16);
    return ('00'.substr(0, 2 - h.length) + h).toUpperCase();
  };

  return "#".concat([toHex(rgba.r), toHex(rgba.g), toHex(rgba.b), toHex(Math.round(rgba.a * 255))].join(''));
}

function HexToRGBA(hex) {
  var rgba = (0, chunk)(hex.slice(1), 2).map(function (c) {
    return parseInt(c, 16);
  });
  return {
    r: rgba[0],
    g: rgba[1],
    b: rgba[2],
    a: Math.round(rgba[3] / 255 * 100) / 100
  };
}

function HexToHSVA(hex) {
  var rgb = HexToRGBA(hex);
  return RGBAtoHSVA(rgb);
}

function HSVAtoHex(hsva) {
  return RGBAtoHex(HSVAtoRGBA(hsva));
}

function parseHex(hex) {
  if (hex.startsWith('#')) {
    hex = hex.slice(1);
  }

  hex = hex.replace(/([^0-9a-f])/gi, 'F');

  if (hex.length === 3 || hex.length === 4) {
    hex = hex.split('').map(function (x) {
      return x + x;
    }).join('');
  }

  if (hex.length === 6) {
    hex = (0, padEnd)(hex, 8, 'F');
  } else {
    hex = (0, padEnd)((0, padEnd)(hex, 6), 8, 'F');
  }

  return "#".concat(hex).toUpperCase().substr(0, 9);
}

function parseGradient(gradient, colors, currentTheme) {
  return gradient.replace(/([a-z]+(\s[a-z]+-[1-5])?)(?=$|,)/gi, function (x) {
    return classToHex(x, colors, currentTheme) || x;
  }).replace(/(rgba\()#[0-9a-f]+(?=,)/gi, function (x) {
    return 'rgba(' + Object.values(HexToRGBA(parseHex(x.replace(/rgba\(/, '')))).slice(0, 3).join(',');
  });
}

function RGBtoInt(rgba) {
  return (rgba.r << 16) + (rgba.g << 8) + rgba.b;
}
/**
 * Returns the contrast ratio (1-21) between two colors.
 *
 * @param c1 First color
 * @param c2 Second color
 */

