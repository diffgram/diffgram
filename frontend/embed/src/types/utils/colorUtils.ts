export function padZero(str: string, len?: number) {
  len = len || 2;
  var zeros = new Array(len).join('0');
  return (zeros + str).slice(-len);
}

export function getContrastColor(hex: string) {
  if (hex.indexOf('#') === 0) {
    hex = hex.slice(1);
  }
  // convert 3-digit hex to 6-digits.
  if (hex.length === 3) {
    hex = hex[0] + hex[0] + hex[1] + hex[1] + hex[2] + hex[2];
  }
  if (hex.length !== 6) {
    throw new Error('Invalid HEX color.');
  }
  // invert color components
  var r = (255 - parseInt(hex.slice(0, 2), 16)).toString(16),
    g = (255 - parseInt(hex.slice(2, 4), 16)).toString(16),
    b = (255 - parseInt(hex.slice(4, 6), 16)).toString(16);
  // pad each with zeros and return
  return '#' + padZero(r) + padZero(g) + padZero(b);
}

export function padEnd(str: string, length: number) {
  var char = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : '0';
  return str + char.repeat(Math.max(0, length - str.length));
}

export function get_random_color() {
  const color = '#' + (Math.random() * 0xFFFFFF << 0).toString(16);
  return color
}

export function chunk(str: string) {
  var size = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : 1;
  var chunked = [];
  var index = 0;

  while (index < str.length) {
    chunked.push(str.substr(index, size));
    index += size;
  }

  return chunked;
}


export function ownKeys(object: any, enumerableOnly: boolean = false) {
  var keys = Object.keys(object);
  if (Object.getOwnPropertySymbols) {
    var symbols = Object.getOwnPropertySymbols(object);
    if (enumerableOnly) symbols = symbols.filter(
      (sym: PropertyKey): boolean | undefined => {
        let property = Object.getOwnPropertyDescriptor(object, sym)
        return property ? property.enumerable : false
      }
    )
    ; // @ts-ignore
    keys.push.apply(keys, symbols);
  }
  return keys;
}

export function _objectSpread(target: string) {
  for (var i = 1; i < arguments.length; i++) {
    var source = arguments[i] != null ? arguments[i] : {};
    if (i % 2) {
      ownKeys(source, true).forEach(
        (key: string) => {
          _defineProperty(target, key, source[key]);
        }
      )
      ;
    } else if (Object.getOwnPropertyDescriptors) {
      Object.defineProperties(target, Object.getOwnPropertyDescriptors(source));
    } else {
      ownKeys(source).forEach(
        (key: string) => {
          const property = Object.getOwnPropertyDescriptor(source, key)
          if (property) {
            Object.defineProperty(target, key, property);
          }

        }
      )
      ;
    }
  }
  return target;
}

export function _defineProperty(obj: any, key: string, value: any) {
  if (key in obj) {
    Object.defineProperty(obj, key, {value: value, enumerable: true, configurable: true, writable: true});
  } else {
    obj[key] = value;
  }
  return obj;
}

export function _slicedToArray(arr: any, i: number) {
  return _arrayWithHoles(arr) || _iterableToArrayLimit(arr, i) || _nonIterableRest();
}

export function _nonIterableRest() {
  throw new TypeError("Invalid attempt to destructure non-iterable instance");
}

export function _iterableToArrayLimit(arr: any, i: number) {
  var _arr = [];
  var _n = true;
  var _d = false;
  var _e = undefined;
  try {
    for (var _i = arr[Symbol.iterator](), _s; !(_n = (_s = _i.next()).done); _n = true) {
      _arr.push(_s.value);
      if (i && _arr.length === i) break;
    }
  } catch (err) {
    _d = true;
    _e = err;
  } finally {
    try {
      if (!_n && _i["return"] != null) _i["return"]();
    } finally {
      if (_d) throw _e;
    }
  }
  return _arr;
}

export function _arrayWithHoles(arr: any) {
  if (Array.isArray(arr)) return arr;
}

