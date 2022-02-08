/* eslint-disable */
import cloneDeepWith from 'lodash/cloneDeepWith';
import { checkDataType } from './getDataType';

export function deepClone(obj) {
  return cloneDeepWith(obj);
}

/**
 * 时间数组转时间戳
 * @param {*} tArr 时间数组 [年，月，日，时，分，秒]
 */
export function convertTimeArrToMS(tArr = [0, 0, 0, 0, 0, 0]) {
  const timeRule = [12, 30, 24, 60, 60];
  return tArr.reduce((pre, num, index) => {
    const r = timeRule.slice(index).reduce((s, n) => {
      s *= n;
      return s;
    }, 1);
    pre += (r * num);
    return pre;
  }, 0);
}

export  function unique(arr) {
  const res = new Map();
  return arr.filter((arr) => !res.has(arr.id) && res.set(arr.id, 1))
}
/**
 * 时间数组实例化成 x年 x月 x日 x时 x分 x秒
 * @param {*} tArr 时间数组 [年，月，日，时，分，秒]
 */
export function convertTimeArrToString(tArr = []) {
  if (!(tArr instanceof Array)) return;
  const timeRule = ['年', '个月', '天', '小时', '分', '秒'];
  const str = tArr.reduce((str, num, index) => {
    if (num) {
      str += (num + timeRule[index]);
    }
    return str;
  }, '');
  return str || '0秒';
}

/**
 *  将毫秒值转换成x时x分x秒的形式
 *  @param {Number} time - 时间的毫秒形式
 *  @return {String} str - 转换后的字符串
 */
export function convertMStoString(time) {
  function getSeconds(sec) {
    return `${sec}${window.app.$t('m.js[\'秒\']')}`;
  }

  function getMinutes(sec) {
    if (sec / 60 >= 1) {
      return `${Math.floor(sec / 60)}${window.app.$t('m.js[\'分\']')}${getSeconds(sec % 60)}`;
    }
    return getSeconds(sec);
  }

  function getHours(sec) {
    if (sec / 3600 >= 1) {
      return `${Math.floor(sec / 3600)}${window.app.$t('m.js[\'小时\']')}${getMinutes(sec % 3600)}`;
    }
    return getMinutes(sec);
  }

  function getDays(sec) {
    if (sec / 86400 >= 1) {
      return `${Math.floor(sec / 86400)}${window.app.$t('m.js[\'天\']')}${getHours(sec % 86400)}`;
    }
    return getHours(sec);
  }

  return time ? getDays(Math.floor(time / 1000)) : 0;
}

export function isEmpty(val) {
  if (val === 0) {
    return false;
  }
  const type = checkDataType(val);
  let isValid = true;
  switch (type) {
    case 'Array':
      isValid = !val.length;
      break;
    case 'Object':
      isValid = JSON.stringify(val) === '{}';
      break;
    default:
      isValid = !val;
  }
  return isValid;
}
/**
 *
 *  @param {Object} queryObject - 对象形式得参数
 *  @return {String} str - 转换后的字符串
 */
export function getQuery (queryObject) {
  const query = Object.entries(queryObject)
    .reduce((result, entry) => {
      result.push(entry.join('='))
      return result
    }, []).join('&')
  return `?${query}`
}

export function  formatTimer(value) {
  const date = new Date(value);
  const y = date.getFullYear();
  let MM = date.getMonth() + 1;
  MM = MM < 10 ? `0${MM}` : MM;
  let d = date.getDate();
  d = d < 10 ? `0${d}` : d;
  let h = date.getHours();
  h = h < 10 ? `0${h}` : h;
  let m = date.getMinutes();
  m = m < 10 ? `0${m}` : m;
  let s = date.getSeconds();
  s = s < 10 ? `0${s}` : s;
  return `${y}-${MM}-${d} ${h}:${m}:${s}`;
}

/**
 * 匹配 html 字符串中 a 标签是否有 target 属性，没有则加上 target="_blank"
 */
export function appendTargetAttrToHtml (html) {
  return html.replace(/\<a (.*?)\>/g, matchStr => {
    const targetReg = /target\=[\'\"](.*?)[\'\"]/g
    const hasTargetAttr = targetReg.test(matchStr)
    return hasTargetAttr
      ? matchStr
      : matchStr.replace(/.$/, ' target="_blank">')
  })
}
