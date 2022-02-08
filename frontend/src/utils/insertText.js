/* eslint-disable*/
/**
 * 在输入框光标处插入字符
 * @param {Object} el dom 元素
 * @param {String} name 唯一标识符，类似 id
 * @param {String} addText 需要插入的字符
 * @param {Object} instance vue 实例 （this）
 */
function insertText(el, name, oldValue, addText, instance) {
  const recordStr = sessionStorage.getItem('cursorIndex');
  const recordJson = recordStr && JSON.parse(recordStr);
  if (
    !el
    || (!el.selectionStart && el.selectionStart !== 0)
    || recordJson.name !== name) {
    return oldValue + addText;
  }
  const { start, end } = recordJson;
  const { scrollTop } = el;
  instance.$nextTick(() => {
    el.selectionStart = start + addText.length;
    el.selectionEnd = start + addText.length;
    el.scrollTop = scrollTop;
    el.focus();
  });
  return oldValue.substr(0, start) + addText + oldValue.substr(end);
}
export default insertText;
