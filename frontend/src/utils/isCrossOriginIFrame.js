export default function isCrossOriginIFrame() {
  try {
    return !window.top.location.hostname;
  } catch (e) {
    return true;
  }
}
