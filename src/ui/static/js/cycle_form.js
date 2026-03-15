document.addEventListener("DOMContentLoaded", () => {
  const startInput = document.getElementById("start_day");
  const endInput = document.getElementById("end_day");

  if (!startInput || !endInput) {
    return;
  }

  const syncEndDate = () => {
    const startValue = startInput.value;

    if (!startValue) {
      endInput.removeAttribute("min");
      return;
    }

    endInput.min = startValue;

    if (!endInput.value || endInput.value < startValue) {
      endInput.value = startValue;
    }
  };

  startInput.addEventListener("change", syncEndDate);
});