export function isCssColor(color: string) {
  return !!color && !!color.match(/^(#|var\(--|(rgb|hsl)a?\()/);
}


export function classToHex(color: string, colors: { [key: string]: any }, currentTheme: string[]) {
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

export function intToHex(color: number) {
  var hexColor = color.toString(16);
  if (hexColor.length < 6) hexColor = '0'.repeat(6 - hexColor.length) + hexColor;
  return '#' + hexColor;
}

/**
 * Converts HSVA to RGBA. Based on formula from https://en.wikipedia.org/wiki/HSL_and_HSV
 *
 * @param color HSVA color as an array [0-360, 0-1, 0-1, 0-1]
 */


export function HSVAtoRGBA(hsva: any) {
  let h = hsva.h,
    s = hsva.s,
    v = hsva.v,
    a = hsva.a;

  let f = (n: number) => {
    let k = (n + h / 60) % 6;
    return v - v * s * Math.max(Math.min(k, 4 - k, 1), 0);
  };

  let rgb = [f(5), f(3), f(1)].map(
    (v) => {
      return Math.round(v * 255);
    }
  )
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


export function RGBAtoHSVA(rgba: any) {
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

export function HSVAtoHSLA(hsva: any) {
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

export function HSLAtoHSVA(hsl: any) {
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

export function RGBAtoCSS(rgba: any) {
  return "rgba(".concat(rgba.r, ", ").concat(rgba.g, ", ").concat(rgba.b, ", ").concat(rgba.a, ")");
}

export function RGBtoCSS(rgba: any) {
  return RGBAtoCSS({...rgba});
}

export function RGBAtoHex(rgba: any) {
  var toHex = (v: number) => {
    var h = Math.round(v).toString(16);
    return ('00'.substr(0, 2 - h.length) + h).toUpperCase();
  };

  return "#".concat([toHex(rgba.r), toHex(rgba.g), toHex(rgba.b), toHex(Math.round(rgba.a * 255))].join(''));
}

export function HexToRGBA(hex: any) {
  // @ts-ignore
  var rgba = (0, chunk)(hex.slice(1), 2).map((c) => {
    return parseInt(c, 16);
  });
  return {
    r: rgba[0],
    g: rgba[1],
    b: rgba[2],
    a: Math.round(rgba[3] / 255 * 100) / 100
  };
}

export function HexToHSVA(hex: any) {
  var rgb = HexToRGBA(hex);
  return RGBAtoHSVA(rgb);
}

export function HSVAtoHex(hsva: any) {
  return RGBAtoHex(HSVAtoRGBA(hsva));
}

export function parseHex(hex: any) {
  if (hex.startsWith('#')) {
    hex = hex.slice(1);
  }

  hex = hex.replace(/([^0-9a-f])/gi, 'F');

  if (hex.length === 3 || hex.length === 4) {
    hex = hex.split('').map((x: number) => {
      return x + x;
    }).join('');
  }

  if (hex.length === 6) {
    // @ts-ignore
    hex = (0, padEnd)(hex, 8, 'F');
  } else {
    // @ts-ignore
    hex = (0, padEnd)((0, padEnd)(hex, 6), 8, 'F');
  }

  return "#".concat(hex).toUpperCase().substr(0, 9);
}

export function parseGradient(gradient: string, colors: string[], currentTheme: string[]) {
  return gradient.replace(/([a-z]+(\s[a-z]+-[1-5])?)(?=$|,)/gi,

  (x) => {
    return classToHex(x, colors, currentTheme) || x;
  }

).replace(/(rgba\()#[0-9a-f]+(?=,)/gi,

  (x) => {
    return 'rgba(' + Object.values(HexToRGBA(parseHex(x.replace(/rgba\(/, '')))).slice(0, 3).join(',');
  }

)
  ;
}

export function RGBtoInt(rgba: any) {
  return (rgba.r << 16) + (rgba.g << 8) + rgba.b;
}

/**
 * Returns the contrast ratio (1-21) between two colors.
 *
 * @param c1 First color
 * @param c2 Second color
 */

