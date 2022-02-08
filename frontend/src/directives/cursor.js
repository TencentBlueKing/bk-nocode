import Vue from 'vue';

const DEFAULT_OPTIONS = {
  active: true,
  offset: [12, 0],
  cls: 'cursor-element',
};

function init(e, binding) {
  const el = e;
  el.mouseEnterHandler = function () {
    const element = document.createElement('div');
    element.id = 'directive-ele';
    element.style.position = 'absolute';
    element.style.zIndex = binding.value.zIndex || '2501';

    el.element = element;
    document.body.appendChild(element);

    element.classList.add(binding.value.cls || DEFAULT_OPTIONS.cls);
    el.addEventListener('mousemove', el.mouseMoveHandler);
  };
  el.mouseMoveHandler = function (event) {
    const { pageX, pageY } = event;
    const elLeft = pageX + DEFAULT_OPTIONS.offset[0];
    const elTop = pageY + DEFAULT_OPTIONS.offset[1];
    el.element.style.left = `${elLeft}px`;
    el.element.style.top = `${elTop}px`;
  };
  el.mouseLeaveHandler = function () {
    el.element && el.element.remove();
    el.element = null;
    el.removeEventListener('mousemove', el.mouseMoveHandler);
  };
  if (binding.value.active) {
    el.addEventListener('mouseenter', el.mouseEnterHandler);
    el.addEventListener('mouseleave', el.mouseLeaveHandler);
  }
}

function destroy(e) {
  const el = e;
  el.element && el.element.remove();
  el.element = null;
  el.removeEventListener('mouseenter', el.mouseEnterHandler);
  el.removeEventListener('mousemove', el.mouseMoveHandler);
  el.removeEventListener('mouseleave', el.mouseLeaveHandler);
}

Vue.directive('cursor', {
  bind(el, bd) {
    const binding = bd;
    binding.value = Object.assign({}, DEFAULT_OPTIONS, binding.value);
    init(el, binding);
  },
  update(el, bd) {
    const binding = bd;
    binding.value = Object.assign({}, DEFAULT_OPTIONS, binding.value);
    destroy(el);
    init(el, binding);
  },
  unbind(el) {
    destroy(el);
  },
});
