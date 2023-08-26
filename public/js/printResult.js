document.getElementById("print").addEventListener("click", () => {
  document.getElementById("print").style.opacity = 0;
  window.print();
  document.getElementById("print").style.opacity = 1;
  // setTimeout(() => {
  // }, 1000);
});
